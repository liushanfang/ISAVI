# ISAVI
## How to build realsense SDK
### Prepare
```bash
sudo apt-get install libudev-dev pkg-config libgtk-3-dev
sudo apt-get install libusb-1.0-0-dev pkg-config
sudo apt-get install libglfw3-dev
sudo apt-get install libssl-dev
```

### build and install librealsense
```bash
git clone https://github.com/IntelRealSense/librealsense
cd librealsense
mkdir build
cd build
cmake ../ -DBUILD_EXAMPLES=true
make
sudo make install
```

### Plugin realsense camera and test
```bash
realsense-viewer
```
### install pyrealsense2
``` bash
pip install pyrealsense2
```
## Set up environment for yolov5/yolov8
reference [link](https://github.com/ultralytics/yolov5)
```bash
pip install PyYAML
pip install ultralytics
pip install -r requirements.txt
```
## Set up environment for ocr part
reference [cnOCR](https://cnocr.readthedocs.io/zh/latest/install/)
```bash
$ pip install cnocr[ort-cpu]
```
or on gpu
```bash
$ pip install cnocr[ort-gpu]
```
## Set up environment for rtmp-server
```bash
sudo apt-get update
sudo apt-get install nginx
sudo apt-get install ffmpeg
sudo ufw allow 'Nginx HTTP'
systemctl status nginx
sudo apt-get install libnginx-mod-rtmp
```
and then edit file /etc/nginx/nginx.conf, add following part to the file:
```bash
rtmp {
        server {
                listen 1935;
                chunk_size 4096;
                allow publish 127.0.0.1;
                allow publish 192.168.1.12;   #Here change according to your IP

                application live {
                        live on;
                        record off;
                }
        }
}
```
Save the file. And Next
```bash
sudo ufw allow 1935/tcp
sudo systemctl reload nginx.service
```
## How to run:
on server side:
```bash
python server.py
```
on client side:
```bash
python client.py
```
