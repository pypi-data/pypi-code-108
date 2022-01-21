# 2021-07-31. Leonardo Molina.
# 2022-01-21. Last modified.

from pathlib import Path
from PyQt5 import QtWidgets
from walkway.capture import Capture
from walkway.gui import GUI
from walkway.recorder import Recorder
from walkway.flexible import Flexible
import sys

def __onBuffering(devices, filename, state):
    if devices.recorder is not None:
        if state == "start":
            if devices.capture0.armed:
                devices.recorder.buffer(filename + ".flac")
        elif state == "cancel":
            devices.recorder.clearBuffer()
        elif state == "stop":
            devices.recorder.saveBuffer()
            

def __onRecording(devices, filename, state):
    if state == "start":
        if devices.recorder is not None:
            devices.recorder.record(filename + ".flac")
        if devices.capture1 is not None:
            devices.capture1.record(True, filename + "-top")
    elif state == "stop":
        if devices.recorder is not None:
            devices.recorder.saveRecording()
        if devices.capture1 is not None:
            devices.capture1.record(False)
            
    
def __onAssign(devices, key, value):
    if devices.recorder is not None:
        if key == "Folder":
            devices.capture1.set(Folder=value)
            devices.recorder.folder = value
        elif key == "Prefix":
            devices.recorder.prefix = value


def dispose(disposable):
    for d in disposable:
        d.dispose()


def errorDialog(message):
    if len(message) > 0:
        appContext = QtWidgets.QApplication([])
        dialog = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Critical, "Critical error", message, QtWidgets.QMessageBox.Ok, QtWidgets.QApplication.activeWindow())
        dialog.show()
        result = appContext.exec()


if __name__ == '__main__':
    devices = Flexible()
    disposable = []
    messages = []
    outputFolder = str(Path.home() / "Videos")
    
    # Try open microphone.
    try:
        recorder = Recorder("Pettersson")
        devices.recorder = recorder
        disposable.append(recorder)
        print("Audio recorder found")
    except Exception as ex:
        devices.recorder = None
        messages.append(str(ex))
        print(str(ex))
    
    # Try connecting to camera id 0.
    capture0 = Capture(DeviceUserID="bottom")
    if capture0.connect():
        appContext = QtWidgets.QApplication([])
        print("Primary camera connected")
        devices.capture0 = capture0
        disposable.append(capture0)
    else:
        capture0.dispose()
        devices.capture0 = None
        message = "Primary camera was not detected."
        messages.append(message)
        print(message)
    
    # Try connecting to camera id 1.
    capture1 = Capture(DeviceUserID="top")
    if capture1.connect():
        print("Secondary camera connected")
        devices.capture1 = capture1
        disposable.append(capture1)
        gui1 = GUI(capture=capture1, profile=(Path.home() / "Documents" / "WalwayExperiment-top.json"))
        print("GUI1 initialized")
        gui1.widgets["folder"].setEnabled(False)
        gui1.widgets["prefix"].setEnabled(False)
        gui1.widgets["record"].setEnabled(False)
        gui1.widgets["arm"].setEnabled(False)
        gui1.widgets["window"].setWindowTitle("Top camera")
    else:
        capture1.dispose()
        devices.capture1 = None
        gui1 = None
        message = "Secondary camera was not detected."
        messages.append(message)
        print(message)

    if devices.capture0 is not None:
        errorDialog('\n'.join("-%s" % message for message in messages))
        capture0.subscribe("buffering", lambda capture, filename, state: __onBuffering(devices, filename, state))
        capture0.subscribe("recording", lambda capture, filename, state: __onRecording(devices, filename, state))
        capture0.subscribe("assign", lambda capture, key, value: __onAssign(devices, key, value))
        capture0.set(Folder=outputFolder)
        gui0 = GUI(capture=capture0, profile=(Path.home() / "Documents" / "WalwayExperiment-bottom.json"))
        print("GUI0 initialized")
        gui0.widgets["window"].setWindowTitle("Bottom camera")
        gui0.show()
        if gui1 is not None:
            gui1.show()
        result = appContext.exec()
        dispose(disposable)
    else:
        dispose(disposable)
        errorDialog('\n'.join("-%s" % message for message in messages))
        result = -1
    sys.exit(result)