import socket
import struct
import pickle
import pyrealsense2 as rs
import numpy as np
import cv2
import threading
import queue
import time
from unifiedData import InputData
import io

# Server configuration
server_address = ('192.168.1.12', 8080)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(server_address)
server_socket.listen(5)
#server_socket.setblocking(0)
# Accept a connection from the client
connection, client_address = server_socket.accept()
print("Connection from:", client_address)

#打开 RealSense 摄像头
pipeline = rs.pipeline()
config = rs.config()
fps = 30
img_width = 640
img_height = 480
config.enable_stream(rs.stream.depth, img_width, img_height, rs.format.z16, fps)
config.enable_stream(rs.stream.color, img_width, img_height, rs.format.bgr8, fps)

profile = pipeline.start(config)

depth_sensor = profile.get_device().first_depth_sensor()
depth_scale = depth_sensor.get_depth_scale()


def get_distance(depth_value, depth_scale):
    distance = depth_value * depth_scale
    return distance

def compress_depth_img(depth_frame, 
                       unit_dim=10):
    # To reduce data size of transpotation, compress the depth image into dim: unit_dim x unit_dim
    step_w = img_width // unit_dim
    step_h = img_height // unit_dim
    compressed_data = np.zeros((unit_dim, unit_dim))
    for i in range(unit_dim):
        for j in range(unit_dim):
            mean_depth = np.mean(depth_frame[step_h*i:step_h*(i+1), step_w*j:step_w*(j+1)])
            compressed_data[i, j] = mean_depth
    return compressed_data

    

frame_buffer = queue.Queue()
MAX_BUFFER_SIZE = 500

def send_frame():
    while True:
        input = frame_buffer.get()
        data = pickle.dumps(input)
        # Send the length of the serialized data to the client
        try:
            print(f"send data, length of data:{len(data)}")
            connection.sendall(struct.pack("L", len(data)) + data)
            ret = connection.settimeout(0.2)
        except:
            print("timeout, skip this frame")
            continue

sending_thread = threading.Thread(target=send_frame)
sending_thread.start()


def show_received():
    data = b""
    payload_size = struct.calcsize("L")

    while True:
        try:
            while len(data) < payload_size:
                data += connection.recv(4096)
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]

            msg_size = struct.unpack("L", packed_msg_size)[0]
            while len(data) < msg_size:
                data += connection.recv(4096)
            frame_data = data[:msg_size]
            data = data[msg_size:]

            # Deserialize the frame
            frame = pickle.loads(frame_data)
            nparr = np.frombuffer(frame, np.uint8)
            frame_raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            cv2.imshow('processed result', frame_raw)
            cv2.waitKey(10)
        except:
            break


try:
    while True:
        frames = pipeline.wait_for_frames()
        color_frame = frames.get_color_frame()
        depth_frame = frames.get_depth_frame()
        if not color_frame or not depth_frame:
            continue
        color_image = np.asanyarray(color_frame.get_data())
        depth_image = np.asanyarray(depth_frame.get_data())
        depth_in_meters = np.vectorize(lambda d: get_distance(d, depth_scale))(depth_image)
        _, send_img = cv2.imencode(".jpg", color_image)
        image_data = send_img.tobytes()
        unit_dim = 10
        depth_data = compress_depth_img(depth_in_meters, unit_dim)
        input_frame = InputData(image_data, depth_data, img_width, img_height, unit_dim)
        if frame_buffer.qsize() < MAX_BUFFER_SIZE:
            frame_buffer.put(input_frame)
        else:
            print("exceed buffer size")
        # receive the result returned by client.
        # connection.setblocking(0)
        show_received()

finally:
    pipeline.stop()
    server_socket.close()
