
from PyQt5.QtWidgets import QDialog, QApplication
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from ipportdialog import *

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import  QTreeWidgetItem, QTreeWidget
from stdcomqt5 import *
from stdcomqt5treeewidget import *

import re, sys

"""
    Common Stec PyQt5 Widgets are being kept
"""


class ipconfigDialog(QDialog):

    """
    IP Form, it is a IP and Port Configuation Dialog
    User can attach to sigNewIPPort to get IP and Port Changes
    """
    sigNewIPPort = pyqtSignal( str,str)
    def __init__(self, callBack = None, ip = "localhost", port = "4897") :
        """

        :param callBack: func( str(ip), str(port))  user function or None
        :param ip:
        :param port:
        """
        super().__init__()
        self.callBack = callBack
        self.ui = Ui_IPConfgDialog()
        self.ui.setupUi(self)
        self.ui.buttonBox.accepted.connect(self._OK)
        self.ui.lineEditIP.setText(str(ip))
        self.ui.lineEditPort.setText(str(port))
        self.show()

    @pyqtSlot()
    def _OK(self) :
        ip = self.ui.lineEditIP.text()
        port = self.ui.lineEditPort.text()
        if self.callBack != None :
            self.callBack(ip,port)
        self.sigNewIPPort.emit(str(ip),str(port))

    def _Cancel(self) :
        print ("Cancel")



class stdcomqt5qtree(QTreeWidget):
    """
    Used to create a communication tree of names based on NextStep names
    """
    newTextSignal = pyqtSignal(str)
    newTextFolder = pyqtSignal(str)
    newTextFolderText = pyqtSignal(str)
    callback = None
    callbackgetdata = None


    def __init__(self, listOf, callback=None, callbackgetdata = None, onclick=True, label="not defined", parent=None):
        super().__init__(parent)
        self.callback = callback
        self.callbackgetdata = callbackgetdata
        self.ui = Ui_stdcomqt5treeewidget()
        self.ui.setupUi(self)
        sortedList = []
        if listOf is not None:
            sortedList = sorted(listOf)

        keys = list()
        self.KeyMap = {"": QTreeWidgetItem}

        for i in range(0, len(sortedList)):
            keyLine = str(sortedList[i])
            key = re.split(r'[.;:,\s]\s*', keyLine)
            if len(key) >= 0:
                word = key[0]
                try:
                    idx = word.index('//')
                    if idx == 0:
                        rdx = word.rindex('/')
                        word = word[idx:rdx]
                        keys.append(word)

                except:
                    keys.append(word)

        keys = dict.fromkeys(keys).keys()
        keys = tuple(keys)
        self.headerItem = QTreeWidgetItem()

        item = QTreeWidgetItem()

        for i in range(0, len(keys)):
            parent = QTreeWidgetItem(self.ui.TreeWidget)
            parent.setText(0, str(keys[i]))
            key = str(keys[i])

            self.KeyMap.update({word: parent})
            for x in range(0, len(sortedList)):
                word = str(sortedList[x])
                try:
                    result = word.index(key)
                    if result == 0:
                        child = QTreeWidgetItem(parent, 10001)
                        child.setText(0, word)
                except:
                    print("Index Key", key)

        self.ui.lineEditLabel.setText(str(label))

        if onclick == True:
            self.ui.TreeWidget.clicked.connect(self._Selected)
        else:
            self.ui.buttonBox.accepted.connect(self._Selected)


    def getData(self, item : QTreeWidgetItem):
        if self.callbackgetdata is not None :
            item.setData(0,Qt.UserRole, self.callbackgetdata(item.text()))

    def SetLineEditText(self, text):
        """
        Internal use
        :param text:
        :return:
        """
        v = str(text)
        self.ui.lineEditInput.setText(v)

    @pyqtSlot(str)
    def AddName(self, name: str):
        """
        Connection from Multiverse, for one name at a time

        :param name:
        :return:
        """

        print("New Name:", name)
        key = re.split(r'[.;:,\s]\s*', name)
        if len(key) >= 0:
            word = key[0]
            parent = None
            try:
                idx = word.index('//')
                if idx == 0:
                    rdx = word.rindex('/')
                    word = word[idx:rdx]
                    if word not in self.KeyMap.keys():
                        parent = QTreeWidgetItem(self.ui.TreeWidget)
                        parent.setText(0, str(word))
                        self.KeyMap.update({word: parent})


            except:
                if word not in self.KeyMap.keys():
                    parent = QTreeWidgetItem(self.ui.TreeWidget)
                    parent.setText(0, str(word))
                    self.KeyMap.update({word: parent})

            if parent == None:
                parent = self.KeyMap.get(word)

            self.ui.TreeWidget.sortByColumn(0, QtCore.Qt.AscendingOrder)
            parent.setForeground(0, QtGui.QBrush(QtGui.QColor("red")))

            child = QTreeWidgetItem(parent, 10001)
            child.setForeground(0, QtGui.QBrush(QtGui.QColor("red")))
            child.setText(0, name)

    @pyqtSlot(list)
    def AddNames(self, names: list):
        """
        adds a list of names
        """
        sortedList = []
        if names is not None:
            sortedList = sorted(names)
            for name in  sortedList :
                self.AddName(str(name))

    def _Selected(self):
        """
        internal use

        :return:
        """
        l = []
        for ix in self.ui.TreeWidget.selectedItems():
            type = ix.type()
            if type == 10001:
                text = ix.text(0)
                l.append(text)
                self.newTextSignal.emit(text)
                self.ui.lineEditLabel.setText(text)

        if self.callback != None and len(l) > 0:
            self.callback(l)

    @pyqtSlot()
    def newTextEnter(self):
        """
        Not used
        :return:
        """
        text = self.ui.lineEditInput.text()
        self.newTextSignal.emit(text)
        print("Just Entered", text)
        if self.callback != None and text != None and text != "":
            l = [text]
            self.callback(l)

