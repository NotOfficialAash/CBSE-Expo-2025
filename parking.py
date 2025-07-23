import tkinter as tk
import serial
import time

# Replace 'COM6' with your Arduino port
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

def update_dashboard():
    try:
        line = arduino.readline().decode().strip()
        if line:
            data = line.split(',')
            if len(data) == 3:
                statuses = [int(x) for x in data]
                free = statuses.count(1)
                occupied = statuses.count(0)

                status_label.config(
                    text=f"Free Slots: {free}   |   Occupied Slots: {occupied}")

                for i in range(3):
                    slot_labels[i].config(
                        text=f"Slot {i+1}: {'Free' if statuses[i] else 'Occupied'}",
                        bg='lightgreen' if statuses[i] else 'tomato'
                    )
    except Exception as e:
        print("Error:", e)

    root.after(500, update_dashboard)

# Tkinter GUI
root = tk.Tk()
root.title("🅿 Smart Parking Dashboard")
root.geometry("360x260")
root.config(bg='white')

title = tk.Label(root, text="🅿 Smart Parking System", font=("Helvetica", 18, "bold"), bg='white')
title.pack(pady=10)

status_label = tk.Label(root, text="Free Slots: -   |   Occupied: -", font=("Helvetica", 12), bg='white')
status_label.pack(pady=5)

slot_labels = []
for i in range(3):
    lbl = tk.Label(root, text=f"Slot {i+1}: -", font=("Helvetica", 12), width=25, bg='lightgray')
    lbl.pack(pady=5)
    slot_labels.append(lbl)

update_dashboard()
root.mainloop()
