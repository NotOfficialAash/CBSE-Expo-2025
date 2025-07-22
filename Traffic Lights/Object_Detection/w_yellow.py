import cv2
import time
import serial
from collections import defaultdict
from ultralytics import solutions

# Connect to Arduino
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)

# Start with Signal A green
current_green = "A"
last_switch_time = time.time()

# Send command to Arduino
def send_command(cmd):
    arduino.write((cmd + "\n").encode())
    print("Sent:", cmd)
    time.sleep(0.05)

# Control red and green lights
def set_signal_state(signal, red, green):
    send_command(f"{signal}_R_{'ON' if red else 'OFF'}")
    send_command(f"{signal}_G_{'ON' if green else 'OFF'}")

# Control yellow light
def set_yellow(signal, state):
    send_command(f"{signal}_Y_{'ON' if state else 'OFF'}")

# Get next signal
def get_next_signal(current):
    return {"A": "B", "B": "C", "C": "A"}[current]

# Switch signals with yellow transition
def switch_signal_with_yellow(prev_signal, next_signal):
    # Step 1: Turn off green of current
    set_signal_state(prev_signal, red=True, green=False)
    # Step 2: Yellow ON for 2s
    set_yellow(prev_signal, True)
    time.sleep(2)
    set_yellow(prev_signal, False)
    # Step 3: Switch green to next signal
    set_signal_state(prev_signal, red=True, green=False)
    set_signal_state(next_signal, red=False, green=True)

# Load video
capture = cv2.VideoCapture("test_rec.mp4")  # Use 0 for webcam

# Define zones
region_points = {
    "Zone A": [(10, 10), (400, 10), (400, 640), (10, 640)],
    "Zone B": [(410, 10), (800, 10), (800, 640), (410, 640)],
    "Zone C": [(810, 10), (1200, 10), (1200, 640), (810, 640)]
}

# Video Writer config
w, h, fps = (int(capture.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("count.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps or 30, (w, h))

# Initialize RegionCounter
regioncounter = solutions.RegionCounter(
    show=False,
    region=region_points,
    model="yolo11n.pt",
    classes=[1, 2, 3, 5, 7]
)

# Set initial signal states
set_signal_state("A", red=False, green=True)
set_signal_state("B", red=True, green=False)
set_signal_state("C", red=True, green=False)

# Main loop
while capture.isOpened():
    success, frame = capture.read()
    if not success:
        print("Video File Not Found or Stream Ended")
        break

    # Run YOLO + RegionCounter
    results = regioncounter(frame)
    annotated_frame = results.plot_im

    # Count objects in each region
    region_object_counts = defaultdict(int)
    for box, cls, track_id in zip(regioncounter.boxes, regioncounter.clss, regioncounter.track_ids):
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        point = regioncounter.Point((cx, cy))
        for region in regioncounter.counting_regions:
            if region["prepared_polygon"].contains(point):
                region_name = region["name"]
                region_object_counts[region_name] += 1

    # Write and display output
    video_writer.write(annotated_frame)
    cv2.imshow("Region Counter", annotated_frame)

    # Extract counts
    traffic_count_A = region_object_counts.get("Zone A", 0)
    traffic_count_B = region_object_counts.get("Zone B", 0)
    traffic_count_C = region_object_counts.get("Zone C", 0)

    # Determine green durations
    duration_A = 9 if traffic_count_A > 1 else 4
    duration_B = 9 if traffic_count_B > 1 else 4
    duration_C = 9 if traffic_count_C > 1 else 4

    if current_green == "A":
        active_duration = duration_A
    elif current_green == "B":
        active_duration = duration_B
    else:
        active_duration = duration_C

    # Time to switch?
    if time.time() - last_switch_time >= active_duration:
        next_green = get_next_signal(current_green)
        switch_signal_with_yellow(current_green, next_green)
        current_green = next_green
        last_switch_time = time.time()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting by user input")
        break

# Cleanup
capture.release()
video_writer.release()
cv2.destroyAllWindows()
