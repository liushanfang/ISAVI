import cv2
import numpy as np
from ultralytics.engine.results import Boxes
import math

conf_threshold = 0.5
cls_name_dict = {0: 'person', 1: 'bicycle', 2: 'car', 3: 'motorcycle', 4: 'airplane', 5: 'bus', 6: 'train', 7: 'truck', 8: 'boat', 
                 9: 'traffic light', 10: 'fire hydrant', 11: 'stop sign', 12: 'parking meter', 13: 'bench', 14: 'bird', 15: 'cat', 
                 16: 'dog', 17: 'horse', 18: 'sheep', 19: 'cow', 20: 'elephant', 21: 'bear', 22: 'zebra', 23: 'giraffe', 24: 'backpack', 
                 25: 'umbrella', 26: 'handbag', 27: 'tie', 28: 'suitcase', 29: 'frisbee', 30: 'skis', 31: 'snowboard', 32: 'sports ball', 
                 33: 'kite', 34: 'baseball bat', 35: 'baseball glove', 36: 'skateboard', 37: 'surfboard', 38: 'tennis racket', 39: 'bottle', 
                 40: 'wine glass', 41: 'cup', 42: 'fork', 43: 'knife', 44: 'spoon', 45: 'bowl', 46: 'banana', 47: 'apple', 48: 'sandwich', 
                 49: 'orange', 50: 'broccoli', 51: 'carrot', 52: 'hot dog', 53: 'pizza', 54: 'donut', 55: 'cake', 56: 'chair', 57: 'couch', 
                 58: 'potted plant', 59: 'bed', 60: 'dining table', 61: 'toilet', 62: 'tv', 63: 'laptop', 64: 'mouse', 65: 'remote', 
                 66: 'keyboard', 67: 'cell phone', 68: 'microwave', 69: 'oven', 70: 'toaster', 71: 'sink', 72: 'refrigerator', 73: 'book', 
                 74: 'clock', 75: 'vase', 76: 'scissors', 77: 'teddy bear', 78: 'hair drier', 79: 'toothbrush'}
color_list = [(0,255,0), (255,0,0), (0,0,255), (255,255,0), (0,255,255), (255,0,255)]


rect_margin = 5

def calc_depth(depth_frame,
               depth_step_w,
               depth_step_h,
               x0: int,
               x1: int,
               y0: int,
               y1: int):
    left = int(x0 / depth_step_w)
    right = math.ceil(x1 / depth_step_w)
    top = int(y0 / depth_step_h)
    bottom = math.ceil(y1 / depth_step_h)
    rect_w = right - left
    rect_h = bottom - top
    if rect_w <= 1 or rect_h <= 1:
        mid_x = int((left + right) / 2)
        mid_y = int((top + bottom) / 2)
        mean_depth = depth_frame[mid_y, mid_x]
    else:
        mean_depth = np.mean(depth_frame[top:bottom, left:right])
    return float(mean_depth)
    

def render_result(frame,
                  depth_data,
                  depth_dim,
                  detectBoxes: Boxes):
    out_classes = detectBoxes.cls
    height, width = frame.shape[:2]
    for i in range(out_classes.numel()):
        if detectBoxes.conf[i] >= conf_threshold:
            cls_id = detectBoxes.cls[i]
            cls_name = cls_name_dict[int(cls_id)]
            coords = detectBoxes.xyxy[i]
            x0 = max(0, int(coords[0]))
            y0 = max(0, int(coords[1]))
            x1 = min(int(coords[2]), width-1)
            y1 = min(int(coords[3]), height-1)
            bound_color = color_list[i%len(color_list)]
            cv2.rectangle(frame, (x0, y0), (x1, y1), bound_color, 2)
            text_x = min(x0+10, width-1)
            text_y = max(0, y0 - 5)
            step_w = int(width / depth_dim)
            step_h = int(height / depth_dim)
            mean_depth = calc_depth(depth_data, step_w, step_h, x0, x1, y0, y1)
            # text_display = cls_name + ", depth:" + round(mean_depth,1)
            text_display = f"{cls_name}: depth: {round(mean_depth, 1)}"
            cv2.putText(frame, text_display,(text_x,text_y),cv2.FONT_HERSHEY_COMPLEX,0.75,(0,255,0),2)
    return frame