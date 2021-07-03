import cv2
font = cv2.FONT_HERSHEY_SIMPLEX
import numpy as np
import thresholds
import config
import argparse
import time


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--video",
        type=bool,
        default=False,
        help="Whether use camera."
    )
    parser.add_argument(
        "--source",
        type=str,
        default="",
        help=
        "path for videos of camera, cam for camera input."
    )
    return parser.parse_args()

def watcher_alert_areas(processed_img):
    cv2.rectangle(processed_img,(1044,752),(1267,827),(0, 255, 0), 2)
    cv2.putText(processed_img,"NUM 2 area!",(1100,730), font, 2, (255, 255, 255), thickness=1)
    # cv2.rectangle(processed_img,(745,765),(884,796),(0, 255, 0), 2)
    # cv2.putText(processed_img,"NUM 2 area!",(800,765), font, 2, (255, 255, 255), thickness=1)
    cv2.rectangle(processed_img,(102,734),(325,867),(0, 255, 0), 2)
    cv2.putText(processed_img,"NUM 1 area!",(200,730), font, 2, (255, 255, 255), thickness=1)
    return processed_img

def revert(xmin,xmax,ymin,ymax):
    if xmin<0:
        xmin=0
    if xmax>config.width:
        xmax=config.width
    if ymin<0:
        ymin=0
    if ymax>config.height:
        ymax=config.height
    return (xmin,xmax,ymin,ymax)

def inside(place,axmin,axmax,aymin,aymax):
    thres=0.2
    pxmin,pxmax,pymin,pymax=place[0:4]

    aarea = (axmax - axmin) * (aymax - aymin)  # cal armor box area

# 求相交矩形的左下和右上顶点坐标(xmin, ymin, xmax, ymax)

    xmin = max(axmin, pxmin)  # 得到左下顶点的横坐标
    ymin = max(aymin, pymin)  # 得到左下顶点的纵坐标
    xmax = min(axmax, pxmax)  # 得到右上顶点的横坐标
    ymax = min(aymax, pymax)  # 得到右上顶点的纵坐标

    # 计算相交矩形的面积

    w = xmax - xmin
    h = ymax - ymin
    if w <=0 or h <= 0:
        return False
    inside_area = w * h
    if inside_area/aarea<thres:
        return False
    else:
        return True

def enemy_area_inside_forwatcher(armor):#armor:armor_count,num,xmin,xmax,ymin,ymax place:xmin,xmax,ymin,ymax
     #armor box area inside /all armor box area   

    axmin,axmax,aymin,aymax=armor[0:4]
    
    if inside(config.place1,axmin,axmax,aymin,aymax):
        return 1
    elif inside(config.place2,axmin,axmax,aymin,aymax):
        return 2
    else:
        return 0

# def unpack_results(result,processed_img,mask,WITH_GMM=True):
def unpack_results(result,img,GMMmask=None,WITH_GMM=False):
    # filtered_results=[]
    # tracking_list = []
    # map_points=[]
    soldiers_dict={}
    soldiers_count=0
    armor_count=0
    armor_result=[]
    o_area=0
    for value in result:
        xmin, ymin, w, h = np.array(value['bbox']).astype(np.int)
        # #print(xmin, ymin, w, h,img.shape)
        cls = value['category']
        score = value['score']
        if cls=="car" or cls=="watcher":
            if WITH_GMM : #这里更改GMM的对象
                o_area=GMMmask.cal_space(xmin,ymin,w,h)

                if score < thresholds.GMM_Object_Detect_threshold or o_area/w/h/255 <thresholds.GMM_threshold:
                    continue
                if score < thresholds.threshold:
                    continue
            else:
                if score < thresholds.threshold:
                    continue

        if cls=="red_armor" or cls=="blue_armor" and score >thresholds.armor_threshold:
            xmin,xmax,ymin,ymax=revert(xmin,xmin+w,ymin,ymin+h)
            color=cls.split('_')[0]
            if color!=config.color:
                # print(color)
                enemy_area=enemy_area_inside_forwatcher((xmin,xmax,ymin,ymax))
                # if enemy_area!=0:
                #     print("enemy_area",enemy_area)
                #     if config.communite == 'enable':
                #         rt.send('sentry',enemy_area)
                    # time.sleep(0.5)
                    #send to sentry

            cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (0, 255, 0), 2)
            cv2.putText(img, '{:s} {}'.format(cls.split('_')[0],"armor"),
                    (xmin, ymin-10), font, 0.5, (255, 255, 255), thickness=1)
    
    return img