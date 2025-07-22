import cv2
from collections import defaultdict
from ultralytics import solutions

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


    # Print object count per region
    print("Tracked object counts (center-in-region):")
    for name in region_points.keys():
        count = region_object_counts.get(name, 0)
        print(f"  {name}: {count}")
    print("-" * 30)



    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting by user input")
        break


# Cleanup
capture.release()
video_writer.release()
cv2.destroyAllWindows()
