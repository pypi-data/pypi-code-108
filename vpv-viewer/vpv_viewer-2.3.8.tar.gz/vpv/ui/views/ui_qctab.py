# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_qctab.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_QC(object):
    def setupUi(self, QC):
        QC.setObjectName("QC")
        QC.resize(758, 848)
        self.verticalLayout = QtWidgets.QVBoxLayout(QC)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(QC)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.listWidgetQcSpecimens = QtWidgets.QListWidget(QC)
        self.listWidgetQcSpecimens.setObjectName("listWidgetQcSpecimens")
        self.verticalLayout.addWidget(self.listWidgetQcSpecimens)
        self.label = QtWidgets.QLabel(QC)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tableWidgetFlagged = QtWidgets.QTableWidget(QC)
        self.tableWidgetFlagged.setObjectName("tableWidgetFlagged")
        self.tableWidgetFlagged.setColumnCount(2)
        self.tableWidgetFlagged.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetFlagged.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidgetFlagged.setHorizontalHeaderItem(1, item)
        self.verticalLayout.addWidget(self.tableWidgetFlagged)
        self.textEditSpecimenNotes = QtWidgets.QTextEdit(QC)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEditSpecimenNotes.sizePolicy().hasHeightForWidth())
        self.textEditSpecimenNotes.setSizePolicy(sizePolicy)
        self.textEditSpecimenNotes.setMaximumSize(QtCore.QSize(16777215, 100))
        self.textEditSpecimenNotes.setObjectName("textEditSpecimenNotes")
        self.verticalLayout.addWidget(self.textEditSpecimenNotes)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBoxFlagWholeImage = QtWidgets.QCheckBox(QC)
        self.checkBoxFlagWholeImage.setObjectName("checkBoxFlagWholeImage")
        self.horizontalLayout_2.addWidget(self.checkBoxFlagWholeImage)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.pushButtonFlagAllLabels = QtWidgets.QPushButton(QC)
        self.pushButtonFlagAllLabels.setObjectName("pushButtonFlagAllLabels")
        self.horizontalLayout_2.addWidget(self.pushButtonFlagAllLabels)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.label_3 = QtWidgets.QLabel(QC)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.pushButtonLoad = QtWidgets.QPushButton(QC)
        self.pushButtonLoad.setObjectName("pushButtonLoad")
        self.horizontalLayout.addWidget(self.pushButtonLoad)
        self.pushButtonSaveQC = QtWidgets.QPushButton(QC)
        self.pushButtonSaveQC.setObjectName("pushButtonSaveQC")
        self.horizontalLayout.addWidget(self.pushButtonSaveQC)
        self.pushButtonNextSpecimen = QtWidgets.QPushButton(QC)
        self.pushButtonNextSpecimen.setObjectName("pushButtonNextSpecimen")
        self.horizontalLayout.addWidget(self.pushButtonNextSpecimen)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(QC)
        QtCore.QMetaObject.connectSlotsByName(QC)

    def retranslateUi(self, QC):
        _translate = QtCore.QCoreApplication.translate
        QC.setWindowTitle(_translate("QC", "Form"))
        self.label_2.setText(_translate("QC", "Specimens"))
        self.label.setText(_translate("QC", "Qc flagged labels"))
        item = self.tableWidgetFlagged.horizontalHeaderItem(0)
        item.setText(_translate("QC", "Label"))
        item = self.tableWidgetFlagged.horizontalHeaderItem(1)
        item.setText(_translate("QC", "Name"))
        self.checkBoxFlagWholeImage.setText(_translate("QC", "Flag whole image"))
        self.pushButtonFlagAllLabels.setText(_translate("QC", "Flag all labels"))
        self.label_3.setText(_translate("QC", "Notes"))
        self.pushButtonLoad.setText(_translate("QC", "Load"))
        self.pushButtonSaveQC.setText(_translate("QC", "Save QC"))
        self.pushButtonNextSpecimen.setText(_translate("QC", "Next image (Alt Gr)"))
import resources_rc
