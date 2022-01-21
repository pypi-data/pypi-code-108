import os
import sys

import time
import subprocess

from wifi import Cell, Scheme
print (list(Cell.all('wlan0')))

def connect_wifi_linux(ssid, key):
    subprocess.check_output(["sudo su"],shell=True)
    cell=list(Cell.all('wlan0'))[0]
    scheme =Scheme.for_cell('wlan0', 'home', cell, key)
    scheme.save()
    scheme.activate()
    
    
if __name__ == "__main__":
    connect_wifi_linux('TP-Link_LP24', 'DaReLoVe501')