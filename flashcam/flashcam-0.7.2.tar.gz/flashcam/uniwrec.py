#!/usr/bin/env python3

# import the necessary packages

#  ls zen_192.168.0.91_20211105_* | while read line; do echo file \'$line\'; done | ffmpeg -protocol_whitelist file,pipe -f concat -i - -c copy zen_192.168.0.91_20211105_.avi

from imutils.video import VideoStream
import socket
import time
import signal
from contextlib import contextmanager
import argparse

import cv2
import datetime
import time

import datetime as dt

import os


from fire import Fire
import imutils

import urllib.request
import numpy as np

# user pass
import  base64

import getpass

import sys

from flashcam.stream_enhancer import Stream_Enhancer
import webbrowser

@contextmanager
def timeout(time):
    # register a function to raise a TimeoutError on the signal
    signal.signal(signal.SIGALRM, raise_timeout)
    # schedule the signal to be sent after 'time'
    signal.alarm(time)
    #print("D... timeout registerred")

    try:
        tok = False
        #print("D... yielding timeout")
        yield
    finally:
        tok = True
        # unregister the signal so it wont be triggered if the timtout is not reached
        #print("D... timeout NOT!  unregisterred")
        signal.signal(signal.SIGALRM, signal.SIG_IGN)


def raise_timeout(signum, frame):
    raise TimeoutError




def adjust_gamma(image, gamma=1.0):
    # build a lookup table mapping the pixel values [0, 255] to
    # their adjusted gamma values
    invGamma = 1.0 / gamma
    table = np.array([((i / 255.0) ** invGamma) * 255
        for i in np.arange(0, 256)]).astype("uint8")
    # apply gamma correction using the lookup table
    return cv2.LUT(image, table)

def img_estim(img, thrshld=127):
    res = np.mean(img)
    return res
    is_light =  res > thrshld
    return 'light' if is_light else 'dark'
    # 40 -> 2.2

#------------------------------------------------------------------------ 3

def get_stream3( videodev, passfile ):
    # localuser
    u,p=getpass.getuser(),"a"
    try:
        with open( os.path.expanduser(passfile) ) as f:
            print("YES---> PASSWORD FILE  ", passfile )
            w1 = f.readlines()
            u= w1[0].strip()
            p= w1[1].strip()
    except:
        print("NO PASSWORD FILE  ", passfile)
        sys.exit(0)

    print("D... capturing from /{}/".format(videodev) )
    #cam = cv2.VideoCapture( videodev )
    #stream = urllib.request.urlopen( videodev )

    request = urllib.request.Request( videodev )
    print("D... USER/PASS", u,p)
    base64string =base64.b64encode( bytes(  '%s:%s' % (u, p ), 'ascii') )
    print("D... stream ok1", base64string)
    request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))

    #request.add_header("Authorization", "Basic %s" % base64string)
    print("D... stream ok2 - request.urlopen (disp)")
    ok = False
    stream = None
    try:
        stream = urllib.request.urlopen(request, timeout=5)
        ok = True
        print("D... stream ok3")
    except urllib.error.HTTPError as e:
        print("Server Offline1 ",e)
        #do stuff here
    except urllib.error.URLError as e:
        print("Server Offline2 ",e)
        #do stuff here
    except:
        ok = False
        stream = None
        print("X.... Stream from urllib Timeouted OR a bad password")
    return stream, u, p





