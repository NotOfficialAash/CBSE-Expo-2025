import cv2
import torch  # PyTorch for YOLOv5
import numpy as np

# Initialize webcam
cap = cv2.VideoCapture(0)  # Use 0 for default webcam, or replace with the video file path

# Load the YOLOv5 model (can be a pre-trained model like 'yolov5s', 'yolov5m', 'yolov5l', 'yolov5x')
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # Use 'yolov5s' for smaller, faster model

# Define the region of interest (ROI) for traffic counting
roi_top_left = (50, 50)  # Example: top left corner of the region
roi_bottom_right = (600, 400)  # Example: bottom right corner of the region

# Variables for traffic density
frame_count = 0
vehicle_count = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Region of Interest (ROI) cropping
    roi_frame = frame[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]]

    # Perform vehicle detection with YOLOv5
    results = model(roi_frame)  # Detect objects in the ROI
    detections = results.pandas().xywh[0]  # Convert results to pandas dataframe

    # Filter out non-vehicle objects (class 2 corresponds to car, 3 to motorcycle, etc.)
    vehicle_detected = 0
    for _, detection in detections.iterrows():
        if detection['class'] in [2, 3, 5, 7]:  # These are classes for car, motorcycle, bus, truck
            vehicle_detected += 1
            # Draw the bounding box around the detected vehicle
            x1, y1, x2, y2 = int(detection['xmin']), int(detection['ymin']), int(detection['xmax']), int(detection['ymax'])
            cv2.rectangle(roi_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    # Update traffic density
    frame_count += 1
    if vehicle_detected > 0:
        vehicle_count += vehicle_detected

    # Calculate the density as the number of vehicles divided by the frame size
    traffic_density = vehicle_count / frame_count if frame_count > 0 else 0

    # Show the traffic density on the frame
    cv2.putText(frame, f'Traffic Density: {traffic_density:.2f}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Traffic Detection with YOLOv5', frame)

    # Exit the loop on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
