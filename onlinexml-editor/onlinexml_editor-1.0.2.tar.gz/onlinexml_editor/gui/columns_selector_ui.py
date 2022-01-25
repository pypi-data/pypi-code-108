# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/columns_selector.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_ColumnSelector(object):
    def setupUi(self, ColumnSelector):
        ColumnSelector.setObjectName("ColumnSelector")
        ColumnSelector.resize(400, 41)
        self.verticalLayout = QtWidgets.QVBoxLayout(ColumnSelector)
        self.verticalLayout.setObjectName("verticalLayout")
        self.but_box = QtWidgets.QDialogButtonBox(ColumnSelector)
        self.but_box.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.but_box.setOrientation(QtCore.Qt.Horizontal)
        self.but_box.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.but_box.setObjectName("but_box")
        self.verticalLayout.addWidget(self.but_box)

        self.retranslateUi(ColumnSelector)
        self.but_box.accepted.connect(ColumnSelector.accept)
        self.but_box.rejected.connect(ColumnSelector.reject)
        QtCore.QMetaObject.connectSlotsByName(ColumnSelector)

    def retranslateUi(self, ColumnSelector):
        _translate = QtCore.QCoreApplication.translate
        ColumnSelector.setWindowTitle(_translate("ColumnSelector", "Dialog"))

