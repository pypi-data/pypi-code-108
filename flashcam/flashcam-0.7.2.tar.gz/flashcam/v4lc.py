#!/usr/bin/env python3
'''
 on https://github.com/TheStaticTurtle/RemoteV4L2-CTL/blob/master/remote_v4l2ctl/utils.py
'''
from flashcam.version import __version__
from fire import Fire
from flashcam import config

#import v4l2py
#from v4l2py import Device

import subprocess as sp

import cv2

import matplotlib.pyplot as plt
import numpy as np
import json

import itertools # duplicite list removeal

import sys

class V4L2_Control:
    """docstring for V4L2_CTL"""

    def __init__(self, control_group, name, addr, type, min=-99, max=-99, step=-99, default=-99, value=-99, flags="none", access="local", device="/dev/video0", callback=None):
        super(V4L2_Control, self).__init__()
        self.control_group = control_group

        self.name = name
        self.addr = addr
        self.type = type
        self.min = min
        self.max = max
        self.step = step
        self.default = default
        self.value = value
        self.flags = flags

        self.access = access
        self.device = device
        self.callback = callback

        self.server = None


    def setServer(self, server):
        self.server = server

    def get_value(self):
        return self.value

    def getmin_value(self):
        return self.min

    def getmax_value(self):
        return self.max

    def setdef_value(self):
        return self.change_value(self.default)

    # uuuuuiiiiiiiiii ---works
    def getdef_value(self):
        return self.default

    def change_value(self, value):
        if value> self.max:
            value = self.max
        if value< self.min:
            value = self.min
        try:
            value = int(value)
        except Exception as e:
            print("change_value: Invalid input -> " + str(e))
            return -1

        if self.step != -99 and value < self.min:
            print("change_value: Value too little", value," x ",self.min)
            return -1

        if self.step != -99 and value > self.max:
            print("change_value: Value too big", value," x ",self.max)
            return -1

        if self.step != -99 and value % self.step != 0:
            print("change_value: Invalid step number (Steps per " + str(self.step) + ")")
            return -1

        if self.type == "custom":
            if self.callback is not None:
                return self.callback(value)

        if self.access == "local":
            #print("Executing: " + ' '.join(['v4l2-ctl', '-d', self.device, '--set-ctrl=' + self.name + '=' + str(value)]))
            try:
                sp.check_output(['v4l2-ctl', '-d', self.device, '--set-ctrl=' + self.name + '=' + str(value)]).decode("utf-8")
                self.value = value
                return 0
            except sp.CalledProcessError as e:
                print(
                    "Failed to execute command" +
                    ' '.join(['v4l2-ctl', '-d', self.device, '--set-ctrl=' + self.name + '=' + str(value)]) +
                    " -> "+str(e)
                )
                return -1
        elif self.access == "remote" and self.server is not None:
            print("Sending remote command: " + self.name + '=' + str(value))
            r = self.server.send_value_set(self.name, value)
            self.value = value
            return r

    def asdict(self):
        return {
            "control_group": self.control_group,
            "name": self.name,
            "addr": self.addr,
            "type": self.type,
            "min": self.min,
            "max": self.max,
            "step": self.step,
            "default": self.default,
            "value": self.value,
            "flags": self.flags
        }
    def __repr__(self):
        return str(self)
    def __str__(self):
        out = "V4L2_Control() -> " + self.name + " " + self.addr + " (" + self.type + ")  :  "
        out += "min=" + str(self.min) + " " if self.min != -99 else ""
        out += "max=" + str(self.max) + " " if self.max != -99 else ""
        out += "step=" + str(self.step) + " " if self.step != -99 else ""
        out += "default=" + str(self.default) + " " if self.default != -99 else ""
        out += "value=" + str(self.value) + " " if self.value != -99 else ""
        out += "flags=" + self.flags + " " if self.flags != "none" else ""
        return out



