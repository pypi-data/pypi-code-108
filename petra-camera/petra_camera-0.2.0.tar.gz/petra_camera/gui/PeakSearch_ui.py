# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'uis/PeakSearch.ui'
#
# Created by: PyQt5 UI code generator 5.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PeakSearch(object):
    def setupUi(self, PeakSearch):
        PeakSearch.setObjectName("PeakSearch")
        PeakSearch.resize(472, 869)
        self.verticalLayout = QtWidgets.QVBoxLayout(PeakSearch)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_8 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.chk_peak_search = QtWidgets.QCheckBox(PeakSearch)
        self.chk_peak_search.setObjectName("chk_peak_search")
        self.horizontalLayout_8.addWidget(self.chk_peak_search)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_8.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_8)
        self.horizontalLayout_10 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.rb_abs_threshold = QtWidgets.QRadioButton(PeakSearch)
        self.rb_abs_threshold.setChecked(True)
        self.rb_abs_threshold.setObjectName("rb_abs_threshold")
        self.horizontalLayout_10.addWidget(self.rb_abs_threshold)
        self.sl_abs_threshold = QtWidgets.QSlider(PeakSearch)
        self.sl_abs_threshold.setMinimum(1)
        self.sl_abs_threshold.setMaximum(16000)
        self.sl_abs_threshold.setSingleStep(1000)
        self.sl_abs_threshold.setOrientation(QtCore.Qt.Horizontal)
        self.sl_abs_threshold.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl_abs_threshold.setTickInterval(500)
        self.sl_abs_threshold.setObjectName("sl_abs_threshold")
        self.horizontalLayout_10.addWidget(self.sl_abs_threshold)
        self.sb_abs_threshold = QtWidgets.QSpinBox(PeakSearch)
        self.sb_abs_threshold.setMinimum(1)
        self.sb_abs_threshold.setMaximum(16000)
        self.sb_abs_threshold.setSingleStep(1000)
        self.sb_abs_threshold.setObjectName("sb_abs_threshold")
        self.horizontalLayout_10.addWidget(self.sb_abs_threshold)
        self.verticalLayout.addLayout(self.horizontalLayout_10)
        self.horizontalLayout_7 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.rb_rel_threshold = QtWidgets.QRadioButton(PeakSearch)
        self.rb_rel_threshold.setChecked(False)
        self.rb_rel_threshold.setObjectName("rb_rel_threshold")
        self.horizontalLayout_7.addWidget(self.rb_rel_threshold)
        self.sl_rel_threshold = QtWidgets.QSlider(PeakSearch)
        self.sl_rel_threshold.setEnabled(False)
        self.sl_rel_threshold.setMinimum(1)
        self.sl_rel_threshold.setSingleStep(10)
        self.sl_rel_threshold.setOrientation(QtCore.Qt.Horizontal)
        self.sl_rel_threshold.setTickPosition(QtWidgets.QSlider.TicksBelow)
        self.sl_rel_threshold.setTickInterval(10)
        self.sl_rel_threshold.setObjectName("sl_rel_threshold")
        self.horizontalLayout_7.addWidget(self.sl_rel_threshold)
        self.sb_rel_threshold = QtWidgets.QSpinBox(PeakSearch)
        self.sb_rel_threshold.setEnabled(False)
        self.sb_rel_threshold.setMinimum(1)
        self.sb_rel_threshold.setSingleStep(10)
        self.sb_rel_threshold.setObjectName("sb_rel_threshold")
        self.horizontalLayout_7.addWidget(self.sb_rel_threshold)
        self.verticalLayout.addLayout(self.horizontalLayout_7)
        spacerItem1 = QtWidgets.QSpacerItem(412, 750, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem1)

        self.retranslateUi(PeakSearch)
        QtCore.QMetaObject.connectSlotsByName(PeakSearch)

    def retranslateUi(self, PeakSearch):
        _translate = QtCore.QCoreApplication.translate
        PeakSearch.setWindowTitle(_translate("PeakSearch", "Peak Search"))
        self.chk_peak_search.setText(_translate("PeakSearch", "Enable peak search"))
        self.rb_abs_threshold.setText(_translate("PeakSearch", "Absolute threshold"))
        self.rb_rel_threshold.setText(_translate("PeakSearch", "Relative thershold"))

