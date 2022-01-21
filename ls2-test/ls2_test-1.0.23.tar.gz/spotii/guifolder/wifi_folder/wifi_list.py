import os
import time
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi

import sys, os, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, currentdir)
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
grandparentdir =  os.path.dirname(parentdir)
sys.path.insert(0, grandparentdir)
g_g_parentdir = os.path.dirname(grandparentdir)
sys.path.insert(0, g_g_parentdir)

import title_rc
from main_paras import getMainTopLeft, queueForGui
import main_paras
from wifi_item import _WifiItem
import wifi_setting
import wifi_password

##for self.interface
##['Enabled', 'Connected', 'Dedicated', 'Wi-Fi']
##      0          1           2           3
class _WifiList(QtWidgets.QDialog):
    def __init__(self,parent=None):
        super(_WifiList, self).__init__(parent)
        loadUi(os.path.join(currentdir,'wifi_list.ui'),self)
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.interfaceMonitor)
        self.pollingTimer = QtCore.QTimer()
        self.pollingTimer.timeout.connect(self.inputPolling)
        
        self.config()
        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint  | QtCore.Qt.Popup)
#        flags = QtCore.Qt.WindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlags(flags)

    def closeEvent(self,event):
        print("_WifiList is closing")
        

    def config(self):
        try:

            
            self.interface = wifi_setting.wifiInterface()
            self.ssid = wifi_setting.wifiSsid()
            w_list=wifi_setting.wifiList()
            
            item= QtWidgets.QListWidgetItem()
            self.list.addItem(item)
            self.list.item(0).setForeground(QtCore.Qt.white)            
            if self.interface[0] == 'Enabled':
                self.list.item(0).setText(self.tr('Turn Off Wi-Fi'))
            else:
                self.list.item(0).setText(self.tr('Turn  On Wi-Fi'))
                w_list=[]

            print(self.interface)
            print(self.ssid)
            print(w_list)
            for each in w_list:
                item= QtWidgets.QListWidgetItem()
                self.list.addItem(item)
                element =_WifiItem()
                if each[0] == self.ssid:
                    self.name_highlight(element.name)
                    self.connected_item = item
                else:
                    self.name_normal(element.name)
                element.name.setText(each[0])
                if each[1] == 'Open':
                    element.security.setStyleSheet('.QLabel{background-image: url(:/wifi/wifi_folder/un_protected.png);background-color: transparent; border:0; color :white}')
                else:
                    element.security.setStyleSheet('.QLabel{background-image: url(:/wifi/wifi_folder/protected.png);background-color: transparent; border:0; color :white}')
                signal=float(each[2].strip('%'))
                if signal > 75:
                    icon = 4
                elif signal > 50:
                    icon = 3
                elif signal > 25:
                    icon = 2
                elif signal > 5:
                    icon = 1
                else:
                    icon = 0
                element.signal.setStyleSheet('.QLabel{background-image: url(:/wifi/wifi_folder/wi-fi_'+str(icon)+'.png);background-color: transparent; border:0; color :white}')
                self.list.setItemWidget(item,element)
            self.list.itemClicked.connect(self.item_click_hook)
        except Exception as error:
            print(error)

    def name_highlight(self, name):
        name.setStyleSheet('.QLabel{background-color: transparent; border:0; color : rgb(248,176,0)}')
        
    def name_normal(self, name):
        name.setStyleSheet('.QLabel{background-color: transparent; border:0; color :white}')
        
    def item_click_hook(self,item):
        try:
            index = self.list.row(item)
            print(index)
            if index == 0: ## Turn on/off
                if self.interface[0] == 'Enabled':
                    #queueForGui.put('turn off wifi')
                    print('turn off wifi')
                    wifi_setting.wifiTurnOff(self.interface[3])
                    self.timer.start(1000)
                else:
                    #queueForGui.put('turn on wifi')
                    print('turn on wifi')
                    wifi_setting.wifiTurnOn(self.interface[3])
                    self.timer.start(6000)
            else:
                newWifiName=self.list.itemWidget(item).name
                global popUp
                popUp = wifi_password._WifiPassword()
                x,y = getMainTopLeft()
                popUp.setName(newWifiName.text())
                popUp.move(x,y)
                popUp.show()
                #print(self.list.itemWidget(item).name.text())
                #print('current connected', self.list.itemWidget(self.connected_item).name.text())
#                 try:
#                     self.name_normal(self.list.itemWidget(self.connected_item).name)
#                 except Exception as err:
#                     print(err)
# 
#                 newWifiName=self.list.itemWidget(item).name
#                 if wifi_setting.wifiConnect(newWifiName.text()):
#                     self.connected_item = item
#                     self.name_highlight(self.list.itemWidget(item).name)
#                 else:
#                     global popUp
#                     popUp = wifi_password._WifiPassword()
#                     x,y = getMainTopLeft()
#                     popUp.setName(newWifiName.text())
#                     popUp.move(x,y)
#                     popUp.show()
#                     main_paras.type_in_que.clear()
#                     self.pollingTimer.start(200)
#                         isSet, newPsw = popUp.result()
#                         if isSet:
#                             print(isSet, newPsw)
#                             if wifi_setting.wifiConnect(newWifiName.text(),newPsw):
#                                 self.connected_item = item
#                                 self.name_highlight(self.list.itemWidget(item).name)
#                                 break;
#                             else:
#                                 popUp = _WrongPassword()
#                                 x,y = getMainTopLeft()
#                                 popUp.move(x,y)
#                                 popUp.exec()
#                         else:
#                             break;
        except Exception as error:
            print(error)
            
            
    
    def interfaceMonitor(self):
        try:
            newState=wifi_setting.wifiInterface()
            print(newState)
            if newState == None:
                print('interfaceMonitor','wrong!')
                self.timer.stop()
                main_paras.guiNotify(WIFI_CHECKING_INDEX)
            
            if(newState[0]!=self.interface[0]):
                print('state changed')
                self.timer.stop()
                self.inerface = newState
                self.list.clear()
                main_paras.guiNotify(WIFI_CHECKING_INDEX)
                self.config()
        except Exception as e:
            print('interfaceMonitor',e)
            
    def inputPolling(self):
        try:
            inputValue = main_paras.type_in_que.get()
            if inputValue!=None:                
                print(inputValue)
#                 if isSet:
#                     print(isSet, newPsw)
#                     if wifi_setting.wifiConnect(newWifiName.text(),newPsw):
#                         self.connected_item = item
#                         self.name_highlight(self.list.itemWidget(item).name)
#                         break;
#                     else:
#                         popUp = _WrongPassword()
#                         x,y = getMainTopLeft()
#                         popUp.move(x,y)
#                         popUp.exec()
#                 else:
#                     break;
                
                self.pollingTimer.stop()
                self.list.clear()
                self.config()
        except Exception as e:
            print('inputPolling',e)

if __name__ == "__main__":
    from PyQt5.QtCore import QTranslator
    import sys
##    trans=QTranslator()
##    trans.load("setting_wrap.qm")
    

    
    app = QtWidgets.QApplication(sys.argv)
##    app.installTranslator(trans)

    QtWidgets.QMainWindow
    window=_WifiList()
    window.show()
    
    
    rtn= app.exec_()
    print('main app return', rtn)
    sys.exit(rtn)
