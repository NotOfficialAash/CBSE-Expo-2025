import cv2
import numpy as np
import time

# Initialize webcam
cap = cv2.VideoCapture(0)

# Define ROIs for Road A, B, and C
roi_A_top_left = (50, 50)
roi_A_bottom_right = (600, 200)

roi_B_top_left = (50, 220)
roi_B_bottom_right = (600, 370)

roi_C_top_left = (50, 390)
roi_C_bottom_right = (600, 540)

# Background subtractors for each road
fgbg_A = cv2.createBackgroundSubtractorMOG2()
fgbg_B = cv2.createBackgroundSubtractorMOG2()
fgbg_C = cv2.createBackgroundSubtractorMOG2()

# Traffic tracking variables
frame_count_A = frame_count_B = frame_count_C = 0
vehicle_count_A = vehicle_count_B = vehicle_count_C = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    ## === ROI A ===
    roi_frame_A = frame[roi_A_top_left[1]:roi_A_bottom_right[1], roi_A_top_left[0]:roi_A_bottom_right[0]]
    fgmask_A = fgbg_A.apply(roi_frame_A)
    _, thresh_A = cv2.threshold(fgmask_A, 200, 255, cv2.THRESH_BINARY)
    contours_A, _ = cv2.findContours(thresh_A, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_detected_A = sum(1 for c in contours_A if cv2.contourArea(c) > 400)
    frame_count_A += 1
    vehicle_count_A += vehicle_detected_A
    traffic_density_A = vehicle_count_A / frame_count_A if frame_count_A > 0 else 0

    for c in contours_A:
        if cv2.contourArea(c) > 400:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi_frame_A, (x, y), (x + w, y + h), (0, 255, 0), 2)

    ## === ROI B ===
    roi_frame_B = frame[roi_B_top_left[1]:roi_B_bottom_right[1], roi_B_top_left[0]:roi_B_bottom_right[0]]
    fgmask_B = fgbg_B.apply(roi_frame_B)
    _, thresh_B = cv2.threshold(fgmask_B, 200, 255, cv2.THRESH_BINARY)
    contours_B, _ = cv2.findContours(thresh_B, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_detected_B = sum(1 for c in contours_B if cv2.contourArea(c) > 400)
    frame_count_B += 1
    vehicle_count_B += vehicle_detected_B
    traffic_density_B = vehicle_count_B / frame_count_B if frame_count_B > 0 else 0

    for c in contours_B:
        if cv2.contourArea(c) > 400:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi_frame_B, (x, y), (x + w, y + h), (255, 0, 0), 2)

    ## === ROI C ===
    roi_frame_C = frame[roi_C_top_left[1]:roi_C_bottom_right[1], roi_C_top_left[0]:roi_C_bottom_right[0]]
    fgmask_C = fgbg_C.apply(roi_frame_C)
    _, thresh_C = cv2.threshold(fgmask_C, 200, 255, cv2.THRESH_BINARY)
    contours_C, _ = cv2.findContours(thresh_C, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vehicle_detected_C = sum(1 for c in contours_C if cv2.contourArea(c) > 400)
    frame_count_C += 1
    vehicle_count_C += vehicle_detected_C
    traffic_density_C = vehicle_count_C / frame_count_C if frame_count_C > 0 else 0

    for c in contours_C:
        if cv2.contourArea(c) > 400:
            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(roi_frame_C, (x, y), (x + w, y + h), (0, 0, 255), 2)

    ## === Drawing ROI Boxes & Density Info ===
    cv2.rectangle(frame, roi_A_top_left, roi_A_bottom_right, (0, 255, 0), 2)
    cv2.rectangle(frame, roi_B_top_left, roi_B_bottom_right, (255, 0, 0), 2)
    cv2.rectangle(frame, roi_C_top_left, roi_C_bottom_right, (0, 0, 255), 2)

    cv2.putText(frame, f'Density A: {traffic_density_A:.2f}', (50, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv2.putText(frame, f'Density B: {traffic_density_B:.2f}', (50, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    cv2.putText(frame, f'Density C: {traffic_density_C:.2f}', (50, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    ## === Show Frame ===
    cv2.imshow('Traffic Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Cleanup
cap.release()
cv2.destroyAllWindows()
