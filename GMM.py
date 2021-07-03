import cv2
import numpy as np
class GMM_mask:
    def __init__(self,kernel_size=(3,3),min_threshold=150,):
        self.fgbg = cv2.createBackgroundSubtractorKNN(detectShadows=False)
        # self.fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)
        self.kernel = cv2.getStructuringElement(cv2.MORPH_RECT, kernel_size)
        self.min_threshold=min_threshold

    def get_mask(self,frame):
        self.fgmask = self.fgbg.apply(frame)
        _, self.fgmask = cv2.threshold(self.fgmask, self.min_threshold, 255, cv2.THRESH_BINARY)
        self.fgmask = cv2.morphologyEx(self.fgmask, cv2.MORPH_OPEN, self.kernel)
        
        return self.fgmask
    
    def cal_space(self,xmin, ymin, w, h):
        return np.sum(self.fgmask[ymin:ymin+h,xmin:xmin+w])
