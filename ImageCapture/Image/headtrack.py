import cv2
import mediapipe as mp
import time
from multiprocessing import shared_memory
import struct

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

base_options_pose = python.BaseOptions(
    model_asset_path=r"C:\pose_landmarker_heavy.task"

)
node = int(0)
latest_pose_landmarks = None
shm = shared_memory.SharedMemory(name="pose_basic", create=True, size=16)

def result_callback_pose(resultspose, image, timestamp_ms):
    global latest_pose_landmarks
    try:
        latest_pose_landmarks = resultspose
    except Exception as e:
        print("Callback error:", e)


optionsPose = vision.PoseLandmarkerOptions(
    base_options=base_options_pose,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback = result_callback_pose,
    min_pose_detection_confidence=0.6,
    min_pose_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detectorPose = vision.PoseLandmarker.create_from_options(optionsPose)
running_mode=vision.RunningMode.LIVE_STREAM
# Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

prev_time = 0

# Skeleton connections (Pose: 33 landmarks, Hand: 20)
POSE_CONNECTIONS = [
    (0,1),(0,4),(1,2),(2,3),(3,7),(4,5),(5,6),(6,8),(10,9), # Face
    (11,13),(13,15),                    # left arm
    (12,14),(14,16),                    # right arm
    (11,12),                            # shoulders
    (11,23),(12,24),                    # torso
    (23,24),                            # hips
    (23,25),(25,27),(27,29),(29,31),    # left leg
    (24,26),(26,28),(28,30),(30,32)     # right leg
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

    detectorPose.detect_async(mp_image, timestamp)

    h, w, _ = frame.shape
   # print(latest_pose_landmarks)
    if latest_pose_landmarks is not None and latest_pose_landmarks.pose_landmarks:
        pose_landmarks = latest_pose_landmarks.pose_landmarks[0]

        # Nose / approximate head position
        head = pose_landmarks[0]

        x = float(head.x)
        y = float(head.y)
        z = float(head.z)
        #print("Coord", x, y, z)

        # Send coordinates to Unity
        shm.buf[:12] = struct.pack('fff', x, y, z)

        # Convert to pixel coordinates for drawing
        px = int(x * w)
        py = int(y * h)

        cv2.circle(frame, (px, py), 5, (0, 0, 255), -1)
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

shm.unlink
shm.close
cap.release()
cv2.destroyAllWindows()