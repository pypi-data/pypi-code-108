import subprocess
import threading
from gpiozero import Button

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
#sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from define import *
import main_paras
from on_off.mainboard_pio import fanFullSpeedOn
powerButton = Button(POWER_BUTTON_PIN,True,None,None,POWER_BUTTON_HOLD_TIME)
def shutDown():
    print("shut down now")
    subprocess.Popen(['shutdown','-h','now'])

class OnOffThread (threading.Thread):
    def __init__(self, threadID, name):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name

    def run (self):
        cmd = 'cat /proc/cpuinfo | grep Serial | cut -d \' \' -f 2'
        main_paras.serial='LS2-'+subprocess.check_output([cmd], shell=True).decode("utf-8")
        main_paras.serial = main_paras.serial.replace('\n','')
        print(main_paras.serial)
        
        powerButton.when_held=shutDown #takePhoto
        fanFullSpeedOn()
            
if __name__ == "__main__":
    OnOff      =OnOffThread(4,"OnOff")

    OnOff.start()
