#!/usr/bin/env python3
from imutils.video import VideoStream
import cv2
import time
import datetime as dt
import socket
from random import randint

import numpy as np

import imutils
import datetime as dt


from flashcam.version import __version__
import os

class Stream_Enhancer:
    """
    definitions of positions on the frame
    ROW COLUMN  - colors defined elsewhere
   4 columns MAX
    """
    # --------------- TOP  0,x
    TIME  = (0,0) #
    DISP  = (0,4) # gree
    MODE  = (0,3) # red
    SUBBG = (0,5) # substract background

    # ------------- LOW LINE
    expo  = (2,0)
    gain  = (2,1)
    gamma = (2,2)
    speedx= (2,3)
    speedy= (2,4)
    #--------------- NEVER when speedxy
    dm=  (2,4) #  it is veeery long, overlaps




    #--------------------- 2 is bottom
    lap = (1,0) # side
    # avoid 2,0
    avg = (3,0) # accum    2,0 is for LOWLINE
    blr = (4,0) # LOW DEEP
    trh = (5,0) # side
    hist= (6,0) # side
    rot = (7,0) # side  /otate in bin...
    # ------ more (with/for uni)
    avi = (8,0) #
    jpg = (9,0) #

    scale = (10,0) #? see

    delta_frame = None
    detect_frame = None
    frame_area = 1

    frame_number = 0

    motion_detected = False
    motion_detected_start = dt.datetime.now()
    expire = 2
    aviopened = False

    avi_last = dt.datetime.now() - dt.timedelta(seconds=90000)
    aviopened_laps = False

    # -- age of frame for speed
    camera_age = 0
    camera_start = dt.datetime.now()

    # -- subtraction of mask
    frame_bg = None
    sub_bg = False

    # background path
    BGFILE = os.path.expanduser('~/.config/flashcam/background.jpg')


    def RC_COLOR(self,row,col):
        if not self.frame_ok: return  # B  G R
        if (row,col) == self.TIME: return (200,0,0)
        if (row,col) == self.MODE: return (0,0,255)
        if (row,col) == self.DISP: return (0,205,0)
        if (row,col) == self.SUBBG: return (90,50,200)

        if (row,col) == self.lap: return (200,100,200) #
        if row==1 and col==1: return (150,150,150) #
        if row==1 and col==2: return (50,50,50) #
        if row==1 and col==3: return (120,120,120) # brown
        if row==1 and col==4: return (180,180,180) # orange

        if (row,col) == self.avg:  return (250,0,0) #
        if (row,col) == self.blr:  return (150,150,0) #
        if (row,col) == self.trh:  return (150,0,150) #
        if (row,col) == self.hist: return (0,120,150) # brown
        if (row,col) == self.dm:   return (50,100,250) # orange
        if (row,col) == self.rot:  return (150,120,150) #


        # left side
        if (row,col) == self.expo:  return (0,0,0) #
        if (row,col) == self.gain:  return (50,50,50) #
        if (row,col) == self.gamma: return (80,80,80) #

        if (row,col) == self.speedx: return (180,80,80) #
        if (row,col) == self.speedy: return (80,180,80) #
        if (row,col) == self.avi:    return (30,30,210) # FOR UNI only
        if (row,col) == self.jpg:    return (0,0,250)   # FOR UNI only
        if (row,col) == self.scale:  return (250,0,250)   # zoom scale

        t=[255,255,255]
        while (t[0]+t[1]+t[2]>400) or  (t[0]+t[1]+t[2]<200) :
            t =  (randint(5,255),randint(5,255),randint(5,255) )
        #print(t[0]+t[1]+t[2])
        return t


#---------------------------------- INIT ----------

    def __init__(self, resolution=(640,480) ):
#    def __init__(self, resolution=(320,240) ):
        print("D... s-e init")
        self.resolution = resolution
        self.posx_offs=5
        self.posy_offs=5
        self.frame_ok = False

        self.first_frame = True
        self.accubuffer = [] # accumulation for motion


#----------------------------------------- RETURN THE FRAME ----BACK
    def get_frame(self,  typ=""):
        if typ=="delta":
            if not(self.delta_frame is None):
                return self.delta_frame

        if typ=="detect":
            if not(self.detect_frame is None):
                return self.detect_frame

        if typ=="histo":
            #if "histo_frame" in locals():
            if not(self.histo_frame is None):
                return self.histo_frame

        return self.frame


