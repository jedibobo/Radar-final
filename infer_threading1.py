from gxipy.gxiapi import Timeout
from camera import GxCamera
from utils import unpack_results
from typing import Mapping
from numpy.lib.utils import source
import paddlex as pdx
import os
import time
import deploy
import cv2
from paddlex.det import transforms
import numpy as np
from utils import unpack_results, parse_args, watcher_alert_areas,concat_imgs
from GMM import GMM_mask
# from SORT import SORT_Tracker
# from RM_radar_communicate.transmit import referee_transmit
import config
import sys
import gxipy as gx
import threading
import queue

device_manager = gx.DeviceManager()

path = "./imgs"
font = cv2.FONT_HERSHEY_SIMPLEX


# digit_model=digit_detector('RM-resnet18/',use_static=False,use_dynamic_input=True,precision_mode="FP16")
# if config.communite == 'enable':
#     referee_transmit_h = referee_transmit(config.color)


eval_transforms = transforms.Compose([
    transforms.Resize(target_size=416, interp='CUBIC'),
    transforms.Normalize(),
])

detect_model = deploy.Predictor('yolov3-inference-416', use_gpu=True, use_trt=True, use_static=True,
                                use_dynamic_input=False, precision_mode="FP16", use_glog=False,
                                memory_optimize=True, use_calib_mode=False,max_trt_batch_size=4)
# use imgs for testing
# mask = GMM_mask()
# tracker=SORT_Tracker()

cv2.namedWindow("cams", cv2.WINDOW_NORMAL)  # 创建一个名为video的窗口
cv2.setWindowProperty("cams", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
def test_images(path):
    pass


info_dict1 = config.cams_dict['cam_left']
info_dict2 = config.cams_dict['cam_mid']
info_dict3 = config.cams_dict['cam_right']

device_manager = gx.DeviceManager()

class camera_thread(threading.Thread):
    def __init__(self,camera_info_dict,device_manager):
        threading.Thread.__init__(self)
        self.cam=GxCamera(info_dict=camera_info_dict, device_manager=device_manager)
        self.cam.cam_start()
        self.img_queue = queue.Queue(2)

    def run(self):
        while True:
            img=self.cam.read_image()
            self.img_queue.put(img)
            
    def get_image(self):
        return self.img_queue.get(timeout=1)
    
    def kill_thread(self):
        self.cam.cam_release()
        
# dev_num, dev_info_list = device_manager.update_device_list() 
def test_video(video_path):
    if video_path == "cam":
        cap = cv2.VideoCapture(0)
    elif video_path == "daheng":
        camera_left=camera_thread(info_dict1,device_manager)
        camera_mid=camera_thread(info_dict2,device_manager)
        camera_right=camera_thread(info_dict3,device_manager)

        camera_left.start()
        camera_mid.start()
        camera_right.start()
        # cap = GxCamera(info_dict,device_manager)
        # cap.cam_start()
    else:
        cap = cv2.VideoCapture(video_path)
    size = None
    # fps = int(cap.get(5))
    fps = 25

    best_target = None
    count=0
    start_all =time.time()
    while True:
        if count <2000:
            count+=1
        else:
            print("avg fps:",2000/(time.time()-start_all))
            break
        start = time.time()
        if video_path == "daheng":
            img_left = camera_left.get_image()
            img_mid =camera_mid.get_image()
            img_right =camera_right.get_image()
            if (img_left is not None) and (img_mid is not None) and (img_right is not None):
                img_left = cv2.cvtColor(img_left, cv2.COLOR_RGB2BGR)
                img_mid = cv2.cvtColor(img_mid,cv2.COLOR_RGB2BGR)
                img_right =cv2.cvtColor(img_right,cv2.COLOR_RGB2BGR)
            else:
                
                camera_left.kill_thread()
                camera_mid.kill_thread()
                camera_right.kill_thread()

                dev_num, dev_info_list = device_manager.update_device_list()
                while dev_num != 4:
                    dev_num, dev_info_list = device_manager.update_device_list()
                # cap = GxCamera(1)
                # cap.cam_start()

                print("restarting camera!!!!!!!!!!!!!!!!!")
                continue
        else:
            _, img = cap.read()
            if img is None:
                break

        results = detect_model.batch_predict((img_left,img_mid,img_right), eval_transforms)
        # fgmask = mask.get_mask(img)  # GMM get fmask for moving objects
        # end=time.time()
        img_left=unpack_results(results[0],img_left,GMMmask=None,WITH_GMM=False)
        img_mid=unpack_results(results[1],img_mid,GMMmask=None,WITH_GMM=False)
        img_right=unpack_results(results[0],img_right,GMMmask=None,WITH_GMM=False)

        cv2.putText(img_left, 'img_left',
                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)        
        cv2.putText(img_mid, 'img_mid',
                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)
        cv2.putText(img_right, 'img_right',
                    (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), thickness=2)
        # img=watcher_alert_areas(img)
        img_concat=concat_imgs(img_left,img_left,img_mid,img_right,config.size_other,config.size)
        # img_concat = cv2.resize(img, (1920//2, 1080//2))
        cv2.imshow("cams",img_concat)

        if size is None:
            size = (img_concat.shape[1], img_concat.shape[0])
            fourcc = cv2.VideoWriter_fourcc(
                'm', 'p', '4', 'v')  # opencv3.0
            videoWriter = cv2.VideoWriter(
                './videos/threecams-result{}.mp4'.format(round(time.time()*1000)), fourcc, fps, size)
        videoWriter.write(img_concat)
        if cv2.waitKey(1) & 0xFF == 27:
            sys.exit(1)
        end = time.time()
        print(1/(end-start))
    # if video_path == "daheng":
    #     cap.cam_release()
    cv2.destroyAllWindows()
    sys.exit(1)


def main():
    args = parse_args()
    if args.video:
        if args.source == "cam":
            test_video("cam")
        elif args.source == "daheng":
            test_video("daheng")
        else:
            test_video(args.source)
    else:
        test_images(path)


main()
