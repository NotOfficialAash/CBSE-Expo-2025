import cv2
import numpy as np
import serial
import time

# Initialize webcam
cap = cv2.VideoCapture(0)  # Use 0 for default webcam, or replace with the video file path

# Background Subtractor
fgbg = cv2.createBackgroundSubtractorMOG2()

# Define the region of interest (ROI) for traffic counting
roi_top_left = (50, 50)  # Example: top left corner of the region
roi_bottom_right = (600, 400)  # Example: bottom right corner of the region

# Variables for traffic density
frame_count = 0
vehicle_count = 0

# Arduino initialization
arduino = serial.Serial("COM3", 9600, timeout=1)
time.sleep(5)

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Region of Interest (ROI) cropping
    roi_frame = frame[roi_top_left[1]:roi_bottom_right[1], roi_top_left[0]:roi_bottom_right[0]]

    # Apply background subtraction
    fgmask = fgbg.apply(roi_frame)

    # Threshold the mask to get binary image
    _, thresh = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)

    # Find contours of the moving objects
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out small contours (noise) and count vehicles
    vehicle_detected = 0
    for contour in contours:
        if cv2.contourArea(contour) > 400:  # Area threshold for vehicle detection
            vehicle_detected += 1
            # Draw the contour around the detected vehicle
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(roi_frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
    # Update traffic density
    frame_count += 1
    if vehicle_detected > 0:
        vehicle_count += vehicle_detected

    # Calculate the density as the number of vehicles divided by the frame size
    traffic_density = vehicle_count / frame_count if frame_count > 0 else 0
    
    # Show the traffic density on the frame
    cv2.putText(frame, f'Traffic Density: {traffic_density:.2f}', (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # Display the frame
    cv2.imshow('Traffic Detection', frame)


    if traffic_density > 5.00:
        arduino.write("ON")
        time.sleep(5)
    else:
        arduino.write("OFF")
        time.sleep(5)

# Release resources
cap.release()
cv2.destroyAllWindows()