#---------------------------  INSERT FRAME TO THIS OBJECT ----
    def add_frame(self, image):
        # print("D... adding fframe")
        try:
            h,w = image.shape[0],image.shape[1]
            self.frame_ok = True
        except Exception as e:
            print("D... in add frame bad frame")
            self.frame_ok = False
            return False
        self.frame = image
        self.maxcol=5 # NORMALLY 4
        # self.maxcol=7 # with x y
        self.maxrow=14
        # #if fontScale == 0.5
        #if w==320:
        #    self.maxcol=2
        #    self.maxrow=5
        # #if fontScale is W/640 *0.5
        if w==320:
        #    self.maxcol=2
            self.maxrow=13

        if self.first_frame:
            self.averageValue1 = np.float32(self.frame)
            self.first_frame = False


        return True


#---------------------------  INSERT FRAME from CAMERA TO THIS OBJECT ----
    def add_frame_from_cam(self):
        """

        """
        self.imstream = VideoStream(0).start()
        self.imstream.stream.set(3, self.resolution[0])
        self.imstream.stream.set(4, self.resolution[1])
        image = self.imstream.read()
        self.imstream.stop()
        return self.add_frame(image)

#--------------------------- imshow ---------------------
    def show_frame(self):
        if not self.frame_ok: return
        cv2.imshow("A", self.frame)
        wkey="a"
        while wkey!=ord("q"):
            wkey = cv2.waitKey(10)
        cv2.destroyAllWindows()

#--------------------------- imshow ---------------------
    def blimp_frame(self):
        if not self.frame_ok: return
        cv2.imshow("A", self.frame)
        cv2.waitKey(100)

    def get_font_params(self, txt):
        if not self.frame_ok: return
        self.font       = cv2.FONT_HERSHEY_SIMPLEX
        self.font       = cv2.FONT_HERSHEY_SIMPLEX
        self.font       = cv2.FONT_HERSHEY_DUPLEX
        self.fontScale  = 0.5 * (self.frame.shape[1]/640)
        self.lineType   = 1
        self.text_width, self.text_height = cv2.getTextSize(txt,
                                                  self.font,
                                                  self.fontScale,
                                                  self.lineType)[0]



#------------------------------------------------------PUT TEXT --------------
    def textbox(self,txt, pos=[5,5], bgcolor=(0,0,0), fgcolor=(255,255,255) , target = None):
        if not self.frame_ok: return


        if target is None:
            framekind = self.frame
        else:
            framekind = target


        self.get_font_params(txt)
        #pos[1]+=self.text_height #

        # letwidth = 25*4*fontScale
        #        txt=txt+" w"+str(self.text_width)+" h"+str(self.text_height)+" @ "+str(pos[0])+","+str(pos[1])
        # top left 0 0
        beginCorner=( pos[0]-1                , pos[1]- self.text_height-1 )
        endCorner  =( pos[0]+self.text_width+1, pos[1]+3   )

        cv2.rectangle(framekind,
                      beginCorner, endCorner,
                      bgcolor, cv2.FILLED)
        cv2.putText(framekind, txt,
                    tuple(pos),
                    self.font,
                    self.fontScale,
                    fgcolor,
                    self.lineType)

#    def timemark(self):
#        # reserve 320
#        self.get_font_params(txt)
#        self.textbox(,  [self,5] )

