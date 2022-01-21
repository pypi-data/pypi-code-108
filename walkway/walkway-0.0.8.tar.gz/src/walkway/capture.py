# 2021-07-31. Leonardo Molina.
# 2022-01-21. Last modified.

from datetime import datetime
from pathlib import Path
from queue import Queue
from threading import Lock, Thread
from walkway.events import Publisher
from walkway.flexible import Flexible

import argparse
import cv2
import json
import logging
import math
import numpy as np
import PySpin
import signal
import sys
import time
import walkway.flir as flir

class DetectionStates:
    Started = 1
    Ended = 2


class RecordSettings:
    def __init__(self, recorder, filename):
        self.once = True
        self.finish = np.Inf
        self.recorder = recorder
        self.filename = filename


def showMessage(image, text, center=(10, 30), color=50, fontScale=1):
    cv2.putText(
        img=image,
        text=text,
        org=center,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=fontScale,
        color=color,
        thickness=3
    )
    cv2.putText(
        img=image,
        text=text,
        org=center,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=fontScale,
        color=255,
        thickness=1
    )


def jsonFile(filename):
    if Path(filename).is_file():
        try:
            f = open(filename)
            json.load(f)
            f.close()
            return filename
        except json.JSONDecodeError as ex1:
            f.close()
            raise ex1
        except Exception as ex2:
            raise ex2
    else:
        raise FileNotFoundError(filename)


