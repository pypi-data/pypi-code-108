#!/usr/bin/env python3
'''
usb see connected things
'''
from flashcam.version import __version__
from fire import Fire
from flashcam import config
#from serial_asyncio import open_serial_connection
import serial # list devices .... nice tool
import serial.tools.list_ports

import glob
import subprocess as sp

import sys


import pandas as pd
import cv2
import time

from contextlib import contextmanager
import signal

from flashcam.v4lc import V4L2_CTL, get_resolutions


# print("v... unit 'unitname' loaded, version:",__version__)

@contextmanager
def timeout(time):
    print("D... registering")
    # register a function to raise a TimeoutError on the signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # schedule the signal to be sent after 'time'
    signal.alarm(time)
    print("D... timeout registerred")

    try:
        tok = False
        print("D... yielding timeout")
        yield
    finally:
        tok = True
        # unregister the signal so it wont be triggered if the timtout is not reached
        print("D... timeout NOT!  unregisterred")
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError




def func(debug = False):

    print("D... in unit unitname function func DEBUG may be filtered")
    print("i... in unit unitname function func - info")
    print("X... in unit unitname function func - ALERT")
    return True

def test_config_save():
    config.CONFIG['filename'] = "~/.config/flashcam/cfg.json"
    config.show_config()
    print( config.get_config_file() )
    return config.save_config()

# def test_config_read():
#     config.CONFIG['filename'] = "~/.config/flashcam/cfg.json"
#     config.load_config()
#     config.show_config()
#     print( config.get_config_file() )
#     assert config.save_config() == True

def test_func():
    print("i... TESTING function func")
    assert func() == True


def usbroot():
    CMD = "lsusb"
    ok=False
    try:
        res=sp.check_output( CMD, shell=True ).decode("utf8")
        ok=True
    except:
        print("X... ... ERROR "+CMD)
    res = res.split("\n")
    hubs = {}
    for i in res:
        #print(i)
        if i.find("root hub")>0:
            #print(i.split()[1])
            hubs[i.split()[1]] = i.split()[-3]
    return hubs

def lsusbv(vm):
    """ verbose lsusb"""
    CMD = "lsusb -v 2>/dev/null"
    ok=False
    try:
        res=sp.check_output( CMD, shell=True ).decode("utf8")
        ok=True
    except:
        print("X... ... ERROR "+CMD)
    res = res.split("\nBus ")
    for i in res:
        if i.find(vm)>0:
            busline = i.split("\n")[0]
            #print("bl",busline)
            bus = busline.split()[0]
            dev = busline.split()[2].split(":")[0]
            fro = i.find("idProduct")
            #print(i)
            #print(i[fro])
            cut = i[fro:]
            #print(cut)
            tro = cut.find("\n")
            #print(fro,tro)
            cut = cut[ :tro]
            name = " ".join( cut.split("\n")[0].split()[2:] ).strip()
            #for j in i.split("\n"):
                #print(bus,dev)
            #    break
    return bus,dev,name


def init_cam(vidnum, res):
    print("D... ini cam", vidnum, res)
    cap = cv2.VideoCapture(vidnum,  cv2.CAP_V4L2)
    # - with C270 - it showed corrupt jpeg
    # - it allowed to use try: except: and not stuck@!!!
    #cap = cv2.VideoCapture(vidnum)
    #   70% stucks even with timeout
    pixelformat = "MJPG"
    w,h =  int(res.split("x")[0]), int(res.split("x")[1])
    fourcc = cv2.VideoWriter_fourcc(*pixelformat)
    cap.set(cv2.CAP_PROP_FOURCC, fourcc)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,   w )
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  h )
    return cap

def show_cam(vidnum, res, recommended=""):
    """
    vidnum = number; res 640x480;
    recommended= ... uses the recommend_video to restart the same cam
    """
    cap = init_cam( vidnum, res)
    nfrm = 0
    if recommended=="":
        wname = "none "+res
    else:
        wname = recommended + " "+ res
    frame_prev = None
    while True:

        timeoutok = False
        ret = True
        frame = None
        if (cap is None) or (not cap.isOpened()):
            print("X... camera None or not Opened")
            ret = False
        else:
            try: #----this catches errors of libjpeg with cv2.CAP_V4L2
    #            with timeout(3): #--- this may help when no CAP_V4L2; MAYNOT
                print("D... reading frame" )
                ret, frame = cap.read()
                #wname = f"res {frame.shape[1]}x{frame.shape[0]}"
                nfrm+=1
                print("D... got frame",nfrm, "ret=", ret)
    #        except TimeoutError:
    #            timeoutok = True
    #            nfrm = 0
            except Exception as ex:
                print("D... SOME OTHER EXCEPTION ON RECV...", ex)

#        if  timeoutok:
#            print("X... timout")

        if not ret:
            time.sleep(0.5)
            print("D... trying to recommend")
            vids = recommend_video(recommended) # try to re-init the same video
            if len(vids)>0:
                vidnum = vids[0]
                cap = init_cam( vidnum, res)
                nfrm = 0

            if  (not frame_prev is None):

                # create gray + moving lines
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
                cv2.namedWindow( wname, cv2.WINDOW_KEEPRATIO)
                cv2.imshow( wname , frame );
                k = cv2.waitKey(1)
                if k == ord("q"):
                    #camera.kill = True
                    break


        if ret and (not frame is None):
            frame_prev = frame
            cv2.namedWindow( wname, cv2.WINDOW_KEEPRATIO)
            cv2.resizeWindow(wname, frame.shape[1], frame.shape[0] )
            cv2.imshow( wname , frame );
            k = cv2.waitKey(1)
            if k == ord("q"):
                break