#----------------------------------------------- DEFINE GRID HERE-------
    def setbox(self, txt, rowcol, side="" , target = None):
        """
        uses textbox, pots on positions....
        """

        if target is None:
            framekind = self.frame
        else:
            framekind = target

        row,col=list(rowcol)
        if not self.frame_ok: return
        stretchy = 2.2
        stretchx = 1.3 # this also compensates center-left align?
        pos=[ self.posx_offs, self.posy_offs ]
        self.get_font_params(" WEB 2.3, ")
        WIDTH = self.text_width
        self.get_font_params(txt)

        if side=="left":  col=0
        if side=="right":  col=-1
        pos[0] = self.posx_offs + int(col*WIDTH*stretchx)
        pos[1] = self.posy_offs + self.text_height + int(row*stretchy*self.text_height)

        # Just columns
        if col>self.maxcol:
            print("X... only {} columns allowed".format(self.maxcol) )
            return

        # manually I set leftside
        # if (row==1)and(col==0):  side="left"
        # if (row==2)and(col==0):  side="left" # low deck
        if (row==3)and(col==0):  side="left"
        if (row==4)and(col==0):  side="left"
        if (row==5)and(col==0):  side="left"

        if (row==6)and(col==0):  side="left"
        if (row==7)and(col==0):  side="left"
        if (row==8)and(col==0):  side="left"
        if (row==9)and(col==0):  side="left"

        if (row==10)and(col==0):  side="left"

        if side=="" and row>2:
            print("X... Too many rows, (0,1,2 only)")
            return

        #------sides
        if side=="left" or side=="right":
            #print("D.. SIDES", self.maxrow, self.maxcol)
            if row>self.maxrow:
                print("X... {} rows {} cols allowed".format(self.maxrow,self.maxcol) )
                return
            #-----OK i go for it---
            #txt=txt[0:3] # i dont restrict...
            #print(txt)
            self.get_font_params("txt")
            WIDTH = self.text_width
            # ----- i dont remember why this ADDITION...
            #pos[1]+= int(2*stretchy*self.text_height)
            #---- right side
            if side=="right":
                pos[0] = self.frame.shape[1] - self.posx_offs - int(stretchx*WIDTH)

        else:
            if row==0:
                if (col==0):
                    NOW = dt.datetime.now()
                    date = NOW.strftime(".. %H:%M:%S %Y/%m/%d")
                    me = socket.gethostname()
                    txt = f"{date} {me} {__version__}"
                    # print("X... timemark requested")
                    self.textbox(txt, pos )
                    if NOW.second % 2 == 0:
                        #  fontsize 0.5=> 10   or 0.3 for RPI 320x240
                        cv2.circle( framekind, (10,10), int(self.fontScale*18), (0,0,255), -1 )

                    else:
                        cv2.circle( framekind, (10,10), int(self.fontScale*18), (0,255,0), -1 )

                    return
                if col<3:
                    return


            #if row==2:
                #pos[1] = self.posy_offs + int(stretchy*self.text_height)
            if row==2:
                pos[1] = self.frame.shape[0] - int(1.5*self.posy_offs)

        #print(pos)
        self.textbox(txt, pos , bgcolor= self.RC_COLOR(row,col) , target = framekind)

    #-------------------------------------------- ENDOF LABELS----------


    def rotate180(self, angle):
        if angle == 0:
            return
        elif angle == 180:
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)
        else:
            self.frame = imutils.rotate(self.frame, angle)

    def save_background(self):
        cv2.imwrite( self.BGFILE , self.frame ) # nicely saved
        self.frame_bg = self.frame.copy() # else artifacts remain
        # frame_bg = self.frame.copy()
        # frame_bg2 = cv2.imencode('.jpg', frame_bg)[1].tobytes()
        # save_bg = False

    def subtract(self):
        if self.frame_bg is None:
            if os.path.exists( self.BGFILE ):
                self.frame_bg = cv2.imread( self.BGFILE )
                print("OLD BACKGROUND IMAGE FOUND", self.frame_bg.shape)
            else:
                return
        frame1 = cv2.subtract(self.frame , self.frame_bg ) #, mask = frame_mask
        # frame 1 is difference...
        # frame1[:22,:]  = self.frame [:22,:]
        # frame1[-22:,:] = self.frame [-22:,:]
        self.frame = frame1



    def reset_camera_start(self):
        self.camera_start = dt.datetime.now()

    def translate(self, speedx = -0.35,  speedy = -0.015 ):
        self.camera_age = (dt.datetime.now() - self.camera_start ).total_seconds()
        dwidth = speedx * self.camera_age  #negative up
        dheight = speedy * self.camera_age  # positive down
        T = np.float32([[1, 0, dwidth], [0, 1, dheight]])
        shifted = cv2.warpAffine(self.frame, T, (self.frame.shape[1], self.frame.shape[0]))
        # print( T )
        self.frame = shifted



    def crosson(self,  dix, diy):
        RADIUS=63
        y = int(self.frame.shape[0]/2)
        x = int(self.frame.shape[1]/2)

        ix = x+dix
        iy = y+diy

        i2=cv2.circle( self.frame, (ix,iy), RADIUS, (0,255,55), 1)
        i2=cv2.line(i2, (ix-RADIUS+5,iy), (ix-5,iy), (0, 255, 55), thickness=1, lineType=8)
        i2=cv2.line(i2, (ix+RADIUS-5,iy), (ix+5,iy), (0, 255, 55), thickness=1, lineType=8)

        i2=cv2.line(i2, (ix,iy-RADIUS+5), (ix,iy-5), (0, 255, 55), thickness=1, lineType=8)
        i2=cv2.line(i2, (ix,iy+RADIUS-5), (ix,iy+5), (0, 255, 55), thickness=1, lineType=8)

        i2=cv2.line(i2, (ix,iy), (ix,iy), (0, 255, 55), thickness=1, lineType=8)
        #return self.frame


    #---------- for motion detect i need a second processing line frame2
    # to keep the camera on

    def setblur(self, blur=0, dmblur = 0):
        if (blur>0) and (blur % 2 ==0):
            print("D... wrong gaussian value, incrementing by 1")
            blur+=1
        if blur>0:
            self.frame = cv2.GaussianBlur(self.frame, (blur, blur), 0)
        if (dmblur>0) and (dmblur % 2 ==0):
            dmblur+=1
        # if dmblur>0:
        #     grayB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        #     grayB = cv2.GaussianBlur(grayB, (dmblur, dmblur), 0)


    def setaccum(self, accumulate=0):
        if accumulate>1:
            cv2.accumulateWeighted(self.frame, self.averageValue1, 1/accumulate )
            #self.frame = self.averageValue1 all is white
            self.frame = cv2.convertScaleAbs(self.averageValue1)


    def chk_threshold(self, threshold=100):
        """
        compare threshold
        """

        # NOT HERE; this is a timelock - only a new seq self.motion_detected = False #  Here the flag is risen
        motion = False
        self.detect_frame = self.frame.copy()
        self.frame_number+= 1

        #print( self.delta_frame)
        if not (self.delta_frame is None):
            thresh = cv2.threshold(self.delta_frame, threshold, 255,
                                cv2.THRESH_BINARY)[1]
            # print(thresh)
            ok = False
            try:
                noz = cv2.countNonZero(thresh)
                ok = True
            except:
                ok = False
            if not(ok):
                return

            thresh = cv2.dilate(thresh, None, iterations=3)
            cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                    cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            totarea = 0
            largest = cnts
            largesta = 0
            largest = []
            frame_area = self.delta_frame.shape[0]*self.delta_frame.shape[1]
            for c in cnts:
                dearea = cv2.contourArea(c)
                # print("    search {}".format( dearea ) )
                totarea+=dearea # total over threshold = totarea; X frame_area
                (x, y, w, h) = cv2.boundingRect(c)
                if (y+h<self.text_height*3) or (y>self.delta_frame.shape[0]-self.text_height*3):
                    continue
                cv2.rectangle(self.detect_frame, (x,y),(x+w,y+h),(0,255,0),1)
                if largesta<dearea:
                    largesta = dearea
                    largest = [c] # cheap trick, one instead of all

            # for c in cnts:
            largesta = int(largesta/frame_area*1000)/10 # recode for late

            motion = False
            # -----one in the list  for now.
            for c in largest:
                area = cv2.contourArea(c)
                # print("Largest: {}/{}  ... {:.2f}%".format(area, frame_area, area/frame_area*100) )
                # rectangl 1% IS FINE. I pUSH to 0.1%
                if (area/frame_area < 0.001) or (area/frame_area > 0.7): #minarea 0.5%
                    # go away for any smaller
                    continue
                (x, y, w, h) = cv2.boundingRect(c)
                # print(  x, y, w, h , self.text_height)

                cv2.rectangle(self.detect_frame, (x,y),(x+w,y+h),(0,0,255),2)  # BGR
                motion = True
                area=w*h


                dtext = "{:.1f}%/{:.1f}%/{}".format(
                    area/frame_area*100, noz*100/frame_area, len(cnts) )
                # --- all with detection is done here.... detect and delta frames must exist then
                self.setbox( f"{dtext}", self.dm ,  target = self.detect_frame )
                self.setbox( f"{dtext}", self.dm ,  target = self.delta_frame )
                self.setbox( f"{dtext}", self.dm    )
                if "self.histo_frame" in locals():
                    self.setbox( f"{dtext}", self.dm ,  target = self.histo_frame )


                if (motion) and (not self.motion_detected):
                    self.motion_detected_start = dt.datetime.now()
                    # print("i... new motion detected", self.motion_detected_start, self.frame_number)
                if motion:
                    self.motion_detected = True
                    # print("i... Motion ON")  # comming here mns already TRUE

                if ((dt.datetime.now() - self.motion_detected_start).total_seconds() > self.expire) :
                    self.motion_detected = False # this kills
                    # print("i... Motion OFF expired", self.expire, self.frame_number)

            if len(largest)==0: # ----------- if no contour - set OFF
                self.motion_detected = False # this kills
                # print("i... Motion OFF", self.frame_number)




    def detmo(self,  dmaccumulate=0, dmblur = 0, threshold = 100 ):
        """
        if there is an accumulation - process it
        if there is NO detection, rewrite the buffer
        """
        if dmaccumulate>1:
            if (dmblur>0) and (dmblur % 2 ==0):
                dmblur+=1


            frame2 = None
            if dmblur==0:
                dmblur=1


            # if (self.motion_detected == False)  or  ((dt.datetime.now() - self.motion_detected_start).total_seconds() > self.expire) :
            #     #if len(self.accubuffer) < dmaccumulate:
            #     print("I... updating accu buffer")
            #     self.accubuffer.append(self.frame)
            #     #return
            #     #self.accubuffer.append(self.frame)
            #     while len(self.accubuffer)>dmaccumulate: # i compare against X frames back
            #         frame2=self.accubuffer.pop(0) # get more time distance

            # elif self.motion_detected == True:
            #     # no append at motion, only show the last
            #     frame2 = self.accubuffer[0]

            self.accubuffer.append(self.frame)
            while len(self.accubuffer)>dmaccumulate: # i compare against X frames back
                frame2=self.accubuffer.pop(0) # get more time distance

            if not (frame2 is None):
                # create version A
                cv2.accumulateWeighted(frame2, self.averageValue1, 1/dmaccumulate, None)
                grayA = cv2.cvtColor(cv2.convertScaleAbs(self.averageValue1), cv2.COLOR_BGR2GRAY)
                grayA = cv2.GaussianBlur(grayA, (dmblur, dmblur), 0)

                # create version B
                grayB = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
                grayB = cv2.GaussianBlur(grayB, (dmblur, dmblur), 0)
                # grayA = cv2.cvtColor(averageValue1, cv2.COLOR_BGR2GRAY)
                #----see the difference
                #frame = cv2.absdiff(grayA, grayB)
                self.delta_frame = cv2.absdiff(grayB, cv2.convertScaleAbs(grayA))
            else:
                print("i... None frame2")
                self.delta_frame = self.frame



