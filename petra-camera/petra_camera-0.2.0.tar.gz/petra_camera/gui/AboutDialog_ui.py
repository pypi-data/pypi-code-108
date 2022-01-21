# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/AboutDialog.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_AboutDialog(object):
    def setupUi(self, AboutDialog):
        AboutDialog.setObjectName("AboutDialog")
        AboutDialog.resize(388, 195)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(AboutDialog.sizePolicy().hasHeightForWidth())
        AboutDialog.setSizePolicy(sizePolicy)
        AboutDialog.setMinimumSize(QtCore.QSize(330, 195))
        AboutDialog.setMaximumSize(QtCore.QSize(450, 195))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(AboutDialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lbLogo = QtWidgets.QLabel(AboutDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.lbLogo.sizePolicy().hasHeightForWidth())
        self.lbLogo.setSizePolicy(sizePolicy)
        self.lbLogo.setMinimumSize(QtCore.QSize(130, 0))
        self.lbLogo.setText("")
        self.lbLogo.setPixmap(QtGui.QPixmap(":/ico/Desy_logo.jpg"))
        self.lbLogo.setObjectName("lbLogo")
        self.horizontalLayout_2.addWidget(self.lbLogo)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(AboutDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.label_4 = QtWidgets.QLabel(AboutDialog)
        self.label_4.setObjectName("label_4")
        self.verticalLayout.addWidget(self.label_4)
        self.lbModified = QtWidgets.QLabel(AboutDialog)
        self.lbModified.setText("")
        self.lbModified.setObjectName("lbModified")
        self.verticalLayout.addWidget(self.lbModified)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.lbEmail = QtWidgets.QLabel(AboutDialog)
        self.lbEmail.setMinimumSize(QtCore.QSize(200, 0))
        self.lbEmail.setObjectName("lbEmail")
        self.verticalLayout.addWidget(self.lbEmail)
        self.horizontalLayout_2.addLayout(self.verticalLayout)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.line = QtWidgets.QFrame(AboutDialog)
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.verticalLayout_2.addWidget(self.line)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(AboutDialog)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.retranslateUi(AboutDialog)
        self.pushButton.clicked.connect(AboutDialog.accept)
        QtCore.QMetaObject.connectSlotsByName(AboutDialog)

    def retranslateUi(self, AboutDialog):
        _translate = QtCore.QCoreApplication.translate
        AboutDialog.setWindowTitle(_translate("AboutDialog", "Camera viewer"))
        self.label_3.setText(_translate("AboutDialog", "2D Data Viewer"))
        self.label_4.setText(_translate("AboutDialog", "Version: 2.0"))
        self.lbEmail.setText(_translate("AboutDialog", "yury.matveev@desy.de"))
        self.pushButton.setText(_translate("AboutDialog", "OK"))

import petra_camera.gui.icons_rc
