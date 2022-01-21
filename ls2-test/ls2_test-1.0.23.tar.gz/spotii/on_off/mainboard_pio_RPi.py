import RPi.GPIO as GPIO
import time

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

from define import *

#GPIO.cleanup()
GPIO.setmode(GPIO.BCM)
GPIO.setup(FAN_PWM_PIN, GPIO.OUT)

fan = GPIO.PWM(FAN_PWM_PIN, 1000)

fan.start(47)
#fan.stop()
# def fanTurnOn(on):
#     global fan
#     if on:
#         fan.ChangeDutyCycle(50)
#     else:
#         fan.stop()
#     
#     
# if __name__ == "__main__":
#     print('on')
#     fanTurnOn(True)
#     time.sleep(10)
#     print('off')
#     fanTurnOn(False)
#     time.sleep(10)
#     print('on')
#     fanTurnOn(True)
#     time.sleep(10)
#     print('off')
#     fanTurnOn(False)

    
   
    
