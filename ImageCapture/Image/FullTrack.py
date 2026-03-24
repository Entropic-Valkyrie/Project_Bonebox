import cv2
import mediapipe as mp
import time

from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Load pose model
base_options = python.BaseOptions(
    model_asset_path=r"C:\hand_landmarker.task"
)

optionsHand = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.6,
    min_hand_presence_confidence=0.6,
    min_tracking_confidence=0.6
)
optionsPose = vision.PoseLandmarkerOptions(
    
)
detectorHand = vision.HandLandmarker.create_from_options(options)
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
POSE_CONNECTIONS = [
    (11,13),(13,15),      # left arm
    (12,14),(14,16),      # right arm
    (11,12),              # shoulders
    (11,23),(12,24),      # torso
    (23,24),              # hips
    (23,25),(25,27),(27,29),(29,31),  # left leg
    (24,26),(26,28),(28,30),(30,32)   # right leg
]