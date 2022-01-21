# -*- coding: utf-8 -*-
import PyQt5
from PyQt5.QtCore import QTranslator

import queue
import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
print('current dir',currentdir)
print('parent dir', parentdir)
sys.path.insert(0, currentdir)
import subprocess
from define import *
from communication.communication import CommunicationThread
from off_line_handler.off_line import OffLineDetectionThread
if sys.platform == 'linux':
    from on_off.on_off import OnOffThread
    from test_handler.test_chip_handler import TestChipHandlerThread
elif sys.platform == 'win32':
    from win_test_handler.test_chip_handler import TestChipHandlerThread
from vkeyboard import handleVisibleChanged
LOCAL_LAUCHER_FOLDER = '/home/pi/app/spotii/launcher'
PROFILE_FOLDER = '/home/pi/app/spotii'
LOCAL_LAUCHER_CHK_FILE = LOCAL_LAUCHER_FOLDER+'/chk_sum.md5'
DESK_TOP = '/home/pi/Desktop'
def preStart():
    try:
        import shutil
        os.makedirs(LOCAL_LAUCHER_FOLDER, exist_ok =True)
        os.makedirs(IMG_PATH, exist_ok =True)

#         cmd = 'chmod +w '+PROFILE_FOLDER
#         subprocess.call([cmd],shell=True)

        try:
            upgrade=subprocess.check_output(['pip3','show','pytz','--disable-pip-version-check']).decode("utf-8")
            print(upgrade)
        except Exception as e:
            print('pytz show exception: ',e)
            try:
                upgrade=subprocess.check_output(['pip3','install','pytz','--disable-pip-version-check']).decode("utf-8")
                print(upgrade)
            except Exception as e:
                print('pytz install exception:',e)                


        lib_path = os.path.dirname(__file__)
        
#        lib_path = '/home/pi/gxf/python/spotii_project/spotii'
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
                        target = os.path.join(DESK_TOP, item)
                        shutil.copy(os.path.join(src, item), target)
                        cmd = 'chmod 777 '+target
                        subprocess.call([cmd],shell=True)
                    elif item.endswith('.py') or item.endswith('.md5') or item.endswith('.ui') or item.endswith('.mp4') or item.endswith('.html'):
                        print('Copying to local laucher folder',item)
                        shutil.copy(os.path.join(src, item), os.path.join(LOCAL_LAUCHER_FOLDER, item))
    except Exception as e:
        print(e)

import sys
import os
from PyQt5 import QtCore, QtGui, QtWidgets


def start():
    from guifolder.gui import MainWindow
    from main_paras import queueForGui, queueForResult, queueForCom, queueForOffLine    
    import main_paras
    
    if sys.platform == 'linux':
        OnOff      =OnOffThread(4,"OnOff")
        OnOff.start()
    TestMonitor=TestChipHandlerThread(3,"TCH",queueForCom, queueForGui, queueForResult)
    TestMonitor.start()
    Comm       =CommunicationThread(2,"Comm",queueForCom, queueForResult)
    Comm.start()

    OffLineMonitor = OffLineDetectionThread(5,"OffLine")
    OffLineMonitor.start()
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    ##main_paras.languageInit()

    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
    window=MainWindow(qForGui = queueForGui)
    
    rtn= app.exec_()
    print('main app return', rtn)
    print("App end.")
    queueForResult.put(CLOSE_NOW)
    queueForCom.put(CLOSE_NOW)
    queueForOffLine.put(CLOSE_NOW)
    TestMonitor.join()
    window.close()
    sys.exit(rtn)

def spot_main():
    if sys.platform == 'linux':
        preStart()
    start()
    
if __name__ == "__main__":
    spot_main()