class Capture(object):
    """
    Capture high frame rate videos of a custom-made, CatWalk like setup for mice using a FLIR's BlackFly camera.
    A video is saved to disk whenever motion is detected and if locomotion satisfies the criteria defined in the configuration (e.g. ignoring brief periods of locomotion).
    A configuration file in JSON format may be provided:
        {
            "SpeedThreshold": 2.00,
            "LocomotionThreshold": 0.05,
            "QuiescenceThreshold": 0.01,
            "MinDuration": 0.75,
            "MaxDuration": 3.00,
            "AreaProportion": 0.25,
            "BlurSize": 0.10,
            "Folder": "C:/Users/Molina/Videos/",
            "Prefix": "WW",
            "OutputQuality": 95,
            "OutputFrameRate": 30,
            "AcquisitionFrameRate": 166,
            "ExposureTime": 1000,
            "GammaEnable": True,
            "Gamma": 0.8,
            "Gain": 15,
            "Width": 1280,
            "Height": 200,
            "OffsetX": 0,
            "OffsetY": 412
        }

    """


    def __saveClipBuffer(self, buffer, nFrames, filename, message=""):
        p = self.__private
        options = PySpin.MJPGOption()
        options.frameRate = p.OutputFrameRate
        options.quality = p.OutputQuality
        recorder = PySpin.SpinVideo()
        try:
            recorder.Open(filename, options)
            success = True
        except Exception as ex:
            logging.error(str(ex))
            success = False

        if success:
            p.fileCount += 1
            message = "[video #%i] %s" % (p.fileCount, message)
            logging.info(message)
            self.__setMessage(message)
            b = len(buffer)
            a = max(0, b - nFrames)
            for i in range(a, b):
                recorder.Append(buffer[i])
            recorder.Close()
        else:
            message = "[not saved] %s" % message
            logging.info(message)
            self.__setMessage(message)

        return success


    def __resetBackground(self):
        p = self.__private
        p.background = cv2.createBackgroundSubtractorMOG2(history=math.ceil(p.processFrequency / p.SpeedThreshold), detectShadows=False)


    @property
    def frame(self):
        p = self.__private
        with p.processLock:
            if p.image is None:
                image = None
            else:
                image = p.image.copy()
                width = image.shape[1]
                if p.trail.size != width:
                    p.trail = np.full(width, False)
                    p.lines = np.empty((0, width))
        return image


    def decorate(self, image, message=False, trail=0):
        p = self.__private
        if image is not None:
            if message:
                trail = max(trail, 0.05)
            margin = int(p.Height * trail)
            image[0:margin, p.trail] = 0
            image[-margin:-1, p.trail] = 0
            if message and time.time() < p.messageToc:
                showMessage(image, *p.message[0], **p.message[1])


    def __setMessage(self, *args, duration=1, **kwargs):
        p = self.__private
        p.messageToc = time.time() + duration
        p.message[0] = args
        p.message[1] = kwargs


    def __capture(self):
        p = self.__private
        while p.capture:
            if p.connect or (p.restartAcquisition and not p.connected):
                if p.connected:
                    logging.warning("Communication with camera %i had been previously established." % p.cameraId)
                else:
                    p.flirSystem = PySpin.System.GetInstance()
                    cameraList = p.flirSystem.GetCameras()
                    
                    if p.DeviceUserID is not None:
                        found = False
                        for cameraId, camera in enumerate(cameraList):
                            wasInitialized = camera.IsInitialized()
                            if not wasInitialized:
                                camera.Init()
                            nodemap = camera.GetNodeMap()
                            if p.DeviceUserID == flir.getValue(nodemap, "DeviceUserID"):
                                found = True
                                break
                            if not wasInitialized:
                                camera.DeInit()
                        if found:
                            p.cameraId = cameraId
                            
                    if p.cameraId >= cameraList.GetSize():
                        p.flirSystem.ReleaseInstance()
                        logging.error("Cannot detect camera %i." % p.cameraId)
                    else:
                        try:
                            p.Camera = cameraList[p.cameraId]
                            p.Camera.Init()
                            p.nodemap = p.Camera.GetNodeMap()
                            p.streamNodemap = p.Camera.GetTLStreamNodeMap()
                            success = True
                        except PySpin.SpinnakerException as ex:
                            logging.error(str(ex))
                            success = False
                        if success:
                            p.connected = True
                            logging.info("Established communication with camera %i." % p.cameraId)
                p.connect = False

            if p.restartAcquisition:
                if p.connected:
                    if p.Camera.IsStreaming():
                        p.Camera.EndAcquisition()

                    flir.setValue(p.streamNodemap, "StreamBufferHandlingMode", "NewestOnly")
                    flir.setValue(p.nodemap, "AcquisitionMode", "Continuous")
                    flir.setValue(p.nodemap, "TriggerMode", "Off")
                    flir.setValue(p.nodemap, "TriggerSelector", "AcquisitionStart")

                    if p.AcquisitionFrameRate is not None:
                        flir.setValue(p.nodemap, "AcquisitionFrameRateEnable", True)
                        flir.setValue(p.nodemap, "AcquisitionFrameRate", p.AcquisitionFrameRate)
                    p.AcquisitionFrameRate = flir.getValue(p.nodemap, "AcquisitionFrameRate")

                    self.__set(
                        ExposureTime=p.ExposureTime,
                        GammaEnable=p.GammaEnable,
                        Gamma=p.Gamma,
                        Gain=p.Gain,
                    )
                    p.ExposureTime = flir.getValue(p.nodemap, "ExposureTime")
                    p.GammaEnable = flir.getValue(p.nodemap, "GammaEnable")
                    p.Gamma = flir.getValue(p.nodemap, "Gamma")
                    p.Gain = flir.getValue(p.nodemap, "Gain")

                    if p.Width is not None:
                        flir.setValue(p.nodemap, "Width", p.Width)
                    p.Width = flir.getValue(p.nodemap, "Width")

                    if p.Height is not None:
                        flir.setValue(p.nodemap, "Height", p.Height)
                    p.Height = flir.getValue(p.nodemap, "Height")

                    if p.OffsetX is not None:
                        flir.setValue(p.nodemap, "OffsetX", p.OffsetX)
                    p.OffsetX = flir.getValue(p.nodemap, "OffsetX")

                    if p.OffsetY is not None:
                        flir.setValue(p.nodemap, "OffsetY", p.OffsetY)
                    p.OffsetY = flir.getValue(p.nodemap, "OffsetY")

                    try:
                        p.Camera.BeginAcquisition()
                        p.started = True
                    except PySpin.SpinnakerException as ex:
                        logging.error("Could not begin acquisition ==> %s" % str(ex))
                else:
                    logging.warning("Communication with camera %i has not been established." % p.cameraId)
                p.restartAcquisition = False

            if p.connected and p.started:
                # Retrieve image from camera.
                try:
                    # fps calculation.
                    delta = time.time() - p.fpsStart
                    if p.fpsArray.size < p.fpsWindow * p.AcquisitionFrameRate:
                        p.fpsArray = np.hstack((p.fpsArray, delta))
                    else:
                        p.fpsArray[:-1] = p.fpsArray[1:]
                        p.fpsArray[-1] = delta
                    p.fpsStart = time.time()
                    flirImage = p.Camera.GetNextImage(int(p.grabTimeout * 1000))
                    if not flirImage.IsIncomplete():
                        if p.captureIndex % max(1, p.AcquisitionFrameRate // p.processFrequency) == 0:
                            image = flirImage.GetNDArray().copy()
                            with p.processLock:
                                p.image = image
                        data = flirImage.Convert(PySpin.PixelFormat_Mono8, PySpin.HQ_LINEAR)
                        if p.record:
                            p.recordingBuffer.put(data)
                            p.recordingCount += 1
                        with p.clipLock:
                            p.clipBuffer.append(data)
                        flirImage.Release()
                        p.failedCapture = None
                        p.captureIndex += 1
                except PySpin.SpinnakerException as ex:
                    msg = str(ex)
                    if p.failedCapture != msg:
                        p.failedCapture = msg
                        logging.error(msg)
                # Free-up space every so often from circular buffer .
                if p.captureIndex % max(1, p.AcquisitionFrameRate // p.bufferCropFrequency) == 0:
                    with p.clipLock:
                        n = len(p.clipBuffer) - math.ceil(p.MaxDuration * p.AcquisitionFrameRate)
                        if n > 0:
                            del p.clipBuffer[:n]



    def __process(self):
        p = self.__private
        while p.process:
            image = self.frame
            if image is None:
                time.sleep(0.001)
            else:
                height, width = image.shape
                # Test for motion.
                ksize = (round(p.BlurSize * height), round(p.BlurSize * width))
                ksize = (ksize[0] + 1 if ksize[0] % 2 == 0 else ksize[0], ksize[1] + 1 if ksize[1] % 2 == 0 else ksize[1])
                blurred = cv2.blur(src=image, ksize=ksize)
                change = p.background.apply(blurred).astype(bool) #shape = 1024x1280

                # Collapse height. A change for each x-pixel is reported when a proportion of y-pixels also change.
                line = change.sum(axis=0) > p.AreaProportion * height
                if p.lines.shape[0] < math.ceil(1 / 2 * p.processFrequency / p.SpeedThreshold):
                    p.lines = np.vstack((p.lines, line))
                    ready = False
                else:
                    p.lines[:-1] = p.lines[1:]
                    p.lines[-1] = line
                    p.trail = p.lines.any(axis=0)
                    ready = True

                if ready:
                    motionScore = p.trail.sum()
                    motionDuration = time.time() - p.motionStart
                    saveBuffer = False
                    if p.motionState == DetectionStates.Ended and motionScore > p.LocomotionThreshold * width:
                        # Acceleration: high-count-lines are pushed while low-count-lines are popped.
                        #logging.info("Motion started... ")
                        p.motionState = DetectionStates.Started
                        p.motionStart = time.time()
                        p.bufferFilename = self.generatePath("buffer")
                        p.publisher.invoke("buffering", self, p.bufferFilename, "start")
                    elif p.motionState == DetectionStates.Started and motionScore < p.QuiescenceThreshold * width:
                            # Deceleration: low-count-lines are pushed while high-count-lines are popped.
                            if motionDuration > p.MinDuration:
                                # Movement lasted enough.
                                saveBuffer = True
                            else:
                                logging.info("Too short! duration:%.2fs" % motionDuration)
                                p.publisher.invoke("buffering", self, p.bufferFilename, "cancel")
                            p.motionState = DetectionStates.Ended
                    elif p.motionState == DetectionStates.Started and motionDuration > p.MaxDuration:
                            # Movement has lasted long enough; force saveBuffer.
                            p.motionState = DetectionStates.Ended
                            saveBuffer = True
                    # Save on background.
                    if saveBuffer:
                        nFrames = math.ceil((time.time() - p.motionStart) * p.AcquisitionFrameRate)
                        message = "Motion criteria met! duration:%.2fs" % motionDuration
                        if p.armed:
                            with p.clipLock:
                                buffer = p.clipBuffer.copy()
                            Thread(target=self.__saveClipBuffer, args=(buffer, nFrames, p.bufferFilename, message)).start()
                            p.publisher.invoke("buffering", self, p.bufferFilename, "stop")
                        else:
                            message = "[not saved] %s" % message
                            logging.info(message)
                            self.__setMessage(message)

                if p.process:
                    time.sleep(1.0 / p.processFrequency)


    def set(self, **settings):
        p = self.__private
        settings = {key: value for key, value in settings.items() if key in p.public}
        return self.__set(**settings)


    def __set(self, block=True, **settings):
        p = self.__private
        restart = False
        success = True

        priority = []
        if {"OffsetX", "Width"} <= set(settings.keys()):
            if settings["OffsetX"] < p.OffsetX:
                priority.append("OffsetX")
            else:
                priority.append("Width")
        if {"OffsetY", "Height"} <= set(settings.keys()):
            if settings["OffsetX"] < p.OffsetX:
                priority.append("OffsetY")
            else:
                priority.append("Height")
        priority1 = {key: value for key, value in settings.items() if key in priority}
        priority2 = {key: value for key, value in settings.items() if key not in priority}

        for key, value in {**priority1, **priority2}.items():
            if value is not None:
                if value != getattr(p, key):
                    logging.info("Changing '{}' to '{}'".format(key, value))
                if key in ("LocomotionThreshold", "QuiescenceThreshold", "MinDuration", "MaxDuration", "AreaProportion", "BlurSize", "OutputQuality", "OutputFrameRate"):
                    p.set(key, value)
                if key in ("Folder", "Prefix"):
                    p.set(key, str(value))
                elif key == "SpeedThreshold":
                    p.set(key, value)
                    self.__resetBackground()
                elif key == "ExposureTime":
                    p.set(key, value)
                    success &= p.connected and flir.setValue(p.nodemap, "ExposureAuto", "Off")
                    success &= p.connected and flir.setValue(p.nodemap, key, value)
                elif key == "GammaEnable":
                    p.set(key, value)
                    success &= p.connected and flir.setValue(p.nodemap, "GammaEnable", value)
                elif key == "Gamma":
                    p.set(key, value)
                    success &= p.connected and flir.setValue(p.nodemap, key, value)
                elif key == "Gain":
                    p.set(key, value)
                    success &= p.connected and flir.setValue(p.nodemap, "GainAuto", "Off")
                    success &= p.connected and flir.setValue(p.nodemap, key, value)
                elif key in ("Width", "Height", "OffsetX", "OffsetY", "AcquisitionFrameRate"):
                    change = False
                    if flir.getValue(p.nodemap, key) != value:
                        if p.record:
                            logging.error("Cannot change '%s' while recording" % key)
                            success = False
                        else:
                            change = True
                    if change:
                        p.set(key, value)
                        restart = True
                        if key in ("Width", "Height"):
                            self.__resetBackground()
                        elif key == "AcquisitionFrameRate":
                            n = round(p.fpsWindow * p.AcquisitionFrameRate)
                            if p.fpsArray.size > n:
                                p.fpsArray = p.fpsArray[:p.fpsArray.size - n - 1]
                                
                p.publisher.invoke("assign", self, key, value)
        
        if restart:
            p.restartAcquisition = True
            while block and p.restartAcquisition:
                time.sleep(1e-6)
        return success


    def get(self, key):
        p = self.__private
        return getattr(p, key) if key in p.public else None


    def connect(self, block=True):
        p = self.__private
        p.connect = True
        while block and p.connect:
            time.sleep(1e-6)
        return self.connected


    @property
    def connected(self):
        p = self.__private
        return p.connected


    def restart(self, block=True):
        p = self.__private
        p.restartAcquisition = True
        while block and p.restartAcquisition:
            time.sleep(1e-6)
        return self.started


    def start(self, armed=True, block=True):
        self.arm(armed)
        return self.restart(block)


    @property
    def started(self):
        p = self.__private
        return p.started


    def show(self, **options):
        # Render-block execution; to be used without a client.
        p = self.__private
        if self.start():
            while self.frame is None:
                time.sleep(1e-6)
            render = True
            while render:
                image = self.frame
                capture.decorate(image, **options)
                cv2.imshow("image", image)
                key = cv2.waitKey(1000 // p.processFrequency) & 0xFF
                if key == ord('q'):
                    render = False


    def arm(self, state):
        p = self.__private
        p.armed = state


    @property
    def armed(self):
        p = self.__private
        return p.armed


    def record(self, state, filename=None):
        p = self.__private
        with p.commandsLock:
            if state == p.record:
                invoke = lambda: None
            else:
                if filename is None:
                    filename = self.generatePath("record")
                    
                if state:
                    options = PySpin.MJPGOption()
                    options.frameRate = p.OutputFrameRate
                    options.quality = p.OutputQuality
                    recorder = PySpin.SpinVideo()
                    try:
                        recorder.Open(filename, options)
                        success = True
                    except Exception as ex:
                        logging.error(str(ex))
                        success = False
                    if success:
                        p.commands.append(RecordSettings(recorder, filename))
                        p.record = True
                        invoke = lambda: p.publisher.invoke("recording", self, filename, "start")
                    else:
                        p.record = False
                        invoke = lambda: None
                else:
                    p.commands[-1].finish = p.recordingCount
                    p.record = False
                    invoke = lambda: p.publisher.invoke("recording", self, filename, "stop")
        invoke()
        return p.record


    @property
    def fps(self):
        p = self.__private
        average = p.fpsArray.mean()
        return 0 if average <= 0 else 1 / average
    

    def save(self, state, block=True):
        p = self.__private
        if state and not p.saveRecording:
            p.saveRecording = True
            p.saveRecordingThread = Thread(target=self.__saveRecording, args=())
            p.saveRecordingThread.start()
        elif p.saveRecording and not state:
            p.saveRecording = False
            if block:
                p.saveRecordingThread.join()
            
    
    @property
    def bufferSize(self):
        p = self.__private
        return p.recordingCount - p.savingCount


    def __saveRecording(self):
        p = self.__private
        
        while p.saveRecording:
            with p.commandsLock:
                if len(p.commands) == 0:
                    time.sleep(0.010)
                else:
                    command = p.commands[0]
                    
                    # Notify user about file start.
                    if command.once:
                        command.once = False
                        logging.info("Working on '%s'" % command.filename)
                    
                    # Move data from buffer to disk.
                    if not p.recordingBuffer.empty():
                        command.recorder.Append(p.recordingBuffer.get())
                        p.savingCount += 1
                        
                    # Notify user about file end.
                    if p.savingCount == command.finish:
                        logging.info("Saved '%s'" % command.filename)
                        command.recorder.Close()
                        del p.commands[0]
                    time.sleep(0.0001)


    def subscribe(self, callback, event):
        p = self.__private
        return p.publisher.subscribe(callback, event)


    def generatePath(self, option):
        p = self.__private
        tic = datetime.now().strftime("%Y%m%d%H%M%S%f")
        if option == "buffer":
            filename = str(Path("%s/%s-T%s" % (p.Folder, p.Prefix, tic)))
        else:
            filename = str(Path("%s/%s-C%s" % (p.Folder, p.Prefix, tic)))
        return filename


    def dispose(self):
        p = self.__private

        if p.processThread.is_alive():
            p.process = False
            p.processThread.join()

        if p.captureThread.is_alive():
            p.capture = False
            p.captureThread.join()
        
        self.save(False, block=True)
        
        with p.commandsLock:
            for command in p.commands:
                command.recorder.Close()
                logging.info("Saved '%s'" % command.filename)
            del p.commands[:]

        if p.connected:
            if p.Camera.IsStreaming():
                p.Camera.EndAcquisition()
            p.Camera.DeInit()
            del p.Camera
            p.flirSystem.ReleaseInstance()
            p.connected = False


    def __init__(self, cameraId=0, DeviceUserID=None):
        p = self.__private = Flexible()

        # Public settings.
        # Speed threshold to detect motion (length-proportion/s).
        p.SpeedThreshold = 2.00
        # Locomotion starts when the number of active x-pixels is larger than k * width.
        p.LocomotionThreshold = 0.05
        # Locomotion stops when the number of active x-pixels is smaller than k * width.
        p.QuiescenceThreshold = 0.01
        # Videos are not saved if they last less than k seconds.
        p.MinDuration = 0.70
        # Videos are split if they last longer than k seconds.
        p.MaxDuration = 3.00
        # Proportion of y-pixels required to activate an x-pixel.
        p.AreaProportion = 0.25
        # Misc.
        p.BlurSize = 0.1
        p.Folder = str(Path.cwd())
        p.Prefix = "WW"
        p.OutputQuality = 95
        p.OutputFrameRate = 30
        p.AcquisitionFrameRate = None
        p.ExposureTime = None
        p.GammaEnable = None
        p.Gamma = None
        p.Gain = None
        p.Width = None
        p.Height = None
        p.OffsetX = None
        p.OffsetY = None

        # Misc settings.
        p.fpsWindow = 5
        p.fpsArray = np.array([])
        p.fpsStart = time.time()
        p.grabTimeout = 1.0
        p.renderFrequency = 30
        p.processFrequency = 30
        p.bufferCropFrequency = 1

        # Motion state machine.
        p.motionStart = time.time()
        p.motionState = DetectionStates.Ended
        p.messageToc = 0
        p.message = [[], {}]
        p.bufferFilename = None
        
        # Misc.
        p.publisher = Publisher()
        p.fileCount = -1
        p.cameraId = cameraId
        p.DeviceUserID = DeviceUserID
        p.image = None
        p.trail = np.full(1, False) # width, False
        p.lines = np.empty((0, 1)) # 0, width
        p.failedCapture = None
        p.restartAcquisition = True
        p.armed = False
        p.started = False
        p.connect = False
        p.connected = False
        p.startTime = time.time() # !! not used

        # Buffering and async.
        p.processLock = Lock()
        p.commandsLock = Lock()
        p.clipLock = Lock()
        p.recordingBuffer = Queue()
        p.clipBuffer = list()
        
        # Allow delayed synchronization of saving continuously recorded data.
        p.captureIndex = 0
        p.recordingCount = 0
        p.savingCount = 0
        p.commands = list()
        p.savingState = False
        
        # User requests.
        p.saveRecording = False
        p.record = False
        
        # Start background threads.
        self.__resetBackground()
        p.capture = True
        p.captureThread = Thread(target=self.__capture, args=())
        p.captureThread.start()
        p.process = True
        p.processThread = Thread(target=self.__process, args=())
        p.processThread.start()

        # Set user parameters.
        p.public = list([
            "Camera",
            "SpeedThreshold",
            "LocomotionThreshold",
            "QuiescenceThreshold",
            "MinDuration",
            "MaxDuration",
            "AreaProportion",
            "BlurSize",
            "Folder",
            "Prefix",
            "OutputQuality",
            "OutputFrameRate",
            "AcquisitionFrameRate",
            "ExposureTime",
            "GammaEnable",
            "Gamma",
            "Gain",
            "Width",
            "Height",
            "OffsetX",
            "OffsetY"
        ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=Capture.__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument('--configuration', type=jsonFile, help="Configuration file in JSON format")
    args = parser.parse_args()

    settings = {}
    if args.configuration is not None:
        with open(args.configuration) as fid:
            settings = json.load(fid)
    capture = Capture()
    capture.set(**settings)
    capture.set(AcquisitionFrameRate=170, OutputFrameRate=170)

    signal.signal(signal.SIGINT, lambda sig, frame: capture.dispose())
    signal.signal(signal.SIGTERM, lambda sig, frame: capture.dispose())


    capture.show(message=True)
    capture.dispose()

    sys.exit(0)