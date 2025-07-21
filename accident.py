import cv2
import time
from twilio.rest import Client

# Load the pretrained accident detection model (dummy example)
model = cv2.dnn.readNetFromONNX("accident_model.onnx")  # use real model

# Twilio setup
account_sid = 'YOUR_TWILIO_SID'
auth_token = 'YOUR_TWILIO_TOKEN'
client = Client(account_sid, auth_token)

def send_sms():
    message = client.messages.create(
        body="🚨 Accident detected at Location X. Immediate help needed!",
        from_='+1234567890',
        to='+91xxxxxxxxxx'
    )
    print("SMS sent:", message.sid)

# Start camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Preprocess frame
    blob = cv2.dnn.blobFromImage(frame, 1/255, (300, 300), swapRB=True)
    model.setInput(blob)
    detections = model.forward()

    # Dummy logic (replace with real detection logic)
    if detect_accident(detections):
        print("Accident Detected!")
        send_sms()
        time.sleep(5)

    cv2.imshow("Live Feed", frame)
    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
