import cv2
import socket
import struct
import pickle
from cnocr import CnOcr
from PIL import ImageFont, ImageDraw, Image
import numpy as np
import threading
import queue
import time
from renderProcess import render_result
from unifiedData import InputData, outputData

frame_queue = queue.Queue()
result_queue = queue.Queue()
MAX_QUEUE_SIZE=500
ocr_threshold = 0.5

def send_back():
    while True:
        try:
            result = result_queue.get_nowait()
            result_data = pickle.dumps(result)
            try:
                print(f"send result data, length of data:{len(result_data)}")
                # client_socket.setblocking(0)
                client_socket.sendall(struct.pack("L", len(result_data)) + result_data)
                ret = client_socket.settimeout(0.5)
            except:
                print("timeout, skip this frame's result")
                continue
        except queue.Empty:
            print("sendback Queue is empty")
            time.sleep(0.1)
            continue

def process_video():
    from ultralytics import YOLO
    model = YOLO('yolov8n.pt')
    while True:
        try:
            input = frame_queue.get_nowait()
            print("Get one frame to process")

            nparr = np.frombuffer(input.color_data, np.uint8)
            frame_raw = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            results = model(frame_raw)
            # annotated_frame = results[0].plot()
            depth_data = input.depth_data
            depth_dim = input.unit_dim
            detect_boxes = results[0].boxes
            frm_id = input.frame_id
            result_frame = render_result(frame_raw, depth_data, depth_dim, detect_boxes)
            #process qrcode
            detector = cv2.QRCodeDetector()
            retval, decoded_info, points, _ = detector.detectAndDecodeMulti(result_frame)
            height, width = result_frame.shape[:2]
            if retval:
                print(f"Decoded Information: {decoded_info}")
                #draw the result of decoded QRCode
                minX = 100000
                minY = 100000
                maxX = -1
                maxY = -1
                assert len(points) == len(decoded_info)
                for point,decoded_val in zip(points, decoded_info):
                    for idx in range(point.shape[0]):
                        x = int(point[idx][0])
                        y = int(point[idx][1])
                        minX = x if x < minX else minX
                        minY = y if y < minY else minY
                        maxX = x if x > maxX else maxX
                        maxY = y if y > maxY else maxY
                    cv2.rectangle(result_frame, (minX, minY), (maxX, maxY), color=(0,255,0), thickness=2)
                    text_x = min(minX+10, width-1)
                    text_y = max(0, minY - 5)
                    text_info = "qrcode: " + decoded_val
                    cv2.putText(result_frame, text_info,(text_x,text_y), cv2.FONT_HERSHEY_COMPLEX,0.75,(0,255,0),2)
            #process ocr part
            ocr = CnOcr(rec_model_name='chinese_cht_PP-OCRv3')
            out = ocr.ocr(frame_raw)

            ocr_text = ''
            fontPath = 'ocr/NotoSerifTC-Regular.otf'
            font = ImageFont.truetype(fontPath, 20)    #set font size
            imgPil = Image.fromarray(result_frame)
            draw = ImageDraw.Draw(imgPil)
            for i in range(len(out)):
                if out[i]['score'] > ocr_threshold:
                    coords = out[i]['position']
                    minX = 100000
                    maxX = -1
                    minY = 100000
                    maxY = -1
                    for coord in coords:
                        x = int(coord[0])
                        y = int(coord[1])
                        minX = minX if minX < x else x
                        minY = minY if minY < y else y
                        maxX = maxX if maxX > x else x
                        maxY = maxY if maxY > y else y
                    if len(out[i]['text']) <= 0:
                        print("skip")
                        continue
                    ocr_text = ocr_text + out[i]['text']
                    draw.rectangle([(minX, minY), (maxX, maxY)], outline="green")
                    text_x = min(minX+10, width-1)
                    text_y = max(0, minY-5)

                    draw.text((text_x, text_y), out[i]['text'], fill=(0,0,255), font=font)

            print(f"ocr text: {ocr_text}")
            out_frame = np.array(imgPil)
            _, img = cv2.imencode(".jpg", out_frame)
            img_bytes = img.tobytes()
            out_result = outputData(img_bytes, width, height, frame_id=frm_id, ocr_text=ocr_text)
            result_queue.put(out_result)
        except queue.Empty:
            print("process Queue is empty")
            time.sleep(0.1)
            continue


model_thread = threading.Thread(target=process_video)
model_thread.start()

return_thread = threading.Thread(target=send_back)
return_thread.start()

time.sleep(1)

# Server configuration
server_address = ('192.168.1.12', 8080)

# Connect to the server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(server_address)




# Receive data from the server
data = b""
payload_size = struct.calcsize("L")

while True:
    try:
        while len(data) < payload_size:
            data += client_socket.recv(4096)
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]

        msg_size = struct.unpack("L", packed_msg_size)[0]
        while len(data) < msg_size:
            data += client_socket.recv(4096)
        frame_data = data[:msg_size]
        data = data[msg_size:]

        # Deserialize the frame
        frame = pickle.loads(frame_data)
        if frame_queue.qsize() < MAX_QUEUE_SIZE:
            frame_queue.put(frame)
        else:
            print("do not process this frame")
    except:
        print("timeout to receive, skip")
        data = b""
        continue
