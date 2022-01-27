# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_sliceLabels.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(526, 81)
        self.verticalLayout = QtWidgets.QVBoxLayout(Form)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelVolume = QtWidgets.QLabel(Form)
        self.labelVolume.setObjectName("labelVolume")
        self.verticalLayout.addWidget(self.labelVolume)
        self.labelData = QtWidgets.QLabel(Form)
        self.labelData.setObjectName("labelData")
        self.verticalLayout.addWidget(self.labelData)
        self.labelVectors = QtWidgets.QLabel(Form)
        self.labelVectors.setObjectName("labelVectors")
        self.verticalLayout.addWidget(self.labelVectors)

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.labelVolume.setText(_translate("Form", "TextLabel"))
        self.labelData.setText(_translate("Form", "TextLabel"))
        self.labelVectors.setText(_translate("Form", "TextLabel"))

