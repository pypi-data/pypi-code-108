# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/CameraWidget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_CameraWindow(object):
    def setupUi(self, CameraWindow):
        CameraWindow.setObjectName("CameraWindow")
        CameraWindow.resize(845, 480)
        self.centralwidget = QtWidgets.QWidget(CameraWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        CameraWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(CameraWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 845, 21))
        self.menubar.setObjectName("menubar")
        CameraWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(CameraWindow)
        self.statusbar.setSizeGripEnabled(False)
        self.statusbar.setObjectName("statusbar")
        CameraWindow.setStatusBar(self.statusbar)
        self.quit_action = QtWidgets.QAction(CameraWindow)
        self.quit_action.setObjectName("quit_action")
        self.actionAbout = QtWidgets.QAction(CameraWindow)
        self.actionAbout.setObjectName("actionAbout")

        self.retranslateUi(CameraWindow)
        QtCore.QMetaObject.connectSlotsByName(CameraWindow)

    def retranslateUi(self, CameraWindow):
        _translate = QtCore.QCoreApplication.translate
        CameraWindow.setWindowTitle(_translate("CameraWindow", "CameraWindow"))
        self.quit_action.setText(_translate("CameraWindow", "Quit..."))
        self.quit_action.setShortcut(_translate("CameraWindow", "Ctrl+Q"))
        self.actionAbout.setText(_translate("CameraWindow", "About..."))

import petra_camera.gui.icons_rc
