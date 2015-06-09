#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""Video Magnifier, for readers with impaired vision

Initially tested only with a Logitech C920 HD webcam on Ubuntu 14.04.  
The C920 has problems with auto-focussing on documents, which is why 
the UVC_xxx functions were added - via the UVCDYNCTRL program (part of 
libwebcam), autofocus can be switched off and focus adjusted manually.

Keyboard controls:
	1 - normal colours
	2 - colours inverted
	3 - auto-contrast off
	4 - auto-contrast on
	5 - black-on-yellow mode off
	6 - black-on-yellow mode on

	num-pad 1 - 100% zoom
	num-pad 2 - 200% zoom
	num-pad 3 - 300% zoom

	up-arrow - increase brightness
	down-arrow - decrease brightness
	left-arrow - decrease contrast
	right-arrow - increase contrast
	Home key - reset to default colours, brightness and contrast

	space-bar - freeze frame, or grab a new frozen frame
	left-Ctrl - unfreeze frame

	F1 - don't show parameter text overlay
	F2 - show parameters overlaid on image

	num-pad Enter - autofocus on
	num-pad '+' - autofocus off, increase focus value
	num-pad '-' - autofocus off, decrease focus value

This module makes extensive use of OpenCV, which (as at May 2015) can not
be used with Python 3.  OpenCV 3.0 should be released late 2015, this will
be compatible with Python 3, and will add text recognition!

Example:
      $ python2.7 VideoMagnifier.py

