# -*- coding: utf-8 -*-

#  Copyright (C) 2021 Vremsoft LLC and/or its subsidiary(-ies).
#  All rights reserved.
#  Contact: Laura Chapman  (edc@vremsoft.com)
#  Commercial Usage
#  Licensees holding valid Vremsoft LLC licenses may use this file in
#  accordance with the License Agreement provided with the
#  Software or, alternatively, in accordance with the terms contained in
#  a written agreement between you and Vremsoft. LLC
#

# Form implementation generated from reading ui file 'ipportdialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_IPConfgDialog(object):
    def setupUi(self, IPConfgDialog):
        IPConfgDialog.setObjectName("IPConfgDialog")
        IPConfgDialog.resize(405, 203)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("images/pjanice.jpg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        IPConfgDialog.setWindowIcon(icon)
        self.verticalLayout = QtWidgets.QVBoxLayout(IPConfgDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(IPConfgDialog)
        self.groupBox.setObjectName("groupBox")
        self.layoutWidget = QtWidgets.QWidget(self.groupBox)
        self.layoutWidget.setGeometry(QtCore.QRect(30, 60, 268, 58))
        self.layoutWidget.setObjectName("layoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.layoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.layoutWidget)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.lineEditIP = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(30)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditIP.sizePolicy().hasHeightForWidth())
        self.lineEditIP.setSizePolicy(sizePolicy)
        self.lineEditIP.setMinimumSize(QtCore.QSize(30, 0))
        self.lineEditIP.setToolTipDuration(-1)
        self.lineEditIP.setObjectName("lineEditIP")
        self.lineEditIP.setStyleSheet("QLineEdit"
                                    "{"
                                    "background : white;"
                                    "}") 
        self.gridLayout.addWidget(self.lineEditIP, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.layoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lineEditPort = QtWidgets.QLineEdit(self.layoutWidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(20)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lineEditPort.sizePolicy().hasHeightForWidth())
        self.lineEditPort.setSizePolicy(sizePolicy)
        self.lineEditPort.setMinimumSize(QtCore.QSize(20, 0))
        self.lineEditPort.setObjectName("lineEditPort")
        self.lineEditPort.setStyleSheet("QLineEdit"
                                        "{"
                                        "background : white;"
                                        "}") 
        self.gridLayout.addWidget(self.lineEditPort, 1, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.buttonBox = QtWidgets.QDialogButtonBox(IPConfgDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(IPConfgDialog)
        self.buttonBox.accepted.connect(IPConfgDialog.accept)
        self.buttonBox.rejected.connect(IPConfgDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(IPConfgDialog)

    def retranslateUi(self, IPConfgDialog):
        _translate = QtCore.QCoreApplication.translate
        IPConfgDialog.setWindowTitle(_translate("IPConfgDialog", "IP Preference"))
        self.groupBox.setTitle(_translate("IPConfgDialog", "IP Service Port"))
        self.label.setText(_translate("IPConfgDialog", "IP Address/Name"))
        self.lineEditIP.setToolTip(_translate("IPConfgDialog", "Enter IP Address of Name"))
        self.lineEditIP.setWhatsThis(_translate("IPConfgDialog", "IP Address or Name"))
        self.label_2.setText(_translate("IPConfgDialog", "Service Port"))
        self.lineEditPort.setToolTip(_translate("IPConfgDialog", "Service Port "))
        self.lineEditPort.setStatusTip(_translate("IPConfgDialog", "Service Port of Multiverse"))
        self.lineEditPort.setWhatsThis(_translate("IPConfgDialog", "Service Port"))

