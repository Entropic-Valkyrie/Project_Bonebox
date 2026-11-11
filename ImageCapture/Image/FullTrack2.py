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

# Sectioning off memory for each key node

shh = shared_memory.SharedMemory(name="pose_head", create=True, size=12)
shls = shared_memory.SharedMemory(name="pose_Lshoulder", create=True, size=12)
shrs = shared_memory.SharedMemory(name="pose_Rshoulder", create=True, size=12)
shle = shared_memory.SharedMemory(name="pose_Lelbow", create=True, size=12)
shre = shared_memory.SharedMemory(name="pose_Relbow", create=True, size=12)
shlw = shared_memory.SharedMemory(name="pose_Lwrist", create=True, size=12)
shrw = shared_memory.SharedMemory(name="pose_Rwrist", create=True, size=12)
shlf = shared_memory.SharedMemory(name="pose_Lfinger", create=True, size=12)
shrf = shared_memory.SharedMemory(name="pose_Rfinger", create=True, size=12)
shlh = shared_memory.SharedMemory(name = "pose_Lhip", create=True, size=12)
shrh = shared_memory.SharedMemory(name="pose_Rhip", create=True, size=12)
shlk = shared_memory.SharedMemory(name="pose_Lknee", create=True, size=12)
shrk =shared_memory.SharedMemory(name="pose_Rknee", create=True, size=12)
shla = shared_memory.SharedMemory(name="pose_Lankle", create=True, size=12)
shra = shared_memory.SharedMemory(name="pose_Rankle", create=True, size=12)
shlfo = shared_memory.SharedMemory(name="pose_Lfoot", create=True, size=12)
shrfo =  shared_memory.SharedMemory(name="pose_Rfoot", create=True, size=12)

# Declaring Lists so future iteration of code is quicker

nodearray = [shh,shls,shrs,shle,shre,shlw,shrw,shlf,shrf,shlh,shrh,shlk,shrk,shla,shra,shlfo,shrfo]
nodearrayval = [0,12,11,14,13,16,15,20,19,24,23,26,25,28,27,32,31]

# Function that defines Latest pose landmarks and handles null points

def result_callback_pose(resultspose, image, timestamp_ms):
    global latest_pose_landmarks
    try:
        latest_pose_landmarks = resultspose
    except Exception as e:
        print("Callback error:", e)


# Holds Settings for the Machine learning algorithm itself

optionsPose = vision.PoseLandmarkerOptions(
    base_options=base_options_pose,
    running_mode=vision.RunningMode.LIVE_STREAM,
    result_callback = result_callback_pose,
    min_pose_detection_confidence=0.6,
    min_pose_presence_confidence=0.6,
    min_tracking_confidence=0.6
)

# Defines running modes and Setting source

detectorPose = vision.PoseLandmarker.create_from_options(optionsPose)
running_mode=vision.RunningMode.VIDEO
# Webcam
cap = cv2.VideoCapture(0)

# Checks for camera, Test 0.1.00-0.1.01

if not cap.isOpened():
    print("Error: Could not open camera.")
    exit()

prev_time = 0

# Skeleton connections (Pose: 33 landmarks)
POSE_CONNECTIONS = [
    (0,12),(0,11), # Face
    (11,13),(13,15),                    # left arm
    (12,14),(14,16),                    # right arm
    (11,12),                            # shoulders
    (11,23),(12,24),                    # torso
    (23,24),                            # hips
    (23,25),(25,27),(27,29),    # left leg
    (24,26),(26,28),(28,30),(30,32)     # right leg
]

# Main Loop

while True:
    # Gets Frame, if no Frame, Exits loop and ends program
    success, frame = cap.read()
    if not success:
        break
    # Orentates Frame so it properly mirrors user
    frame = cv2.flip(frame, 1)

    # Converts to correct colour format
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    # Defines image
    mp_image = mp.Image(
        image_format=mp.ImageFormat.SRGB,
        data=rgb_frame
    )
    # For framerate estimation
    timestamp = int(time.time() * 1000)

    h, w, _ = frame.shape

    #Allows for Asynchronos processing of pose detection

    detectorPose.detect_async(mp_image, timestamp)
    #Checks that there is a pose, and that it is in Latest_pose_landmarks
    if latest_pose_landmarks is not None and latest_pose_landmarks.pose_landmarks:

        for pose_landmarks in latest_pose_landmarks.pose_landmarks:
           # Declares loop needed variables
            points = []
            p = 0
            n = 0
            # Looping through nodes
            for n, landmark in enumerate(pose_landmarks):
                #Provides Coordinates
                x = int(landmark.x * w)
                y = int(landmark.y * h)

                points.append((x, y))
                # checks if current node equals one of the required nodes
                if n in nodearrayval:
                    p = nodearrayval.index(n)
                    #Passes value through to correct Memory Address (I.E: Head coord goes to shh)
                    nodearray[p].buf[:12] = struct.pack(
                        'fff',
                        float(landmark.x),
                        float(landmark.y),
                        float(landmark.z)
                    )
                #print(f"Python wrote: {x:.1f}, {y:.1f}, {z:.1f}")

                #Draw joint
                cv2.circle(frame, (x, y), 5, (0,0,255), -1)

            # Draw bones
            for connection in POSE_CONNECTIONS:
                start = points[connection[0]]
                end = points[connection[1]]

                cv2.line(frame,start, end, (255,0,0), 2)
        # FPS calculation
    current_time = time.time()
    fps = 1 / (current_time - prev_time) if prev_time != 0 else 0
    prev_time = current_time

    #Prints FPS to display
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
i = 0
while i < nodearray.len:

    nodearray[i].unlink
    nodearray.close
    i += 1
cap.release()
cv2.destroyAllWindows()