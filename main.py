import os
import torch
import pyrealsense2 as rs
import numpy as np
import cv2

pipeline = rs.pipeline()
config = rs.config()
config.enable_stream(rs.stream.color, 640, 480, rs.format.rgb8, 30)
 # Here we can choose other models with higher precision but lower speed
model = torch.hub.load(repo_or_dir=os.getcwd(), model='yolov5n', trust_repo=True, source='local')
pipeline.start(config)

try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()

        if not color_frame:
            continue

        color_image = np.asanyarray(color_frame.get_data())
        color_image = cv2.cvtColor(color_image, cv2.COLOR_RGB2BGR)
        results = model(color_image)
        results.show()

        if cv2.waitKey(1) & 0xff == 27:
            break

finally:
    pipeline.stop()
    cv2.destroyAllWindows()
