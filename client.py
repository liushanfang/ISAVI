import cv2
import pyrealsense2 as rs
import numpy as np
import subprocess

#打开 RealSense 摄像头
pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

rtmp_server = "rtmp://192.168.1.14/live/stream_key"

ffmpeg_cmd = [
    "ffmpeg",
    "-f", "rawvideo",
    "-pixel_format", "bgr24",
    "-video_size", "640x480",
    "-framerate", "30",
    "-i", "-",
    "-c:v", "libx264",
    "-pix_fmt", "yuv420p",
    "-f", "flv",
    rtmp_server
]

ffmpeg_process = subprocess.Popen(
    ffmpeg_cmd,
    stdin=subprocess.PIPE
)

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        if not color_frame:
            continue
        frame_data = np.asanyarray(color_frame.get_data())
        ffmpeg_process.stdin.write(frame_data.tobytes())
except KeyboardInterrupt:
    pass
finally:
    ffmpeg_process.stdin.close()
    ffmpeg_process.wait()
    pipeline.stop()