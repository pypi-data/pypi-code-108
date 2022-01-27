# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_change_vol_name.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_VolNameDialog(object):
    def setupUi(self, VolNameDialog):
        VolNameDialog.setObjectName("VolNameDialog")
        VolNameDialog.resize(395, 94)
        self.gridLayout = QtWidgets.QGridLayout(VolNameDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.lineEditVolName = QtWidgets.QLineEdit(VolNameDialog)
        self.lineEditVolName.setObjectName("lineEditVolName")
        self.gridLayout.addWidget(self.lineEditVolName, 0, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonOk = QtWidgets.QPushButton(VolNameDialog)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.horizontalLayout.addWidget(self.pushButtonOk)
        self.pushButtonCancel = QtWidgets.QPushButton(VolNameDialog)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayout.addWidget(self.pushButtonCancel)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 0, 1, 1)

        self.retranslateUi(VolNameDialog)
        QtCore.QMetaObject.connectSlotsByName(VolNameDialog)

    def retranslateUi(self, VolNameDialog):
        _translate = QtCore.QCoreApplication.translate
        VolNameDialog.setWindowTitle(_translate("VolNameDialog", "Dialog"))
        self.pushButtonOk.setText(_translate("VolNameDialog", "OK"))
        self.pushButtonCancel.setText(_translate("VolNameDialog", "Cancel"))