# ------------------------------------------------------- HISTO ---------------------------
    def histo_mean(self):

        BINS = 128
        #bins = np.arange(BINS)
        bins = np.arange(BINS).reshape(1,BINS)

        framegray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)

        hist_gray = cv2.calcHist([framegray], [0], None, [BINS], [0, 255])
        # cv2.normalize(hist_gray,hist_gray,0,255,cv2.NORM_MINMAX)

        #hist_gray = hist_gray/hist_gray.max() # norm 1
        #mean = 1

        #print(f"i... mimax mean  {hist_gray.min():4.1f},  {hist_gray.max():4.1f}, {hist_gray.mean():4.1f} ... {mean}" )
        #print( hist_gray[:9],  bins[:9]  , len(hist_gray), len(bins) , type(hist_gray), type(bins) )


        mean = np.dot( bins, hist_gray )[0][0]/hist_gray.sum()/2.55
        #print("MEAN",mean)
        #print( "LEN TYPE", len(mean),type(mean) )

        #cv2.normalize(hist_gray,hist_gray)
        #mean = hist_gray.mean()/BINS #/len(hist_gray)
        ###mean = mean.mean()/BINS
        # mean = hist_gray.mean() #/len(hist_gray)
        # min1 = hist_gray.min()
        # max1 = hist_gray.max() #/len(hist_gray)
        #print(f"i... .flattened gray    {mean}")
        #  {min1:.1f} {max1:.1f}
        return mean  #/255*100

    def zoom(self, scale, x=None,y=None):
        #scale = zoom
        #get the webcam size


        height, width, channels = self.frame.shape
        #prepare the crop
        centerX = int(height/2)
        centerY = int(width/2)

        #if not x is None:
        #    centerX+= x
        #if not y is None:
        #    centerY+= y
        if (x!=0) or (y!=0):
            dwidth = -x    #negative up
            dheight = -y   # positive down
            T = np.float32([[1, 0, dwidth], [0, 1, dheight]])
            self.frame = cv2.warpAffine(self.frame, T, (self.frame.shape[1], self.frame.shape[0]))

        # return
        radiusX,radiusY= int(height/2/scale),int(width/2/scale)

        minX,maxX=centerX-radiusX,centerX+radiusX
        minY,maxY=centerY-radiusY,centerY+radiusY
        #minX=max(minX,0)
        #minY=max(minY,0)
        #maxX=min(maxX,height)
        #maxY=min(maxY,width)

        #print(" cut x=",minX,maxX, "  and y=",minY,maxY )
        cropped = self.frame[minX:maxX, minY:maxY]
        #print("CENTER:",centerX, centerY,"#",  cropped.shape, scale,"x")
        self.frame = cv2.resize(cropped, (width, height))


    def histo(self):

        h = self.frame.copy()
        BINS = 128
        bins = np.arange(BINS).reshape(BINS,1)
        color = [ (255,0,0),(0,255,0),(0,0,255) ]

        for ch, col in enumerate(color):
            hist_item = cv2.calcHist([self.frame],[ch],None,[BINS],[0,255])
            #cv2.normalize(hist_item,hist_item, 0, 255, cv2.NORM_MINMAX)
            hist_item = hist_item/hist_item.max()*255
            hist=np.int32(np.around(hist_item))
            pts = np.column_stack((bins*int(640/BINS),475-(hist*440/255).astype(int)))
            cv2.polylines(h,[pts],False,col)

        framegray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        hist_gray = cv2.calcHist([framegray], [0], None, [BINS], [0, 255])
        #cv2.normalize(hist_gray,hist_gray,0,255,cv2.NORM_MINMAX)
        hist_gray = hist_gray/hist_gray.max()*255

        hist=np.int32(np.around(hist_gray))
        pts = np.column_stack((bins*int(640/BINS),475-(hist*440/255).astype(int)))
        cv2.polylines(h,[pts], False,  [255,255,255], thickness= 2 )

        self.histo_frame = h




