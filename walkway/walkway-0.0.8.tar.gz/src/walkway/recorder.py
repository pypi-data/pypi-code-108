# 2021-10-03. Leonardo Molina.
# 2021-10-12. Last modified.

from datetime import datetime
from pathlib import Path
from threading import Lock, Thread
from walkway.flexible import Flexible

import logging
import sounddevice as sd
import soundfile as sf
import sys
import time

class Recorder:
    def __onInput(self, data, frames, time, status):
        p = self.__private
        with p.recordingLock:
            if p.recording:
                p.recordingFile.write(data.copy())
        with p.bufferLock:
            if p.buffering:
                p.buffer.append(data.copy())
                
    
    def __start(self):
        p = self.__private
        if not p.acquiring and (p.recording or p.buffering):
            p.acquiring = True
            p.stream.start()
    
    
    def __stop(self):
        p = self.__private
        if p.acquiring and not p.recording and not p.buffering:
            p.acquiring = False
            p.stream.stop()
    
    
    @property
    def folder(self):
        p = self.__private
        return p.folder
    
    
    @folder.setter
    def folder(self, folder):
        p = self.__private
        with p.recordingLock:
            with p.bufferLock:
                p.folder = folder
            
    
    @property
    def prefix(self):
        p = self.__private
        return p.prefix
    
    
    @prefix.setter
    def prefix(self, prefix):
        p = self.__private
        with p.recordingLock:
            with p.bufferLock:
                p.prefix = prefix
    
    
    def record(self, filename=None):
        p = self.__private
        with p.recordingLock:
            if not p.recording:
                if filename is None:
                    filename = self.generatePath("record")
                p.recordingFilename = filename
                try:
                    p.recordingFile = sf.SoundFile(filename, mode='x', samplerate=p.samplerate, channels=p.channels)
                    success = True
                except Exception as ex:
                    logging.error(str(ex))
                    success = False
                if success:
                    logging.info("Recording continously to '%s'" % p.recordingFilename)
                    p.recording = True
                else:
                    p.recording = False
        if p.recording:
            self.__start()
        
    
    def saveRecording(self):
        p = self.__private
        with p.recordingLock:
            if p.recording:
                p.recording = False
                p.recordingFile.close()
                logging.info("Saved '%s'" % p.recordingFilename)
        self.__stop()
    
    
    def buffer(self, filename=None):
        p = self.__private
        with p.bufferLock:
            if not p.buffering:
                p.buffering = True
                if filename is None:
                    filename = self.generatePath("buffer")
                p.bufferFilename = filename
        self.__start()
        
    
    def saveBuffer(self):
        p = self.__private
        with p.bufferLock:
            if p.buffering:
                p.buffering = False
                buffer = p.buffer.copy()
                p.buffer.clear()
                Thread(target=self.__saveBuffer, args=(buffer, p.bufferFilename)).start()
        self.__stop()
        
        
    def __saveBuffer(self, buffer, filename, message=""):
        p = self.__private
        try:
            file = sf.SoundFile(filename, mode='x', samplerate=p.samplerate, channels=p.channels)
            success = True
        except Exception as  ex:
            logging.error(str(ex))
            success = False
        if success:
            p.fileCount += 1
            logging.info("[audio #%i] %s" % (p.fileCount, message))
            for data in buffer:
                file.write(data)
    
    
    def clearBuffer(self):
        p = self.__private
        with p.bufferLock:
            p.buffering = False
            p.buffer.clear()
        self.__stop()
        
        
    def generatePath(self, option):
        p = self.__private
        tic = datetime.now().strftime("%Y%m%d%H%M%S%f")
        if option == "buffer":
            filename = str(Path("%s/%s-T%s.flac" % (p.folder, p.prefix, tic)))
        else:
            filename = str(Path("%s/%s-C%s.flac" % (p.folder, p.prefix, tic)))
        return filename
    
    
    def dispose(self):
        p = self.__private
        self.clearBuffer()
        self.saveRecording()
        p.stream.stop()
        p.stream.close()
    
        
    def __init__(self, device=None, **options):
        p = self.__private = Flexible()
        
        # State variables.
        p.fileCount = -1
        p.buffer = list()
        p.acquiring = False
        p.buffering = False
        p.recording = False
        p.bufferLock = Lock()
        p.recordingLock = Lock()
        p.bufferFilename = None
        p.recordingFilename = None
        p.recordingFile = None
        p.startTime = time.time()
        
        # Settings.
        p.folder = str(Path.cwd())
        p.prefix = "WW"
        
        options = {key: value for key, value in options.items() if key not in ("device", "callback")}
        
        if isinstance(device, str):
            # Find text matches.
            name = device.lower()
            
            # Get api name for each device.
            devices = sd.query_devices()
            nDevices = len(devices)
            hostapis = sd.query_hostapis()
            for d in range(nDevices):
                index = devices[d]["hostapi"]
                devices[d]["hostapi"] = hostapis[index]["name"]
            
            # Sort according to best API.
            inputs = []
            for priority in ("Windows WASAPI", "Windows DirectSound", "MME"):
                for (index, item) in enumerate(devices):
                    if item["name"].lower().find(name) >= 0 and item["max_input_channels"] > 0 and item["hostapi"] == priority:
                        item["id"] = index
                        inputs.append(item)
            
            # Get best in list.
            if len(inputs) >  0:
                index = inputs[0]["id"]
                if "samplerate" not in options.keys():
                    options["samplerate"] = devices[index]["default_samplerate"]
                p.stream = sd.InputStream(device=index, callback=self.__onInput, **options)
                success = True
            else:
                name = device
                device = None
                try:
                    p.stream = sd.InputStream(device=name, callback=self.__onInput, **options)
                except Exception as ex:
                    logging.error("Could not load device '%s' ==> %s" % (name, str(ex)))
                    raise ex
        else:
            try:
                p.stream = sd.InputStream(device=device, callback=self.__onInput, **options)
            except Exception as ex:
                logging.error(str(ex))
                raise ex
        
        p.samplerate = round(p.stream.samplerate)
        p.channels = p.stream.channels
        
            
if __name__ == "__main__":
    recorder = Recorder()
    print("Started")
    recorder.prefix = "TEST"
    recorder.folder = str(Path.home())
    for i in range(3):
        recorder.record()
        recorder.buffer()
        time.sleep(1)
        recorder.saveRecording()
        recorder.saveBuffer()
    recorder.dispose()
    print("Finished")