# def verify_resolutions(vidnum, reslist):

#     cap = cv2.VideoCapture(vidnum)
#     resolutions = {}

#     for r in sorted(reslist):
#         w,h =  int(r.split("x")[0]), int(r.split("x")[1])
#         w,h = 160,120
#         print(f"D... {w} x {h}")
#         pixelformat = "NV12"
#         fourcc = cv2.VideoWriter_fourcc(*pixelformat)
#         cap.set(cv2.CAP_PROP_FOURCC, fourcc)
#         cap.set(cv2.CAP_PROP_FRAME_WIDTH,   w )
#         cap.set(cv2.CAP_PROP_FRAME_HEIGHT,  h )

#         for i in range(20):
#             #ret, frame = cap.read()
#             #time.sleep(0.5)
#             ret, frame = cap.read()
#             #if not frame is None:
#             if ret:
#                 cv2.imshow( f"name{w}x{h}", frame );
#                 cv2.waitKey(1)
#             else:
#                 time.sleep(0.05)
#         width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#         height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
#         print(f"D... {w} x {h} -> {width} x {height}")

#         if width!=0:
#             resolutions[str(width)+"x"+str(height)] = "OK"

#     print(resolutions)



def recommend_video( prefname=None ):
    """
    glob through /dev/video*
    recommend video device:  without paramenter - the list is returned, else if string matches

    0     001 006 2.0 	0458:708c 	 Genius WideCam F100 	 14.0-usb-0:9:1.0 	 12e
    ./usbcheck.py "Genius W"
    """
    usb_hubs = usbroot()

    devices=serial.tools.list_ports.comports()
    print("____________________serial  devices _______"+"_"*37)
    for i in devices:
        print(i)
    #print("D... this was serial devices")

    recommvid=[]
    vids=glob.glob("/dev/video*")
    print("____________________video   devices _______"+"_"*37)
    print(f"video bus dev UsbTyp vendor:model   product            IDpath            capabi")
    recomvid = []
    for vid in sorted(vids):
        CMD = f"udevadm info --name={vid}"
        # print(f"D... cmd={CMD}")
        res = ""
        ok=False
        try:
            res=sp.check_output( CMD, shell=True ).decode("utf8")
            ok=True
        except:
            print("X... ... ERROR "+CMD)

        if ok:
            #print(res)
            try: # I saw there was no result...when reconnecting camera....
                vendor = [x for x in res.split() if x.find("ID_VENDOR_ID=")>=0][0]
                vendor = vendor.split("=")[1]
                model = [x for x in res.split() if x.find("ID_MODEL_ID=")>=0][0]
                model =  model.split("=")[1]
                vname = [x for x in res.split() if x.find("ID_SERIAL=")>=0][0]
                vname = vname.split("=")[1]
                id_path = [x for x in res.split() if x.find("ID_PATH=")>=0][0]
                id_path = id_path.split("=")[1]
                id_path = ":".join( id_path.split(":")[2:] )
                ok = True
            except  Exception as ex:
                print("X... udevadm error...", ex, vid)
                ok = False

            if ok:
                print(f"D...  getting capabilities", )
                cc = V4L2_CTL( vid )
                capa = cc.get_capbilities()
                GE = ""
                if "gain" in capa:
                    GE = "g"
                if "exposure_absolute" in capa:
                    GE+= "e"
                # print(   )

                if len(capa) > 0:
                    bus,dev,name = lsusbv(f"{vendor}:{model}")
                    #print(usb_hubs)
                    vidid = int(vid[vid.find('/dev/video')+10:])
                    pref = " "
                    if prefname is None:
                        recomvid.append( vidid )
                    else:
                        if (name.find(str(prefname))>=0) or (id_path.find(str(prefname))>=0):
                            recomvid.append( vidid)
                            pref = "*"
                        #if self.verbose:print("     ",vendor, model, vname)
                    print(f"{vidid:2d}   {bus:4s} {dev:4s} {usb_hubs[bus]:6s} {vendor:4s}:{model:4s}  {name:20s}  {id_path:16s}  {len(capa)}{GE}   {pref}" )
                    # verify_resolutions( vidid, resolutions )
            # print(prefname, recomvid)
    print("|"*80)
    if not prefname is None:
        if len(recomvid)==0:
            print("X... config WANTS the camera",prefname)
            print("X... NOT FOUND")
    # print("D... recommending:",recomvid)
    # print("i... recommending:",recomvid)
    # print("i... recommending:",recomvid)
    # print("i... recommending:",recomvid)
    print("i... recommending video#:",recomvid[0], " ... full list:", recomvid)

    #resolutions = get_resolutions( recomvid[0] )
    # show_cam( recomvid[0], resolutions[-1] )

    return recomvid





if __name__ == "__main__":
    print("i... in the __main__ of unitname of flashcam")
    Fire(recommend_video)