class V4L2_CTL():
    """docstring for V4L2_CTL"""

    def __init__(self, device="/dev/video0"):
        super(V4L2_CTL, self).__init__()
        self.device = device
        self.controls = self._list_controls()
        self.capabilities = []
        self.update_capabilities()

        for control in self.controls:
            #print(control.name)
            setattr(self, "set_" + control.name, control.change_value)
            setattr(self, "getmin_" + control.name, control.getmin_value)
            setattr(self, "getmax_" + control.name, control.getmax_value)
            setattr(self, "setdef_" + control.name, control.setdef_value)
            setattr(self, "get_" + control.name, control.get_value)
            setattr(self, "getdef_" + control.name, control.getdef_value)

    def get_capbilities_as_json(self):
        return json.dumps([x.asdict() for x in self.controls])

    def get_capbilities(self):
        li = [x.asdict() for x in self.controls]
        ca = []
        for i in li:
            ca.append( i["name"] )
        return ca


    # def refresh(self):
    #     super(V4L2_CTL, self).__init__()
    #     self.controls = self._list_controls()
    #     self.capabilities = []
    #     self.update_capabilities()
    #     for control in self.controls:
    #         #print(control.name)
    #         setattr(self, "set_" + control.name, control.change_value)
    #         setattr(self, "getmin_" + control.name, control.getmin_value)
    #         setattr(self, "getmax_" + control.name, control.getmax_value)
    #         setattr(self, "setdef_" + control.name, control.setdef_value)
    #         setattr(self, "get_" + control.name, control.get_value)
    #         setattr(self, "getdef_" + control.name, control.getdef_value)


    def update_capabilities(self):
        self.capabilities = [x.name for x in self.controls]

    def has_capability(self,what):
        return what in self.capabilities

    def _list_controls(self):
        controls = []
        #print("Executing: " + ' '.join(['v4l2-ctl', '-d', self.device, '-l']))
        CMD = ['which','v4l2-ctl']
        child = sp.Popen( CMD, stdout = sp.PIPE )
        returncode = child.returncode
        # print(f"i... v4l2-ctl:", returncode, 'str=',child.communicate()[0] )
        if not(returncode is None):
            print("X... install v4l2-ctl:  apt install v4l-utils")
            sys.exit(1)

        CMDL = ['v4l2-ctl', '-d', self.device, '-l']
        #print("i... ", CMDL )
        output = ""
        try:
            output = sp.check_output( CMDL ).decode("utf-8")  # TODO: Check if the output is valid
        except Exception as e:
            print("!... Exception when", CMDL)
    #print(f"i... output = /{output}/")
        if len(output) <2:
            #print("D... no output, returning")
            return []

        raw_ctrls = [x for x in output.split('\n') if x]  # TODO: Same

        last_control_group = "unknown"
        for raw_ctrl in raw_ctrls:
            if raw_ctrl[0] != ' ':
                last_control_group = ('_'.join(raw_ctrl.split(" ")[:-1])).lower()
                print("Found new control group: " + last_control_group)
            else:
                # Remove double white spaces
                while "  " in raw_ctrl:
                    raw_ctrl = raw_ctrl.replace("  ", " ")

                raw_ctrl_what, raw_ctrl_values = raw_ctrl.split(":")
                raw_ctrl_what = [x for x in raw_ctrl_what.split(' ') if x and x != ' ']

                values = {
                    "min": -99,
                    "max": -99,
                    "step": -99,
                    "default": -99,
                    "value": -99,
                    "flags": "none"
                }

                for name, value in [name_value_combo.split("=") for name_value_combo in raw_ctrl_values.split(" ") if
                                    "=" in name_value_combo]:
                    values[name] = value

                ctrlr = V4L2_Control(
                    last_control_group,
                    raw_ctrl_what[0],
                    raw_ctrl_what[1],
                    raw_ctrl_what[2].replace("(", "").replace(")", ""),
                    min=int(values["min"]),
                    max=int(values["max"]),
                    step=int(values["step"]),
                    default=int(values["default"]),
                    value=int(values["value"]),
                    flags=values["flags"],
                    device=self.device
                )

                #print("N..." + str(ctrlr))
                controls.append(ctrlr)


        return controls


#------------------------------------------------------------------------------------------------

# print("v... unit 'unitname' loaded, version:",__version__)






