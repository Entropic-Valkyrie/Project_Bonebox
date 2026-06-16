# producer_basic.py
from multiprocessing import shared_memory
import struct
import time

# 3 floats = 12 bytes
shm = shared_memory.SharedMemory(name="pose_basic", create=True, size=12)

x, y, z = 0.0, 0.0, 0.0

try:
    while True:
        x += 1.0
        y += 2.0
        z += 3.0

        # pack 3 floats into bytes
        shm.buf[:12] = struct.pack('fff', x, y, z)

        print(f"Python wrote: {x:.1f}, {y:.1f}, {z:.1f}")
        

finally:
    shm.close()
    shm.unlink()