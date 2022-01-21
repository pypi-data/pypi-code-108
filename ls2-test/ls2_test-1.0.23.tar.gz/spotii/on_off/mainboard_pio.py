import RPi.GPIO as GPIO
from gpiozero import Button
from gpiozero import LED, PWMLED
import time

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from define import *



#fan=LED(FAN_PWM_PIN, active_high=False, initial_value=True)
fan=PWMLED(FAN_PWM_PIN, active_high=False, initial_value=0, frequency = 300)
hub_reset=LED(HUB_RST_PIN, initial_value=1)

def fanTurnOn(on):
    global fan
    if on:
        fan.value=0.88
    else:
        fan.value=0
def fanFullSpeedOn():
    global fan
    fan.value=1
    
    
    
if __name__ == "__main__":
    print('on')
    fanTurnOn(True)
    time.sleep(10)
    print('off')
    fanTurnOn(False)
    time.sleep(10)
    print('on')
    fanTurnOn(True)
    time.sleep(10)
    print('off')
    fanTurnOn(False)

    
   
    
