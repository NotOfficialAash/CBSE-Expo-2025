import serial
import tkinter as tk
import threading
import time

# Set your correct COM port here
SERIAL_PORT = "COM3"  # change to your port like COM3, COM4 etc.
BAUD_RATE = 9600

# Setup serial connection
try:
    arduino = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
except:
    print("Couldn't connect to Arduino. Check your COM port.")

# GUI setup
root = tk.Tk()
root.title("Smart Parking Dashboard")
root.geometry("400x300")
root.config(bg="#f4f4f4")

title_label = tk.Label(root, text="SMART PARKING STATUS", font=("Helvetica", 16, "bold"), bg="#f4f4f4")
title_label.pack(pady=10)

slot_labels = []
for i in range(4):  # 4 slots
    label = tk.Label(root, text=f"Slot {i+1}: ...", font=("Helvetica", 14), bg="#f4f4f4")
    label.pack()
    slot_labels.append(label)

free_label = tk.Label(root, text="Total Free Slots: ...", font=("Helvetica", 14, "bold"), fg="green", bg="#f4f4f4")
free_label.pack(pady=20)

status_label = tk.Label(root, text="", font=("Helvetica", 12), fg="red", bg="#f4f4f4")
status_label.pack()

def update_dashboard():
    while True:
        try:
            line = arduino.readline().decode('utf-8').strip()
            if line.startswith("Slot"):
                parts = line.split(":")
                slot_num = int(parts[0].split()[1])
                status = parts[1].strip()
                slot_labels[slot_num - 1].config(text=f"Slot {slot_num}: {status}", fg="green" if status == "Free" else "red")
            elif line.startswith("Total Free Slots"):
                count = line.split(":")[1].strip()
                free_label.config(text=f"Total Free Slots: {count}")
        except Exception as e:
            status_label.config(text=f"Error: {str(e)}")
        time.sleep(0.1)

# Threading to avoid freezing GUI
threading.Thread(target=update_dashboard, daemon=True).start()

root.mainloop()
