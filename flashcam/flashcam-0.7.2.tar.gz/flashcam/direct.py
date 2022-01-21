#!/usr/bin/env python3


'''
This is screen interface
'''

from flashcam.version import __version__
from fire import Fire
from flashcam import config
from flashcam.real_camera import Camera

import time

import datetime as dt
import numpy as np

import cv2

import sys

# here is the config and camera TOO
import flashcam.web
# runs camera = Camera()
#from flashcam.web import camera_ins

import socket
import os
import webbrowser

def show_cam():

    camera = Camera( ) # creating the OBJECT

    framecnt = 0
    framecnttrue = 0
    ss_time = 0
    wname = "placeholder"
    while True:
        time.sleep(0.1)
        framecnt+=1
        print("D... get_frame (gen)")
        frame = camera.get_frame()
        print("D... got_frame (gen)")
        start = dt.datetime.now()
        blackframe = np.zeros((480,640,3), np.uint8)

        #----- i dont send None now, but this helped to avoid crash
        if (frame is None):
            # frame=cv2.imencode('.jpg', frame)[1].tobytes()
        #else:
            continue
        stop = dt.datetime.now()
        ss_time = (stop-start).total_seconds()


        cv2.namedWindow( wname, cv2.WINDOW_KEEPRATIO)
        cv2.resizeWindow(wname, frame.shape[1], frame.shape[0] )

        cv2.imshow( wname , frame );
        key = cv2.waitKey(1)
        if key == ord("q"):
            print("X... kill set to True")
            camera.killme()
            return

        # ================================= taken from uniwrec==========
        # if (not frame is None) and (rpi_name!="") and (key == ord('a')):
        #     print("A PRESSED! - saving AVI")
        #     save = True
        #     sfilenamea,saviout = setupsave()
        #     print(">>>", sfilenamea )

        # if (not frame is None) and (rpi_name!="") and (key == ord('z')):
        #     print("Z PRESSED! - STOPPING stopping saving AVI")
        #     save = False
        #     sfilenamea = ""


        saved_jpg = False
        if (not frame is None) and (key == ord('s')):
            print("S PRESSED!")
            sname = "snapshot"
            saved_jpg = True
            sfilename = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
            # defined above # sme = socket.gethostname()
            sme = socket.gethostname()

            sfilename = f"{sme}{sname}_{sfilename}.jpg"
            sfilename = os.path.expanduser( "~/"+sfilename )
            # sfourcc = cv2.VideoWriter_fourcc(*'XVID')
            # saviout = cv2.VideoWriter( sfilename , sfourcc , 25.0, (640,480))
            isWritten = cv2.imwrite( sfilename, frame )
            if isWritten:
                print('Image is successfully saved as file.', sfilename)




def main():
    print("D... screen view")
    show_cam()

if __name__ == '__main__':
    print("i... APP RUN FROM direct.py")

    Fire(main)
