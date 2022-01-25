from .dobotedu import DobotEDU
from tkinter import ttk
from scipy.io.wavfile import write
from DobotRPC import loggers
from threading import Thread
import asyncio
import sys


def pass_run():
    pass


def hightlight(single_line):
    print(single_line)


loggers.set_use_console(False)
loggers.set_use_file(False)
loggers.set_level(loggers.DEBUG)

loop = asyncio.get_event_loop()
dobot_edu = DobotEDU()
dobotEdu = dobot_edu
magicbox = dobot_edu.magicbox
m_lite = dobot_edu.m_lite
dobot_magician = dobot_edu.magician
go = dobot_edu.magiciango
ocr = dobot_edu.ocr
nlp = dobot_edu.nlp
ai = dobot_edu.pyimageom
beta_go = dobot_edu.beta_go
speech = dobot_edu.speech
robot = dobot_edu.robot
util = dobot_edu.util
face = dobot_edu.face
tmt = dobot_edu.tmt

argv = sys.argv
if len(argv) == 4:
    dobot_edu.set_portname(argv[1])
    dobot_edu.token = (argv[2])
    dobot_edu.url = (argv[3])

    from .pause.pauseserver import pause_run, asyn_main
    dobot_edu.set_pause(pause_run)

    loop = asyncio.new_event_loop()
    thread = Thread(target=asyn_main, args=(loop, ))
    thread.setDaemon(True)
    thread.start()

else:
    dobot_edu.set_pause(pass_run)

# __all__ = ("DobotEDU")
