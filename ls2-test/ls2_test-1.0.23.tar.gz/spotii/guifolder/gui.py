import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QTranslator

from PyQt5.uic import loadUi
import pathlib
import queue
import time
import subprocess

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)

sys.path.insert(0, parentdir)
sys.path.insert(0, currentdir)

from MyToolButton import MyToolButton
from MyStackedWidget import MyStackedWidget
import title_rc
from profile_folder.profile_wrap import _ProfileDialog
from help_folder.help_wrap import  _HelpDialog
from setting_folder.setting_wrap import _SettingDialog
from wifi_folder.wifi_list import _WifiList
from wifi_folder import wifi_setting
from volume.volume import _Volume
from define import *
from main_paras import setMainTopLeft, getMainTopLeft, mainChannelStart, setDetectionMode, getDetectionMode, queueForGui
import main_paras
from wrong_password import _WrongPassword
from vkeyboard import handleVisibleChanged
if sys.platform == 'linux':
    from  on_off.mainboard_pio import fanTurnOn
    #from  on_off.mainbaord_pio import hub_reset
currentPath=pathlib.Path(__file__).parent.absolute()




class EmitThread(QtCore.QThread):
    signal= QtCore.pyqtSignal(object)
    def __init__(self, sharedQue):
        QtCore.QThread.__init__(self)
        self.qForGui=sharedQue
    def run(self):
        print("Start emit thread")
        while True:
            try:
                qItem=self.qForGui.get()
                print('in gui', qItem)
                self.signal.emit(qItem)
                self.qForGui.task_done()
            except Exception as e:
                 print(e)
        
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None, qForGui=None):
        super(MainWindow, self).__init__(parent)
        self.trans=QTranslator()
#        QtWidgets.QApplication.instance().removeTranslator(trans)
        print( main_paras.info.show())
        print('language: ', main_paras.info.getCurrentLanguage())        
        language_qm = os.path.join(parentdir,main_paras.defaultLanguageFolder,main_paras.info.getCurrentLanguage(),'lng.qm')
        self.trans.load(language_qm)
        QtWidgets.QApplication.instance().installTranslator(self.trans)

        
        emitThread = EmitThread(qForGui)
        emitThread.signal.connect(self.emitHook)
        emitThread.start()
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint)
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)
        loadUi(os.path.join(currentPath,'spotii.ui'),self)
        self.tempPolling = QtCore.QTimer()
        self.tempPolling.timeout.connect(self.tempMonitor)
        self.time = QtCore.QTimer()
        self.time.timeout.connect(self.showTime)

        self.currentWifi = '__lp_ls2_nothing__'

        self.page=0
        self.slots = []
        self.allIcons = []
        main_paras.setAllDefault()
        self.config()
        self.show()
        
        
    def tempMonitor(self):

        self.wifiChecking()
        if sys.platform == 'linux':
            try:
                result=subprocess.check_output(['vcgencmd','measure_temp']).decode("utf-8")
                tmp=int(float(result.split('=')[1].split('\'')[0]))
                #print(tmp)
                #fanTurnOn(False)
                if tmp > TEMP_ON_VALUE:
                    fanTurnOn(True)
                elif tmp < TEMP_OFF_VALUE:
                    fanTurnOn(False)
                
            except Exception as error:
                print(error)
                
    def showTime(self):
        try:
            
##            # getting current time
##            current_time = QtCore.QTime.currentTime()
##      
##            # converting QTime object to string
##            label_time = current_time.toString('hh:mm')

            label_time = time.strftime('%H:%M')
      
            # showing it to the label
            self.time_label.setText(label_time)
            
        except Exception as error:
            print(error)
        
        
    def config(self):
        try:
            slot_no = 0
            self.slots = self.findChildren(QtWidgets.QStackedWidget)
            for each in self.slots:
                each.setCurrentIndex(0)
                each.setSlotNo(slot_no)
                slot_no+=1
