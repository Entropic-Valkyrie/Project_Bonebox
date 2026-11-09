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

nodearray = [shh,shls,shrs,shle,shre,shlw,shrw,shlf,shrf,shlh,shrh,shlk,shrk,shla,shra,shlfo,shrfo]
nodearrayval = [0,12,11,14,13,16,15,20,19,24,23,26,25,28,27,32,31]
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
running_mode=vision.RunningMode.VIDEO
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

    h, w, _ = frame.shape

    detectorPose.detect_async(mp_image, timestamp)
    if latest_pose_landmarks is not None and latest_pose_landmarks.pose_landmarks:

        for pose_landmarks in latest_pose_landmarks.pose_landmarks:
           
            points = []
            p = 0
            n = 0
            # Convert normalized coordinates into pixels
            for n, landmark in enumerate(pose_landmarks):

                x = int(landmark.x * w)
                y = int(landmark.y * h)

                points.append((x, y))

                if n in nodearrayval:
                    p = nodearrayval.index(n)

                    nodearray[p].buf[:12] = struct.pack(
                        'fff',
                        float(landmark.x),
                        float(landmark.y),
                        float(landmark.z)
                    )

                    print(f"Updated {p}: landmark {n}")
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