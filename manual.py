import serial
import time

# Set the COM port and baud rate — match it with your Arduino settings
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)  # Give Arduino some time to reset

# Function to send command
def send_command(cmd):
    arduino.write((cmd + '\n').encode())  # Send command with newline
    time.sleep(0.5)
    response = arduino.readline().decode().strip()  # Read Arduino response
    print(f"Arduino response: {response}")

# Example usage
while True:
    send_command(input("Enter Command: "))