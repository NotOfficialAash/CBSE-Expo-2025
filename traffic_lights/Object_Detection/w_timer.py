# Authors:
#  - Aashrith Srinivasa
#  - Atrey K Urs
#  - Punya S
#  - Aarav V

#
# Special Thanks:
#  - Niranth 

import cv2
import serial
import time
from collections import defaultdict
from ultralytics import solutions


''' 
        Establish Connection with Arduino Module
Replace COM6 with the port your Arduino is conencted to (You'll find it in the Arduino IDE).
time.sleep(2) is used to give time for Arduino to initialize itself.
'''
arduino = serial.Serial("COM6", 9600, timeout=1)
time.sleep(2)


'''
        Send Command to Arduino Through the Port Opened
The Arduino is programmed to stop reading the input buffer at \n. So we use \n to define the end of command.
.encode() is used in this case as Arduino accepts only bytestings.
time.sleep() to send commands in a moderate rate and not overload Arduino with instructions.
'''
def send_signal_command(cmd):
    arduino.write((cmd + "\n").encode())
    print("Sent:", cmd)
    time.sleep(0.05)


'''
        Send Remaining Time to Arduino Through the Port Opened
Same as send_signal_command, but instead we send the remaining time to be displayed in the OLED screen to Arduino.
remaining_time argument needs a string datatype not integer.
'''
def send_time_command(remaining_time):
    arduino.write((remaining_time + "\n").encode())
    print("Sent: TIME", remaining_time)
    time.sleep(0.05)


'''
        Set the State of One Signal Unit
You need to specify the name of the Signal Unit and then set lights to be ON or OFF.
'''
def set_signal_state(signal, red, yellow, green):
    send_signal_command(f"{signal}_R_{'ON' if red else 'OFF'}")
    send_signal_command(f"{signal}_Y_{'ON' if yellow else 'OFF'}")
    send_signal_command(f"{signal}_G_{'ON' if green else 'OFF'}")


'''
        Closing Arduino for a Safe Exit
Sends exit command to stop all I/O operations through the arduino pins for a safe exit of the programs.
'''
def close_arduino():
    send_signal_command("EXIT")


'''
        Initialize Important Variables
signal_order specifies the order in which the signals need to be changed.
current_green is used to keep track of which signal unit is currently green
last_switch_time is used to keep track of the instant a signal unit/lights switched.
'''
signal_order = {"A" : "B", "B" : "C", "C" : "A"}
current_green = "A"
next_green = signal_order[current_green]
current_phase = "green"
last_sent_second = -1
last_switch_time = time.time()


'''
        Start/Open the Video Feed to be Analyzed
In case of a video file, enter the file name inside quotes.
In case of a live video feed through a camera, make sure to connect the camera to the PC and use whole numbers to access each camera. For example, 0 will use the default camera
'''
capture = cv2.VideoCapture(1)


