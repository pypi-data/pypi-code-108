# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/LogWidget.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LogWidget(object):
    def setupUi(self, LogWidget):
        LogWidget.setObjectName("LogWidget")
        LogWidget.resize(561, 410)
        self.horizontalLayout = QtWidgets.QHBoxLayout(LogWidget)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.teLogs = QtWidgets.QPlainTextEdit(LogWidget)
        self.teLogs.setReadOnly(True)
        self.teLogs.setObjectName("teLogs")
        self.horizontalLayout.addWidget(self.teLogs)

        self.retranslateUi(LogWidget)
        QtCore.QMetaObject.connectSlotsByName(LogWidget)

    def retranslateUi(self, LogWidget):
        _translate = QtCore.QCoreApplication.translate
        LogWidget.setWindowTitle(_translate("LogWidget", "Form"))

