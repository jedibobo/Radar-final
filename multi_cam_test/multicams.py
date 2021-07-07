from ctypes import create_unicode_buffer
from typing import Sequence
import gxipy as gx
import cv2
import sys
import time
import os
import multiprocessing as mp


from camera import GxCamera

class Multicam:
    def __init__(self,cams_dict,device_manager):
        self.cam_wide = GxCamera(info_dict=cams_dict['cam_wide'], device_manager=device_manager)
        self.cam_left =GxCamera(info_dict=cams_dict["cam_left"],device_manager=device_manager)
        self.cam_mid =GxCamera(info_dict=cams_dict["cam_mid"],device_manager=device_manager)
        self.cam_right =GxCamera(info_dict=cams_dict["cam_right"],device_manager=device_manager)
        self.pool=mp.Pool(processes=4)

    def cams_start(self):
        self.cam_wide.cam_start()
        self.cam_left.cam_start()
        self.cam_mid.cam_start()
        self.cam_right.cam_start()

    def cams_release(self):
        self.cam_wide.cam_release()
        self.cam_left.cam_release()
        self.cam_mid.cam_release()
        self.cam_right.cam_release()

    def read_all(self):
        # imgs = self.pool.map(thread_cam_read,[self.cam_wide,self.cam_left,self.cam_mid,self.cam_right] )
        img_wide=self.cam_wide.read_image()
        img_left=self.cam_left.read_image()
        img_mid=self.cam_mid.read_image()
        img_right=self.cam_right.read_image()
        return tuple([img_wide,img_left,img_mid,img_right])
        # return tuple(imgs)

# def thread_cam_read(cam): 
#     return cam.read_image()


def concat_imgs(img_wide,img_left,img_mid,img_right,src_size,dst_size):
    img_wide=cv2.resize(img_wide,src_size,interpolation=cv2.INTER_CUBIC)
    img_list=[[img_wide,img_left],[img_mid,img_right]]
    img_concat=cv2.vconcat([cv2.hconcat(img) for img in img_list])
    # print(img_concat.shape)
    # cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # 创建一个名为video的窗口
    # cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    img_concat=cv2.resize(img_concat,dst_size,interpolation=cv2.INTER_CUBIC)
    return img_concat

class Multivcam:#read test videos
    def __init__(self,cams_dict,device_manager):
        self.cam_wide = GxCamera(info_dict=cams_dict['cam_wide'], device_manager=device_manager)
        self.cam_left =GxCamera(info_dict=cams_dict["cam_left"],device_manager=device_manager)
        self.cam_mid =GxCamera(info_dict=cams_dict["cam_mid"],device_manager=device_manager)
        self.cam_right =GxCamera(info_dict=cams_dict["cam_right"],device_manager=device_manager)

    def cams_start(self):
        self.cam_wide.cam_start()
        self.cam_left.cam_start()
        self.cam_mid.cam_start()
        self.cam_right.cam_start()

    def cams_release(self):
        self.cam_wide.cam_release()
        self.cam_left.cam_release()
        self.cam_mid.cam_release()
        self.cam_right.cam_release()

    def read_all(self):
        return (self.cam_wide.read_image(),self.cam_left.read_image(),self.cam_mid.read_image(),self.cam_right.read_image())

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