def display3(videodev, save = False,
         passfile="~/.pycamfw_userpass"):
    stream = None
    stream_length = 1024*50
    if stream is None: # LOGIN
        stream, u, p = get_stream3(videodev, passfile)


    #print(stream)

    ret_val=0
    oi = 0
    oi_frame = 0
    io_none = 0
    bytex = b''
    while ret_val == 0:
        oi+= 1
        #with timeout(2):
        got_data = False
        frameok = False

        try:
            # THIS CAN TIMEOUT ######################################### i catch
            bytex += stream.read(stream_length) # i multiply by 10 as later...
            got_data = True
        except:
            print("X... exception - timout in 1.st stream.read, ")
            #bytex+=b"\x00\x00\x00"
            #bytex = b""

        a = bytex.find(b'\xff\xd8') #frame starting
        b = bytex.find(b'\xff\xd9') #frame ending

        #print(f" {len(bytex):7d} {got_data}   {a:8} {b:8}    {b+2-a}")

        if a != -1 and b != -1:
            io_none = 0
            jpg = bytex[a:b+2]
            bytex = bytex[a+2:]
            bytex = bytex[b+2:]
            frameok = False
            try:
                frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                #ret_val= 1
                io_none = 0
                frameok = True
            except:
                ret_val = 0

        else:
            ret_val = 0
            #print("D...                        frame set None http",oi,len(bytex), end="\r")
            #bytex+=b""
            #time.sleep(0.1)
            io_none+=1
            if io_none>30: #max size of jpg
                stream = None
                print("X... ---------------   frame not seen too long:", io_none, "... breaking")
                io_none = 0
                break

        if (oi_frame % 20) ==0:
            print("_"*70)
            print(f"       #     d_size  got      a      b       jpglen frame   f#" )
            print("_"*70)

        print(f"{oi:8d}  {len(bytex):7d} {got_data}   {a:8} {b:8}    {b+2-a}  {frameok}  {oi_frame}", end = "\n" if frameok else "\r" , flush=True)

        if frameok:
            oi_frame+= 1

            cv2.imshow( videodev, frame)
            key = cv2.waitKey(1)



# ================================================================================================

def display2(videodev, save = False,
             passfile="~/.pycamfw_userpass",
             rotate = 0):
    """
    """
    #sname,sfilenamea,sme,sfilenamea,sfilenamea,sfourcc,saviout

    sme = socket.gethostname()
    def setupsave():
        sname = "rec"
        sname = videodev
        sname = sname.replace("http","")
        sname = sname.replace("//","")
        sname = sname.replace(":","")
        sname = sname.replace("5000/video","")
        sname = sname.replace("8000/video","")

        sfilenamea = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        sme = socket.gethostname()
        sfilenamea = f"{sme}_{sname}_{sfilenamea}.avi"
        sfilenamea = os.path.expanduser("~/" + sfilenamea)
        sfourcc = cv2.VideoWriter_fourcc(*'XVID')
        saviout = cv2.VideoWriter( sfilenamea,sfourcc,25.0, (640,480))
        print( sfilenamea )
        print( sfilenamea )
        print( sfilenamea )
        print( sfilenamea )
        return sfilenamea,saviout

    def get_stream():
        # localuser
        stream = None # i return
        u,p=getpass.getuser(),"a"
        try:
            with open( os.path.expanduser(passfile) ) as f:
                print("YES---> PASSWORD FILE  ", passfile )
                w1 = f.readlines()
                u= w1[0].strip()
                p= w1[1].strip()
        except:
            print("NO PASSWORD FILE  ", passfile)


        print("D... capturing from web:/{}/".format(videodev) )
        #cam = cv2.VideoCapture( videodev )
        #stream = urllib.request.urlopen( videodev )

        request = urllib.request.Request( videodev )
        print("D... USER/PASS", u,p)
        base64string =base64.b64encode( bytes(  '%s:%s' % (u, p ), 'ascii') )
        print("D... stream ok1", base64string)
        request.add_header("Authorization", "Basic %s" % base64string.decode('utf-8'))

        #request.add_header("Authorization", "Basic %s" % base64string)
        print("D... stream ok2 - request.urlopen (disp)")
        ok = False
        try:
            stream = urllib.request.urlopen(request, timeout=5)
            ok = True
            print("D... stream ok3")
        except urllib.error.HTTPError as e:
            print("Server Offline1? ",e)
            #do stuff here
        except urllib.error.URLError as e:
            print("Server Offline2? ",e)
            #do stuff here
        except:
            ok = False
            stream = None
            print("X.... Timeouted on URLOPEN")


        return stream, u, p


    # ********************************************************** main loop
    io_none = 0 # to reset stream
    sfilename = ""  # move up to limi # of AVI files.... tst?
    sfilenamea = ""
    stream_length = 1024*50
    if save:
        sfilenamea,saviout = setupsave()
    while True: #==================== MAIN LOOP =================


        mjpg =False


        # #===================== OPENCV START CAPTURE==========================

        bytex = b'' # stream
        rpi_name = videodev

        if (str(videodev).find("http://")==0) or (str(videodev).find("https://")==0):
            # infinite loop for stream authentication
            stream = None
            while stream is None:
                print("D... waiting for stream")
                ### HERE PUT BWIMAGE
                #cv2.imshow(rpi_name, frame) # 1 window for each RPi
                if "frame" in locals():
                    print("D... frame in locals() ")
                    if (not frame is None):
                        print("D.... graying")
                        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                        (w, h, c) = frame.shape

                        for i in range(0,w,10):
                            x1, y1 = 0, i
                            x2, y2 = h, i
                            line_thickness = 1
                            cv2.line(gray, (x1, y1), (x2, y2), (111, 111, 111),
                                 thickness=line_thickness)
                        cv2.imshow(rpi_name, gray) # 1 window for each RPi
                        key = cv2.waitKey(1)

                time.sleep(1)
                stream, u, p  = get_stream()
        else:
            print("X... use http:// address")
            sys.exit(0)



        if (str(videodev).find("http://")==0) or (str(videodev).find("https://")==0):
            ret_val=0
            oi = 0
            while ret_val == 0:
                oi+=1

                #with timeout(2):
                print("D... IN 1st TIO..", end="")
                try:
                    # THIS CAN TIMEOUT #########################################
                    print("D... try ...", end="")
                    bytex += stream.read(stream_length) #  must be long enough?
                except:
                    print("X... exception - timout in 1.st stream.read, ")
                    #bytex+=b"\x00\x00\x00"
                    bytex = b""


                a = bytex.find(b'\xff\xd8') #frame starting
                b = bytex.find(b'\xff\xd9') #frame ending
                if a != -1 and b != -1:
                    io_none = 0
                    jpg = bytex[a:b+2]
                    bytex = bytex[b+2:]
                    # frame = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.CV_LOAD_IMAGE_COLOR)
                    if len(jpg)>1000:  # was crash here
                        frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                        ret_val= 1
                        io_none = 0
                        stream_length = b+2-a
                    else:
                        ret_val = 0
                        # print("D...                ok frame http",oi,len(bytex) )
                else:
                    ret_val = 0
                    print("D...                        frame set None http",oi,len(bytex), end="\r")
                    # it can count to milions here.... why? need to check stream ## OTHER CRASHES
                    #  i try two things now:
                    #bytex+=b""
                    time.sleep(0.2)
                    io_none+=1
                    if io_none>20:
                        stream = None
                        print("X... ---------------  too many unseen frames", io_none, "breaking")
                        io_none = 0
                        break

                    #frame = None
        if stream is None:
            continue