#                self.slots.append(Ui_Slot(slot))
                #self.slots.append(slot)

            
            self.allIcons = self.title.findChildren(QtWidgets.QToolButton)
            for icon in self.allIcons:
                icon.setCursor(QtGui.QCursor(QtCore.Qt.PointingHandCursor))

            
            self.test_mode.clicked.connect(self.test_mode_hook)

            print ('testing mode:', main_paras.info.getTestMode())

            if main_paras.info.getTestMode() == TEST_MODE_SPEED:
                self.test_mode.setText(self.tr('SPEED'))
            else:
                self.test_mode.setText(self.tr('NORMAL'))

            #self.help.clicked.connect(self.helpHookForTest)
            
            mainChannelStart(self.mainChannelHook)
            #self.chip_mode.setText(self.tr(getDetectionMode()))
            QtCore.QTimer.singleShot(0, self.setupAferUi)

            self.wifiChecking()
            self.time.start(1000)
            self.tempPolling.start(10000)
            
            if sys.platform == 'linux':
                try:
                    result=subprocess.check_output(['sudo','chmod','777','/home/pi/app/spotii/profile.json']).decode("utf-8")
                    
                except Exception as error:
                    print(error)
            
            
        except Exception as error:
            print(error)

    def wifiChecking(self):
        wifi_ssid = wifi_setting.wifiSsid()
        #print('ssid: ',wifi_ssid)
        if  self.currentWifi != wifi_ssid:
            icon = QtGui.QIcon()
            if wifi_ssid == None:
                main_paras.setWifiStatus(False)
                print('set to invalid')
                icon.addPixmap(QtGui.QPixmap(":/wifi/png/title/spot-icons-wifi-invalid.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
                icon.addPixmap(QtGui.QPixmap(":/wifi/png/title/spot-icons-wifi-invalid.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
            else:
                main_paras.setWifiStatus(True)
                print('set to normal')
                icon.addPixmap(QtGui.QPixmap(":/wifi/png/title/spot-icons-wifi-inactive.png"), QtGui.QIcon.Active, QtGui.QIcon.Off)
                icon.addPixmap(QtGui.QPixmap(":/wifi/png/title/spot-icons-wifi-active.png"), QtGui.QIcon.Active, QtGui.QIcon.On)
            self.wifi.setIcon(icon)
            self.wifi.repaint()
            self.currentWifi = wifi_ssid
        
    def test_mode_hook(self):
        try:
            if not self.test_mode.isChecked():
                self.test_mode.setText(self.tr('NORMAL'))
                main_paras.info.setTestMode(TEST_MODE_NORMAL)
            else:
                self.test_mode.setText(self.tr('SPEED'))
                main_paras.info.setTestMode(TEST_MODE_SPEED)
        except Exception as e:
            print(e)

    def mainChannelHook(self,item):
        try:
            print('main Channel', item)
            if   item == MAIN_PARA_CASSETTE_TYPE_CHIP:
                self.chip_mode.setText(self.tr('AUTO MODE'))
                setDetectionMode(CASSETTE_DETECTION_MODE_AUTO)
                for each in self.slots:
                    each.setStatus(SLOT_STATUS_EMPTY, '')
            elif item == MAIN_PARA_CASSETTE_TYPE_QR:
                self.chip_mode.setText(self.tr('MANUAL MODE'))
                setDetectionMode(CASSETTE_DETECTION_MODE_MANUAL)
                for each in self.slots:
                    each.setStatus(SLOT_STATUS_SCAN, '')
        except Exception as e:
            print(e)

    def quitHook(self):
        print('will quit')
        #QtWidgets.qApp.quit()
        self.close()


    def setupAferUi(self):
        try:
            x = self.geometry().x()
            y = self.geometry().y()
            print('main x, y', x, y)
            setMainTopLeft(x, y)
            
            main_x, main_y =getMainTopLeft()
            self.help.setup(_HelpDialog, main_x, main_y)
            self.wifi.setup(_WifiList, main_x+205, main_y-7)
            self.volume.setup(_Volume, main_x+255, main_y-7)
            self.setting.setup(_SettingDialog, main_x+313, main_y-7)
            self.profile_icon.setup(_ProfileDialog, main_x+345, main_y-7)

##            self.wifi.setup(_WifiList, main_x+225, main_y-7)
##            self.volume.setup(_Volume, main_x+275, main_y-7)
##            self.setting.setup(_SettingDialog, main_x+325, main_y-7)
##            self.profile_icon.setup(_ProfileDialog, main_x+357, main_y-7)
            
        except Exception as e:
            print(e)
        
    def helpHookForTest(self):
        try:
            print('help test')

            self.page= (self.page+1) %self.slots[0].totalPage()
            for index in range(0,5):                
                self.slots[index].setStatus(self.page,'La0456789')
        except Exception as e:
            print(e)

    
    def emitHook(self,item):
        try:
            print(time.strftime('%Y%m%d%H%M%S'),"emitHook:",item)
            slotNo  = item[0]
            errCode = item[1]
            qrCode  = item[2]
            global popUp
            if slotNo == SIGN_IN_FIRST_INDEX:
                
                popUp = _WrongPassword()
                popUp.setMessage(self.tr("Sign in and enter basic test information."),self.tr('Ok'))
                x,y = getMainTopLeft()
                popUp.move(x,y)
                popUp.show()

##            elif slotNo == CHECK_NETWORK_INDEX:
##                
##                popUp = _WrongPassword()
##                popUp.setMessage(self.tr("Check network."),self.tr('Try again'))
##                x,y = getMainTopLeft()
##                popUp.move(x,y)
##                popUp.show()

            elif slotNo == LANGUAGE_CHANGE_INDEX:
                print('LANGUAGE_CHANGE_INDEX')
                self.language_change()
                
            elif slotNo == WIFI_CHECKING_INDEX:
                print('WIFI_CHECKING_INDEX')
                self.wifiChecking()
                
            elif slotNo == NON_SLOT_INDEX:
                for i in range(TOTAL_SLOTS):
                    self.slots[i].setStatus(SLOT_STATUS_WARNING, 'Checking...')
            elif errCode == DEVICE_STATE_TAKING_PHOTO:
                self.slots[item[0]].detecting_(qrCode)
                
            elif errCode == DEVICE_STATE_MANUAL_SCAN:
                self.slots[item[0]].setStatus(SLOT_STATUS_SCAN, qrCode)
            elif errCode == DEVICE_STATE_MANUAL_FLIP:
                self.slots[item[0]].setStatus(SLOT_STATUS_FLIP, qrCode)
            elif errCode == DEVICE_STATE_MANUAL_INVALID_QR:
                self.slots[item[0]].setStatus(SLOT_STATUS_INVALID_QR, qrCode)
            elif errCode == Positive_test_result:
                self.slots[item[0]].setStatus(SLOT_STATUS_POSITIVE, qrCode)
            elif errCode == Negative_test_result:
                self.slots[item[0]].setStatus(SLOT_STATUS_NEGATIVE, qrCode)
            elif errCode == Invalid_image_identifier:
                self.slots[item[0]].setStatus(SLOT_STATUS_INVALID, qrCode)
            elif errCode == DEVICE_STATE_CASSETTE_EMPTY:
                self.slots[item[0]].setStatus(SLOT_STATUS_EMPTY, qrCode)
            else:
                self.slots[item[0]].setStatus(SLOT_STATUS_WARNING, qrCode)
        except Exception as e:
            print('emitHook',e)
        
    def closeEvent(self,event):
        self.tempPolling.stop()
        if sys.platform == 'linux':
            fanTurnOn(False)
        
        print("Main window is closing")

    def language_change(self):

##        QtWidgets.QApplication.instance().removeTranslator(self.trans)
##        trans.load(os.path.join(parentdir,"en-zh-cn.qm"))
##        QtWidgets.QApplication.instance().installTranslator(trans)
        self.close()
        self.__init__(qForGui = queueForGui)
        print('main gui repaint done')
        
        
    
if __name__ == "__main__":
    import sys

    ##main_paras.languageInit()
    
    print(QtWidgets.qApp)
#     if(QtWidgets.qApp.focusWindow().isModal()):
#         pass
#            qGuiApp->focusWindow()->setModality(Qt::WindowModal);
    os.environ["QT_IM_MODULE"] = "qtvirtualkeyboard"

    
#    trans=QTranslator()
#    trans.load(os.path.join(parentdir,"en.qm"))
#    trans.load(os.path.join(parentdir,"en-jp.qm"))
    
    app = QtWidgets.QApplication(sys.argv)
    QtGui.QGuiApplication.inputMethod().visibleChanged.connect(handleVisibleChanged)
#    app.installTranslator(trans)
    
    window=MainWindow(qForGui = queueForGui)
    rtn= app.exec_()
    print('main app return', rtn)
    window.close()
    sys.exit(rtn)
