# from camera import GxCamera
from multicams import Multicam, concat_imgs

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
from utils import unpack_results, parse_args, watcher_alert_areas
from GMM import GMM_mask

import config
import sys
import gxipy as gx
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
                                memory_optimize=True, max_trt_batch_size=4,use_calib_mode=False,)
# use imgs for testing
mask = GMM_mask()
# tracker=SORT_Tracker()


def test_images(path):
    pass


def test_video(video_path):
    if video_path == "cam":
        cap = cv2.VideoCapture(0)  # stil single usb
    elif video_path == "daheng":
        device_manager = gx.DeviceManager()
        dev_num, dev_info_list = device_manager.update_device_list() 
        caps = Multicam(config.cams_dict,device_manager)
        caps.cams_start()
    else:
        cap = cv2.VideoCapture(video_path)
    size = None
    # fps = int(cap.get(5))
    fps = 25

    # best_target=None
    cv2.namedWindow("result", cv2.WINDOW_NORMAL)  # 创建一个名为video的窗口
    cv2.setWindowProperty("result", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    while True:
        start = time.time()
        if video_path == "daheng":
            img_tuple = caps.read_all()
            if img_tuple[0] is not None and img_tuple[1] is not None and img_tuple[2] is not None and img_tuple[3] is not None:
                img_tuple = (cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
                             for img in img_tuple)
            else:
                caps.cams_release()

                # 相机全部重启
                device_manager = gx.DeviceManager()
                dev_num, dev_info_list = device_manager.update_device_list()
                while dev_num != 4:
                    dev_num, dev_info_list = device_manager.update_device_list()
                caps = Multicam(config.cams_dict,device_manager)
                caps.cams_start()
                # 防止imshow的问题，重启所有cams
                print("restarting all cameras!!!!!!!!!!!!!!!!!")
                continue
        else:
            _, img = cap.read()
            if img is None:
                break
        img_wide, img_left, img_mid, img_right=img_tuple
        # print(type(img_right),type(img_tuple))
        print(img_wide.shape,img_left.shape,img_mid.shape)
        # results = detect_model.batch_predict((img_wide,img_wide,img_wide,img_wide), eval_transforms)
        # fgmask = mask.get_mask(img_wide)  # GMM get fmask for moving objects
        # # end=time.time()
        # img_wide = unpack_results(
        #     results[0], img_wide, GMMmask=mask, WITH_GMM=True)
        # img_left = unpack_results(
        #     results[1], img_left, GMMmask=None, WITH_GMM=False)
        # img_mid = unpack_results(
        #     results[2], img_mid, GMMmask=None, WITH_GMM=False)
        # img_right = unpack_results(
        #     results[3], img_right, GMMmask=None, WITH_GMM=False)

        img_concat = concat_imgs(img_wide, img_left, img_mid, img_right,
                                 src_size=config.size_other, dst_size=config.size)


        cv2.imshow("result",img_concat)

        if size is None:
            size = (img_concat.shape[1], img_concat.shape[0])
            fourcc = cv2.VideoWriter_fourcc(
                'm', 'p', '4', 'v')  # opencv3.0
            videoWriter = cv2.VideoWriter(
                './videos/result{}.mp4'.format(round(time.time()*1000)), fourcc, fps, size)
        videoWriter.write(img_concat)
        if cv2.waitKey(1) & 0xFF == 27:
            sys.exit(1)
        end = time.time()
        print(1/(end-start))
    if video_path == "daheng":
        caps.cams_release()

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
