import cv2
from ultralytics import solutions

capture = cv2.VideoCapture("test_rec.mp4")
assert capture.isOpened(), "Error reading video file/input"

region_points = [(50, 650), (90, 650), (90, 50), (50, 50)]

# Video Writer to write ROIs adn object names on the video feed
w, h, fps = (int(capture.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
video_writer = cv2.VideoWriter("count.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))


counter = solutions.ObjectCounter(
    show=False,
    region=region_points,
    model="yolo11n.pt",
    classes=[0, 1, 2, 3, 5, 7]
)

while capture.isOpened():
    success, frame = capture.read()

    if not success:
        print("Video File Not Found")
        break

    results = counter(frame)

    video_writer.write(results.plot_im)
    cv2.imshow("Region Counter", results.plot_im)

    print(results)

    # Exit on 'q' key
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("Exiting by user input")
        break

capture.release()
video_writer.release()
cv2.destroyAllWindows()