"""

import cv2
import string, copy
import UVC_functions
import numpy as np
import ConfigParser
from PIL import Image, ImageEnhance

COLOUR_BLACK = (0, 0, 0)
COLOUR_BLUE = (255, 0, 0)
COLOUR_GREEN = (0, 255, 0)
COLOUR_RED = (0, 0, 255)
COLOUR_CYAN = (255, 255, 0)
COLOUR_MAGENTA = (255, 0, 255)
COLOUR_YELLOW = (0, 255, 255)
COLOUR_WHITE = (255, 255, 255)

def ConfigSectionMap(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def main():
    cv2.namedWindow("Video Magnifier", 1)

    # capture from default camera
    cap = cv2.VideoCapture(-1)

    if not (cap.isOpened()):
        print("Failed to open the webcam device!")
    else:
        print("Webcam device opened OK")
        print("UVC device name:", UVC_functions.device_name())
        main_loop(cap)

    cv2.destroyAllWindows()
    cv2.VideoCapture(-1).release()


def main_loop(cap):
    inverted = False
    autocontrast = False
    black_on_yellow = False
    freeze = False
    magnification = 1.0
    brightness = 1.0
    contrast = 1.0
    sharpness = 1.0
    show_params = False
    take_new_frame = False
    UVC_functions.set_autofocus(True)
    autofocus = True
    focusval = 0
    rotate180 = False

    # default values for grabbed-frame height and width:
    cam_width = 1920
    cam_height = 1080
    crop_width = 100
    crop_height = 100

    config = ConfigParser.ConfigParser()
    cfg_read = config.read("EVidMag.cfg")
    print(cfg_read)
    if cfg_read == []:
        print("Unable to read configuration file VidMag.cfg!")
    else:
        user_options = []
        try:
            user_options = ConfigSectionMap(config, "USER")
        except:
            print("Failed to read section [USER] from configuration file!")
        print("User options:", user_options)
        camera_cfg_file = user_options['camera_config']
        if camera_cfg_file != "":
            camera_cfg_file += ".cfg"
            cam_config = ConfigParser.ConfigParser()
            cam_cfg_read = cam_config.read(camera_cfg_file)
            if cam_cfg_read != []:
                cam_options = ConfigSectionMap(cam_config, "Resolution")
                try:
                    cam_width = int(cam_options['width'])
                    cam_height = int(cam_options['height'])
                except ValueError:
                    print("Height or Width setting invalid!")
            else:
                print("Invalid Camera_Config specified in VidMan.cfg, section [USER] - using default frame size 1920 x 1080")
        else:
            print("No Camera_Config specified in VidMan.cfg, section [USER] - using default frame size 1920 x 1080")
        crop_height_str = user_options['crop_height']
        try:
            crop_height = int(crop_height_str)
        except ValueError:
            crop_height = cam_height
        crop_width_str = user_options['crop_width']
        try:
            crop_width = int(crop_width_str)
        except ValueError:
            crop_width = cam_width
        crop_width = min(crop_width, cam_width)
        crop_height = min(crop_height, cam_height)

    # TEMPORARY!!!
    #exit()
    # TEMPORARY!!!

    # Set the width and height to maximum
    # Logitech C920:
#    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, cam_width)
#    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, cam_height)
    # Logitech Quickcam Pro 9000:
    # cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1600)
    #cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1200)
    # Ipevo Ziggi HD:
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_WIDTH, 1920)
    cap.set(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT, 1080)

    img = np.zeros((cam_height, cam_width, 3), np.uint8)  # initialise img as blank
    cv2.putText(img, "No camera", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 5.0, COLOUR_GREEN, 2)

    while True:
        if not freeze:  # "live" mode - grab a new image on each pass round this loop
            ret, img = cap.read()
            print ret
            working_img = img  # save creating a new object - directly modify the newly-grabbed frame
        else:  # freeze-frame
            if take_new_frame:
                take_new_frame = False
                for i in range(0, 5):  # (need to flush some buffered frames from the camera)
                    ret, img = cap.read()
            working_img = copy.copy(img)  # keep the grabbed frame unmodified, create a copy to work on

        # crop the captured frame, if required:
        if (crop_width < cam_width) or (crop_height < cam_height):
            working_img = working_img[0.5 * (cam_height - crop_height):0.5 * (cam_height + crop_height),
                          0.5 * (cam_width - crop_width):0.5 * (cam_width + crop_width)]

        if rotate180:
            working_img = cv2.flip(working_img, -1)  # compensate for webcam being mounted effectively upside-down

        if inverted:
            working_img = 255 - working_img

        if magnification > 1.0:
            height, width = working_img.shape[:2]
            cropped_img = working_img[0.5 * height * (1 - 1 / magnification):0.5 * height * (1 + 1 / magnification),
                          0.5 * width * (1 - 1 / magnification):0.5 * width * (1 + 1 / magnification)]
            #working_img = cv2.resize(cropped_img, None, fx=magnification, fy=magnification, interpolation = cv2.INTER_CUBIC)
            working_img = cv2.resize(cropped_img, None, fx=magnification, fy=magnification, interpolation=cv2.INTER_LINEAR)
        #OR
        #height, width = cropped_img.shape[:2]
        #res = cv2.resize(cropped_img, (magnification*width, magnification*height), interpolation = cv2.INTER_CUBIC)

        if brightness != 1.0 or contrast != 1.0 or sharpness != 1.0:
            pil_image = Image.fromarray(working_img) # convert OpenCV image to PIL format

            if brightness != 1.0:
                enh = ImageEnhance.Brightness(pil_image)
                pil_image = enh.enhance(brightness)

            if contrast != 1.0:
                enh = ImageEnhance.Contrast(pil_image)
                pil_image = enh.enhance(contrast)

            if sharpness != 1.0:
                enh = ImageEnhance.Sharpness(pil_image)
                pil_image = enh.enhance(sharpness)

            working_img = np.array(pil_image) # convert PIL-format image back to OpenCV format

        if black_on_yellow:
            # note that [:,:,0] is blue, [:,:,1] is green, [:,:,2] is red
            working_img[:, :, 0] = 0

        if autocontrast:
            grayscale_img = cv2.cvtColor(working_img, cv2.COLOR_BGR2GRAY)
            working_img = cv2.equalizeHist(grayscale_img)
        # or... try Contrast-Limited Adaptive Histogram Equalization:
        #clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        #working_img = clahe.apply(grayscale_img)

        if autofocus:
            focusval = UVC_functions.get_focus()

        if show_params:
            if autocontrast:
                cv2.putText(working_img, "Autocontrast on", (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOUR_WHITE, 2)
                cv2.putText(working_img, "Autocontrast on", (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOUR_BLACK, 2)
            else:
                cv2.putText(working_img, "Brightness: " + str(brightness), (20, 30), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            COLOUR_YELLOW, 2)
                cv2.putText(working_img, "Contrast: " + str(contrast), (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            COLOUR_YELLOW, 2)
                cv2.putText(working_img, "Sharpness: " + str(sharpness), (20, 110), cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                            COLOUR_YELLOW, 2)
            cv2.putText(working_img, "Focus: " + str(focusval), (20, 150), cv2.FONT_HERSHEY_SIMPLEX, 1.0, COLOUR_YELLOW, 2)

        cv2.imshow("Video Magnifier", working_img)

        if not freeze:
            key_wait_time = 100  # image live-update mode - wait 100ms
        else:
            key_wait_time = 0  # i.e. if frame is frozen, wait indefinitely for a key to be pressed
        key = cv2.waitKey(key_wait_time) % 256  # LSB equates to ASCII code for most keys
        print(key)
        if key == 27:  # Esc - quit the program
            break
        elif key == ord('1'):  # 1 - normal colours
            inverted = False
        elif key == ord('2'):  # 2 - colours inverted
            inverted = True
        elif key == ord('3'):  # 3 - auto-contrast off
            autocontrast = False
        elif key == ord('4'):  # 4 - auto-contrast on
            autocontrast = True
        elif key == ord('5'):  # 5 - black-on-yellow mode off
            black_on_yellow = False
        elif key == ord('6'):  # 6 - black-on-yellow mode on
            black_on_yellow = True
        elif key == 176:  # num-pad 0 - decrease sharpness
            sharpness -= 0.1
            if sharpness < 0.0:
                sharpness = 0.0
        elif key == 174:  # num-pad . - increase sharpness
            sharpness += 0.1
            if sharpness > 10.0:
                sharpness = 10.0
        elif key == 177:  # num-pad 1 - 100% zoom
            magnification = 1.0
        elif key == 178:  # num-pad 2 - 200% zoom
            magnification = 2.0
        elif key == 179:  # num-pad 3 - 300% zoom
            magnification = 3.0
        elif key == 227:  # left-Ctrl - unfreeze frame
            freeze = False
        elif key == 82:  # up-arrow - increase brightness
            brightness += 0.1
            if brightness > 10.0:
                brightness = 10.0
        elif key == 84:  # down-arrow - decrease brightness
            brightness -= 0.1
            if brightness < 0.0:
                brightness = 0.0
        elif key == 81:  # left-arrow - decrease contrast
            contrast -= 0.1
            if contrast < 0.0:
                contrast = 0.0
        elif key == 83:  # right-arrow - increase contrast
            contrast += 0.1
            if contrast > 10.0:
                contrast = 10.0
        elif key == 80:  # Home key - reset to default colours
            brightness = 1.0
            contrast = 1.0
            sharpness = 1.0
            inverted = False
            autocontrast = False
            black_on_yellow = False
        elif key == 32:  # space-bar - freeze frame, or grab a new frozen frame
            if freeze:
                take_new_frame = True
            freeze = True
        elif key == 190:  # F1 - don't show parameter text overlay
            show_params = False
        elif key == 191:  # F2 - show parameters overlaid on image
            show_params = True
        elif key == 141:  # Num Enter - autofocus on
            UVC_functions.set_autofocus(True)
            autofocus = True
        elif key == 171:  # Num + - autofocus off, increase focus value
            if autofocus:
                UVC_functions.set_autofocus(False)
                autofocus = False
            focusval += 5
            UVC_functions.set_focus(focusval)
        elif key == 173:  # Num - - autofocus off, decrease focus value
            if autofocus:
                UVC_functions.set_autofocus(False)
                autofocus = False
            focusval -= 5
            UVC_functions.set_focus(focusval)
    # (end of main loop)

if __name__ == "__main__":
    main()
	
