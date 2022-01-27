# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_editor_tab.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_console(object):
    def setupUi(self, console):
        console.setObjectName("console")
        console.resize(593, 603)
        self.verticalLayout = QtWidgets.QVBoxLayout(console)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mainLayout = QtWidgets.QVBoxLayout()
        self.mainLayout.setObjectName("mainLayout")
        self.tableViewVolumes = QtWidgets.QTableView(console)
        self.tableViewVolumes.setObjectName("tableViewVolumes")
        self.mainLayout.addWidget(self.tableViewVolumes)
        self.verticalLayout.addLayout(self.mainLayout)
        self.pushButton = QtWidgets.QPushButton(console)
        self.pushButton.setObjectName("pushButton")
        self.verticalLayout.addWidget(self.pushButton)

        self.retranslateUi(console)
        QtCore.QMetaObject.connectSlotsByName(console)

    def retranslateUi(self, console):
        _translate = QtCore.QCoreApplication.translate
        console.setWindowTitle(_translate("console", "Form"))
        self.pushButton.setText(_translate("console", "save selected images"))

from . import resources_rc
