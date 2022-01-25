# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/property.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Property(object):
    def setupUi(self, Property):
        Property.setObjectName("Property")
        Property.resize(469, 41)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Property)
        self.horizontalLayout.setContentsMargins(0, -1, 0, -1)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_1 = QtWidgets.QLabel(Property)
        self.label_1.setObjectName("label_1")
        self.horizontalLayout.addWidget(self.label_1)
        self.le_name = QtWidgets.QLineEdit(Property)
        self.le_name.setObjectName("le_name")
        self.horizontalLayout.addWidget(self.le_name)
        self.label_2 = QtWidgets.QLabel(Property)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout.addWidget(self.label_2)
        self.le_value = QtWidgets.QLineEdit(Property)
        self.le_value.setObjectName("le_value")
        self.horizontalLayout.addWidget(self.le_value)
        self.cmd_delete = QtWidgets.QPushButton(Property)
        self.cmd_delete.setObjectName("cmd_delete")
        self.horizontalLayout.addWidget(self.cmd_delete)

        self.retranslateUi(Property)
        QtCore.QMetaObject.connectSlotsByName(Property)

    def retranslateUi(self, Property):
        _translate = QtCore.QCoreApplication.translate
        Property.setWindowTitle(_translate("Property", "Form"))
        self.label_1.setText(_translate("Property", "Name:"))
        self.label_2.setText(_translate("Property", "Value:"))
        self.cmd_delete.setText(_translate("Property", "Delete"))

