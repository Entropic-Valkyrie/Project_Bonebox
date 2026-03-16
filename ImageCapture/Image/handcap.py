import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load pose model
base_options = python.BaseOptions(
    model_asset_path=r"C:\hand_landmarker.task"
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

detector = vision.HandLandmarker.create_from_options(options)
running_mode=vision.RunningMode.VIDEO
# Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

prev_time = 0

# Skeleton connections (MediaPipe 33 landmark model)
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),      # Thumb
    (0,5),(5,9),(9,13),(13,17),(0,17),      # Palm
    (5,6),(6,7),(7,8),              # Index
    (9,10),(10,11),(11,12),      # Middle
    (13,14),(14,15),(15,16),              # Ring
    (17,18),(18,19),(19,20)  # left leg
]

while True:

    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )

    timestamp = int(time.time() * 1000)

    results = detector.detect_for_video(mp_image, timestamp)

    h, w, _ = frame.shape

    if results.hand_landmarks:

        for hand_landmarks in results.hand_landmarks:

            points = []

            # Convert normalized coordinates → pixels
            for landmark in hand_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))

                #Draw joint
                cv2.circle(frame, (x, y), 5, (0,255,0), -1)

            # Draw bones
            for connection in HAND_CONNECTIONS:
                start = points[connection[0]]
                end = points[connection[1]]

                cv2.line(frame,start, end, (0,255,0), 2)

    # FPS calculation
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    prev_time = current_time

    cv2.putText(
        frame,
        f"FPS: {int(fps)}",
        (20,40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0,255,255),
        2
    )

    cv2.imshow("Pose Tracker", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()