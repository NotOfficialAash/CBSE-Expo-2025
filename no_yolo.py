import cv2
import numpy as np
# import serial
import time

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define ROIs for Road A and Road B
roi_A_top_left = (50, 50)
roi_A_bottom_right = (600, 250)

roi_B_top_left = (50, 270)
roi_B_bottom_right = (600, 470)

# Background subtractors for both roads
fgbg_A = cv2.createBackgroundSubtractorMOG2()
fgbg_B = cv2.createBackgroundSubtractorMOG2()

# Traffic tracking variables
frame_count_A = 0
vehicle_count_A = 0

frame_count_B = 0
vehicle_count_B = 0

# Arduino initialization
# arduino = serial.Serial("COM3", 9600, timeout=1)
# time.sleep(5)

prev_state_A = None
prev_state_B = None

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # === ROI A ===
    roi_frame_A = frame[roi_A_top_left[1]:roi_A_bottom_right[1], roi_A_top_left[0]:roi_A_bottom_right[0]]
    fgmask_A = fgbg_A.apply(roi_frame_A)
    _, thresh_A = cv2.threshold(fgmask_A, 200, 255, cv2.THRESH_BINARY)
    contours_A, _ = cv2.findContours(thresh_A, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_detected_A = 0
    for c in contours_A:
        if cv2.contourArea(c) > 400:
            vehicle_detected_A += 1
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi_frame_A, (x, y), (x + w, y + h), (0, 255, 0), 2)

    frame_count_A += 1
    vehicle_count_A += vehicle_detected_A
    traffic_density_A = vehicle_count_A / frame_count_A if frame_count_A > 0 else 0

    # === ROI B ===
    roi_frame_B = frame[roi_B_top_left[1]:roi_B_bottom_right[1], roi_B_top_left[0]:roi_B_bottom_right[0]]
    fgmask_B = fgbg_B.apply(roi_frame_B)
    _, thresh_B = cv2.threshold(fgmask_B, 200, 255, cv2.THRESH_BINARY)
    contours_B, _ = cv2.findContours(thresh_B, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_detected_B = 0
    for c in contours_B:
        if cv2.contourArea(c) > 400:
            vehicle_detected_B += 1
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi_frame_B, (x, y), (x + w, y + h), (255, 0, 0), 2)

    frame_count_B += 1
    vehicle_count_B += vehicle_detected_B
    traffic_density_B = vehicle_count_B / frame_count_B if frame_count_B > 0 else 0

    # === Drawing ROI Boxes & Info ===
    cv2.rectangle(frame, roi_A_top_left, roi_A_bottom_right, (0, 255, 0), 2)
    cv2.rectangle(frame, roi_B_top_left, roi_B_bottom_right, (255, 0, 0), 2)

    cv2.putText(frame, f'Density A: {traffic_density_A:.2f}', (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.putText(frame, f'Density B: {traffic_density_B:.2f}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 0, 0), 2)

    # === Arduino Serial Communication ===
    # current_state_A = "AON" if traffic_density_A > 5.00 else "AOFF"
    # if current_state_A != prev_state_A:
    #     arduino.write(current_state_A.encode())
    #     prev_state_A = current_state_A
    #     time.sleep(2)

    # current_state_B = "BON" if traffic_density_B > 5.00 else "BOFF"
    # if current_state_B != prev_state_B:
    #     arduino.write(current_state_B.encode())
    #     prev_state_B = current_state_B
    #     time.sleep(2)

    # === Display the frame ===
    cv2.imshow('Traffic Detection', frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
# arduino.close()