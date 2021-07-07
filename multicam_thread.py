from ctypes import create_unicode_buffer
from typing import Sequence
import gxipy as gx
import cv2
import sys
import time
import os
import multiprocessing as mp
import queue
import threading

from camera import GxCamera

class camera_thread(threading.Thread):
    def __init__(self,info_dict,device_manager):
        threading.Thread.__init__(self)
        self.cam=GxCamera(info_dict=info_dict, device_manager=device_manager)
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

class Multicam:
    def __init__(self,cams_dict,device_manager):
        self.cam_wide = camera_thread(info_dict=cams_dict['cam_wide'], device_manager=device_manager)
        self.cam_left =camera_thread(info_dict=cams_dict["cam_left"],device_manager=device_manager)
        self.cam_mid =camera_thread(info_dict=cams_dict["cam_mid"],device_manager=device_manager)
        self.cam_right =camera_thread(info_dict=cams_dict["cam_right"],device_manager=device_manager)
        # self.pool=mp.Pool(processes=4)

    def cams_start(self):
        self.cam_wide.start()
        self.cam_left.start()
        self.cam_mid.start()
        self.cam_right.start()

    def cams_release(self):
        self.cam_wide.kill_thread()
        self.cam_left.kill_thread()
        self.cam_mid.kill_thread()
        self.cam_right.kill_thread()

    def read_all(self):
        # imgs = self.pool.map(thread_cam_read,[self.cam_wide,self.cam_left,self.cam_mid,self.cam_right] )
        img_wide=self.cam_wide.get_image()
        img_left=self.cam_left.get_image()
        img_mid=self.cam_mid.get_image()
        img_right=self.cam_right.get_image()
        return tuple([img_wide,img_left,img_mid,img_right])
        # return tuple(imgs)

def concat_imgs(img_wide,img_left,img_mid,img_right,src_size,dst_size):
    img_wide=cv2.resize(img_wide,src_size,interpolation=cv2.INTER_CUBIC)
    img_list=[[img_wide,img_left],[img_mid,img_right]]
    img_concat=cv2.vconcat([cv2.hconcat(img) for img in img_list])
    # print(img_concat.shape)
    # cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # 创建一个名为video的窗口
    # cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    img_concat=cv2.resize(img_concat,dst_size,interpolation=cv2.INTER_CUBIC)
    return img_concat

# import config
# device_manager = gx.DeviceManager()
# dev_num, dev_info_list = device_manager.update_device_list() 
# caps=Multicam(config.cams_dict,device_manager=device_manager)
# caps.cams_start()
# fourcc = cv2.VideoWriter_fourcc(*'XVID')
# out = cv2.VideoWriter("result.avi", fourcc, 25, config.size)
# fps = 25

# size=None
# count=0
# while True:
#     count+=1
#     if count>100:
#         break
#     img_wide,img_left,img_mid,img_right=caps.read_all()

#     # img_wide=cv2.resize(img_wide,config.size_other,interpolation=cv2.INTER_CUBIC)
#     # print(img_wide.shape,img_left.shape,img_mid.shape)
#     img_concat=concat_imgs(img_wide,img_left,img_mid,img_right,config.size_other,config.size)

#     cv2.imshow('video', img_concat)   # 将捕捉到的图像在video窗口显示
#     # out.write(img_concat)    # 将捕捉到的图像存储
#     if size is None:
#         size = (img_concat.shape[1], img_concat.shape[0])
#         fourcc = cv2.VideoWriter_fourcc(
#             'X', 'V', 'I', 'D')  # opencv3.0
#         videoWriter = cv2.VideoWriter(
#             "result.avi", fourcc, fps, size)
    
#     out.write(img_concat)
#     # 按esc键退出程序
#     if cv2.waitKey(1) & 0xFF == 27:
#         break 