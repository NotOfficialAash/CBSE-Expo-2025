# ===== traffic_system.py =====
# This file handles everything: traffic control, accident detection (YOLO), Arduino, OLED, Flask API

import cv2
import time
import serial
import threading
from flask import Flask, request, jsonify
from collections import defaultdict
from ultralytics import solutions
from flask_cors import CORS

# === Arduino Setup ===
arduino = serial.Serial("COM3", 9600, timeout=1)
time.sleep(2)

# === Flask Setup ===
app = Flask(__name__)
CORS(app)

emergency_mode = False


# === Accident Flask Routes ===
@app.route("/api/confirm-accident", methods=["POST"])
def confirm_accident():
    global emergency_mode
    data = request.json
    if data.get("confirmed"):
        emergency_mode = True
        send_command("EMERGENCY_MODE")
        print("🚨 Accident confirmed, emergency mode ON")
        return jsonify({"message": "Accident confirmed and emergency mode ON"})
    return jsonify({"message": "No confirmation received"})

@app.route("/api/reset", methods=["POST"])
def reset():
    global emergency_mode
    emergency_mode = False
    send_command("RESET_MODE")
    print("✅ System reset to normal mode")
    return jsonify({"message": "Reset to normal mode"})

# === YOLO Region Counter Setup ===
capture = cv2.VideoCapture(0)
region_points = {
    "Zone A": [(10, 10), (600, 10), (600, 840), (10, 840)],
    "Zone B": [(610, 10), (800, 10), (800, 840), (610, 840)],
    "Zone C": [(810, 10), (1200, 10), (1200, 840), (810, 840)]
}

regioncounter = solutions.RegionCounter(
    show=False,
    region=region_points,
    model="yolo11n.pt",
    classes=[1, 2, 3, 5, 7],
    conf=0.1
)

current_green = "A"
last_switch_time = time.time()

# === OLED Display ===
def update_oled_timer(t):
    send_command(f"TIMER_{t}")  # Assumes Arduino reads this format

# === Traffic Control Thread ===
def traffic_loop():
    global current_green, last_switch_time, emergency_mode

    set_signal_state("A", red=False, green=True)
    set_signal_state("B", red=True, green=False)
    set_signal_state("C", red=True, green=False)

    while capture.isOpened():
        success, frame = capture.read()
        if not success:
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
                    name = region["name"]
                    region_object_counts[name] += 1

        traffic_count_A = region_object_counts.get("Zone A", 0)
        traffic_count_B = region_object_counts.get("Zone B", 0)
        traffic_count_C = region_object_counts.get("Zone C", 0)

        duration_A = 9 if traffic_count_A > 1 else 4
        duration_B = 9 if traffic_count_B > 1 else 4
        duration_C = 9 if traffic_count_C > 1 else 4

        if emergency_mode:
            update_oled_timer("E")  # 'E' for emergency
            time.sleep(1)
            continue

        if current_green == "A":
            duration = duration_A
        elif current_green == "B":
            duration = duration_B
        else:
            duration = duration_C

        t_left = duration - (time.time() - last_switch_time)
        update_oled_timer(int(t_left) if t_left > 0 else 0)

        if time.time() - last_switch_time >= duration:
            next_green = get_next_signal(current_green)
            switch_signal_with_yellow(current_green, next_green)
            current_green = next_green
            last_switch_time = time.time()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    capture.release()
    cv2.destroyAllWindows()

# === Main Runner ===
if __name__ == "__main__":
    t1 = threading.Thread(target=traffic_loop)
    t1.start()
    app.run(debug=True, port=5000)