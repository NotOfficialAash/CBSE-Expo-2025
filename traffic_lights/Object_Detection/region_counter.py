import cv2
import time
import serial
from collections import defaultdict
from ultralytics import solutions

# Connect to Arduino
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)

# Timing and control
last_switch_time = time.time()
current_green = "A"  # Start with Signal A

def send_command(cmd):
    arduino.write((cmd + "\n").encode())
    print("Sent:", cmd)
    time.sleep(0.05)

def set_signal_state(signal, red, green):
    send_command(f"{signal}_R_{'ON' if red else 'OFF'}")
    send_command(f"{signal}_G_{'ON' if green else 'OFF'}")

def switch_signal():
    global current_green
    if current_green == "A":
        current_green = "B"
    elif current_green == "B":
        current_green = "C"
    else:
        current_green = "A"

# Load video or webcam
capture = cv2.VideoCapture("test_rec.mp4")  # Use 0 for webcam

# Define 3 separate regions with meaningful names
region_points = {
    "Zone A": [(10, 10), (400, 10), (400, 640), (10, 640)],
    "Zone B": [(410, 10), (800, 10), (800, 640), (410, 640)],
    "Zone C": [(810, 10), (1200, 10), (1200, 640), (810, 640)]
}

# Video Writer config
w, h, fps = (int(capture.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("count.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps or 30, (w, h))

# Initialize RegionCounter with multiple regions
regioncounter = solutions.RegionCounter(
    show=False,
    region=region_points,
    model="yolo11n.pt",
    classes=[1, 2, 3, 5, 7]
)

# Main loop
while capture.isOpened():
    success, frame = capture.read()
    if not success:
        print("Video File Not Found or Stream Ended")
        break

    # Run RegionCounter
    results = regioncounter(frame)
    annotated_frame = results.plot_im

    # Manually count tracked objects inside each region
    region_object_counts = defaultdict(int)
    for box, cls, track_id in zip(regioncounter.boxes, regioncounter.clss, regioncounter.track_ids):
        cx = (box[0] + box[2]) / 2
        cy = (box[1] + box[3]) / 2
        point = regioncounter.Point((cx, cy))

        for region in regioncounter.counting_regions:
            if region["prepared_polygon"].contains(point):
                region_name = region["name"]
                region_object_counts[region_name] += 1

    # Show and write
    video_writer.write(annotated_frame)
    cv2.imshow("Region Counter", annotated_frame)


    # # Print object count per region
    # print("Tracked object counts (center-in-region):")
    # for name in region_points.keys():
    #     count = region_object_counts.get(name, 0)
    #     print(f"  {name}: {count}")
    # print("-" * 30)

    # Extract counts from regions
    traffic_count_A = region_object_counts.get("Zone A", 0)
    traffic_count_B = region_object_counts.get("Zone B", 0)
    traffic_count_C = region_object_counts.get("Zone C", 0)

    # Determine durations based on traffic density
    duration_A = 9 if traffic_count_A > 1 else 4
    duration_B = 9 if traffic_count_B > 1 else 4
    duration_C = 9 if traffic_count_C > 1 else 4

    if current_green == "A":
        active_duration = duration_A
    elif current_green == "B":
        active_duration = duration_B
    else:
        active_duration = duration_C

    # Time to switch signal?
    if time.time() - last_switch_time >= active_duration:
        switch_signal()
        last_switch_time = time.time()

    # Apply current signal states
    set_signal_state("A", red=(current_green != "A"), green=(current_green == "A"))
    set_signal_state("B", red=(current_green != "B"), green=(current_green == "B"))
    set_signal_state("C", red=(current_green != "C"), green=(current_green == "C"))


    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting by user input")
        break


# Cleanup
capture.release()
video_writer.release()
cv2.destroyAllWindows()
