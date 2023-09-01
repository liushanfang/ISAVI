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
## Set up environment for yolov5
reference [link](https://github.com/ultralytics/yolov5)
```bash
pip install PyYAML
pip install ultralytics
pip install -r requirements.txt
```
