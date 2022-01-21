# -*- coding: utf-8 -*-
import queue
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
print('current dir',currentdir)
print('parent dir', parentdir)
sys.path.insert(0, currentdir)

from define import *
from communication.communication import CommunicationThread
from on_off.on_off import OnOffThread
from test_handler.test_chip_handler import TestChipHandlerThread
from vkeyboard import handleVisibleChanged
LOCAL_LAUCHER_FOLDER = '/home/pi/app/spotii/launcher'
LOCAL_LAUCHER_CHK_FILE = LOCAL_LAUCHER_FOLDER+'/chk_sum.md5'
DESK_TOP = '/home/pi/Desktop'
def preStart():
    try:
        import shutil
        os.makedirs(LOCAL_LAUCHER_FOLDER, exist_ok =True)
        os.makedirs(IMG_PATH, exist_ok =True)
        
        lib_path = os.path.dirname(__file__)
        
        
        print('main directory:', lib_path)
        if lib_path == '':
            pass
        else:
            upgrade_launcher = False
            if os.path.exists(LOCAL_LAUCHER_CHK_FILE):
                with open(lib_path+'/launcher/'+'chk_sum.md5',"rb") as lib_file:
                    lib_check_sum=lib_file.read()
                    print('lib check sum ',lib_check_sum)
                with open(LOCAL_LAUCHER_CHK_FILE,"rb") as local_file:
                    local_check_sum=local_file.read()
                    print('local check sum ',local_check_sum)
                if lib_check_sum != local_check_sum:
                    upgrade_launcher = True
            else:
                upgrade_launcher = True
                
            if upgrade_launcher:
                print('upgrading launcher..')
                src=os.path.join(lib_path,'launcher')
                for item in os.listdir(src):
                    #print(item)
                    if item.endswith('.sh'):
                        print('Copying to deskTop', item)
                        shutil.copy(os.path.join(src, item), os.path.join(DESK_TOP, item))
                    elif item.endswith('.py') or item.endswith('.md5'):
                        print('Copying to local laucher folder',item)
                        shutil.copy(os.path.join(src, item), os.path.join(LOCAL_LAUCHER_FOLDER, item))
    except Exception as e:
        print(e)

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from guifolder.gui import MainWindow
from main_paras import queueForGui, queueForResult, queueForCom

def spot_main():
    preStart()    
    Comm       =CommunicationThread(2,"Comm",queueForCom, queueForResult)
    TestMonitor=TestChipHandlerThread(3,"TCH",queueForCom, queueForGui, queueForResult)
    OnOff      =OnOffThread(4,"OnOff")

    Comm.start()
    OnOff.start()
    TestMonitor.start()

    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
    window=MainWindow(qForGui = queueForGui)
    print('-- main window loaded --')
    rtn= app.exec_()
    print('main app return', rtn)
    print("App end.")
    queueForResult.put(CLOSE_NOW)
    queueForCom.put(CLOSE_NOW)
    TestMonitor.join()

    sys.exit(rtn)
    
if __name__ == "__main__":
    
    spot_main()