# --------------------------------------------------------save avi ------------
    def save_avi(self, seconds =  1, name = "" ):
        """

        """
        #print("i... save_avi", seconds, name)
        # -------------- one shot
        if seconds == 0:
            return
        elif seconds<0:
            if not self.aviopened:
                filename = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                me = socket.gethostname()
                filename = f"{me}{name}_{filename}.avi"
                filename = os.path.expanduser("~/"+filename)
                print(filename)
                print(filename)
                print(filename)
                print(filename)

                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.aviout = cv2.VideoWriter( filename , fourcc , 25.0, (640,480))
                self.aviopened = True

            self.aviout.write(self.frame)
        # -------------- timelapse if seconds>0:
        elif seconds>0:
            if not self.aviopened_laps:
                filename = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
                me = socket.gethostname()
                filename = f"{me}_laps{seconds:04d}_{filename}.avi"
                filename = os.path.expanduser("~/"+filename)
                print(filename)
                print(filename)
                print(filename)
                print(filename)

                fourcc = cv2.VideoWriter_fourcc(*'XVID')
                self.aviout_laps = cv2.VideoWriter( filename , fourcc , 10.0, (640,480))
                self.aviopened_laps = True
                # self.avi_last = dt.datetime.now()


            if (dt.datetime.now()-self.avi_last).total_seconds() > seconds:
                self.aviout_laps.write(self.frame)
                self.avi_last = dt.datetime.now()
                print("i... saving timelaps",dt.datetime.now() )




#===============================================================
if __name__=="__main__":
    es1 = Stream_Enhancer()
    #if not(es1.add_frame_from_cam()):
    es1.add_frame_from_cam()
    # es1.show_frame()

    print("DD..... RUNALl")
    for i in range(1000):
        for row in range(4): # max 3 rows
            for col in range(6): # 5 columns @ 480 max
                es1.setbox("_Row{}COL{}_".format(row,col), (row,col) )
        for row in range(16): # 5 columns @ 480 max
            es1.setbox("{}COL{}_".format(row,col), (row,col), "left")
        for row in range(16): # 5 columns @ 480 max
            es1.setbox("{}COL{}_".format(row,col), (row,col), "right")

        es1.setbox("MODE avg ",es1.MODE)
        es1.setbox("DISP laps ",es1.DISP)

        es1.setbox("avg = 1 ",es1.avg)
        es1.setbox("blr = 0 ",es1.blr)

        es1.blimp_frame()