#----------------------------------------------------------------

        first = True

        timestamp_of_last_socket_refresh = time.time()


        i = 0
        fps = 0
        resetfps = True
        lastminu = 88
        motion_last = "999999"

        i7 = 0
        artdelay=0.05

        connection_ok = True

        # ---- bytes per second.  strange looks like 7MB/s
        BPS = 0
        BPSlast=0
        BPStag = dt.datetime.now()
        FPS = 0
        FPSlast = 0
        frames_total = 0

        senh = Stream_Enhancer()
        saved_jpg = False

        while connection_ok: #========================================================
            # read the frame from the camera and send it to the server
            #time.sleep(0.05)

            print("-", end="")
            #while True:
            if (str(videodev).find("http://")==0) or (str(videodev).find("https://")==0):
                artdelay = 0
                ret_val = 0
                try:
                    with timeout(4):
                        while ret_val == 0:
                            for i8 in range(1): # I decimate and remove delay
                                #print("1-", flush=True,end="")
                                bytex += stream.read(stream_length)
                                a = bytex.find(b'\xff\xd8') #frame starting
                                b = bytex.find(b'\xff\xd9') #frame ending
                                if a != -1 and b != -1:
                                    jpg = bytex[a:b+2]
                                    BPS+=len(jpg)/1024
                                    if len(jpg)>0:
                                        FPS+=1
                                    bytex = bytex[b+2:]
                                    frame = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)
                                    stream_length = b+2-a

                                    ret_val=1
                                    print("   {:4.1f}Mb/s {}fps {} {}".format(
                                        # len(bytex)/1024,
                                        BPSlast*8/1024,
                                        FPSlast,
                                        str(datetime.datetime.now())[:-5],
                                        sfilenamea.replace('/home/','')
                                    ) , end="\r")

                                else:
                                    ret_val = 0
                                    # frame = None
                                    # print("Non  sizE={:6.0f}kB ".format(len(bytex)/1024), end = "\r" )
                                    # print("Non", end = "\r" )
                except:
                    print("X... exception - connection lost, ")
                    ret_val = 0
                    #frame = None
                    print("RDE  siZe={:6.0f}kB ".format(len(bytex)/1024), end = "\n" )
                    connection_ok = False


                #print("-2", flush=True,end="")
                if (dt.datetime.now()-BPStag).total_seconds()>1:
                    BPStag = dt.datetime.now()
                    BPSlast=BPS
                    BPS=0
                    FPSlast = FPS
                    FPS=0


                #while


            if connection_ok:
                if (ret_val == 0) or (type(frame)=="NoneType"):
                    print("Not a good frame", type(frame), end="\r")
                    continue
                (w, h, c) = frame.shape
                frame_area = w*h
                motion_det = False
                print(".", end="")
                #print("RPINAME=",rpi_name)
                #print(frame)

                wname = videodev

                frames_total+= 1
                # cv2.namedWindow( wname, cv2.WINDOW_KEEPRATIO ,cv2.WINDOW_GUI_EXPANDED)
                cv2.namedWindow( wname , cv2.WINDOW_KEEPRATIO ) # 2 may allow resize on gigavg
                # cv2.namedWindow( wname , 2 ) # 2 may allow resize on gigavg
                if frames_total < 2:
                    #cv2.namedWindow(wname,cv2.WND_PROP_FULLSCREEN)
                    # ?https://stackoverflow.com/questions/62870031/pixel-coordinates-and-colours-not-showing
                    # TRICK !!!!!!!!!!!!
                    # https://stackoverflow.com/a/52776376
                    cv2.setWindowProperty(wname, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
                    bit_fs = 0
                    if sme in ['gigavg','vaio']:
                        bit_fs =1
                    cv2.setWindowProperty(wname, cv2.WND_PROP_FULLSCREEN,  bit_fs)
                    cv2.resizeWindow(wname, frame.shape[1], frame.shape[0] )

                if save:
                    # print("AVI")
                    saviout.write(frame)
                    if senh.add_frame(frame):
                        # print("avi..")
                        senh.setbox(f"AVI",  senh.avi)
                        frame = senh.get_frame(  )
                if saved_jpg:
                    if senh.add_frame(frame):
                        # print("avi..")
                        senh.setbox(f"JPG",  senh.jpg)
                        frame = senh.get_frame(  )

                if rotate == 180:
                    frame = cv2.rotate(frame, cv2.ROTATE_180)
                    #frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)

                cv2.imshow(rpi_name, frame ) # 1 window for each RPi
                #cv2.setWindowProperty(rpi_name, cv2.WND_PROP_TOPMOST, 1)
                # cv2.namedWindow(rpi_name, cv2.WINDOW_GUI_EXPANDED)
                # time.sleep(0.2)
                key = cv2.waitKey(1)

                if (not frame is None) and (rpi_name!="") and (key == ord('h')):
                    print("h PRESSED! - ")
                    print("""
 h ... show this help
 a ... SAVING AVI
 z ... stopping AVI
 w ... openning web browser
 s ... saving JPG
 q ... quit
""")

                if (not frame is None) and (rpi_name!="") and (key == ord('w')):
                    print("W PRESSED! - openning web browser")
                    webbrowser.open( videodev.replace("/video","" ) ) # BRUTAL


                if (not frame is None) and (rpi_name!="") and (key == ord('a')):
                    print("A PRESSED! - saving AVI")
                    save = True
                    sfilenamea,saviout = setupsave()
                    print(">>>", sfilenamea )

                if (not frame is None) and (rpi_name!="") and (key == ord('z')):
                    print("Z PRESSED! - STOPPING stopping saving AVI")
                    save = False
                    sfilenamea = ""

                if (not frame is None) and (rpi_name!="") and (key == ord('q')):
                    print("Q PRESSED!")
                    sys.exit(1)

                saved_jpg = False
                if (not frame is None) and (rpi_name!="") and (key == ord('s')):
                    print("S PRESSED!")
                    sname = "snapshot"
                    saved_jpg = True
                    sfilename = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                    # defined above # sme = socket.gethostname()
                    sfilename = f"{sme}{sname}_{sfilename}.jpg"
                    sfilename = os.path.expanduser( "~/"+sfilename )
                    # sfourcc = cv2.VideoWriter_fourcc(*'XVID')
                    # saviout = cv2.VideoWriter( sfilename , sfourcc , 25.0, (640,480))
                    isWritten = cv2.imwrite( sfilename, frame )
                    if isWritten:
                        print('Image is successfully saved as file.', sfilename)





if __name__=="__main__":
    Fire( display3)
    #Fire({ "disp":display2,   "disp2":display2    })
