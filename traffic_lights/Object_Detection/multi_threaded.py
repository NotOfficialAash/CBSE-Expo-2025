import cv2
import time
import serial
import threading
from collections import defaultdict
from ultralytics import solutions

# Connect to Arduino
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)

# Shared signal info
current_green = "A"
last_switch_time = time.time()
traffic_counts = {"A": 0, "B": 0, "C": 0}
lock = threading.Lock()

# Send command to Arduino
def send_command(cmd):
    arduino.write((cmd + "\n").encode())
    print("Sent:", cmd)
    time.sleep(0.05)

def set_signal_state(signal, red, green):
    send_command(f"{signal}_R_{'ON' if red else 'OFF'}")
    send_command(f"{signal}_G_{'ON' if green else 'OFF'}")

def set_yellow(signal, state):
    send_command(f"{signal}_Y_{'ON' if state else 'OFF'}")

def get_next_signal(current):
    return {"A": "B", "B": "C", "C": "A"}[current]

def switch_signal_with_yellow(prev_signal, next_signal):
    # Yellow transition
    set_signal_state(prev_signal, red=False, green=False)
    set_yellow(prev_signal, True)
    time.sleep(2)
    set_yellow(prev_signal, False)
    set_signal_state(prev_signal, red=True, green=False)

    set_signal_state(next_signal, red=False, green=False)
    set_yellow(next_signal, True)
    time.sleep(2)
    set_yellow(next_signal, False)
    set_signal_state(next_signal, red=False, green=True)

def arduino_close():
    set_signal_state("A", red=False, green=False)
    set_signal_state("B", red=False, green=False)
    set_signal_state("C", red=False, green=False)

# 🚦 Worker thread: Handles Arduino switching independently
def signal_controller():
    global current_green, last_switch_time
    while True:
        time.sleep(1)
        with lock:
            tA, tB, tC = traffic_counts["A"], traffic_counts["B"], traffic_counts["C"]
            duration_A = 9 if tA > 1 else 4
            duration_B = 9 if tB > 1 else 4
            duration_C = 9 if tC > 1 else 4
            active_duration = {"A": duration_A, "B": duration_B, "C": duration_C}[current_green]

            if time.time() - last_switch_time >= active_duration:
                next_green = get_next_signal(current_green)
                switch_signal_with_yellow(current_green, next_green)
                current_green = next_green
                last_switch_time = time.time()

# 🔁 Region Counter setup
capture = cv2.VideoCapture("test_rec.mp4")
region_points = {
    "Zone A": [(10, 10), (600, 10), (600, 840), (10, 840)],
    "Zone B": [(610, 10), (800, 10), (800, 840), (610, 840)],
    "Zone C": [(810, 10), (1200, 10), (1200, 840), (810, 840)]
}

w, h, fps = (int(capture.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("count.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps or 30, (w, h))

regioncounter = solutions.RegionCounter(
    show=False,
    region=region_points,
    model="yolo11n.pt",
    classes=[1, 2, 3, 5, 7],
    conf=0.1
)

# Initial signal state
set_signal_state("A", red=False, green=True)
set_signal_state("B", red=True, green=False)
set_signal_state("C", red=True, green=False)

# ✅ Start Arduino signal thread
controller_thread = threading.Thread(target=signal_controller, daemon=True)
controller_thread.start()

# 🧠 Main YOLO + Frame Loop
while capture.isOpened():
    success, frame = capture.read()
    if not success:
        print("Video File Not Found or Stream Ended")
        arduino_close()
        break

    results = regioncounter(frame)
    annotated_frame = results.plot_im

    region_object_counts = defaultdict(int)
    for box, cls, track_id in zip(regioncounter.boxes, regioncounter.clss, regioncounter.track_ids):
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        point = regioncounter.Point((cx, cy))
        for region in regioncounter.counting_regions:
            if region["prepared_polygon"].contains(point):
                region_name = region["name"]
                region_object_counts[region_name] += 1

    # Update shared traffic count safely
    with lock:
        traffic_counts["A"] = region_object_counts.get("Zone A", 0)
        traffic_counts["B"] = region_object_counts.get("Zone B", 0)
        traffic_counts["C"] = region_object_counts.get("Zone C", 0)

    print(traffic_counts)

    video_writer.write(annotated_frame)
    cv2.imshow("Region Counter", annotated_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting by user input")
        arduino_close()
        break

# Cleanup
capture.release()
video_writer.release()
cv2.destroyAllWindows()
