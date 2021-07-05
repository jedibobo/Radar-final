# source = "videos/Walking Next to People.MP4"
# frame_size = (704, 1280)
# source = 0
# frame_size = (480, 640)
# frame_size = (512, 960)
# img_size = (256, 416)  # (320, 192) or (416, 256) or (608, 352) for (height, width)
# conf_thres = .3
# nms_thres = .5
iou_thres = .3
max_age = 500
maturity_period = 5


color = "red"
communite = 'disable'

width=1920
height=1200

place1=(102,325,734,867)
place2=(1044,1267,752,827)

cams_dict = {'cam_wide':  {"cam_sn": "NE0200060045", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_left':  {"cam_sn": "FG0210060411", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_mid':   {"cam_sn": "FG0210060412", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3},
             'cam_right': {"cam_sn": "FG0210060413", "expose": 35000, "gain": 8.0, "gamma_value": 1.85, "contrast_value": 0,'blue_ratio':1.3}
             }
#camera sizes 
size_wide = (1920, 1200)
size_other=(1280,960)
size=(1920,1080)