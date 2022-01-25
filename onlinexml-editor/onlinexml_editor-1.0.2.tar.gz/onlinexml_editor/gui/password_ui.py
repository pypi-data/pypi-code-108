# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/password.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PasswordSetup(object):
    def setupUi(self, PasswordSetup):
        PasswordSetup.setObjectName("PasswordSetup")
        PasswordSetup.resize(320, 119)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(PasswordSetup.sizePolicy().hasHeightForWidth())
        PasswordSetup.setSizePolicy(sizePolicy)
        PasswordSetup.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtWidgets.QGridLayout(PasswordSetup)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(PasswordSetup)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.le_current = QtWidgets.QLineEdit(PasswordSetup)
        self.le_current.setEchoMode(QtWidgets.QLineEdit.Password)
        self.le_current.setObjectName("le_current")
        self.gridLayout.addWidget(self.le_current, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(PasswordSetup)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.le_new = QtWidgets.QLineEdit(PasswordSetup)
        self.le_new.setEchoMode(QtWidgets.QLineEdit.Password)
        self.le_new.setObjectName("le_new")
        self.gridLayout.addWidget(self.le_new, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(PasswordSetup)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)
        self.le_repeat = QtWidgets.QLineEdit(PasswordSetup)
        self.le_repeat.setEchoMode(QtWidgets.QLineEdit.Password)
        self.le_repeat.setObjectName("le_repeat")
        self.gridLayout.addWidget(self.le_repeat, 2, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(PasswordSetup)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 0, 1, 2)

        self.retranslateUi(PasswordSetup)
        self.buttonBox.accepted.connect(PasswordSetup.accept)
        self.buttonBox.rejected.connect(PasswordSetup.reject)
        QtCore.QMetaObject.connectSlotsByName(PasswordSetup)

    def retranslateUi(self, PasswordSetup):
        _translate = QtCore.QCoreApplication.translate
        PasswordSetup.setWindowTitle(_translate("PasswordSetup", "Password setup"))
        self.label.setText(_translate("PasswordSetup", "Current password"))
        self.label_2.setText(_translate("PasswordSetup", "New password"))
        self.label_3.setText(_translate("PasswordSetup", "Repeat new password"))

