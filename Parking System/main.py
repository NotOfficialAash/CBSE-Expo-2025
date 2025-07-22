import serial
import time

# Replace 'COM6' with your Arduino COM port (Linux: '/dev/ttyUSB0' or '/dev/ttyACM0')
arduino = serial.Serial('COM6', 9600, timeout=1)
time.sleep(2)  # Wait for connection to establish

def parse_status(values):
    slots = ["S1", "S2", "S3"]
    free_count = 0
    for i, val in enumerate(values):
        if val == '1':
            print(f"{slots[i]}: Free")
            free_count += 1
        elif val == '0':
            print(f"{slots[i]}: Occupied")
        else:
            print(f"{slots[i]}: Invalid")
    print(f"Total Free Slots: {free_count}")
    print("-" * 30)

try:
    while True:
        line = arduino.readline().decode().strip()
        if line:
            sensor_values = line.split(",")
            if len(sensor_values) == 3:
                parse_status(sensor_values)
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopped.")
finally:
    arduino.close()
