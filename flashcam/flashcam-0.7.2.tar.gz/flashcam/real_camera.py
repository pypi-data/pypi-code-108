import cv2
from flashcam.base_camera2 import BaseCamera

from flashcam.usbcheck import recommend_video
# import base_camera  #  Switches: slowrate....

import datetime
import time
import socket

import glob

import subprocess as sp
import numpy as np

import flashcam.config as config

from  flashcam.stream_enhancer import Stream_Enhancer


from flashcam import v4lc
from flashcam.v4lc import set_gem

from flashcam.mmapwr import mmread_n_clear

import os
import sys

# -----------------------------------------------------------------

# -----------------------------------------------------------------

class Camera(BaseCamera):
    video_source = 0

    @staticmethod
    def init_cam(  ):
        """
        should return videocapture device
        but also sould set Camerare.video_source
        """

        # ----------------------------
        #    we need to get in into the thread.....
        #  NOT NOW - all is taken from BaseCam
        # def __init__(self, target_frame = "direct" , average = 0, blur = 0 , threshold = 0):


        # res = "640x480"
        res = config.CONFIG["res"]
        print("D... init_cam caleld with:", res )
        print("i... init_cam caleld with:", res )
        print("D... init_cam caleld with:",  config.CONFIG["product"] )
        print("i... init_cam caleld with:",  config.CONFIG["product"] )

        vids = recommend_video( config.CONFIG["product"]  )

        if len(vids)>0:
            vidnum = vids[0]
            cap = cv2.VideoCapture(vidnum,  cv2.CAP_V4L2)

            # config.CONFIG["camera_on"] = True

            # - with C270 - it showed corrupt jpeg
            # - it allowed to use try: except: and not stuck@!!!
            #cap = cv2.VideoCapture(vidnum)
            #   70% stucks even with timeout


            pixelformat = "MJPG"
            pixelformat = "YUYV"
            w,h =  int(res.split("x")[0]), int(res.split("x")[1])
            fourcc = cv2.VideoWriter_fourcc(*pixelformat)
            cap.set(cv2.CAP_PROP_FOURCC, fourcc)
            cap.set(cv2
                    .CAP_PROP_FRAME_WIDTH,   w )
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  h )
            return cap,vidnum
        return None, None


    @staticmethod
    def frames( ):
        """
        product= ... uses the recommend_video to restart the same cam
        """
        # i need these to be in globals() ----evaluate from web.py
        global substract_background,save_background
        global speedx, speedy, restart_translate, average
        global gamma_divide, gamma_multiply,gamma_setdef
        global gain_divide,gain_multiply,gain_setdef
        global expo_divide,expo_multiply,expo_setdef
        global timelaps, rotate180
        global fixed_image # show not camera but image
        global zoom

        # print("i... staticmethod frames @ real -  enterred; target_frame==", target_frame)
        senh = Stream_Enhancer()

        # === I must have these GLOBAL and PREDEFINED HERE <= web.py
        # --------------------------------  control
        # -----------get parameters for DetMot, same for web as for all
        #print(config.CONFIG)
        #print( "AVERAGE I AM HAVING ",config.CONFIG['average'] )
        framekind = config.CONFIG['framekind']
        average      = int(config.CONFIG['average'])
        threshold    = int(config.CONFIG['threshold'])
        blur         = int(config.CONFIG['blur'])
        timelaps     = int(config.CONFIG['laps'])
        histogram    = config.CONFIG['histogram']
        res          = config.CONFIG['res']
        speedx       = float(config.CONFIG['x'])
        speedy       = float(config.CONFIG['y'])
        rotate180    = int(config.CONFIG['otate'])
        zoom         = int(config.CONFIG['zoom'])

        # ------------------    to evaluate commands from web.py
        substract_background = False
        save_background = False
        restart_translate = False

        gamma_divide = False
        gamma_multiply =False
        gamma_setdef =False

        gain_divide = False
        gain_multiply =False
        gain_setdef =False

        expo_divide = False
        expo_multiply =False
        expo_setdef =False

        # rotate180 = False # i define earlier from CONFIG

        fixed_image = None # just camera.

        camera = Camera(  )
        vidnum = None
        while vidnum is None:
            cap, vidnum = camera.init_cam(  )
            if vidnum is None:
                print("!... no video recommended, locked in a loop (realcam/frames)")
                fullpath_fixed_image = "~/.config/flashcam/monoskop.jpg"
                fullpath_fixed_image = os.path.expanduser( fullpath_fixed_image )
                if os.path.exists(fullpath_fixed_image):
                    frame = cv2.imread( fullpath_fixed_image)
                    print(f"i...  {fullpath_fixed_image}")
                    senh.add_frame(frame)
                    senh.setbox(" ", senh.TIME)
                    frame = senh.get_frame(  )
                    # this is not giving anything
                    yield frame
                else:
                    print(f"!... monoskop.jpg not found {fullpath_fixed_image}")
                time.sleep(1)

        cc = v4lc.V4L2_CTL("/dev/video"+str(vidnum))
        capa = cc.get_capbilities()


        # I CALL SET_GAM from
        set_gem(cc, config.CONFIG['gain'],
                config.CONFIG['expo'],
                config.CONFIG['mmaga'])


        # very stupid camera    ZC0303 Webcam
        if "exposure" in capa:
            exposure = cc.get_exposure()
            exposuredef = cc.getdef_exposure()
            print(f"i... EXPOAUTO == {exposure} vs def={exposuredef}; ")


        if "exposure_auto" in capa:
            expo_auto = cc.get_exposure_auto()
            expo_autodef = cc.getdef_exposure_auto()
            print(f"i... EXPOAUTO == {expo_auto} vs def={expo_autodef}; ")

        if "exposure_absolute" in capa:
            exposure_absolute = cc.get_exposure_absolute()

        if "gain" in capa:
            gain = cc.get_gain()
            gaindef = cc.getdef_gain()
        if "gamma" in capa:
            gamma = cc.get_gamma()
            gammadef = cc.getdef_gamma()


        nfrm = 0
        if config.CONFIG["product"]:
            wname = "none "
        else:
            wname = config.CONFIG["product"]


        frame_prev = None
        while True:


            timeoutok = False
            ret = False
            frame = None
            if type(cap) == tuple:
                print("TUPLE cap:",cap)
                cap = cap[0] # THIS IS STRANGE FOR newcam20211117
                print("new:", cap , type(cap) )

            if (cap is None) or (not cap.isOpened()):
                print("X... camera is None ")
                ret = False
            elif not cap.isOpened():
                print("X... camera  not Opened(real)")
                ret = False
            else:
                try: #----this catches errors of libjpeg with cv2.CAP_V4L2
                    print(f"i... frame {nfrm:8d}   ", end="\r" )
                    ret, frame = cap.read()
                    BaseCamera.nframes+=1

                    #wname = f"res {frame.shape[1]}x{frame.shape[0]}"
                    nfrm+=1
                    #print(f"D... got frame (frames iter)   ret={ret}  {frame.shape}")
                except Exception as ex:
                    print("D... SOME OTHER EXCEPTION ON RECV...", ex)
                    config.CONFIG["camera_on"] = False


            if not ret:
                time.sleep(0.5)
                config.CONFIG["camera_on"] = False

                cap = Camera.init_cam( )
                nfrm = 0

                # create gray + moving lines BUT prev_frame is bad sometimes
                try:
                    print("D... trying to gray frame")
                    frame = cv2.cvtColor(frame_prev, cv2.COLOR_BGR2GRAY)
                    height, width = frame.shape[0] , frame.shape[1]

                    skip = 10
                    startl = 2*(nfrm % skip) # moving lines
                    for il in range(startl,height,skip):
                        x1, y1 = 0, il
                        x2, y2 = width, il
                        #image = np.ones((height, width)) * 255
                        line_thickness = 1
                        cv2.line(frame, (x1, y1), (x2, y2), (111, 111, 111),
                                 thickness=line_thickness)
                except:
                    print("X... prev_frame was bad, no gray image")

            #print("D... ret==", ret)
            if ret: #********************************************************* operations
                # fixed_image = "beamon.jpg"
                if not(fixed_image is None):
                    fullpath_fixed_image = "~/.config/flashcam/"+fixed_image
                    fullpath_fixed_image = os.path.expanduser( fullpath_fixed_image )
                    if os.path.exists(fullpath_fixed_image):
                        frame = cv2.imread( fullpath_fixed_image)

                frame_prev = frame
                if senh.add_frame(frame):  # it is a proper image....


                    #------------------------------ BRUTAL ------------test exposure V4L
                    if (BaseCamera.nframes % 10==0):
                        cc = v4lc.V4L2_CTL("/dev/video"+str(vidnum))
                        capa = cc.get_capbilities()
                        #cc.refresh()
                        exposure_absolute = 100
                        expo_auto = 3
                        expo_autodef = 3


                        # stupid camera ZC0303 Webcam - parallel to exposure_auto
                        if "exposure" in capa:
                            exposure = cc.get_exposure()

                        if "exposure_auto" in capa: # notauto? alway show _absolute
                            expo_auto = cc.get_exposure_auto()
                            expo_autodef = cc.getdef_exposure_auto()
                            print(f"i... EXPOAUTO == {expo_auto} vs def={expo_autodef}; ")

                        if "exposure_absolute" in capa:
                            exposure_absolute = cc.get_exposure_absolute()


                        if "gain" in capa:
                            gain = cc.get_gain()
                            gaindef = cc.getdef_gain()
                        if "gamma" in capa:
                            gamma = cc.get_gamma()
                            gammadef = cc.getdef_gamma()
                    #--------------------------------------------------------------------------

                    #=========== BEFORE OTHER === Create final image ====
                    #=========== like ZOOM
                    #=========== THEN CALCULATE HISTO =====
                    #=========== THEN do other stuff
                    # senh has a frame now
                    if rotate180!=0:   # rotate earlier than zoom
                        senh.rotate180( rotate180 ) #arbitrary int angle

                    if zoom!=1:
                    #if int(config.CONFIG['zoom'])!=1:
                        try:
                            crocfg = os.path.expanduser("~/.config/flashcam/cross.txt")
                            cross_dx, cross_dy  = None, None
                            if os.path.exists(crocfg):
                                with open(crocfg) as f:
                                    cross_dx, cross_dy  = [int(x) for x in next(f).split()]
                                    senh.zoom( zoom ,cross_dx, cross_dy )
                        except Exception as e:
                            print("!... Problem ar cross.txt file:",e)

                    # ----------  I need to calculate histogram before labels...
                    if histogram: # just calculate a number on plain frame
                        hmean = senh.histo_mean( )

                    # ---------- before anything - we decode the web command EXECUTE EXECUTION

                    expression,value = mmread_n_clear( )
                    #print(f"i... expression == {expression}  value == {value}")
                    # --- fixed_image
                    try:
                        globals()[expression] = eval(value)
                    except:
                        print("X... EXEC FAIL",expression,value)

                    # print("i... fixed:", fixed_image)
                    # print(".... substract_background", substract_background, not(substract_background) )
                    # globals()["substract_background"] = value



                    if save_background:
                        print("D... HERE I SAVE save_background of mask")
                        print("D... HERE I SAVE save_background of mask")
                        print("D... HERE I SAVE save_background of mask")
                        senh.save_background()
                        save_background = False  # ONE SHOT

                    if substract_background:
                        # print("D... HERE I MUST DO subtraction of mask")
                        # print("D... HERE I MUST DO subtraction of mask")
                        print("D... HERE I MUST DO subtraction of mask",speedx, speedy)
                        senh.subtract()

                    # - compensate for speed of the sky
                    if (speedx!=0) or (speedy!=0):
                        senh.translate( speedx, speedy)

                    if restart_translate:
                        senh.reset_camera_start()
                        restart_translate = False

                    # average  THIS IS HERE to be changed TOO (ACCUM)
                    # print("i.... average", average)

                    # timelaps  THIS IS HERE to be changed TOO
                    # print("i.... timelaps", timelaps)

                    #print("i... GAMMAS ", gamma, gammadef )

                    if gamma_divide:
                        gamma_divide = False
                        if "gamma" in capa:
                            cc.set_gamma( int(gamma/2) )
                    if gamma_multiply:
                        gamma_multiply = False
                        if "gamma" in capa:
                            if gamma!=0:
                                cc.set_gamma( int(gamma*2) )
                            else:
                                cc.set_gamma( int(1) )
                    if gamma_setdef:
                        gamma_setdef = False
                        if "gamma" in capa:
                            cc.setdef_gamma( )


                    if gain_divide:
                        gain_divide = False
                        if "gain" in capa:
                            cc.set_gain( int(gain/2) )
                    if gain_multiply:
                        gain_multiply = False
                        if "gain" in capa:
                            if gain!=0:
                                cc.set_gain( int(gain*2) )
                            else:
                                cc.set_gain( int(1) )
                    if gain_setdef:
                        gain_setdef = False
                        if "gain" in capa:
                            cc.setdef_gain( )


                    if expo_divide:
                        expo_divide = False
                        if "exposure_absolute" in capa:
                            cc.set_exposure_auto(1)
                            exposure_absolute = cc.get_exposure_absolute()
                            cc.set_exposure_absolute( int(exposure_absolute/2) )
                    if expo_multiply:
                        expo_multiply = False
                        if "exposure_absolute" in capa:
                            cc.set_exposure_auto(1)
                            exposure_absolute = cc.get_exposure_absolute()
                            if exposure_absolute!=0:
                                cc.set_exposure_absolute( int(exposure_absolute*2) )
                            else:
                                cc.set_exposure_absolute( int(1) )
                    if expo_setdef:
                        expo_setdef = False
                        if "exposure_auto" in capa:
                            cc.setdef_exposure_auto()
                            cc.setdef_exposure_absolute( )


                    #--------------- now apply labels ------i cannot get rid in DETM---
                    #--------- all this will be on all rames histo,detect,direct,delta
                    senh.setbox(" ", senh.TIME)
                    if framekind in ["detect","delta","histo"]:
                        senh.setbox(f"DISP {framekind}",senh.DISP)
                    if average>0:
                        senh.setbox(f"acc {average}",  senh.avg)
                    if blur>0:
                        senh.setbox(f"blr  {blur}",  senh.blr)
                    if threshold>0:
                        senh.setbox(f"trh  {threshold}",  senh.trh)
                    if timelaps>0:
                        senh.setbox(f"laps {timelaps}",  senh.lap)
                    if histogram:
                        senh.setbox(f"his {hmean:3.0f}",  senh.hist)
                    if speedx!=0:
                        #print(speedx)
                        senh.setbox(f"x {speedx:.3f}",  senh.speedx)
                    if speedy!=0:
                        senh.setbox(f"y {speedy:.3f}",  senh.speedy)
                    if zoom!=1:
                        senh.setbox(f"z {zoom:1d}x", senh.scale)
                    if substract_background:
                        senh.setbox("-BCKG",  senh.SUBBG )
                    if rotate180!=0:
                        senh.setbox("ROT",  senh.rot )


                    # ----------------expo gain gamma
                    # very stupid camera    ZC0303 Webcam
                    if "exposure" in capa:
                        if exposure!=exposuredef: # manual
                            senh.setbox(f"expo {exposure}",  senh.expo)

                    if "exposure_auto" in capa:
                        if expo_auto!=expo_autodef: # manual
                            senh.setbox(f"expo {exposure_absolute}",  senh.expo)

                    if ("gain" in capa) and (gain!=gaindef): # gain is not frequently tunable
                        senh.setbox(f"g {gain}",  senh.gain)

                    if ("gamma" in capa):
                        if (gamma!=gammadef): # manual
                            senh.setbox(f"m {gamma}",  senh.gamma)


                    # ----  for detmo ---- work with detect motion--------------------
                    if (threshold>0) :
                        senh.setbox("MODE DM", senh.MODE) #---push UP to avoid DetMot
                        senh.detmo( average, blur)
                        senh.chk_threshold( threshold )
                        if senh.motion_detected:
                            # print("D... sav mot", senh.motion_detected)
                            senh.save_avi( seconds = -1, name = "dm" )
                    else:
                        senh.setaccum( average  )
                        senh.setblur( blur )
                        #senh.setbox("MODE  ", senh.MODE)

                    # ---draw histogram
                    if framekind == "histo":
                        senh.histo( )

                    if timelaps>0:
                        senh.save_avi( seconds = timelaps )



                    #------------yield the resulting frame-----------------------------
                    if framekind in ["detect","delta","histo"]:
                        frame = senh.get_frame(  typ = framekind)
                    else:
                        frame = senh.get_frame(  )

            yield frame



    @staticmethod
    def set_video_source(source):
        """
        never user whatsoever !
        """
        print("D... set_video_source: source=", source)
        camera = cv2.VideoCapture( source,  cv2.CAP_V4L2)
        print("D... ",camera)
        print("D... setting MJPG writer....FMP4 works too")
        # camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        camera.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('F','M','P','4'))
        print("D... first camera read ....")
        ok = False
        try:
            _, img = camera.read()
            print(img.size) # this can fail and reset to DEV 0
            ok = True
        except Exception as ex:
            print("X... CAMERA read ... FAILED",ex)

        if ok:
            return camera
        return None
