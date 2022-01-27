# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_label_filter.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_LabelFilter(object):
    def setupUi(self, LabelFilter):
        LabelFilter.setObjectName("LabelFilter")
        LabelFilter.resize(440, 66)
        LabelFilter.setAutoFillBackground(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LabelFilter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_9 = QtWidgets.QLabel(LabelFilter)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.lineEditShowLabel = QtWidgets.QLineEdit(LabelFilter)
        self.lineEditShowLabel.setObjectName("lineEditShowLabel")
        self.verticalLayout.addWidget(self.lineEditShowLabel)

        self.retranslateUi(LabelFilter)
        QtCore.QMetaObject.connectSlotsByName(LabelFilter)

    def retranslateUi(self, LabelFilter):
        _translate = QtCore.QCoreApplication.translate
        LabelFilter.setWindowTitle(_translate("LabelFilter", "Form"))
        self.label_9.setText(_translate("LabelFilter", "Show only these lables (space-seperated list of label numbers)"))