def set_gem(cc, gain, expo, mmaga):
    capa = cc.get_capbilities()

    if not expo is None:
        if (expo == "auto") or (expo == "def"):
            if "exposure_absolute" in capa:
                print("D... AUTO EXPOSURE ON")
                cc.setdef_exposure_auto() # doesnt do default 3
                print("ex def",cc.get_exposure_auto())
                cc.setdef_exposure_auto()  # i thik he knows what is auto
        elif expo !=-1:
            if "exposure_absolute" in capa:
                if "exposure_auto" in capa:
                    print("D... AUTO EXPOSURE OFF")
                    cc.setdef_exposure_auto() # doesnt do default 3
                    print("ex def",cc.get_exposure_auto())
                    cc.set_exposure_auto(1)  # I just a guess, 1 may be manual, 3


                    ex = cc.get_exposure_absolute()
                    mine = cc.getmin_exposure_absolute()
                    maxe = cc.getmax_exposure_absolute()
                    print(f"i... current exposure {ex}   range {mine}, {maxe}")

                    ex = int( expo * (maxe-mine)+mine)
                    print("i... new = ",ex)
                    if ex>maxe: ex=maxe
                    if ex<mine: ex=mine

                    cc.set_exposure_absolute(ex)
            # very stupid wabcam
            elif "exposure" in capa:
                ex = cc.get_exposure()
                mine = cc.getmin_exposure()
                maxe = cc.getmax_exposure()
                print(f"i... current exposure {ex}   range {mine}, {maxe}")

                ex = int( expo * (maxe-mine)+mine)
                print("i... new = ",ex)
                if ex>maxe: ex=maxe
                if ex<mine: ex=mine

                cc.set_exposure(ex)
            else:
                print("X... exposure_absolute NOR exposure not in capacities")
    if not gain is None:
        if gain == "def":
            if "gain" in capa:
                cc.setdef_gain()
        elif gain !=-1:
            if "gain" in capa:
                ga = cc.get_gain()
                ming = cc.getmin_gain()
                maxg = cc.getmax_gain()
                print(f"i... current gain {ga}   range {ming}, {maxg}")

                ga = int( gain * (maxg-ming)+ming)
                print("i... new = ",ga)
                if ga>maxg: ga=maxg
                if ga<ming: ga=ming

                cc.set_gain(ga)
            else:
                print("X... gain noit in capacities")

    if not mmaga is None:
        if mmaga == "def":
            if "gamma" in capa:
                cc.setdef_gamma()
        elif mmaga !=-1:
            if "gamma" in capa:
                ga = cc.get_gamma()
                ming = cc.getmin_gamma()
                maxg = cc.getmax_gamma()
                print(f"i... current gamma {ga}   range {ming}, {maxg}")

                ga = int( mmaga * (maxg-ming)+ming)
                print("i... new = ",ga)
                if ga>maxg: ga=maxg
                if ga<ming: ga=ming

                cc.set_gamma(ga)
            else:
                print("X... gamma not in capacities")

    #------------------------------------------end of function--- SET_GEM








def func(debug = False):

    print("D... in unit unitname function func DEBUG may be filtered")
    print("i... in unit unitname function func - info")
    print("X... in unit unitname function func - ALERT")
    return True

# def test_config_save():
#     config.CONFIG['filename'] = "~/.config/flashcam/cfg.json"
#     config.show_config()
#     print( config.get_config_file() )
#     return config.save_config()

# def test_config_read():
#     config.CONFIG['filename'] = "~/.config/flashcam/cfg.json"
#     config.load_config()
#     config.show_config()
#     print( config.get_config_file() )
#     assert config.save_config() == True

def test_func():
    print("i... TESTING function func")
    assert func() == True

#------------------------------------------------------------------------------------------------

def get_resolutions(vidnum):
    CMD = ['v4l2-ctl', '-d', "/dev/video"+str(vidnum),  "--list-formats-ext"]
    #print("i... cmd = {CMD}")
    output = sp.check_output(CMD).decode(
            "utf-8")  # TODO: Check if the output is valid
    output = output.split("\n")
    output = sorted( [ x.split("Discrete ")[-1] for x in output if x.find("Size: Discrete")>0 ])

    output = [tupl for tupl in {item for item in output }]
    output = sorted( output, key = lambda x: int(x.split("x")[0]) * int(x.split("x")[1]) )
    #o = [ float(o.split("x")[0]+"."+o.split("x")[1]) for o in output]
    print(output)
    return output



def tune_histo(cc, h_avg):

    glow,ghigh = 100, 120

    capa = cc.get_capbilities()
    maxg,gg,ming = 2,1,0
    maxe,ex,mine = 500,100,100

    if "gain" in capa:
        gg = cc.get_gain()
        maxg = cc.getmax_gain()
        ming = cc.getmix_gain()


    if "exposure_absolute" in capa:
        ex = cc.get_exposure_absolute()
        mine = cc.getmin_exposure_absolute()
        maxe = cc.getmax_exposure_absolute()


    #print(f"                   {ming} - {gg} - {maxg} ; {mine}-{ex}-{maxe} ")
    if h_avg<glow:
        #print("              +2    ", gg,ex)
        ex = int(1.1*ex)
        #print("              +2!    ", gg,ex)
        gg = int(1.1*gg)
    elif h_avg>ghigh:
        ex = int(0.9*ex)
        gg = int(0.9*ex)

    if gg>maxg: gg=maxg
    if gg<ming: gg=ming

    if ex>maxe: ex=maxe
    if ex<mine: ex=mine

    #print("                  ", gg,ex)

    if "exposure_absolute" in capa: cc.set_exposure_absolute(ex)
    if "gain" in capa: cc.set_gain(gg)

    # if gg>maxg:
    #     if h_avg<glow:
    #         ex+=2
    #         cc.set_exposure_absolute(ex)
    #     elif h_avg>ghigh:
    #        gg-=2
    #        if "gain" in capa: cc.set_gain(gg)
    # elif gg<ming:
    #     if h_avg>ghigh:
    #        ex-=2
    #        cc.set_exposure_absolute(ex)
    #     if h_avg<glow:
    #        gg+=2
    #        if "gain" in capa: cc.set_gain(gg)
    # else:
    #     if h_avg<glow:
    #         gg+=2
    #         if "gain" in capa: cc.set_gain(gg)
    #     elif h_avg>ghigh:
    #         gg-=2
    #         if "gain" in capa: cc.set_gain(gg)
    #res = cc.set_exposure_absolute(ex)
    return gg,ex


