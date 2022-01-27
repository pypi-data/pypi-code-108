# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_gradient_editor.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_GradientEditor(object):
    def setupUi(self, GradientEditor):
        GradientEditor.setObjectName("GradientEditor")
        GradientEditor.resize(674, 147)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(GradientEditor)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(GradientEditor)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(GradientEditor)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.verticalLayout_2.addLayout(self.gridLayout)
        self.horizontalLayoutMain = QtWidgets.QHBoxLayout()
        self.horizontalLayoutMain.setObjectName("horizontalLayoutMain")
        self.pushButtonCancel = QtWidgets.QPushButton(GradientEditor)
        self.pushButtonCancel.setObjectName("pushButtonCancel")
        self.horizontalLayoutMain.addWidget(self.pushButtonCancel)
        self.pushButtonOk = QtWidgets.QPushButton(GradientEditor)
        self.pushButtonOk.setObjectName("pushButtonOk")
        self.horizontalLayoutMain.addWidget(self.pushButtonOk)
        self.verticalLayout_2.addLayout(self.horizontalLayoutMain)

        self.retranslateUi(GradientEditor)
        QtCore.QMetaObject.connectSlotsByName(GradientEditor)

    def retranslateUi(self, GradientEditor):
        _translate = QtCore.QCoreApplication.translate
        GradientEditor.setWindowTitle(_translate("GradientEditor", "Dialog"))
        self.label.setText(_translate("GradientEditor", "positve LUT"))
        self.label_2.setText(_translate("GradientEditor", "negative LUT"))
        self.pushButtonCancel.setText(_translate("GradientEditor", "Cancel"))
        self.pushButtonOk.setText(_translate("GradientEditor", "OK"))

