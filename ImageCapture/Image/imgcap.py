import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load pose model
base_options = python.BaseOptions(
    model_asset_path=r"C:\pose_landmarker_heavy.task"
)

options = vision.PoseLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO
)

detector = vision.PoseLandmarker.create_from_options(options)

# Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

prev_time = 0

# Skeleton connections (MediaPipe 33 landmark model)
POSE_CONNECTIONS = [
    (11,13),(13,15),      # left arm
    (12,14),(14,16),      # right arm
    (11,12),              # shoulders
    (11,23),(12,24),      # torso
    (23,24),              # hips
    (23,25),(25,27),(27,29),(29,31),  # left leg
    (24,26),(26,28),(28,30),(30,32)   # right leg
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

    if results.pose_landmarks:

        for pose_landmarks in results.pose_landmarks:

            points = []

            # Convert normalized coordinates → pixels
            for landmark in pose_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                points.append((x, y))

                #Draw joint
                cv2.circle(frame, (x, y), 5, (0,255,0), -1)

            # Draw bones
            for connection in POSE_CONNECTIONS:
                start = points[connection[0]]
                end = points[connection[1]]

                cv2.line(frame,start, end, (255,0,0), 2)

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