'''
        Get Frame Width, Height and FPS
Get the required information from the VideoCapture object "capture" and store it variables.
Create a VideoWriter object "video_writer" to write/annotate on the original video frames.
count.avi is the output file created while annotating the original video frames
cv2.VideoWriter_fourcc() is used to create a Four Character Code (32-bit integer) used to define the file format of the input video feed 
'''
width, height, fps = (int(capture.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("count.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height))


'''
        Define Different Regions to be Tracked
To define a region use a list and (x,y) coordinates of each point.
For multiple regions, use a dictionary to define regions with their respective names.
In most cases, vertically/horizontally straight lines are drawn from one point to the other.
WARNING: It is a pain to define these region points for anything that is vertically/horizontally NOT straight like slant shapes / tarpeziums 
'''
region_points = {
    "Zone A" : [(0, 205), (0, 375), (250, 375), (250, 205)],
    "Zone B" : [(350, 230), (350, 420), (630, 420), (630, 230)],
    "Zone C" : [(70, 100), (70, 190), (280, 190), (280, 100)]
}


'''
        Create a Region Counter Object to Count Objects
show - Specify whether to use the inbuilt video feed viewer or not. In our case we'll use CV2 as it provides more control over the viewer window.
model - Specify the YOLO model to be used.
region - Specify the regions to be used to count the objects.
classes - Define (using a list) which objects should be detected and tracked by YOLO. Here we use 1, 2, 3, 5, 7 which are the respective classes for bicycles, cars, trucks, busses and motorbikes. Refer to the COCO training dataset to define this list
conf - Used to set the confidence threshold for the model to detect the objects.
verbose - Internal logging system provided by YOLO. Useful for analytics.
device - Specify the device on which YOLO will run. CPU for cpu and whole number 0, 1 and such (depends on the number of GPUs connected) for using your GPU.
'''
region_counter = solutions.RegionCounter(
    show=False,
    model="yolo11s.pt",
    region=region_points,
    classes=[1, 2, 3, 5, 7],
    conf=0.1,

    verbose=False,
    device="CPU"
)


'''
        Set Initial Sigal Unit State
'''
set_signal_state("A", red=False, yellow=False, green=True)
set_signal_state("B", red=True, yellow=False, green=False)
set_signal_state("C", red=True, yellow=False, green=False)


'''
        Main Loop Runs if Video Capture is Open
'''
while capture.isOpened():
    '''
    Checks if capture object could successfully read frames from the video feed.
    '''
    success, frame = capture.read()
    if not success:
        print("Video File Not Found or Stream Ended")
        break


    '''
    Call the region_counter object and store the return values in results.
    Plot the regiosn and annotate frames.
    Write the annotated frames on the original video feed.
    Use CV2 to display the annotated frame.
    '''
    results = region_counter(frame)
    annotated_frame = results.plot_im

    video_writer.write(annotated_frame)
    cv2.imshow("Traffic Signal Intersection", annotated_frame)


    '''
    Create a dictionary to store the count of objects in a specific region.
    Get the coordinates of the center of each object box and check to which region the cnter is the closest.
    Update the dictionary.
    '''
    region_object_counts = defaultdict(int)
    for box, cls, track_id in zip(region_counter.boxes, region_counter.clss, region_counter.track_ids):
        center_x = (box[0] + box[2]) / 2
        center_y = (box[1] + box[3]) / 2
        point = region_counter.Point((center_x, center_y))

        for region in region_counter.counting_regions:
            if region["prepared_polygon"].contains(point):
                region_name = region["name"]
                region_object_counts[region_name] += 1


    '''
    Store the count of each region in separate variables (print it out just for reference).
    '''
    traffic_count_A = region_object_counts.get("Zone A", 0)
    traffic_count_B = region_object_counts.get("Zone B", 0)
    traffic_count_C = region_object_counts.get("Zone C", 0)
    print(traffic_count_A, traffic_count_B, traffic_count_C)


    '''
    Calculate the duration of the green light based on the number of vehicles in a specific region
    '''
    duration_A = 9 if traffic_count_A > 1 else 4
    duration_B = 9 if traffic_count_B > 1 else 4
    duration_C = 9 if traffic_count_C > 1 else 4
    duration_yellow_stop = 1
    duration_yellow_start = 1
    
    if current_green == "A":
        duration_active = duration_A
    elif current_green == "B":
        duration_active = duration_B
    else:
        duration_active = duration_C


    '''
    Calculate the current time and the elapsed time.
    Will be used to check the duration of the green and yellow lights.
    '''
    current_time = time.time()
    elapsed_time = current_time - last_switch_time
    time_counter = duration_active


    '''
    Logic for a countdown timer to be displayed for the signals
    '''
    current_second = int(elapsed_time)
    if current_second != last_sent_second:
        last_sent_second = current_second

        if current_phase == "green":
            remaining = max(0, duration_active - current_second)
            send_time_command(str(remaining))
            print(f"Time Remaining {current_phase}:", remaining)

        elif current_phase == "yellow_stop":
            remaining = max(0, duration_yellow_stop - current_second)
            send_time_command(str(remaining))
            print(f"Time Remaining {current_phase}:", remaining)

        elif current_phase == "yellow_start":
            remaining = max(0, duration_yellow_start - current_second)
            send_time_command(str(remaining))
            print(f"Time Remaining {current_phase}:", remaining)

        elif current_phase == "red":
            # Not strictly necessary in your current design (since red is implicit),
            # but if you ever want to show remaining red for the currently non-green signals,
            # you can extend it here.
            pass


    '''
    Logic to switch signals (and signal units) after the set time has be elapsed.
    '''
    if current_phase == "green":
        if elapsed_time >= duration_active:
            set_signal_state(current_green, red=False, yellow=True, green=False)
            current_phase = "yellow_stop"
            last_switch_time = current_time

    elif current_phase == "yellow_stop":
        if elapsed_time >= duration_yellow_stop:
            set_signal_state(current_green, red=True, yellow=False, green=False)
            set_signal_state(next_green, red=False, yellow=True, green=False)
            current_phase = "yellow_start"
            last_switch_time = current_time

    elif current_phase == "yellow_start":
        if elapsed_time >= duration_yellow_start:
            set_signal_state(next_green, red=False, yellow=False, green=True)
            current_green = next_green
            next_green = signal_order[current_green]
            current_phase = "green"
            last_switch_time = current_time


    '''
    Always check for the exit clause of the program. Allows the user to manually exit from the program.
    '''
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Program Exited by User Input")
        break


'''
        Safely Release Objects, Close Arduino and Exit
'''
close_arduino()
capture.release()
video_writer.release()
cv2.destroyAllWindows()   
