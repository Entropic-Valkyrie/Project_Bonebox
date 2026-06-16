import cv2
import mediapipe as mp
import time
from multiprocessing import shared_memory
import struct

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load pose model
base_options_hand = python.BaseOptions(
    model_asset_path=r"C:\hand_landmarker.task"

)
base_options_pose = python.BaseOptions(
    model_asset_path=r"C:\pose_landmarker_heavy.task"

)

latest_hand_landmarks = None
latest_pose_landmarks = None
shm = shared_memory.SharedMemory(name="pose_basic", create=True, size=12)

def result_callback_hand(resultshand, image, timestamp_ms):
    global latest_hand_landmarks
    try:
        latest_hand_landmarks = resultshand
    except Exception as e:
        print("Callback error:", e)
def result_callback_pose(resultspose, image, timestamp_ms):
    global latest_pose_landmarks
    try:
        latest_pose_landmarks = resultspose
    except Exception as e:
        print("Callback error:", e)

optionsHand = vision.HandLandmarkerOptions(
    base_options=base_options_hand,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback = result_callback_hand,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
optionsPose = vision.PoseLandmarkerOptions(
    base_options=base_options_pose,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback = result_callback_pose,
    min_pose_detection_confidence=0.6,
    min_pose_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
detectorHand = vision.HandLandmarker.create_from_options(optionsHand)
detectorPose = vision.PoseLandmarker.create_from_options(optionsPose)
running_mode=vision.RunningMode.VIDEO
# Webcam
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

prev_time = 0

# Skeleton connections (Pose: 33 landmarks, Hand: 20)
HAND_CONNECTIONS = [
    (0,1),(1,2),(2,3),(3,4),            # Thumb
    (0,5),(5,9),(9,13),(13,17),(0,17),  # Palm
    (5,6),(6,7),(7,8),                  # Index
    (9,10),(10,11),(11,12),             # Middle
    (13,14),(14,15),(15,16),            # Ring
    (17,18),(18,19),(19,20)             # left leg
]
POSE_CONNECTIONS = [
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

    detectorHand.detect_async(mp_image, timestamp)

    h, w, _ = frame.shape

    if latest_hand_landmarks is not None and latest_hand_landmarks.hand_landmarks:

        for hand_landmarks in latest_hand_landmarks.hand_landmarks:

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
    detectorPose.detect_async(mp_image, timestamp)
    if latest_pose_landmarks is not None and latest_pose_landmarks.pose_landmarks:

        for pose_landmarks in latest_pose_landmarks.pose_landmarks:

            points = []

            # Convert normalized coordinates → pixels
            for landmark in pose_landmarks:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                
                points.append((x, y))
                        # pack 3 floats into bytes
                shm.buf[:12] = struct.pack('fff', float(landmark.x), float(landmark.y), float(landmark.z))

                #print(f"Python wrote: {x:.1f}, {y:.1f}, {z:.1f}")

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