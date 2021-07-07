import gxipy as gx
import cv2

import numpy as np

import time


class GxCamera():
    def __init__(self, info_dict=None, device_manager=None):
        self.cam=device_manager.open_device_by_sn(info_dict['cam_sn'])
        self.cam.ExposureTime.set(info_dict['expose'])
        # set gain
        self.cam.Gain.set(info_dict['gain'])

        # fps,may not be effective
        # self.cam.AcquisitionFrameRateMode.set(1)
        # self.cam.AcquisitionFrameRate.set(60.0)
        # white balance
        self.cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.RED)  # .set(2.0)
        self.cam.BalanceRatio.set(2.0)
        self.cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.GREEN)
        self.cam.BalanceRatio.set(info_dict['blue_ratio'])
        self.cam.BalanceRatioSelector.set(gx.GxBalanceRatioSelectorEntry.BLUE)
        self.cam.BalanceRatio.set(2.0)

        # get param of improving image quality
        if self.cam.GammaParam.is_readable():
            self.gamma_value = info_dict['gamma_value']
            self.gamma_lut = gx.Utility.get_gamma_lut(self.gamma_value)
        else:
            self.gamma_lut = None
        if self.cam.ContrastParam.is_readable():
            self.contrast_value = info_dict['contrast_value']
            self.contrast_lut = gx.Utility.get_contrast_lut(
                self.contrast_value)
        else:
            self.contrast_lut = None
        if self.cam.ColorCorrectionParam.is_readable():
            self.color_correction_param = self.cam.ColorCorrectionParam.get()
        else:
            self.color_correction_param = 0

        # start data acquisition
        # self.cam.stream_on()

    def cam_start(self):
        self.cam.stream_on()

    def read_image(self):
        # get raw image
        raw_image = None
        while raw_image is None:
            raw_image = self.cam.data_stream[0].get_image()

        # if raw_image is None:
        #     print("Getting image failed.")
        #     return None

        # get RGB image from raw image
        rgb_image = raw_image.convert("RGB")
        numpy_image = rgb_image.get_numpy_array()
        numpy_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
        # if rgb_image is None:
        #     return None

        # improve image quality
        # print("color_correction_param", self.color_correction_param,
        #       "contrast_lut", self.contrast_lut, "gamma_lut", self.gamma_lut)
        rgb_image.image_improvement(
            self.color_correction_param, self.contrast_lut, self.gamma_lut)

        # create numpy array with data from raw image
        numpy_image = rgb_image.get_numpy_array()
        # numpy_image[1] = numpy_image[1]*0.65
        # show acquired image
        # img = Image.fromarray(numpy_image, 'RGB')
        # img.show()

        # print height, width, and frame ID of the acquisition image
        # print("Frame ID: %d   Height: %d   Width: %d"
        #       % (raw_image.get_frame_id(), raw_image.get_height(), raw_image.get_width()))
        return numpy_image

    def cam_release(self):
        # stop data acquisition
        self.cam.stream_off()

        # close device
        self.cam.close_device()


