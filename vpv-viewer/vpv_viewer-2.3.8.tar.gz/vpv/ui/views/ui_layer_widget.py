# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_layer_widget.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Layer(object):
    def setupUi(self, Layer):
        Layer.setObjectName("Layer")
        Layer.resize(1030, 51)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Layer)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.comboBoxVol = QtWidgets.QComboBox(Layer)
        self.comboBoxVol.setObjectName("comboBoxVol")
        self.gridLayout.addWidget(self.comboBoxVol, 0, 0, 1, 1)
        self.comboBoxLut = QtWidgets.QComboBox(Layer)
        self.comboBoxLut.setObjectName("comboBoxLut")
        self.gridLayout.addWidget(self.comboBoxLut, 0, 1, 1, 1)
        self.horizontalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Layer)
        QtCore.QMetaObject.connectSlotsByName(Layer)

    def retranslateUi(self, Layer):
        _translate = QtCore.QCoreApplication.translate
        Layer.setWindowTitle(_translate("Layer", "Form"))

