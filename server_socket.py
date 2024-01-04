import socket
import struct
import pickle
import pyrealsense2 as rs
import numpy as np
import cv2
import threading
import queue
import time

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
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

pipeline.start(config)

frame_buffer = queue.Queue()
MAX_BUFFER_SIZE = 500

def send_frame():
    while True:
        frame = frame_buffer.get()
        frame_data = np.asanyarray(frame.get_data())
        # Serialize the frame
        _, send_img = cv2.imencode(".jpg", frame_data)
        send_img_bytes = send_img.tobytes()
        data = pickle.dumps(send_img_bytes)
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

# def show_received():
#     data = b""
#     payload_size = struct.calcsize("L")

#     while True:
#         try:
#             data = connection.recv(1024)
#             print(f"get respond: {data}")
#         except:
#             break


def show_received():
    data = b""
    payload_size = struct.calcsize("L")
    # print("Debug, ======payload size:", payload_size)

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
        if not color_frame:
            continue
        if frame_buffer.qsize() < MAX_BUFFER_SIZE:
            frame_buffer.put(color_frame)
        else:
            print("exceed buffer size")
        # receive the result returned by client.
        # connection.setblocking(0)
        show_received()

finally:
    pipeline.stop()
    server_socket.close()