def main( devid ):
    """
    Here it is a test to set exposure and gain by histogram
    """
    #cam = Device.from_id(0)
    #print( cam.info)
    #print()
    #print(cam.video_capture.get_format())
    cc = V4L2_CTL("/dev/video"+str(devid))
    vid = cv2.VideoCapture(devid)


    lw=1
    bins=256

    initme = True
    gain = 100
    capa = cc.get_capbilities()

    if "exposure_auto" in capa:
        print("D... AUTO EXPOSURE OFF")
        cc.setdef_exposure_auto() # doesnt do default 3
        print("ex def",cc.get_exposure_auto())
        cc.set_exposure_auto(1)

    #print("ex 3",cc.get_exposure_auto())
    if "gain" in capa:
        cc.setdef_gain()
        gg = cc.get_gain()
        print("defgain ",gg)

    if "exposure_absolute" in capa:
        ex = cc.get_exposure_absolute()
        cc.setdef_exposure_absolute()

    gain= 0

    #create two subplots
    ax1 = plt.subplot(1,2,1)
    ax2 = plt.subplot(1,2,2)
    lineGray, = ax2.plot(np.arange(bins), np.zeros((bins,1)), c='r', lw=lw)
    ax2.set_xlim(-10, bins + 10)

    while(True):# https://github.com/nrsyed/computer-vision/blob/master/real_time_histogram/real_time_histogram.py
        #print(" ... gain,  exposure   ",cc.get_gain(), cc.get_exposure_absolute() )

        ret, frame = vid.read()
        # if initme:

        #     #ax2.set_ylim(0, 1)
        #     ax1.set_axis_off()
        #     ax2.spines['right'].set_visible(False)
        #     #ax.spines['bottom'].set_visible(False)
        #     ax2.spines['left'].set_visible(False)
        #     #ax2.set_axis_off()

        #     #create two image plots
        #     im1 = ax1.imshow(frame)

        #     #im2 = ax2.imshow(frame)
        #     #plt.autoscale(enable=True, axis='x', tight=True)
        #     #ax1 = plt.gca()  # only to illustrate what `ax` is
        #     #ax1.autoscale(enable=True, axis='both', tight=True)
        #     #ax2.autoscale(enable=True, axis='both', tight=True)
        #     plt.rcParams['axes.xmargin'] = 0
        #     plt.rcParams['axes.ymargin'] = 0
        #     plt.ion()
        #     ####print("i... plt show")
        #     #plt.show()
        #     #plt.pause(0.01)
        #     initme = False

        framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([framegray], [0], None, [256], [0, 256])
        hist = cv2.normalize(hist, hist).flatten()
        hist /= hist.sum()

        #h_avg = (hist*np.arange(bins)).sum()
        #h_std = ((hist*np.arange(bins)*np.arange(bins)).sum())**0.5


        #------------------ https://stackoverflow.com/questions/9390592/drawing-histogram-in-opencv-python
        #h = np.zeros((300,256,3))
        h = np.zeros((480,640,3))
        h = frame.copy()
        #h = np.flipud(h)

        BINS = 64
        bins = np.arange(BINS).reshape(BINS,1)
        color = [ (255,0,0),(0,255,0),(0,0,255) ]

        for ch, col in enumerate(color):
            hist_item = cv2.calcHist([frame],[ch],None,[BINS],[0,255])
            cv2.normalize(hist_item,hist_item, 0, 255, cv2.NORM_MINMAX)
            hist=np.int32(np.around(hist_item))
            pts = np.column_stack((bins*int(640/BINS),480-(hist*480/255).astype(int)))
            cv2.polylines(h,[pts],False,col)

        framegray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        hist_gray = cv2.calcHist([framegray], [0], None, [BINS], [0, 255])
        cv2.normalize(hist_gray,hist_gray,0,255,cv2.NORM_MINMAX)
        hist=np.int32(np.around(hist_gray))
        pts = np.column_stack((bins*int(640/BINS),480-(hist*480/255).astype(int)))
        cv2.polylines(h,[pts], False,  [255,255,255], thickness= 2 )


        #h=np.flipud(h)

        cv2.imshow('colorhist',h)
        #cv2.waitKey(1)


        #gg,ex = tune_histo(cc, h_avg)
        #print(f" g={gg} e={ex}   {h_avg:.1f} ({h_std:.1f}) ", end = "\r" )


        #im1.set_data(frame)
        #lineGray.set_ydata(hist)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    vid.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    print("i... in the __main__ of unitname of flashcam")
    Fire(main)
