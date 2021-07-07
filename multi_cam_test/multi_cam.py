from typing import Sequence
import gxipy as gx
import cv2
import sys
import time
import os


from camera import GxCamera
cams_dict = {'cam_wide':  {"cam_sn": "NE0200060045", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_left':  {"cam_sn": "FG0210060411", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_mid':   {"cam_sn": "FG0210060412", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_right': {"cam_sn": "FG0210060413", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3}
             }


gain = 8.0
exposuretime = 35000
gamma_value = 1.85
contrast_value = 0


device_manager = gx.DeviceManager()
dev_num, dev_info_list = device_manager.update_device_list()
# print(dev_info_list)


cam_wide = GxCamera(info_dict=cams_dict['cam_wide'], device_manager=device_manager)
cam_left =GxCamera(info_dict=cams_dict["cam_left"],device_manager=device_manager)
cam_mid =GxCamera(info_dict=cams_dict["cam_mid"],device_manager=device_manager)
cam_right =GxCamera(info_dict=cams_dict["cam_right"],device_manager=device_manager)

cam_wide.cam_start()
cam_left.cam_start()
cam_mid.cam_start()
cam_right.cam_start()
# 视频存储的格式
fourcc = cv2.VideoWriter_fourcc(*'XVID')
# 帧率
#fps = cam.AcquisitionFrameRate.get()
# 视频的宽高
#size = (cam.Width.get(),cam.Height.get())
size_wide = (1920, 1200)
size_other=(1280,960)
size=(1920,1080)
# print(cam.Width.get(),cam.Height.get())
# 文件名定义
# filename = './video_' + \
#     time.strftime("%Y%m%d_%H%M%S", time.localtime())+'.avi'
# 视频存储
out = cv2.VideoWriter("result.avi", fourcc, 25, size)
fps = 25
sequence_cam=['wide','left','mid','right']

# size = None
count=0
while True:
    count+=1
    if count>100:
        break
    img_wide=cam_wide.read_image()
    img_left=cam_left.read_image()
    img_mid=cam_mid.read_image()
    img_right=cam_right.read_image()

    img_wide=cv2.resize(img_wide,size_other,interpolation=cv2.INTER_CUBIC)
    print(img_wide.shape,img_left.shape,img_mid.shape)
    img_list=[[img_wide,img_left],[img_mid,img_right]]
    img_concat=cv2.vconcat([cv2.hconcat(img) for img in img_list])
    # print(img_concat.shape)
    cv2.namedWindow('video', cv2.WINDOW_NORMAL)  # 创建一个名为video的窗口
    cv2.setWindowProperty('video', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    img_concat=cv2.resize(img_concat,size,interpolation=cv2.INTER_CUBIC)
    cv2.imshow('video', img_concat)   # 将捕捉到的图像在video窗口显示
    # out.write(img_concat)    # 将捕捉到的图像存储
    if size is None:
        size = (img_concat.shape[1], img_concat.shape[0])
        fourcc = cv2.VideoWriter_fourcc(
            'X', 'V', 'I', 'D')  # opencv3.0
        videoWriter = cv2.VideoWriter(
            "result.avi", fourcc, fps, size)
    
    out.write(img_concat)
    # 按esc键退出程序
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 停止录制,关闭设备
cam_wide.cam_release()
cam_left.cam_release()
cam_mid.cam_release()
cam_right.cam_release()


