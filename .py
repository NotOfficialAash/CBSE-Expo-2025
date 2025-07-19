import cv2
import numpy as np
import time

# --- Configuration ---
CAMERA_INDEX = 0  # usually 0 for default webcam
DENSITY_THRESHOLD = 5000  # adjust this based on lighting/camera angle
LOW_DENSITY_GREEN_TIME = 5  # seconds
HIGH_DENSITY_GREEN_TIME = 15  # seconds
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

def calculate_density(frame):
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Blur to reduce noise
    blur = cv2.GaussianBlur(gray, (15, 15), 0)
    # Threshold to binary image
    _, thresh = cv2.threshold(blur, 100, 255, cv2.THRESH_BINARY)
    # Count white pixels (could indicate vehicles)
    white_pixels = cv2.countNonZero(thresh)
    return white_pixels

def show_traffic_light(color, seconds):
    for i in range(seconds, 0, -1):
        img = np.zeros((300, 200, 3), dtype=np.uint8)
        if color == "green":
            cv2.circle(img, (100, 200), 50, (0, 255, 0), -1)
        elif color == "red":
            cv2.circle(img, (100, 50), 50, (0, 0, 255), -1)
        elif color == "yellow":
            cv2.circle(img, (100, 125), 50, (0, 255, 255), -1)
        
        cv2.putText(img, f"{color.upper()} {i}s", (20, 290),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        cv2.imshow("Traffic Light", img)
        if cv2.waitKey(1000) & 0xFF == 27:
            break

def smart_traffic_light_loop():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    print("Starting Smart Traffic Light System. Press 'q' to exit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to grab frame.")
            break

        density = calculate_density(frame)
        print(f"Detected Density: {density}")

        # Display detection frame
        cv2.putText(frame, f"Density: {density}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.imshow("Camera View", frame)

        # Decide time based on density
        if density > DENSITY_THRESHOLD:
            green_time = HIGH_DENSITY_GREEN_TIME
        else:
            green_time = LOW_DENSITY_GREEN_TIME

        # Simulate one traffic cycle
        show_traffic_light("red", 3)
        show_traffic_light("yellow", 2)
        show_traffic_light("green", green_time)
        show_traffic_light("yellow", 2)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    smart_traffic_light_loop()
