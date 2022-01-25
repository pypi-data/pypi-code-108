# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/about.ui'
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
        self.lbLogo.setPixmap(QtGui.QPixmap(":/ico/desy_logo.jpg"))
        self.lbLogo.setObjectName("lbLogo")
        self.horizontalLayout_2.addWidget(self.lbLogo)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(AboutDialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.lb_version = QtWidgets.QLabel(AboutDialog)
        self.lb_version.setObjectName("lb_version")
        self.verticalLayout.addWidget(self.lb_version)
        self.lb_modified = QtWidgets.QLabel(AboutDialog)
        self.lb_modified.setText("")
        self.lb_modified.setObjectName("lb_modified")
        self.verticalLayout.addWidget(self.lb_modified)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.lb_email = QtWidgets.QLabel(AboutDialog)
        self.lb_email.setMinimumSize(QtCore.QSize(200, 0))
        self.lb_email.setObjectName("lb_email")
        self.verticalLayout.addWidget(self.lb_email)
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
        AboutDialog.setWindowTitle(_translate("AboutDialog", "Online.xml Editor"))
        self.label_3.setText(_translate("AboutDialog", "Online.xml editor"))
        self.lb_version.setText(_translate("AboutDialog", "Version: 1.0"))
        self.lb_email.setText(_translate("AboutDialog", "yury.matveev@desy.de"))
        self.pushButton.setText(_translate("AboutDialog", "OK"))

import onlinexml_editor.gui.icons_rc
