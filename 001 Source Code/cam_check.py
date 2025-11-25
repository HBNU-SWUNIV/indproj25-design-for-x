import cv2
import os
import time
import logging
import shutil
import csv
from datetime import datetime

#CAMERA_PATH = "/dev/v4l/by-id/usb-Sonix_Technology_Co.__Ltd._USB_2.0_Camera_SN0001-video-index0"
CAMERA_PATH = "/dev/v4l/by-id/usb-HCVsight_FHD_webcam-video-index0"
SAVE_DIR = "./result"
MAX_IMAGES = 50
CAPTURE_INTERVAL = 30
LOG_FILE = "./capture.log"
CSV_FILE = "./temp.csv"
LOG_DIR = os.path.dirname(LOG_FILE)
OLD_LOG_DIR = os.path.join(LOG_DIR, "log_old")

cap = None

def open_camera():
    global cap
    while True:
        if os.path.exists(CAMERA_PATH):
            temp_cap = cv2.VideoCapture(CAMERA_PATH)
            if temp_cap.isOpened():
                cap = temp_cap
                logging.info(f"카메라 접속 성공 {CAMERA_PATH}")
                cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'YUYV'))
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
                cap.set(cv2.CAP_PROP_FPS, 5)

                width  = cap.get(cv2.CAP_PROP_FRAME_WIDTH) 
                height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
                fps    = cap.get(cv2.CAP_PROP_FPS)
                fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
                fourcc_str = "".join([chr((fourcc >> 8 * i) & 0xFF) for i in range(4)])
                print(f"해상도:{int(width)} x {int(height)}, FPS:{fps}, FOURCC:{fourcc_str}")
                logging.info(f"해상도:{int(width)} x {int(height)}, FPS:{fps}, FOURCC:{fourcc_str}")
                return True
            else:
                logging.warning(f"Found {CAMERA_PATH} but failed to open. Retrying...")
        else:
            logging.warning(f"{CAMERA_PATH} not found. Waiting...")
        time.sleep(2)

def capture_image():
    global cap
    success = False
    try:
        if cap is None or not cap.isOpened():
            logging.error("Camera not opened. Trying to reopen...")
            open_camera()

        # 카메라 문제로 한 번에 안잡히는 경우 여러번 불러와서 잡도록 설정
        for _ in range(3):
            ret, frame = cap.read()
            time.sleep(0.1)

        if not ret:
            logging.warning("Frame read failed. Reopening camera...")
            cap.release()
            open_camera()
            return None

        if not os.path.exists(SAVE_DIR):
            os.makedirs(SAVE_DIR)

        filename = datetime.now().strftime("%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(SAVE_DIR, filename)
        cv2.imwrite(filepath, frame)
        return filepath
    except Exception as e:
        logging.exception(f"Unexpected error during capture: {e}")
        return None

if __name__ == "__main__":
    try:
        open_camera()
        while True:
            capture_image()
            time.sleep(CAPTURE_INTERVAL)
    finally:
        if cap:
            cap.release()