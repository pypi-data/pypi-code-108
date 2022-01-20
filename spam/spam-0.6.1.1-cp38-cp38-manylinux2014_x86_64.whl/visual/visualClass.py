"""
Library of SPAM functions for graphical alignment
Copyright (C) 2020 SPAM Contributors

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option)
any later version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
more details.

You should have received a copy of the GNU General Public License along with
this program.  If not, see <http://www.gnu.org/licenses/>.
"""


# system
import os
import os.path

# pyQt
from PyQt5 import QtCore
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QComboBox, QLineEdit, QGridLayout, QSlider, QHBoxLayout, QRadioButton, QCheckBox
from PyQt5.QtCore import Qt

# image.tif->QtImage
import qimage2ndarray

# alternative to lambda
from functools import partial

# science
import numpy
import tifffile

# spam
import spam.DIC
import spam.deformation
from spam.DIC import DICToolkit
import spam.DIC.correlateGM as cGM
import spam.helpers
import spam.visual.QtImageViewer as QtImageViewer

# matplotlib
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
# from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
mpl.rc('font', size=10)
cmapPhases = 'Set1_r'


class ereg(QWidget):
    def __init__(self, _images, enterPhi, names, binning=None, imUpdate=0):
        # init every graphical widget and create all the variables that will be used

        QWidget.__init__(self)
        # This list contiains the original Phi in position 0 and the updating Phi in position 1
        self.Phis = [enterPhi, enterPhi]
        self.parameters = spam.deformation.decomposePhi(enterPhi)
        # This is the reference image that will be deformed by Phi
        self.imUpdate = imUpdate
        self.refImage = _images[self.imUpdate]
        # These are the two currently shown images, images[1] will be updated
        self.images = [_images[0], _images[1]]
        self.Im1 = QtImageViewer.QtImageViewer()
        self.Im2 = QtImageViewer.QtImageViewer()
        self.comparison = QtImageViewer.QtImageViewer()
        # self.Im1.setFixedWidth(self.frameGeometry().width())
        # self.Im2.setFixedWidth(self.frameGeometry().width())
        # self.comparison.setFixedWidth(self.frameGeometry().width())
        self.axis = 'z'
        self.nbCB = 5
        self.changeColor = False
        self.comparisonMode = 0
        self.slice = []
        self.binning = binning
        sliceIm1 = [int(self.images[0].shape[0] / 2), int(self.images[0].shape[1] / 2), int(self.images[0].shape[2] / 2)]
        sliceIm2 = [int(self.images[1].shape[0] / 2), int(self.images[1].shape[1] / 2), int(self.images[1].shape[2] / 2)]
        self.slice.append(sliceIm1)
        self.slice.append(sliceIm2)
        self.tArray = [round(self.parameters['t'][0], 3), round(self.parameters['t'][1], 3), round(self.parameters['t'][2], 3)]
        self.rArray = [round(self.parameters['r'][0], 3), round(self.parameters['r'][1], 3), round(self.parameters['r'][2], 3)]
        self.zArray = [round(self.parameters['U'][0, 0], 3), round(self.parameters['U'][1, 1], 3), round(self.parameters['U'][2, 2], 3), 1]
        self.iterations = 0
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phis[1])
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phis[1]))

        # third line: secondary grids

        # transformation grid
        # transformation grid: translations
        # transformation grid: translations buttons
        self.tXPlus5Button = QPushButton("+5")
        self.tXPlus1Button = QPushButton("+1")
        self.tXMinus1Button = QPushButton("-1")
        self.tXLabel = QLineEdit("{:.3f}".format(self.tArray[2]))
        self.tXMinus5Button = QPushButton("-5")
        self.tYPlus5Button = QPushButton("+5")
        self.tYPlus1Button = QPushButton("+1")
        self.tYLabel = QLineEdit("{:.3f}".format(self.tArray[1]))
        self.tYMinus1Button = QPushButton("-1")
        self.tYMinus5Button = QPushButton("-5")
        self.tZPlus5Button = QPushButton("+5")
        self.tZPlus1Button = QPushButton("+1")
        self.tZLabel = QLineEdit("{:.3f}".format(self.tArray[0]))
        self.tZMinus1Button = QPushButton("-1")
        self.tZMinus5Button = QPushButton("-5")
        # transformation grid: translations connects
        self.tXPlus5Button.clicked.connect(partial(self.modifyPhi, "tX", 5))
        self.tXPlus1Button.clicked.connect(partial(self.modifyPhi, "tX", 1))
        self.tXMinus1Button.clicked.connect(partial(self.modifyPhi, "tX", -1))
        self.tXMinus5Button.clicked.connect(partial(self.modifyPhi, "tX", -5))
        self.tYPlus5Button.clicked.connect(partial(self.modifyPhi, "tY", 5))
        self.tYPlus1Button.clicked.connect(partial(self.modifyPhi, "tY", 1))
        self.tYMinus1Button.clicked.connect(partial(self.modifyPhi, "tY", -1))
        self.tYMinus5Button.clicked.connect(partial(self.modifyPhi, "tY", -5))
        self.tZPlus5Button.clicked.connect(partial(self.modifyPhi, "tZ", 5))
        self.tZPlus1Button.clicked.connect(partial(self.modifyPhi, "tZ", 1))
        self.tZMinus1Button.clicked.connect(partial(self.modifyPhi, "tZ", -1))
        self.tZMinus5Button.clicked.connect(partial(self.modifyPhi, "tZ", -5))
        # transformation grid: translations widgets

        # transformation grid: rotations
        # transformation grid: rotations buttons
        self.rXPlus5Button = QPushButton("5°↺")
        self.rXPlus1Button = QPushButton("1°↺")
        self.rXLabel = QLineEdit("{:.2f}".format(self.rArray[0]))
        self.rXMinus1Button = QPushButton("-1°↻")
        self.rXMinus5Button = QPushButton("-5°↻")
        # transformation grid: rotations connect
        self.rXPlus5Button.clicked.connect(partial(self.modifyPhi, "rX", 5))
        self.rXPlus1Button.clicked.connect(partial(self.modifyPhi, "rX", 1))
        self.rXMinus1Button.clicked.connect(partial(self.modifyPhi, "rX", -1))
        self.rXMinus5Button.clicked.connect(partial(self.modifyPhi, "rX", -5))
        # transformation grid: rotations widgets

        # transformation grid: zooms
        # transformation grid: zooms buttons
        self.zXPlus5Button  = QPushButton("+0.05")
        self.zXPlus1Button  = QPushButton("+0.01")
        self.zXLabel = QLineEdit(str(self.zArray[2]))
        self.zXMinus1Button = QPushButton("-0.01")
        self.zXMinus5Button = QPushButton("-0.05")
        self.zYPlus5Button  = QPushButton("+0.05")
        self.zYPlus1Button  = QPushButton("+0.01")
        self.zYLabel = QLineEdit(str(self.zArray[1]))
        self.zYMinus1Button = QPushButton("-0.01")
        self.zYMinus5Button = QPushButton("-0.05")
        self.zZPlus5Button  = QPushButton("+0.05")
        self.zZPlus1Button  = QPushButton("+0.01")
        self.zZLabel = QLineEdit(str(self.zArray[0]))
        self.zZMinus1Button = QPushButton("-0.01")
        self.zZMinus5Button = QPushButton("-0.05")
        self.zAPlus5Button  = QPushButton("+0.05")
        self.zAPlus1Button  = QPushButton("+0.01")
        self.zALabel = QLineEdit(str(self.zArray[0]))
        self.zAMinus1Button = QPushButton("-0.01")
        self.zAMinus5Button = QPushButton("-0.05")
        # transformation grid: zooms connect
        self.zXPlus5Button.clicked.connect( partial(self.modifyPhi, "zX",  0.05))
        self.zXPlus1Button.clicked.connect( partial(self.modifyPhi, "zX",  0.01))
        self.zXMinus1Button.clicked.connect(partial(self.modifyPhi, "zX", -0.01))
        self.zXMinus5Button.clicked.connect(partial(self.modifyPhi, "zX", -0.05))
        self.zYPlus5Button.clicked.connect( partial(self.modifyPhi, "zY",  0.05))
        self.zYPlus1Button.clicked.connect( partial(self.modifyPhi, "zY",  0.01))
        self.zYMinus1Button.clicked.connect(partial(self.modifyPhi, "zY", -0.01))
        self.zYMinus5Button.clicked.connect(partial(self.modifyPhi, "zY", -0.05))
        self.zZPlus5Button.clicked.connect( partial(self.modifyPhi, "zZ",  0.05))
        self.zZPlus1Button.clicked.connect( partial(self.modifyPhi, "zZ",  0.01))
        self.zZMinus1Button.clicked.connect(partial(self.modifyPhi, "zZ", -0.01))
        self.zZMinus5Button.clicked.connect(partial(self.modifyPhi, "zZ", -0.05))
        self.zAPlus5Button.clicked.connect( partial(self.modifyPhi, "zA",  0.05))
        self.zAPlus1Button.clicked.connect( partial(self.modifyPhi, "zA",  0.01))
        self.zAMinus1Button.clicked.connect(partial(self.modifyPhi, "zA", -0.01))
        self.zAMinus5Button.clicked.connect(partial(self.modifyPhi, "zA", -0.05))
        # transformation grid: zooms widgets

        # transformation grid: reset and validate buttons
        self.resetIdentityButton = QPushButton("Identity")
        self.resetTSVButton = QPushButton("TSV")
        self.validateButton = QPushButton("Apply Values")
        self.resetIdentityButton.clicked.connect(self.resetIdentity)
        self.resetTSVButton.clicked.connect(self.resetTSV)
        self.validateButton.clicked.connect(self.validate)

        # transformation grid: axes
        blankLabel = QLabel()
        self.currentAxisLabel = QComboBox()
        self.currentAxisLabel.addItems(["z", "y", "x"])
        rightArrow = QLabel("→")
        self.rightAxis = QLabel("x")
        bottomArrow = QLabel("↓")
        self.bottomAxis = QLabel("y")
        self.currentAxisLabel.currentIndexChanged.connect(self.changeAxis)
        # viewer grid

        # viewer grid: axis buttons
        # self.zRadioButton = QRadioButton("Z")
        # self.yRadioButton = QRadioButton("Y")
        # self.xRadioButton = QRadioButton("X")
        # self.zRadioButton.setChecked(True)
        # self.yRadioButton.setChecked(False)
        # self.xRadioButton.setChecked(False)
        # self.axisGroup = QButtonGroup()
        # self.axisGroup.addButton(self.zRadioButton)
        # self.axisGroup.addButton(self.yRadioButton)
        # self.axisGroup.addButton(self.xRadioButton)
        # viewer grid: axis connect
        # self.zRadioButton.toggled.connect(partial(self.changeAxis, "z"))
        # self.yRadioButton.toggled.connect(partial(self.changeAxis, "y"))
        # self.xRadioButton.toggled.connect(partial(self.changeAxis, "x"))

        ## viewer grid: flip buttons
        #flipZButton = QPushButton("Flip z")
        #flipYButton = QPushButton("Flip y")
        #flipXButton = QPushButton("Flip x")
        ## viewer grid: flip connect
        #flipZButton.clicked.connect(partial(self.flip, "z"))
        #flipYButton.clicked.connect(partial(self.flip, "y"))
        #flipXButton.clicked.connect(partial(self.flip, "x"))
        ## viewer grid: flip widgets

        # viewer grid50

        # viewer grid: label, sliders and buttons
        self.im1Slider = QSlider(QtCore.Qt.Horizontal)
        self.im2Slider = QSlider(QtCore.Qt.Horizontal)
        self.im1Slider.setMinimum(1)
        self.im2Slider.setMinimum(1)
        self.im1Slider.setMaximum(self.images[0].shape[0] - 1)
        self.im2Slider.setMaximum(self.images[1].shape[0] - 1)
        self.im1Slider.setValue(self.slice[0][0])
        self.im2Slider.setValue(self.slice[1][0])
        self.labelSlice1 = QLabel("{}: {}".format(self.axis, self.im1Slider.value()))
        self.labelSlice2 = QLabel("{}: {}".format(self.axis, self.im2Slider.value()))
        self.labelSlice1.setFixedWidth(50)
        self.labelSlice2.setFixedWidth(50)
        self.buttonMinusIm1 = QPushButton("<")
        self.buttonMinusIm2 = QPushButton("<")
        self.buttonPlusIm1 = QPushButton(">")
        self.buttonPlusIm2 = QPushButton(">")
        self.slaveBox = QCheckBox("Link im1 im2 slices views")
        self.im1Spacer = QLabel("")

        d = self.im2Slider.value() - self.im1Slider.value()
        self.delta = QLabel(u"\u0394" + self.axis + ": " + str(d))
        self.equalizerButton = QPushButton(u"Apply \u0394{}={}".format(self.axis, d))
        # viewer grid: set sliders
        # viewer grid: connect
        self.im1Slider.valueChanged.connect(self.slideIm1)
        self.im2Slider.valueChanged.connect(self.slideIm2)
        self.buttonMinusIm1.clicked.connect(lambda: self.slideIm1(self.im1Slider.value() - 1))
        self.buttonMinusIm2.clicked.connect(lambda: self.slideIm2(self.im2Slider.value() - 1))
        # self.buttonMinusIm2.clicked.connect(partial(self.slideIm2, self.im2Slider.value() - 1))
        self.buttonPlusIm1.clicked.connect(lambda: self.slideIm1(self.im1Slider.value() + 1))
        self.buttonPlusIm2.clicked.connect(lambda: self.slideIm2(self.im2Slider.value() + 1))
        # self.buttonPlusIm2.clicked.connect(partial(self.slideIm2, self.im2Slider.value() + 1))
        self.slaveBox.setChecked(True)
        self.slaveBox.toggled.connect(self.checkSlave)
        self.equalizerButton.clicked.connect(self.equalize)

        # comparison grid

        # comparison grid: labels and buttons
        self.minusRadioButton = QRadioButton("Im2-Im1")
        self.minusAbsRadioButton = QRadioButton("|Im2-Im1|")
        self.CBRadioButton = QRadioButton("CheckerBoard")
        self.changeColorCheck = QCheckBox("Change color")
        self.minusCBButton = QPushButton("-")
        self.plusCBButton = QPushButton("+")
        self.nbCBLabel = QLabel("{} squares".format(self.nbCB))

        self.minusRadioButton.setChecked(True)
        self.minusAbsRadioButton.setChecked(False)
        self.CBRadioButton.setChecked(False)

        if self.binning is None:
            self.nameEntry = QLineEdit("{}-{}-PhiEye.tsv".format(os.path.splitext(os.path.basename(names[0]))[0], os.path.splitext(os.path.basename(names[1]))[0]))
        else:
            self.nameEntry = QLineEdit("{}-{}-PhiEye-bin{}.tsv".format(os.path.splitext(os.path.basename(names[0]))[0], os.path.splitext(os.path.basename(names[1]))[0], self.binning))
        self.saveButton = QPushButton("Save")
        self.resultLabel = QLabel()

        # comparison grid: connect
        self.minusRadioButton.toggled.connect(partial(self.changeComp, 0))
        self.CBRadioButton.toggled.connect(partial(self.changeComp, 2))
        self.minusAbsRadioButton.toggled.connect(partial(self.changeComp, 1))
        self.changeColorCheck.toggled.connect(self.changeColorF)
        self.minusCBButton.clicked.connect(partial(self.changeCB, '-'))
        self.plusCBButton.clicked.connect(partial(self.changeCB, '+'))
        self.saveButton.clicked.connect(self.saveTSV)

        # phi and iterations
        self.vPhi1  = QLabel("{:.2f}".format(self.Phis[1][0][0]))
        self.vPhi2  = QLabel("{:.2f}".format(self.Phis[1][0][1]))
        self.vPhi3  = QLabel("{:.2f}".format(self.Phis[1][0][2]))
        self.vPhi4  = QLabel("{:.2f}".format(self.Phis[1][0][3]))
        self.vPhi5  = QLabel("{:.2f}".format(self.Phis[1][1][0]))
        self.vPhi6  = QLabel("{:.2f}".format(self.Phis[1][1][1]))
        self.vPhi7  = QLabel("{:.2f}".format(self.Phis[1][1][2]))
        self.vPhi8  = QLabel("{:.2f}".format(self.Phis[1][1][3]))
        self.vPhi9  = QLabel("{:.2f}".format(self.Phis[1][2][0]))
        self.vPhi10 = QLabel("{:.2f}".format(self.Phis[1][2][1]))
        self.vPhi11 = QLabel("{:.2f}".format(self.Phis[1][2][2]))
        self.vPhi12 = QLabel("{:.2f}".format(self.Phis[1][2][3]))
        self.vPhi13 = QLabel("{:.2f}".format(self.Phis[1][3][0]))
        self.vPhi14 = QLabel("{:.2f}".format(self.Phis[1][3][1]))
        self.vPhi15 = QLabel("{:.2f}".format(self.Phis[1][3][2]))
        self.vPhi16 = QLabel("{:.2f}".format(self.Phis[1][3][3]))
        self.vPhi1.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi2.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi3.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi4.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi5.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi6.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi7.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi8.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi9.setStyleSheet( "QLabel {font-weight: bold;}")
        self.vPhi10.setStyleSheet("QLabel {font-weight: bold;}")
        self.vPhi11.setStyleSheet("QLabel {font-weight: bold;}")
        self.vPhi12.setStyleSheet("QLabel {font-weight: bold;}")

        # PLACE ALL GRIDS AND WIDGETS

        # main grid
        self.winGrid = QGridLayout(self)

        # secondary grids left middle right top and bottom
        self.tGrid  = QGridLayout()
        self.bGrid  = QGridLayout()
        self.tlGrid = QGridLayout()
        self.tmGrid = QGridLayout()
        self.trGrid = QGridLayout()
        self.blGrid = QGridLayout()
        self.bmGrid = QGridLayout()
        self.brGrid = QGridLayout()

        # place secondary grids
        self.winGrid.addLayout(self.tGrid, 0, 0, 1, 12)
        self.winGrid.addLayout(self.bGrid, 1, 0, 1, 12)

        self.tGrid.addLayout(self.tlGrid, 0, 0, 1, 4)
        self.tGrid.addLayout(self.tmGrid, 0, 4, 1, 4)
        self.tGrid.addLayout(self.trGrid, 0, 8, 1, 4)

        self.bGrid.addLayout(self.blGrid, 1, 0, 1, 6)
        self.bGrid.addLayout(self.bmGrid, 1, 6, 1, 3)
        self.bGrid.addLayout(self.brGrid, 1, 9, 1, 3)

        # TOP GRID (IMAGE TITLE + IMAGES + VIEW BUTTONS)

        # TOP GRID LINE 1: Images title
        self.tlGrid.addWidget(QLabel(names[0]), 0, 0, 1, 12)
        self.tmGrid.addWidget(QLabel(names[1]), 0, 0, 1, 12)
        self.trGrid.addWidget(QLabel("Comparison"), 0, 0, 1, 12)

        # TOP GRID LINE 2: Images
        self.tlGrid.addWidget(self.Im1,        1, 0, 1, 12)
        self.tmGrid.addWidget(self.Im2,        1, 0, 1, 12)
        self.trGrid.addWidget(self.comparison, 1, 0, 1, 12)
        self.Im1.setMinimumWidth(300)
        self.Im2.setMinimumWidth(300)
        self.comparison.setMinimumWidth(300)

        # TOP GRID LINE 3: LEFT AND MIDDLE sliders
        self.tlGrid.addWidget(self.labelSlice1,    2,  1, 1, 1)
        self.tmGrid.addWidget(self.labelSlice2,    2,  1, 1, 1)
        self.tlGrid.addWidget(self.im1Slider,      2,  2, 1, 9)
        self.tmGrid.addWidget(self.im2Slider,      2,  2, 1, 9)
        self.tlGrid.addWidget(self.buttonMinusIm1, 2,  0, 1, 1)
        self.tlGrid.addWidget(self.buttonPlusIm1,  2, 11, 1, 1)
        self.tmGrid.addWidget(self.buttonMinusIm2, 2,  0, 1, 1)
        self.tmGrid.addWidget(self.buttonPlusIm2,  2, 11, 1, 1)
        self.labelSlice1.setFixedHeight(25)
        self.labelSlice2.setFixedHeight(25)
        self.labelSlice1.setFixedWidth(50)
        self.labelSlice2.setFixedWidth(50)
        self.buttonMinusIm1.setFixedWidth(25)
        self.buttonPlusIm1.setFixedWidth(25)
        self.buttonMinusIm2.setFixedWidth(25)
        self.buttonPlusIm2.setFixedWidth(25)
        self.im1Slider.setMinimumWidth(50)
        #self.im1Slider.setMinimumHeight(75)
        self.im2Slider.setMinimumWidth(50)

        # TOP GRID LINE 3: RIGHT comparison types
        # label = QLabel("Comparison:")
        # label = QLabel("")
        # self.trGrid.addWidget(label, 2, 0, 1, 1)
        # label.setFixedHeight(25)
        compareBoxe = QHBoxLayout()
        compareBoxe.addWidget(self.minusRadioButton)
        compareBoxe.addWidget(self.minusAbsRadioButton)
        compareBoxe.addWidget(self.CBRadioButton)
        compareBoxe.setAlignment(Qt.AlignCenter)
        self.trGrid.addLayout(compareBoxe, 2, 0, 1, 12)
        self.minusRadioButton.setFixedHeight(25)
        self.minusRadioButton.setFixedWidth(70)
        self.minusAbsRadioButton.setFixedWidth(80)
        self.CBRadioButton.setFixedWidth(120)

        # TOP GRID LINE 4: LEFT Sync
        self.im1Spacer = QLabel("")
        self.tlGrid.addWidget(self.im1Spacer, 3, 1, 1, 5)
        self.im1Spacer.setFixedHeight(25)
        self.tmGrid.addWidget(self.slaveBox,  3, 1, 1, 5)
        self.slaveBox.setFixedHeight(25)
        # self.tmGrid.addWidget(self.delta, 3, 4, 1, 4)
        self.tmGrid.addWidget(self.equalizerButton, 3, 6, 1, 5)
        # self.tmGrid.addWidget(self.equalizerButton, 7, 0, 1, 3)
        self.equalizerButton.hide()
        # TOP GRID LINE 4: LEFT flip buttons
        #label = QLabel("Flip")
        #self.tlGrid.addWidget(label, 3, 1, 1, 1)
        #box = QHBoxLayout()
        #box.addWidget(flipZButton)
        #box.addWidget(flipYButton)
        ##box.addWidget(flipXButton)
        #self.tlGrid.addLayout(box, 3, 2, 1, 9)
        ## self.tlGrid.addWidget(flipZButton, 3, 2, 1, 3)
        ## self.tlGrid.addWidget(flipYButton, 3, 5, 1, 3)
        ## self.tlGrid.addWidget(flipXButton, 3, 8, 1, 3)
        #label.setFixedHeight(25)
        # flipZButton.setFixedWidth(50)
        # flipYButton.setFixedWidth(50)
        # flipXButton.setFixedWidth(50)

        # TOP GRID LINE 4: RIGHT checker board options
        # self.trGrid.addWidget(QLabel("#squares:"), 3, 0, 1, 1)
        box = QHBoxLayout()
        box.addWidget(self.minusCBButton)
        box.addWidget(self.nbCBLabel)
        box.addWidget(self.plusCBButton)
        box.addWidget(self.changeColorCheck)
        box.setAlignment(Qt.AlignCenter)
        self.trGrid.addLayout(box, 3, 0, 1, 12)
        self.minusCBButton.setFixedWidth(25)
        self.nbCBLabel.setFixedWidth(70)
        self.changeColorCheck.setFixedWidth(110)
        self.plusCBButton.setFixedWidth(25)
        self.nbCBLabel.setFixedHeight(25)

        # TOP GRID LINE 5: LEFT empty
        # label = QLabel("")
        # self.tlGrid.addWidget(label, 4, 0, 1, 12)
        # label.setFixedHeight(25)

        # TOP GRID LINE 5: MIDDLE axis of view
        # axesBox = QHBoxLayout()
        # axesBox.addWidget(self.zRadioButton)
        # axesBox.addWidget(self.yRadioButton)
        # axesBox.addWidget(self.xRadioButton)
        # label = QLabel("View axis")
        # self.tmGrid.addWidget(label, 4, 0, 1, 2)
        # self.tmGrid.addLayout(axesBox, 4, 2, 1, 4)
        # label.setFixedHeight(25)

        # TOP GRID LINE 5: RIGHT empty
        # label = QLabel("")
        # self.trGrid.addWidget(label, 4, 0, 1, 12)
        # label.setFixedHeight(25)

        # BOTTOM GRID (Transformation)

        # BOTTOM GRID LEFT (TRANSLATION)
        label = QLabel("Translation")
        label.setAlignment(Qt.AlignCenter)
        self.blGrid.addWidget(label, 0, 0, 1, 3)
        self.blGrid.addWidget(QLabel("T: x"), 1, 0, 1, 1)
        self.blGrid.addWidget(QLabel("T: y"), 1, 1, 1, 1)
        self.blGrid.addWidget(QLabel("T: z"), 1, 2, 1, 1)
        self.blGrid.addWidget(self.tXPlus5Button, 2, 0, 1, 1)
        self.blGrid.addWidget(self.tXPlus1Button, 3, 0, 1, 1)
        self.blGrid.addWidget(self.tXLabel, 4, 0, 1, 1)
        self.blGrid.addWidget(self.tXMinus1Button, 5, 0, 1, 1)
        self.blGrid.addWidget(self.tXMinus5Button, 6, 0, 1, 1)
        self.blGrid.addWidget(self.tYPlus5Button, 2, 1, 1, 1)
        self.blGrid.addWidget(self.tYPlus1Button, 3, 1, 1, 1)
        self.blGrid.addWidget(self.tYLabel, 4, 1, 1, 1)
        self.blGrid.addWidget(self.tYMinus1Button, 5, 1, 1, 1)
        self.blGrid.addWidget(self.tYMinus5Button, 6, 1, 1, 1)
        self.blGrid.addWidget(self.tZPlus5Button, 2, 2, 1, 1)
        self.blGrid.addWidget(self.tZPlus1Button, 3, 2, 1, 1)
        self.blGrid.addWidget(self.tZLabel, 4, 2, 1, 1)
        self.blGrid.addWidget(self.tZMinus1Button, 5, 2, 1, 1)
        self.blGrid.addWidget(self.tZMinus5Button, 6, 2, 1, 1)
        self.tXPlus5Button.setFixedWidth(50)
        self.tXPlus1Button.setFixedWidth(50)
        self.tXLabel.setFixedWidth(50)
        self.tXMinus1Button.setFixedWidth(50)
        self.tXMinus5Button.setFixedWidth(50)
        self.tYPlus5Button.setFixedWidth(50)
        self.tYPlus1Button.setFixedWidth(50)
        self.tYLabel.setFixedWidth(50)
        self.tYMinus1Button.setFixedWidth(50)
        self.tYMinus5Button.setFixedWidth(50)
        self.tZPlus5Button.setFixedWidth(50)
        self.tZPlus1Button.setFixedWidth(50)
        self.tZLabel.setFixedWidth(50)
        self.tZMinus1Button.setFixedWidth(50)
        self.tZMinus5Button.setFixedWidth(50)

        label = QLabel("")
        self.blGrid.addWidget(label, 0, 3, 7, 1)
        label.setFixedWidth(10)

        # BOTTOM GRID LEFT (ROTATIONS)
        label = QLabel("Rotation")
        label.setAlignment(Qt.AlignCenter)
        self.blGrid.addWidget(label, 0, 4, 1, 1)
        self.rotationLabel = QLabel("R: z")
        self.blGrid.addWidget(self.rotationLabel, 1, 4, 1, 1)
        self.blGrid.addWidget(self.rXPlus5Button, 2, 4, 1, 1)
        self.blGrid.addWidget(self.rXPlus1Button, 3, 4, 1, 1)
        self.blGrid.addWidget(self.rXLabel, 4, 4, 1, 1)
        self.blGrid.addWidget(self.rXMinus1Button, 5, 4, 1, 1)
        self.blGrid.addWidget(self.rXMinus5Button, 6, 4, 1, 1)
        self.rXPlus5Button.setFixedWidth(50)
        self.rXPlus1Button.setFixedWidth(50)
        self.rXLabel.setFixedWidth(50)
        self.rXMinus1Button.setFixedWidth(50)
        self.rXMinus5Button.setFixedWidth(50)

        label = QLabel("")
        self.blGrid.addWidget(label,               0, 5, 7, 1)
        label.setFixedWidth(10)

        # BOTTOM GRID LEFT (ZOOMS)
        label = QLabel("Zoom")
        label.setAlignment(Qt.AlignCenter)
        self.blGrid.addWidget(label,               0, 6, 1, 3)
        self.blGrid.addWidget(QLabel("Z: x"),      1, 6, 1, 1)
        self.blGrid.addWidget(QLabel("Z: y"),      1, 7, 1, 1)
        self.blGrid.addWidget(QLabel("Z: z"),      1, 8, 1, 1)
        # self.blGrid.addWidget(QLabel("Z: all"),   1, 9, 1, 1)
        self.blGrid.addWidget(self.zXPlus5Button,  2, 6, 1, 1)
        self.blGrid.addWidget(self.zXPlus1Button,  3, 6, 1, 1)
        self.blGrid.addWidget(self.zXLabel,        4, 6, 1, 1)
        self.blGrid.addWidget(self.zXMinus1Button, 5, 6, 1, 1)
        self.blGrid.addWidget(self.zXMinus5Button, 6, 6, 1, 1)
        self.blGrid.addWidget(self.zYPlus5Button,  2, 7, 1, 1)
        self.blGrid.addWidget(self.zYPlus1Button,  3, 7, 1, 1)
        self.blGrid.addWidget(self.zYLabel,        4, 7, 1, 1)
        self.blGrid.addWidget(self.zYMinus1Button, 5, 7, 1, 1)
        self.blGrid.addWidget(self.zYMinus5Button, 6, 7, 1, 1)
        self.blGrid.addWidget(self.zZPlus5Button,  2, 8, 1, 1)
        self.blGrid.addWidget(self.zZPlus1Button,  3, 8, 1, 1)
        self.blGrid.addWidget(self.zZLabel,        4, 8, 1, 1)
        self.blGrid.addWidget(self.zZMinus1Button, 5, 8, 1, 1)
        self.blGrid.addWidget(self.zZMinus5Button, 6, 8, 1, 1)
        # self.blGrid.addWidget(self.zAPlus5Button, 2, 9, 1, 1)
        # self.blGrid.addWidget(self.zAPlus1Button, 3, 9, 1, 1)
        # self.blGrid.addWidget(self.zALabel, 4, 9, 1, 1)
        # self.blGrid.addWidget(self.zAMinus1Button, 5, 9, 1, 1)
        # self.blGrid.addWidget(self.zAMinus5Button, 6, 9, 1, 1)
        self.zZPlus5Button.setFixedWidth(50)
        self.zZPlus1Button.setFixedWidth(50)
        self.zZLabel.setFixedWidth(50)
        self.zZMinus1Button.setFixedWidth(50)
        self.zZMinus5Button.setFixedWidth(50)
        self.zYPlus5Button.setFixedWidth(50)
        self.zYPlus1Button.setFixedWidth(50)
        self.zYLabel.setFixedWidth(50)
        self.zYMinus1Button.setFixedWidth(50)
        self.zYMinus5Button.setFixedWidth(50)
        self.zXPlus5Button.setFixedWidth(50)
        self.zXPlus1Button.setFixedWidth(50)
        self.zXLabel.setFixedWidth(50)
        self.zXMinus1Button.setFixedWidth(50)
        self.zXMinus5Button.setFixedWidth(50)
        # self.zAPlus5Button.setFixedWidth(50)
        # self.zAPlus1Button.setFixedWidth(50)
        # self.zALabel.setFixedWidth(50)
        # self.zAMinus1Button.setFixedWidth(50)
        # self.zAMinus5Button.setFixedWidth(50)

        label = QLabel("")
        label.setAlignment(Qt.AlignCenter)
        self.blGrid.addWidget(label, 0, 10, 7, 3)

        # BOTTOM GRID LEFT (reset + apply)
        # self.blGrid.addWidget(self.resetTSVButton, 5, 11, 2, 1)
        # self.blGrid.addWidget(self.validateButton, 4, 11, 1, 1)
        # self.validateButton.setFixedWidth(50)

        self.resetTSVButton.setFixedWidth(50)
        self.blGrid.addWidget(QLabel("reset:"), 7, 0, 1, 1)
        self.blGrid.addWidget(self.resetIdentityButton, 7, 1, 1, 2)
        self.blGrid.addWidget(self.resetTSVButton, 7, 4, 1, 1)
        self.blGrid.addWidget(self.validateButton, 7, 6, 1, 3)

        # BOTTOM GRID MIDDLE (axis)
        label = QLabel("Change axis of view")
        label.setAlignment(Qt.AlignCenter)
        self.bmGrid.addWidget(label, 0, 0, 1, 3)
        # self.bmGrid.addWidget(self.zRadioButton, 1, 0, 1, 1)
        # self.bmGrid.addWidget(self.yRadioButton, 1, 1, 1, 1)
        # self.bmGrid.addWidget(self.xRadioButton, 1, 2, 1, 1)
        # self.bmGrid.addLayout(axesBox, 1, 0, 1, 3)
        label.setFixedHeight(25)
        # self.zRadioButton.setFixedWidth(30)
        # self.yRadioButton.setFixedWidth(30)
        # self.xRadioButton.setFixedWidth(30)
        # self.zRadioButton.setFixedHeight(25)
        # self.yRadioButton.setFixedHeight(25)
        # self.xRadioButton.setFixedHeight(25)

        blankLabel = QLabel("")
        self.bmGrid.addWidget(blankLabel, 2, 0)
        self.bmGrid.addWidget(rightArrow, 2, 1)
        self.bmGrid.addWidget(bottomArrow, 3, 0)
        self.bmGrid.addWidget(self.currentAxisLabel, 2, 0)
        self.bmGrid.addWidget(self.rightAxis, 2, 2)
        self.bmGrid.addWidget(self.bottomAxis, 4, 0)

        self.currentAxisLabel.setFixedWidth(50)
        self.currentAxisLabel.setFixedHeight(25)
        self.rightAxis.setFixedWidth(25)
        self.rightAxis.setFixedHeight(25)
        self.bottomAxis.setFixedWidth(25)
        self.bottomAxis.setFixedHeight(25)
        rightArrow.setFixedWidth(25)
        rightArrow.setFixedHeight(25)
        bottomArrow.setFixedWidth(25)
        bottomArrow.setFixedHeight(25)
        # self.bmGrid.addLayout(axeGrid, 0, 0, 3, 3)

        # BOTTOM GRID RIGHT (phi)
        phiGrid = QGridLayout()
        label = QLabel("Phi = ")
        phiGrid.addWidget(label, 1, 0, 2, 1)
        label.setStyleSheet("QLabel {font-weight: bold;}")
        phiGrid.addWidget(self.vPhi1,  0, 1)
        phiGrid.addWidget(self.vPhi2,  0, 2)
        phiGrid.addWidget(self.vPhi3,  0, 3)
        phiGrid.addWidget(self.vPhi4,  0, 4)
        phiGrid.addWidget(self.vPhi5,  1, 1)
        phiGrid.addWidget(self.vPhi6,  1, 2)
        phiGrid.addWidget(self.vPhi7,  1, 3)
        phiGrid.addWidget(self.vPhi8,  1, 4)
        phiGrid.addWidget(self.vPhi9,  2, 1)
        phiGrid.addWidget(self.vPhi10, 2, 2)
        phiGrid.addWidget(self.vPhi11, 2, 3)
        phiGrid.addWidget(self.vPhi12, 2, 4)
        phiGrid.addWidget(self.vPhi13, 3, 1)
        phiGrid.addWidget(self.vPhi14, 3, 2)
        phiGrid.addWidget(self.vPhi15, 3, 3)
        phiGrid.addWidget(self.vPhi16, 3, 4)
        self.vPhi1.setFixedHeight(10)
        self.vPhi2.setFixedHeight(10)
        self.vPhi3.setFixedHeight(10)
        self.vPhi4.setFixedHeight(10)
        self.vPhi5.setFixedHeight(10)
        self.vPhi6.setFixedHeight(10)
        self.vPhi7.setFixedHeight(10)
        self.vPhi8.setFixedHeight(10)
        self.vPhi9.setFixedHeight(10)
        self.vPhi10.setFixedHeight(10)
        self.vPhi11.setFixedHeight(10)
        self.vPhi12.setFixedHeight(10)
        self.vPhi13.setFixedHeight(10)
        self.vPhi14.setFixedHeight(10)
        self.vPhi15.setFixedHeight(10)
        self.vPhi16.setFixedHeight(10)
        self.brGrid.addLayout(phiGrid, 3, 0, 4, 4)
        # self.nbIteration = QLabel("Iterations: " + str(self.iterations))
        # self.trGrid.addWidget(self.nbIteration, 7, 1)

        # LAST LINE: saving and messages
        box = QHBoxLayout()
        box.addWidget(QLabel("Save your transformation settings (phi) in a tsv file for later use (optional)"))
        box.addWidget(self.nameEntry)
        box.addWidget(self.saveButton)
        self.winGrid.addLayout(box, 2, 1)
        self.winGrid.addWidget(self.resultLabel, 3, 1)
        self.resultLabel.setFixedHeight(20)
        self.nameEntry.setFixedHeight(20)

        self.showImages()

    def slideIm1(self, value):
        if value < self.im1Slider.maximum() and value > self.im1Slider.minimum():
            self.im1Slider.setValue(value)
            # check the selected axe
            if self.axis == "z":   self.slice[0][0] = value
            elif self.axis == "y": self.slice[0][1] = value
            elif self.axis == "x": self.slice[0][2] = value
            # change the label with the new value
            self.labelSlice1.setText("{}: {}".format(self.axis, self.im1Slider.value()))
            # check if the 2slidebars are linked together
            if self.slaveBox.isChecked():
                self.im2Slider.setValue(value)
                if self.axis == "z":   self.slice[1][0] = value
                elif self.axis == "y": self.slice[1][1] = value
                elif self.axis == "x": self.slice[1][2] = value
                self.labelSlice2.setText("{}: {}".format(self.axis, self.im2Slider.value()))
            self.showImages()  # call the function to display images
            # change the delta string
            # self.delta.setText("Delta " + self.axis + ": " + str(self.im2Slider.value() - self.im1Slider.value()))
            d = self.im2Slider.value() - self.im1Slider.value()
            self.delta.setText(u"\u0394" + self.axis + ": " + str(d))
            self.equalizerButton.setText(u"Apply \u0394{}={}".format(self.axis, d))

    def slideIm2(self, value):
        # same as the slideIm1() but for other parameters
        if value < self.im2Slider.maximum() and value > self.im2Slider.minimum():
            self.im2Slider.setValue(value)
            if self.axis == "z":   self.slice[1][0] = value
            elif self.axis == "y": self.slice[1][1] = value
            elif self.axis == "x": self.slice[1][2] = value
            self.labelSlice2.setText("{}: {}".format(self.axis, self.im2Slider.value()))
            if self.slaveBox.isChecked():
                self.im1Slider.setValue(value)
                if self.axis == "z":   self.slice[0][0] = value
                elif self.axis == "y": self.slice[0][1] = value
                elif self.axis == "x": self.slice[0][2] = value
                self.labelSlice1.setText("{}: {}".format(self.axis, self.im1Slider.value()))
            self.showImages()
            # self.delta.setText("Delta " + self.axis + ": " + str(self.im2Slider.value() - self.im1Slider.value()))
            d = self.im2Slider.value() - self.im1Slider.value()
            self.delta.setText(u"\u0394" + self.axis + ": " + str(d))
            self.equalizerButton.setText(u"Apply \u0394{}={}".format(self.axis, d))

    def showImages(self):
        # check the selected axe and set the new slice to display
        if self.axis == 'z':
            self.Im1.setImage(qimage2ndarray.array2qimage(self.images[0][self.slice[0][0], :, :], normalize=True))
            self.Im2.setImage(qimage2ndarray.array2qimage(self.images[1][self.slice[1][0], :, :], normalize=True))
        elif self.axis == 'y':
            self.Im1.setImage(qimage2ndarray.array2qimage(self.images[0][:, self.slice[0][1], :], normalize=True))
            self.Im2.setImage(qimage2ndarray.array2qimage(self.images[1][:, self.slice[1][1]], normalize=True))
        elif self.axis == 'x':
            self.Im1.setImage(qimage2ndarray.array2qimage(self.images[0][:, :, self.slice[0][2]], normalize=True))
            self.Im2.setImage(qimage2ndarray.array2qimage(self.images[1][:, :, self.slice[1][2]], normalize=True))
        if self.comparisonMode == 0:  # check the comparison mode and then display the computed comparison
            if self.axis == 'z':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.subtract(self.images[0][self.slice[0][0], :, :],
                                                                                    self.images[1][self.slice[1][0], :, :]), normalize=True))
            elif self.axis == 'y':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.subtract(self.images[0][:, self.slice[0][1], :],
                                                                                    self.images[1][:, self.slice[1][1], :]), normalize=True))
            elif self.axis == 'x':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.subtract(self.images[0][:, :, self.slice[0][2]],
                                                                                    self.images[1][:, :, self.slice[1][2]]), normalize=True))
        elif self.comparisonMode == 1:
            if self.axis == 'z':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.absolute(numpy.subtract(self.images[0][self.slice[0][0], :, :],
                                                                                                   self.images[1][self.slice[1][0], :, :])), normalize=True))
            elif self.axis == 'y':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.absolute(numpy.subtract(self.images[0][:, self.slice[0][1], :],
                                                                                                   self.images[1][:, self.slice[1][1], :])), normalize=True))
            elif self.axis == 'x':
                self.comparison.setImage(qimage2ndarray.array2qimage(numpy.absolute(numpy.subtract(self.images[0][:, :, self.slice[0][2]],
                                                                                                   self.images[1][:, :, self.slice[1][2]])), normalize=True))
        elif self.comparisonMode == 2:
            if self.axis == 'z':
                if self.changeColorCheck.isChecked():
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][self.slice[0][0], :, :] + self.images[1].max() * (1 / 6),
                                                                                          self.images[1][self.slice[1][0], :, :],
                                                                                          self.nbCB, False, False), normalize=True))
                else:
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][self.slice[0][0], :, :],
                                                                                          self.images[1][self.slice[1][0], :, :],
                                                                                          self.nbCB, False, False), normalize=True))
            elif self.axis == 'y':
                if self.changeColorCheck.isChecked():
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][:, self.slice[0][1], :] + self.images[1].max() * (1 / 6),
                                                                                          self.images[1][:, self.slice[1][1], :],
                                                                                          self.nbCB, False, False), normalize=True))
                else:
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][:, self.slice[0][1], :],
                                                                                          self.images[1][:, self.slice[1][1], :],
                                                                                          self.nbCB, False, False), normalize=True))
            elif self.axis == 'x':
                if self.changeColorCheck.isChecked():
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][:, :, self.slice[0][2]] + self.images[1].max() * (1 / 6),
                                                                                          self.images[1][:, :, self.slice[1][2]],
                                                                                          self.nbCB, False, False), normalize=True))
                else:
                    self.comparison.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.images[0][:, :, self.slice[0][2]],
                                                                                          self.images[1][:, :, self.slice[1][2]],
                                                                                          self.nbCB, False, False), normalize=True))
        # update the diplayed phi
        self.vPhi1.setText( str(round(self.Phis[1][0][0], 3)))
        self.vPhi2.setText( str(round(self.Phis[1][0][1], 3)))
        self.vPhi3.setText( str(round(self.Phis[1][0][2], 3)))
        self.vPhi4.setText( str(round(self.Phis[1][0][3], 3)))
        self.vPhi5.setText( str(round(self.Phis[1][1][0], 3)))
        self.vPhi6.setText( str(round(self.Phis[1][1][1], 3)))
        self.vPhi7.setText( str(round(self.Phis[1][1][2], 3)))
        self.vPhi8.setText( str(round(self.Phis[1][1][3], 3)))
        self.vPhi9.setText( str(round(self.Phis[1][2][0], 3)))
        self.vPhi10.setText(str(round(self.Phis[1][2][1], 3)))
        self.vPhi11.setText(str(round(self.Phis[1][2][2], 3)))
        self.vPhi12.setText(str(round(self.Phis[1][2][3], 3)))
        self.vPhi13.setText(str(round(self.Phis[1][3][0], 3)))
        self.vPhi14.setText(str(round(self.Phis[1][3][1], 3)))
        self.vPhi15.setText(str(round(self.Phis[1][3][2], 3)))
        self.vPhi16.setText(str(round(self.Phis[1][3][3], 3)))

    def changeAxis(self, i):
        # change the axe value
        if i == 0:
            axe = "z"
        elif i == 1:
            axe = "y"
        elif i == 2:
            axe = "x"
        self.axis = axe
        self.rotationLabel.setText("R: {}".format(axe))
        # self.currentAxisLabel.setText(self.axis)
        # check the selected axe and then update the slidebars limits to the new axe and change the displayed hint about axes
        if axe == "z":
            self.im1Slider.setMaximum(self.images[1].shape[0] - 1)
            self.im1Slider.setValue(self.slice[1][0])
            self.im2Slider.setMaximum(self.images[0].shape[0] - 1)
            self.im2Slider.setValue(self.slice[0][0])
            self.bottomAxis.setText("y")
            self.rightAxis.setText("x")
            self.rXLabel.setText("{:.2f}".format(self.rArray[0]))
        elif axe == "y":
            self.im1Slider.setMaximum(self.images[1].shape[1] - 1)
            self.im1Slider.setValue(self.slice[1][1])
            self.im2Slider.setMaximum(self.images[0].shape[1] - 1)
            self.im2Slider.setValue(self.slice[0][1])
            self.bottomAxis.setText("z")
            self.rightAxis.setText("x")
            self.rXLabel.setText("{:.2f}".format(self.rArray[1]))
        elif axe == "x":
            self.im1Slider.setMaximum(self.images[1].shape[2] - 1)
            self.im1Slider.setValue(self.slice[1][2])
            self.im2Slider.setMaximum(self.images[0].shape[2] - 1)
            self.im2Slider.setValue(self.slice[0][2])
            self.bottomAxis.setText("z")
            self.rightAxis.setText("y")
            self.rXLabel.setText("{:.2f}".format(self.rArray[2]))
        self.showImages()
        # self.delta.setText("Delta " + self.axis + ": " + str(self.im2Slider.value() - self.im1Slider.value()))
        d = self.im2Slider.value() - self.im1Slider.value()
        self.delta.setText(u"\u0394" + self.axis + ": " + str(d))
        self.equalizerButton.setText(u"Apply \u0394{}={}".format(self.axis, d))

    def checkSlave(self):
        # check if the toggle checked or unchecked and then replace the slidebars at the same place
        if self.slaveBox.isChecked():
            self.slideIm1(self.im1Slider.value())
            self.equalizerButton.hide()
        else:
            self.equalizerButton.show()
        # self.delta.setText("Delta " + self.axis + ": " + str(self.im2Slider.value() - self.im1Slider.value()))
        d = self.im2Slider.value() - self.im1Slider.value()
        self.delta.setText(u"\u0394" + self.axis + ": " + str(d))
        self.equalizerButton.setText(u"Apply \u0394{}={}".format(self.axis, d))

    def changeComp(self, value):
        # change the comparison variable to the selected one and display the new one
        self.comparisonMode = value
        self.showImages()

    def changeCB(self, value):
        # check if + or - was clicked and then increase or decrease the number of tiles
        if value == "+":
            self.nbCB = self.nbCB + 2
        elif value == "-" and self.nbCB > 1:
            self.nbCB = self.nbCB - 2
        self.nbCBLabel.setText("{} squares".format(self.nbCB))
        self.CBRadioButton.setChecked(True)
        self.showImages()

    def changeColorF(self):
        if self.changeColorCheck.isChecked():
            self.CBRadioButton.setChecked(True)
        self.showImages()

    def modifyPhi(self, mod, value):
        # create a transformation dictionary
        # phiPrev = spam.deformation.computePhi({'t': [self.tArray[0], self.tArray[1], self.tArray[2]],
        #                              'r': [self.rArray[0], self.rArray[1], self.rArray[2]],
        #                              'z': [self.zArray[0], self.zArray[1], self.zArray[2]]})
        phiRotPrev = spam.deformation.computePhi({'r': [self.rArray[0], self.rArray[1], self.rArray[2]]})
        deltaRot = numpy.zeros(3, dtype='<f8')

        if mod == "tZ":  # check which value to increase and then increase the good one to load the new image
            self.tArray[0] = (self.tArray[0] + value)
            self.tZLabel.setText("{:.3f}".format(self.tArray[0]))
        elif mod == "tY":
            self.tArray[1] = (self.tArray[1] + value)
            self.tYLabel.setText("{:.3f}".format(self.tArray[1]))
        elif mod == "tX":
            self.tArray[2] = (self.tArray[2] + value)
            self.tXLabel.setText("{:.3f}".format(self.tArray[2]))
        # elif mod == "rZ":
        #     self.rArray[0] = (self.rArray[0] + value)
        #     self.rZLabel.setText(str(self.rArray[0]))
        # elif mod == "rY":
        #     self.rArray[1] = (self.rArray[1] + value)
        #     self.rYLabel.setText(str(self.rArray[1]))
        elif mod == "rX":
            if self.axis == "x":
                i = 2
            elif self.axis == "y":
                i = 1
            elif self.axis == "z":
                i = 0
            deltaRot[i] = value
            self.rXLabel.setText("{:.2f}".format(self.rArray[i] + deltaRot[i]))
        elif mod == "zZ":
            self.zArray[0] = (round( self.zArray[0] + value, 3))
            self.zZLabel.setText(str(self.zArray[0]))
        elif mod == "zY":
            self.zArray[1] = (round( self.zArray[1] + value, 3))
            self.zYLabel.setText(str(self.zArray[1]))
        elif mod == "zX":
            self.zArray[2] = (round( self.zArray[2] + value, 3))
            self.zXLabel.setText(str(self.zArray[2]))
        elif mod == "zA":
            self.zArray[0] = (round( self.zArray[0] + value, 3))
            self.zZLabel.setText(str(self.zArray[0]))
            self.zArray[1] = (round( self.zArray[1] + value, 3))
            self.zYLabel.setText(str(self.zArray[1]))
            self.zArray[2] = (round( self.zArray[2] + value, 3))
            self.zXLabel.setText(str(self.zArray[2]))
            self.zArray[3] = (round( self.zArray[3] + value, 3))
            self.zALabel.setText(str(self.zArray[3]))

        if deltaRot.sum() != 0:
            newRotPhi = spam.deformation.computePhi({'r': deltaRot})
            totalPhi = numpy.dot(newRotPhi, phiRotPrev)
            # totalPhi = numpy.dot(phiRotPrev, newRotPhi)
            decomposedPhi = spam.deformation.decomposePhi(totalPhi)
            self.rArray = decomposedPhi['r']

        # create a transformation dictionary
        transformation = {'t': [self.tArray[0], self.tArray[1], self.tArray[2]],
                          'r': [self.rArray[0], self.rArray[1], self.rArray[2]],
                          'z': [self.zArray[0], self.zArray[1], self.zArray[2]]}

        # modify phi that has to be applied then apply it
        self.Phis[1] = spam.deformation.computePhi(transformation)
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phis[1])
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phis[1]))
        # call showimages() to see graphically the change
        self.showImages()
        self.iterations = (self.iterations + 1)
        # self.nbIteration.setText("Iterations: " + str(self.iterations))
        self.resultLabel.setText("Phi needs to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")

    def saveTSV(self):
        # save a tifffile using a spam function
        if self.nameEntry.text() != "":
            tmp = self.nameEntry.text()
            fileName = tmp if tmp.split(".")[-1] in ["tsv"] else tmp + ".tsv"
            # save.writeRegistrationTSV(fileName, (numpy.array(self.images[1].shape) - 1) / 2.0, {
            #                           'PhiCentre': self.Phis[1], "returnStatus": 2, "iterations": self.iterations, "error": 100, "deltaPhiNorm": 0.1})
            centre = (numpy.array(self.images[0].shape)-1)/2.0
            if self.binning is None:
                TSVheader = "Zpos\tYpos\tXpos\tFzz\tFzy\tFzx\tZdisp\tFyz\tFyy\tFyx\tYdisp\tFxz\tFxy\tFxx\tXdisp\treturnStatus\tdeltaPhiNorm\terror\titerations"
                output = numpy.array([[centre[0]], [centre[1]], [centre[2]],
                                    [self.Phis[1][0, 0]], [self.Phis[1][0, 1]], [self.Phis[1][0, 2]], [self.Phis[1][0, 3]],
                                    [self.Phis[1][1, 0]], [self.Phis[1][1, 1]], [self.Phis[1][1, 2]], [self.Phis[1][1, 3]],
                                    [self.Phis[1][2, 0]], [self.Phis[1][2, 1]], [self.Phis[1][2, 2]], [self.Phis[1][2, 3]],
                                    [0], [1.0], [self.images[0].mean()], [0] ])
            else:
                TSVheader = "Zpos\tYpos\tXpos\tFzz\tFzy\tFzx\tZdisp\tFyz\tFyy\tFyx\tYdisp\tFxz\tFxy\tFxx\tXdisp\treturnStatus\tdeltaPhiNorm\terror\titerations\tbin"
                output = numpy.array([[centre[0]], [centre[1]], [centre[2]],
                                    [self.Phis[1][0, 0]], [self.Phis[1][0, 1]], [self.Phis[1][0, 2]], [self.Phis[1][0, 3]],
                                    [self.Phis[1][1, 0]], [self.Phis[1][1, 1]], [self.Phis[1][1, 2]], [self.Phis[1][1, 3]],
                                    [self.Phis[1][2, 0]], [self.Phis[1][2, 1]], [self.Phis[1][2, 2]], [self.Phis[1][2, 3]],
                                    [0], [1.0], [self.images[0].mean()], [0], [self.binning] ])
            numpy.savetxt(fileName, output.T, fmt='%.7f', delimiter='\t', newline='\n', comments='', header=TSVheader)
            self.resultLabel.setText("Phi saved in: {}".format(os.path.join(os.getcwd(), fileName)))
            self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: green;}")

        else:
            self.resultLabel.setText("Please enter a name")
            self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")

    def validate(self):
        # try for each entry if the value is numerical, if they are they are used to change phi
        #   else the ones which aren't numerical are replaced by the last valid value
        phiRotPrev = spam.deformation.computePhi(
            {'r': [self.rArray[0], self.rArray[1], self.rArray[2]]})
        deltaRot = numpy.zeros(3, dtype='<f8')
        try:
            self.tArray[0] = float(self.tZLabel.text())
        except BaseException:
            self.tZLabel.setText("{:.3f}".format(self.tArray[0]))

        try:
            self.tArray[1] = float(self.tYLabel.text())
        except BaseException:
            self.tYLabel.setText("{:.3f}".format(self.tArray[1]))

        try:
            self.tArray[2] = float(self.tXLabel.text())
        except BaseException:
            self.tXLabel.setText("{:.3f}".format(self.tArray[2]))

        if self.axis == "x":
            i = 2
        elif self.axis == "y":
            i = 1
        elif self.axis == "z":
            i = 0

        try:
            self.rArray[i] = float(self.tXLabel.text())
            deltaRot[i] = float(self.rXLabel.text())
            # if deltaRot.sum() != 0:
            newRotPhi = spam.deformation.computePhi({'r': deltaRot})
            totalPhi = numpy.dot(newRotPhi, phiRotPrev)
            # totalPhi = numpy.dot(phiRotPrev, newRotPhi)
            decomposedPhi = spam.deformation.decomposePhi(totalPhi)
            self.rArray = decomposedPhi['r']
            self.rXLabel.setText("{:.2f}".format(self.rArray[0]))
        except BaseException:
            self.rXLabel.setText("{:.2f}".format(self.rArray[0]))
        # try:
        #     self.rArray[2] = float(self.rXLabel.text())
        # except BaseException:
        #
        #     self.rXLabel.setText(str(self.rArray[2]))

        try:
            float(self.zALabel.text())
            if float(self.zALabel.text()) != 1.0:
                self.zArray[0] = float(self.zALabel.text())
                self.zArray[1] = float(self.zALabel.text())
                self.zArray[2] = float(self.zALabel.text())
                self.zArray[3] = float(self.zALabel.text())
            else:
                try:
                    self.zArray[0] = float(self.zZLabel.text())
                except BaseException:
                    self.zZLabel.setText(str(self.zArray[0]))

                try:
                    self.zArray[1] = float(self.zYLabel.text())
                except BaseException:
                    self.zYLabel.setText(str(self.zArray[1]))

                try:
                    self.zArray[2] = float(self.zXLabel.text())
                except BaseException:
                    self.zXLabel.setText(str(self.zArray[2]))
        except BaseException:
            try:
                self.zArray[0] = float(self.zZLabel.text())
            except BaseException:
                self.zZLabel.setText(str(self.zArray[0]))

            try:
                self.zArray[1] = float(self.zYLabel.text())
            except BaseException:
                self.zYLabel.setText(str(self.zArray[1]))

            try:
                self.zArray[2] = float(self.zXLabel.text())
            except BaseException:
                self.zXLabel.setText(str(self.zArray[2]))
            self.zALabel.setText(str(self.zArray[3]))

        transformation = {'t': [self.tArray[0], self.tArray[1], self.tArray[2]],
                          'r': [self.rArray[0], self.rArray[1], self.rArray[2]],
                          'z': [self.zArray[0], self.zArray[1], self.zArray[2]]}
        self.Phis[1] = spam.deformation.computePhi(transformation)
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phis[1])
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phis[1]))
        # call load image to see graphicaly the change
        self.showImages()
        self.iterations = (self.iterations + 1)
        # self.nbIteration.setText("Iterations: " + str(self.iterations))

    def resetTSV(self):
        # replace each value in the entry by the one of the entered Phi eye(4,4) if there wasn't a tsv file load
        self.tArray = [round(self.parameters['t'][0], 3),    round(self.parameters['t'][1], 3),    round(self.parameters['t'][2], 3)]
        self.rArray = [round(self.parameters['r'][0], 3),    round(self.parameters['r'][1], 3),    round(self.parameters['r'][2], 3)]
        self.zArray = [round(self.parameters['U'][0, 0], 3), round(self.parameters['U'][1, 1], 3), round(self.parameters['U'][2, 2], 3), 1]
        # update Phi
        self.Phis[1] = self.Phis[0]
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phis[1])
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phis[1]))
        self.tZLabel.setText("{:.3f}".format(self.tArray[0]))
        self.tYLabel.setText("{:.3f}".format(self.tArray[1]))
        self.tXLabel.setText("{:.3f}".format(self.tArray[2]))
        # self.rZLabel.setText(str(self.rArray[0]))
        # self.rYLabel.setText(str(self.rArray[1]))
        # self.rXLabel.setText(str(self.rArray[2]))
        if self.axis == "x":
            i = 2
        elif self.axis == "y":
            i = 1
        elif self.axis == "z":
            i = 0
        self.rXLabel.setText("{:.2f}".format(self.rArray[i]))
        self.zZLabel.setText(str(self.zArray[0]))
        self.zYLabel.setText(str(self.zArray[1]))
        self.zXLabel.setText(str(self.zArray[2]))
        self.zALabel.setText(str(self.zArray[3]))
        self.iterations = 0
        self.showImages()
        # self.nbIteration.setText("Iterations: " + str(self.iterations))

    def resetIdentity(self):
        self.tArray = [0, 0, 0]
        self.rArray = [0, 0, 0]
        self.zArray = [1, 1, 1, 1]
        self.Phis[1] = numpy.eye(4, 4)
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phis[1])
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phis[1]))
        self.tZLabel.setText("{:.3f}".format(self.tArray[0]))
        self.tYLabel.setText("{:.3f}".format(self.tArray[1]))
        self.tXLabel.setText("{:.3f}".format(self.tArray[2]))
        # self.rZLabel.setText(str(self.rArray[0]))
        # self.rYLabel.setText(str(self.rArray[1]))
        # self.rXLabel.setText(str(self.rArray[2]))
        if self.axis == "x":
            i = 2
        elif self.axis == "y":
            i = 1
        elif self.axis == "z":
            i = 0
        self.rXLabel.setText("{:.2f}".format(self.rArray[i]))
        self.zZLabel.setText(str(self.zArray[0]))
        self.zYLabel.setText(str(self.zArray[1]))
        self.zXLabel.setText(str(self.zArray[2]))
        self.zALabel.setText(str(self.zArray[3]))
        self.iterations = 0
        self.showImages()

    def output(self):
        # just return the modified phy
        out = self.Phis[1]
        return out

    #def flip(self, axe):
        ## just flip the selected axe
        #if axe == 'z':
            #self.images[1] = numpy.flip(self.images[1], 0)
            #self.images[2] = numpy.flip(self.images[2], 0)
        #elif axe == 'y':
            #self.images[1] = numpy.flip(self.images[1], 1)
            #self.images[2] = numpy.flip(self.images[2], 1)
        #elif axe == 'x':
            #self.images[1] = numpy.flip(self.images[1], 2)
            #self.images[2] = numpy.flip(self.images[2], 2)
        #self.resultLabel.setText("Flip option is just for visualisation, it will not transform your image.")
        #self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")

        #self.showImages()

    def equalize(self):
        self.modifyPhi("t" + self.axis.upper(), self.im2Slider.value() - self.im1Slider.value())
        self.slideIm2(self.im1Slider.value())


class QtCropWidget(QWidget):
    def __init__(self, images, phi, crop, names, binning=1, imUpdate=0):
        QWidget.__init__(self)
        self.imUpdate = imUpdate
        self.refImage = images[self.imUpdate]
        self.viewerZ = QtImageViewer.QtImageViewer()
        self.viewerY = QtImageViewer.QtImageViewer()
        self.viewerX = QtImageViewer.QtImageViewer()
        self.images = images
        self.Phi = phi
        self.binning = binning
        self.indexImDisp = 0
        # Update second image
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phi)
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phi))
        self.z = [crop[0].start, crop[0].stop, int((crop[0].stop - crop[0].start) / 2)]
        self.y = [crop[1].start, crop[1].stop, int((crop[1].stop - crop[1].start) / 2)]
        self.x = [crop[2].start, crop[2].stop, int((crop[2].stop - crop[2].start) / 2)]
        gridBig = QGridLayout(self)
        labelAxisZ = QLabel("z")
        labelAxisZRight = QLabel("→ x")
        labelAxisZDown = QLabel("↓\ny")
        gridBig.addWidget(labelAxisZ, 1, 1)
        gridBig.addWidget(labelAxisZRight, 1, 2)
        gridBig.addWidget(labelAxisZDown, 2, 1)

        labelAxisY = QLabel("y")
        labelAxisYRight = QLabel("→ x")
        labelAxisYDown = QLabel("↓\nz")
        gridBig.addWidget(labelAxisY, 1, 3)
        gridBig.addWidget(labelAxisYRight, 1, 4)
        gridBig.addWidget(labelAxisYDown, 2, 3)

        labelAxisX = QLabel("x")
        labelAxisXRight = QLabel("→ y")
        labelAxisXDown = QLabel("↓\nz")
        gridBig.addWidget(labelAxisX, 3, 1)
        gridBig.addWidget(labelAxisXRight, 3, 2)
        gridBig.addWidget(labelAxisXDown, 4, 1)

        gridBig.addWidget(self.viewerZ, 2, 2)
        gridBig.addWidget(self.viewerY, 2, 4)
        gridBig.addWidget(self.viewerX, 4, 2)
        self.showImages()
        grid = QGridLayout()
        self.im1Radio = QRadioButton(names[0])
        self.im1Radio.setChecked(True)
        self.im1Radio.toggled.connect(partial(self.changeImage, 0))
        self.im2Radio = QRadioButton(names[1])
        self.im2Radio.toggled.connect(partial(self.changeImage, 1))
        gridBig.addWidget(self.im1Radio, 3, 3)
        gridBig.addWidget(self.im2Radio, 3, 4)

        self.ZSliderMin = QSlider(QtCore.Qt.Horizontal)
        self.ZSliderMin.setMinimum(1)
        self.ZSliderMin.setMaximum(self.z[1] - 1)
        self.ZSliderMin.setValue(self.z[0])
        self.ZSliderMax = QSlider(QtCore.Qt.Horizontal)
        self.ZSliderMax.setMinimum(self.z[0])
        self.ZSliderMax.setMaximum(self.images[0].shape[0] - 1)
        self.ZSliderMax.setValue(self.z[1])
        self.YSliderMin = QSlider(QtCore.Qt.Horizontal)
        self.YSliderMin.setMinimum(1)
        self.YSliderMin.setMaximum(self.y[1] - 1)
        self.YSliderMin.setValue(self.y[0])
        self.YSliderMax = QSlider(QtCore.Qt.Horizontal)
        self.YSliderMax.setMinimum(self.y[0])
        self.YSliderMax.setMaximum(self.images[0].shape[1] - 1)
        self.YSliderMax.setValue(self.y[1])
        self.XSliderMin = QSlider(QtCore.Qt.Horizontal)
        self.XSliderMin.setMinimum(1)
        self.XSliderMin.setMaximum(self.x[1] - 1)
        self.XSliderMin.setValue(self.x[0])
        self.XSliderMax = QSlider(QtCore.Qt.Horizontal)
        self.XSliderMax.setMinimum(self.x[0])
        self.XSliderMax.setMaximum(self.images[0].shape[2] - 1)
        self.XSliderMax.setValue(self.x[1])

        self.ZSliderView = QSlider(QtCore.Qt.Horizontal)
        self.ZSliderView.setMinimum(self.z[0])
        self.ZSliderView.setMaximum(self.z[1])
        self.ZSliderView.setValue(self.z[2])
        self.YSliderView = QSlider(QtCore.Qt.Horizontal)
        self.YSliderView.setMinimum(self.y[0])
        self.YSliderView.setMaximum(self.y[1])
        self.YSliderView.setValue(self.y[2])
        self.XSliderView = QSlider(QtCore.Qt.Horizontal)
        self.XSliderView.setMinimum(self.x[0])
        self.XSliderView.setMaximum(self.x[1])
        self.XSliderView.setValue(self.x[2])

        self.ZSliderMin.valueChanged.connect(self.slideZMin)
        self.ZSliderMax.valueChanged.connect(self.slideZMax)
        self.YSliderMin.valueChanged.connect(self.slideYMin)
        self.YSliderMax.valueChanged.connect(self.slideYMax)
        self.XSliderMin.valueChanged.connect(self.slideXMin)
        self.XSliderMax.valueChanged.connect(self.slideXMax)
        self.ZSliderView.valueChanged.connect(self.slideZView)
        self.YSliderView.valueChanged.connect(self.slideYView)
        self.XSliderView.valueChanged.connect(self.slideXView)

        ZMinLabel = QLabel("min Z:")
        grid.addWidget(ZMinLabel, 1, 1)
        self.ZMinLabelValue = QLabel(str(self.ZSliderMin.value()))
        grid.addWidget(self.ZMinLabelValue, 1, 2)
        ZMaxLabel = QLabel("max Z:")
        grid.addWidget(ZMaxLabel, 1, 3)
        self.ZMaxLabelValue = QLabel(str(self.ZSliderMax.value()))
        grid.addWidget(self.ZMaxLabelValue, 1, 4)
        ZViewLabel = QLabel("view Z:")
        grid.addWidget(ZViewLabel, 1, 5)
        self.ZViewLabelValue = QLabel(str(self.ZSliderView.value()))
        grid.addWidget(self.ZViewLabelValue, 1, 6)
        YMinLabel = QLabel("min Y:")
        grid.addWidget(YMinLabel, 3, 1)
        self.YMinLabelValue = QLabel(str(self.YSliderMin.value()))
        grid.addWidget(self.YMinLabelValue, 3, 2)
        YMaxLabel = QLabel("max Y:")
        grid.addWidget(YMaxLabel, 3, 3)
        self.YMaxLabelValue = QLabel(str(self.YSliderMax.value()))
        grid.addWidget(self.YMaxLabelValue, 3, 4)
        YViewLabel = QLabel("view Y:")
        grid.addWidget(YViewLabel, 3, 5)
        self.YViewLabelValue = QLabel(str(self.YSliderView.value()))
        grid.addWidget(self.YViewLabelValue, 3, 6)
        XMinLabel = QLabel("min X:")
        grid.addWidget(XMinLabel, 5, 1)
        self.XMinLabelValue = QLabel(str(self.XSliderMin.value()))
        grid.addWidget(self.XMinLabelValue, 5, 2)
        XMaxLabel = QLabel("max X:")
        grid.addWidget(XMaxLabel, 5, 3)
        self.XMaxLabelValue = QLabel(str(self.XSliderMax.value()))
        grid.addWidget(self.XMaxLabelValue, 5, 4)
        XViewLabel = QLabel("view X:")
        grid.addWidget(XViewLabel, 5, 5)
        self.XViewLabelValue = QLabel(str(self.XSliderView.value()))
        grid.addWidget(self.XViewLabelValue, 5, 6)
        grid.addWidget(self.ZSliderMin, 2, 1, 1, 2)
        grid.addWidget(self.ZSliderMax, 2, 3, 1, 2)
        grid.addWidget(self.ZSliderView, 2, 5, 1, 2)
        grid.addWidget(self.YSliderMin, 4, 1, 1, 2)
        grid.addWidget(self.YSliderMax, 4, 3, 1, 2)
        grid.addWidget(self.YSliderView, 4, 5, 1, 2)
        grid.addWidget(self.XSliderMin, 6, 1, 1, 2)
        grid.addWidget(self.XSliderMax, 6, 3, 1, 2)
        grid.addWidget(self.XSliderView, 6, 5, 1, 2)
        saveButton = QPushButton('save', self)
        saveButton.clicked.connect(self.saveTSVCrop)
        grid.addWidget(saveButton, 7, 5, 1, 2)
        labelSave = QLabel("Save your crop settings in a tsv file for later use (optional)")
        self.nameEntry = QLineEdit("{}-{}-crop-bin{}.tsv".format(names[0][0:-4], names[1][0:-4], self.binning))
        self.resultLabel = QLabel()
        grid.addWidget(labelSave, 7, 1, 1, 2)
        grid.addWidget(self.nameEntry, 7, 3, 1, 2)
        grid.addWidget(self.resultLabel, 8, 3, 1, 2)
        gridBig.addLayout(grid, 4, 4)

    def showImages(self):
        self.viewerZ.setImage(qimage2ndarray.array2qimage(self.images[self.indexImDisp][    self.z[2],       self.y[0]:self.y[1], self.x[0]:self.x[1]], normalize=True))
        self.viewerY.setImage(qimage2ndarray.array2qimage(self.images[self.indexImDisp][self.z[0]:self.z[1],       self.y[2],     self.x[0]:self.x[1]], normalize=True))
        self.viewerX.setImage(qimage2ndarray.array2qimage(self.images[self.indexImDisp][self.z[0]:self.z[1], self.y[0]:self.y[1],     self.x[2]      ], normalize=True))

    def slideZMin(self, value):
        if value < self.z[1]:
            self.z[0] = value
        else:
            self.z[0] = self.z[1] - 1
            self.ZSliderMin.setValue(self.z[1] - 1)
        self.ZSliderMax.setMinimum(self.z[0])
        self.ZSliderView.setMinimum(self.z[0])
        if self.z[2] < value:
            self.z[2] = self.z[0]
            self.ZSliderView.setValue(self.z[0])
        self.ZMinLabelValue.setText(str(self.ZSliderMin.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideZMax(self, value):
        if value > self.z[0]:
            self.z[1] = value
        else:
            self.z[1] = self.z[0] + 1
            self.ZSliderMax.setValue(self.z[0] + 1)
        self.ZSliderMin.setMaximum(self.z[1] - 1)
        self.ZSliderView.setMaximum(self.z[1] - 1)
        if self.z[2] > value:
            self.z[2] = self.z[1]
            self.ZSliderView.setValue(self.z[1])
        self.ZMaxLabelValue.setText(str(self.ZSliderMax.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideYMin(self, value):
        if value < self.y[1]:
            self.y[0] = value
        else:
            self.y[0] = self.y[1] - 1
            self.YSliderMin.setValue(self.y[1] - 1)
        self.YSliderMax.setMinimum(self.y[0])
        self.YSliderView.setMinimum(self.y[0])
        if self.y[2] < value:
            self.y[2] = self.y[0]
            self.YSliderView.setValue(self.y[0])
        self.YMinLabelValue.setText(str(self.YSliderMin.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideYMax(self, value):
        if value > self.y[0]:
            self.y[1] = value
        else:
            self.y[1] = self.y[0] + 1
            self.YSliderMax.setValue(self.y[0] + 1)
        self.YSliderMin.setMaximum(self.y[1] - 1)
        self.YSliderView.setMaximum(self.y[1] - 1)
        if self.y[2] > value:
            self.y[2] = self.y[1]
            self.YSliderView.setValue(self.y[1])
        self.YMaxLabelValue.setText(str(self.YSliderMax.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideXMin(self, value):
        if value < self.x[1]:
            self.x[0] = value
        else:
            self.x[0] = self.x[1] - 1
            self.XSliderMin.setValue(self.x[1] - 1)
        self.XSliderMax.setMinimum(self.x[0])
        self.XSliderView.setMinimum(self.x[0])
        if self.x[2] < value:
            self.x[2] = self.x[0]
            self.XSliderView.setValue(self.x[0])
        self.XMinLabelValue.setText(str(self.XSliderMin.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideXMax(self, value):
        if value > self.x[0]:
            self.x[1] = value
        else:
            self.x[1] = self.x[0] + 1
            self.XSliderMax.setValue(self.x[0] + 1)
        self.XSliderMin.setMaximum(self.x[1] - 1)
        self.XSliderView.setMaximum(self.x[1] - 1)
        if self.x[2] > value:
            self.x[2] = self.x[1]
            self.XSliderView.setValue(self.x[1])
        self.XMaxLabelValue.setText(str(self.XSliderMax.value()))
        self.resultLabel.setText("Crop settings need to be saved")
        self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")
        self.showImages()

    def slideZView(self, value):
        if value > self.z[0] and value < self.z[1]:
            self.z[2] = value
        elif value > self.z[0] and value > self.z[1]:
            self.z[2] = self.z[1]
            self.ZSliderView.setValue(self.z[1])
        elif value < self.z[0] and value < self.z[1]:
            self.z[2] = self.z[0]
            self.ZSliderView.setValue(self.z[0])
        self.ZViewLabelValue.setText(str(self.ZSliderView.value()))
        self.showImages()

    def slideYView(self, value):
        if value > self.y[0] and value < self.y[1]:
            self.y[2] = value
        elif value > self.y[0] and value > self.y[1]:
            self.y[2] = self.y[1]
            self.YSliderView.setValue(self.y[1])
        elif value < self.y[0] and value < self.y[1]:
            self.x[2] = self.x[0]
            self.YSliderView.setValue(self.x[0])
        self.YViewLabelValue.setText(str(self.YSliderView.value()))
        self.showImages()

    def slideXView(self, value):
        if value > self.x[0] and value < self.x[1]:
            self.x[2] = value
        elif value > self.x[0] and value > self.x[1]:
            self.x[2] = self.x[1]
            self.XSliderView.setValue(self.x[1])
        elif value < self.x[0] and value < self.x[1]:
            self.x[2] = self.x[0]
            self.XSliderView.setValue(self.x[0])
        self.XViewLabelValue.setText(str(self.XSliderView.value()))
        self.showImages()

    def saveTSVCrop(self):
        if self.nameEntry.text() != "":
            tmp = self.nameEntry.text()
            fileName = tmp if tmp.split(".")[-1] in ["tsv"] else tmp + ".tsv"
            TSVheader = "Zs\tZe\tYs\tYe\tXs\tXe\tbin"
            output = numpy.array([[self.z[0]], [self.z[1]],
                                  [self.y[0]], [self.y[1]],
                                  [self.x[0]], [self.x[1]],
                                  [self.binning]])
            numpy.savetxt(fileName,
                          output.T,
                          fmt='%.7f',
                          delimiter='\t',
                          newline='\n',
                          comments='',
                          header=TSVheader)
            self.resultLabel.setText("Crop saved in: {}".format(os.path.join(os.getcwd(), fileName)))
            self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: green;}")
        else:
            self.resultLabel.setText("Please enter a name")
            self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: orange;}")

    def output(self):
        return(slice(self.z[0], self.z[1]), slice(self.y[0], self.y[1]), slice(self.x[0], self.x[1]))

    def changeImage(self, val):
        self.indexImDisp = val
        self.showImages()


class JHist(QWidget):
    def __init__(self, images, phi, crop, fontColor, names, imUpdate):
        import spam.helpers
        QWidget.__init__(self)
        self.imUpdate = imUpdate
        self.refImage = images[imUpdate]
        self.images = images
        self.Phi = phi
        if   self.imUpdate == 0:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=self.Phi)
        elif self.imUpdate == 1:
            self.images[self.imUpdate] = spam.DIC.applyPhi(self.refImage, Phi=numpy.linalg.inv(self.Phi))
        self.crop = crop
        self.images[0] = self.images[0][self.crop]
        self.images[1] = self.images[1][self.crop]
        self.fontColor = fontColor
        self.names = names

        # rescale both images to min/max
        self.greyLimitsOrig = [[self.images[0].min(), self.images[0].max()],
                               [self.images[1].min(), self.images[1].max()]]
        self.greyLimitsCrop = [[self.images[0].min(), self.images[0].max()],
                               [self.images[1].min(), self.images[1].max()]]

        self.imagesRescaled = []
        for i in range(2):
            print("Rescale im{} from {} to int8".format(
                i + 1, self.images[i].dtype))
            self.imagesRescaled.append(spam.helpers.rescaleToInteger(
                self.images[i], scale=self.greyLimitsOrig[i], nBytes=1))

        self.grid = QGridLayout(self)
        self.grid.setColumnStretch(1, 2)
        self.grid.setColumnStretch(2, 1)
        self.grid.setRowStretch(1, 2)
        self.grid.setRowStretch(3, 5)

        self.BINS = 64
        self.minDistanceSlider = QSlider(QtCore.Qt.Horizontal)
        self.minDistanceSlider.setMinimum(0)
        self.minDistanceSlider.setMaximum(self.BINS)
        self.minDistanceSlider.setValue(self.BINS / 20)
        self.nbMaxPeakSlider = QSlider(QtCore.Qt.Horizontal)
        self.nbMaxPeakSlider.setMinimum(1)
        self.nbMaxPeakSlider.setMaximum(40)
        self.nbMaxPeakSlider.setValue(10)
        self.selectBins = QComboBox()
        self.selectBins.addItems(["Coarse", "Medium", "Fine"])
        self.selectBins.currentIndexChanged.connect(self.changeBins)
        self.grid.addWidget(self.selectBins, 4, 1)

        # we set sliders min and max to be the actual initial max and min value of the images
        self.im1MinSlider = QSlider(QtCore.Qt.Horizontal)
        self.im1MinSlider.setMinimum(self.greyLimitsOrig[0][0])
        self.im1MinSlider.setMaximum(self.greyLimitsOrig[0][1])
        self.im1MinSlider.setValue(  self.greyLimitsOrig[0][0])

        self.im1MaxSlider = QSlider(QtCore.Qt.Horizontal)
        self.im1MaxSlider.setMinimum(self.greyLimitsOrig[0][0])
        self.im1MaxSlider.setMaximum(self.greyLimitsOrig[0][1])
        self.im1MaxSlider.setValue(  self.greyLimitsOrig[0][1])

        self.im2MinSlider = QSlider(QtCore.Qt.Horizontal)
        self.im2MinSlider.setMinimum(self.greyLimitsOrig[1][0])
        self.im2MinSlider.setMaximum(self.greyLimitsOrig[1][1])
        self.im2MinSlider.setValue(  self.greyLimitsOrig[1][0])

        self.im2MaxSlider = QSlider(QtCore.Qt.Horizontal)
        self.im2MaxSlider.setMinimum(self.greyLimitsOrig[1][0])
        self.im2MaxSlider.setMaximum(self.greyLimitsOrig[1][1])
        self.im2MaxSlider.setValue(self.greyLimitsOrig[1][1])

        slidegrid = QGridLayout()
        slidegrid.addWidget(QLabel("Histogram parameters:"), 0, 1)
        im1MinSliderLabel = QLabel(names[0] + " min :")
        self.im1MinSliderLabelValue = QLabel(  "0%\n{}".format(self.greyLimitsOrig[0][0]))
        self.im1MinSliderLabelValue.setFixedWidth(50)
        im1MaxSliderLabel = QLabel(names[0] + " max :")
        self.im1MaxSliderLabelValue = QLabel("100%\n{}".format(self.greyLimitsOrig[0][1]))
        self.im1MaxSliderLabelValue.setFixedWidth(50)
        im2MinSliderLabel = QLabel(names[1] + " min :")
        self.im2MinSliderLabelValue = QLabel(  "0%\n{}".format(self.greyLimitsOrig[1][0]))
        self.im2MinSliderLabelValue.setFixedWidth(50)
        im2MaxSliderLabel = QLabel(names[1] + " max :")
        self.im2MaxSliderLabelValue = QLabel("100%\n{}".format(self.greyLimitsOrig[1][1]))
        self.im2MaxSliderLabelValue.setFixedWidth(50)
        distanceMinLabel = QLabel(
            "Distance min (or whateverwhaaatever this is):")
        self.distanceMinSliderLabelValue = QLabel(str(self.minDistanceSlider.value()))
        self.distanceMinSliderLabelValue.setFixedWidth(25)
        plusDistanceButton = QPushButton("+")
        minusDistanceButton = QPushButton("-")

        nbPeakLabel = QLabel("Number of peaks max")
        self.nbPeakLabelValue = QLabel(str(self.nbMaxPeakSlider.value()))
        self.nbPeakLabelValue.setFixedWidth(25)
        plusNBPeakButton = QPushButton("+")
        minusNBPeakButton = QPushButton("-")

        self.im1MinSlider.valueChanged.connect(self.slideIm1Min)
        self.im1MaxSlider.valueChanged.connect(self.slideIm1Max)
        self.im2MinSlider.valueChanged.connect(self.slideIm2Min)
        self.im2MaxSlider.valueChanged.connect(self.slideIm2Max)
        self.minDistanceSlider.valueChanged.connect(self.changeDistance)
        self.nbMaxPeakSlider.valueChanged.connect(self.changeNBP)
        plusDistanceButton.clicked.connect(partial(self.plusOrMinusDist, "+"))
        minusDistanceButton.clicked.connect(partial(self.plusOrMinusDist, "-"))
        plusNBPeakButton.clicked.connect(partial(self.plusOrMinusNBP, "+"))
        minusNBPeakButton.clicked.connect(partial(self.plusOrMinusNBP, "-"))

        slidegrid.addWidget(im1MinSliderLabel, 1, 1)
        slidegrid.addWidget(self.im1MinSliderLabelValue, 1, 2)
        slidegrid.addWidget(im1MaxSliderLabel, 1, 5)
        slidegrid.addWidget(self.im1MaxSliderLabelValue, 1, 6)
        blankLabel1 = QLabel("")
        slidegrid.addWidget(blankLabel1, 2, 1)
        slidegrid.addWidget(im2MinSliderLabel, 3, 1)
        slidegrid.addWidget(self.im2MinSliderLabelValue, 3, 2,)
        slidegrid.addWidget(im2MaxSliderLabel, 3, 5)
        slidegrid.addWidget(self.im2MaxSliderLabelValue, 3, 6)
        blankLabel2 = QLabel("")
        slidegrid.addWidget(blankLabel2, 4, 1)
        blankLabel3 = QLabel("")
        blankLabel3.setFixedWidth(100)
        slidegrid.addWidget(blankLabel3, 0, 7, 1, 2)
        slidegrid.addWidget(self.im1MinSlider, 1, 3, 1, 2)
        slidegrid.addWidget(self.im1MaxSlider, 1, 7, 1, 2)
        slidegrid.addWidget(self.im2MinSlider, 3, 3, 1, 2)
        slidegrid.addWidget(self.im2MaxSlider, 3, 7, 1, 2)
        slidegrid.addWidget(distanceMinLabel, 5, 1, 1, 2)
        slidegrid.addWidget(minusDistanceButton, 5, 4)
        slidegrid.addWidget(plusDistanceButton, 5, 5)
        slidegrid.addWidget(self.distanceMinSliderLabelValue, 5, 3)
        slidegrid.addWidget(self.minDistanceSlider, 5, 6, 1, 3)
        slidegrid.addWidget(nbPeakLabel, 6, 1, 1, 2)
        slidegrid.addWidget(minusNBPeakButton, 6, 4)
        slidegrid.addWidget(plusNBPeakButton, 6, 5)
        slidegrid.addWidget(self.nbPeakLabelValue, 6, 3)
        slidegrid.addWidget(self.nbMaxPeakSlider, 6, 6, 1, 3)

        applyButton = QPushButton("Recompute histogram")
        applyButton.clicked.connect(self.computeHistogram)
        blankLabel3 = QLabel("")
        slidegrid.addWidget(blankLabel3, 7, 1)
        slidegrid.addWidget(applyButton, 8, 1, 1, 7)
        self.grid.addLayout(slidegrid, 1, 2)
        self.grid.addWidget(QLabel(""), 2, 2)
        self.resGrid = QGridLayout()
        self.grid.addLayout(self.resGrid, 3, 2)

        self.computeHistogram()

    def slideIm1Max(self, value):
        if value <= self.greyLimitsCrop[0][0]:
            self.im1MaxSlider.setValue(self.greyLimitsCrop[0][0] + 1)
        self.greyLimitsCrop[0][1] = self.im1MaxSlider.value()
        p = 100.0 * (self.greyLimitsCrop[0][1] - self.greyLimitsOrig[0][0]) / (
            self.greyLimitsOrig[0][1] - self.greyLimitsOrig[0][0])
        self.im1MaxSliderLabelValue.setText(
            "{:,.0f}%\n{}".format(p, self.greyLimitsCrop[0][1]))

    def slideIm2Max(self, value):
        if value <= self.greyLimitsCrop[1][0]:
            self.im2MaxSlider.setValue(self.greyLimitsCrop[1][0] + 1)
        self.greyLimitsCrop[1][1] = self.im2MaxSlider.value()
        p = 100.0 * (self.greyLimitsCrop[1][1] - self.greyLimitsOrig[1][0]) / (
            self.greyLimitsOrig[1][1] - self.greyLimitsOrig[1][0])
        self.im2MaxSliderLabelValue.setText(
            "{:,.0f}%\n{}".format(p, self.greyLimitsCrop[1][1]))

    def slideIm1Min(self, value):
        if value >= self.greyLimitsCrop[0][1]:
            self.im1MinSlider.setValue(self.greyLimitsCrop[0][1] - 1)
        self.greyLimitsCrop[0][0] = self.im1MinSlider.value()
        p = 100.0 * (self.greyLimitsCrop[0][0] - self.greyLimitsOrig[0][0]) / (
            self.greyLimitsOrig[0][1] - self.greyLimitsOrig[1][0])
        self.im1MinSliderLabelValue.setText(
            "{:,.0f}%\n{}".format(p, self.greyLimitsCrop[0][0]))

    def slideIm2Min(self, value):
        if value >= self.greyLimitsCrop[1][1]:
            self.im2MinSlider.setValue(self.greyLimitsCrop[1][1] - 1)
        self.greyLimitsCrop[1][0] = self.im2MinSlider.value()
        p = 100.0 * (self.greyLimitsCrop[1][0] - self.greyLimitsOrig[1][0]) / (
            self.greyLimitsOrig[1][1] - self.greyLimitsOrig[1][0])
        self.im2MinSliderLabelValue.setText(
            "{:,.0f}%\n{}".format(p, self.greyLimitsCrop[1][0]))

    def changeBins(self, i):
        if i == 0:
            self.BINS = 64
        elif i == 1:
            self.BINS = 128
        elif i == 2:
            self.BINS = 256

        self.minDistanceSlider.setMaximum(self.BINS)
        self.computeHistogram()

    def changeDistance(self):
        self.distanceMinSliderLabelValue.setText(
            str(self.minDistanceSlider.value()))

    def plusOrMinusDist(self, val):
        if val == '+' and self.minDistanceSlider.value() < self.minDistanceSlider.maximum():
            self.minDistanceSlider.setValue(self.minDistanceSlider.value() + 1)
        elif val == '-' and self.minDistanceSlider.value() > self.minDistanceSlider.minimum():
            self.minDistanceSlider.setValue(self.minDistanceSlider.value() - 1)
        self.changeDistance()

    def changeNBP(self):
        self.nbPeakLabelValue.setText(
            str(self.nbMaxPeakSlider.value()))

    def plusOrMinusNBP(self, val):
        if val == '+' and self.nbMaxPeakSlider.value() < self.nbMaxPeakSlider.maximum():
            self.nbMaxPeakSlider.setValue(self.nbMaxPeakSlider.value() + 1)
        elif val == '-' and self.nbMaxPeakSlider.value() > self.nbMaxPeakSlider.minimum():
            self.nbMaxPeakSlider.setValue(self.nbMaxPeakSlider.value() - 1)
        self.changeDistance()

    def computeHistogram(self):
        # import spam.helpers
        import skimage.feature

        # delete max checkboxes
        for i in reversed(range(self.resGrid.count())):
            self.resGrid.itemAt(i).widget().setParent(None)

        self.hist, xedge, yedge = numpy.histogram2d((numpy.ravel(self.images[0])), numpy.ravel(self.images[1]), range=self.greyLimitsCrop, bins=(self.BINS, self.BINS))
        self.hist /= self.hist.sum()

        # find maxima
        minDistance = self.minDistanceSlider.value()
        excludeBorder = False
        maxTmp1 = skimage.feature.peak_local_max(self.hist, min_distance=minDistance, num_peaks=self.nbMaxPeakSlider.value(), exclude_border=excludeBorder)
        self.maxMax = min(self.nbMaxPeakSlider.value(), len(maxTmp1))

        # Organise maxima into muF, muG, p(f,g) the sort at take the maximum
        maxTmp2 = numpy.zeros((self.maxMax, 5))
        for i, (f, g) in enumerate(maxTmp1):
            maxTmp2[i] = [f, g, self.hist[f, g], 0, 0]
            if i >= self.maxMax - 1:
                break

        # maxima of size n times 5
        # [x, y, z, a, b, c circle radius (for fitting), has been fitted (dirty hack to pass variable to fitEllipsoid)]
        self.maxima = [m for m in maxTmp2[maxTmp2[:, 2].argsort()[::-1]]]

        # create max checkboxes
        titre = QLabel("Select your maxima for the fitting :")
        titre.setFixedWidth(600)
        self.resGrid.addWidget(titre, 1, 0, 1, 5)
        self.checkMaxima = []
        self.slides = []
        self.fitButtons = []
        self.distanceLabels = []
        self.resLabels = []
        self.gaussianParameters = []  # x,y,z,a,b,c for each fitted point

        for i in range(len(self.maxima)):
            check = QCheckBox("M{}({}, {}) = {:.2g}".format(i + 1, *self.maxima[i]))
            self.checkMaxima.append(check)
            self.resGrid.addWidget(check, 2 * (i % 10) + 2, 4 * int(i / 10))
            self.checkMaxima[i].toggled.connect(self.fitEllipsoid)
            slide = QSlider(QtCore.Qt.Horizontal)
            slide.setMinimum(0)
            slide.setMaximum(self.BINS)
            slide.setValue(0)
            slide.setMinimumWidth(75)
            self.resGrid.addWidget(slide, 2 * (i % 10) + 2, 4 * int(i / 10) + 1)
            slide.hide()
            self.slides.append(slide)
            button = QPushButton("fit")
            self.resGrid.addWidget(button, 2 * (i % 10) + 2, 4 * int(i / 10) + 3)
            button.hide()
            self.fitButtons.append(button)
            labeld = QLabel()
            labeld.setFixedWidth(15)
            self.resGrid.addWidget(labeld, 2 * (i % 10) + 2, 4 * int(i / 10) + 2)
            labeld.hide()
            self.distanceLabels.append(labeld)
            label = QLabel("")
            label.setMinimumWidth(200)

            self.resGrid.addWidget(label, (2 * (i % 10) + 2) + 1, 4 * int(i / 10), 1, 4)

            self.resLabels.append(label)
        # for i in range(len(self.checkMaxima)):

        self.showHistogram()

    def fitEllipsoid(self):
        from scipy.optimize import curve_fit

        # for fitting
        GLOBALx = 0.0
        GLOBALy = 0.0
        GLOBALz = 0.0

        def computeLambda(a, b, c, x, xMean, y, yMean):
            return numpy.longfloat(0.5 * (a * (x - xMean)**2 + 2.0 * b * (x - xMean) * (y - yMean) + c * (y - yMean)**2))

        def gaussian2Delliptical(XY, a, b, c):
            # invert x and y on purpose to be consistent with H
            grid = numpy.array(numpy.meshgrid(XY[1], XY[0]))
            field = numpy.zeros(grid.shape[1:3])
            for ny in range(grid.shape[2]):
                y = grid[0, 0, ny]
                for nx in range(grid.shape[1]):
                    x = grid[1, nx, 0]
                    field[nx, ny] = float(
                        GLOBALz) * numpy.exp(-computeLambda(a, b, c, x, GLOBALx, y, GLOBALy))
            return field.ravel()

        for i, check in enumerate(self.checkMaxima):
            checked = check.isChecked()
            computed = bool(self.maxima[i][4])

            if checked and not computed:
                print("fit maximum number {}".format(i + 1))
                self.maxima[i][3] = self.BINS / 10
                self.maxima[i][4] = 1
                self.slides[i].show()
                self.slides[i].setValue(self.maxima[i][3])
                self.slides[i].valueChanged.connect(partial(self.slideIndexedValChange, i))
                self.fitButtons[i].show()
                self.fitButtons[i].clicked.connect(partial(self.reFit, i))
                self.distanceLabels[i].setText(str(self.slides[i].value()))
                self.distanceLabels[i].show()
                GLOBALx = self.maxima[i][0]
                GLOBALy = self.maxima[i][1]
                GLOBALz = self.maxima[i][2]
                fitDistance = self.maxima[i][3]

                # modified histogram taking into account the fitting distance
                pFit = self.hist.copy()
                for nf in range(pFit.shape[0]):
                    for ng in range(pFit.shape[1]):
                        dist = numpy.sqrt(
                            (nf - GLOBALx)**2.0 + (ng - GLOBALy)**2.0)  # cicrle
                        if dist > fitDistance:
                            pFit[nf, ng] = 0.0

                X = numpy.linspace(0, self.BINS - 1, self.BINS)
                Y = numpy.linspace(0, self.BINS - 1, self.BINS)
                (a, b, c), _ = curve_fit(gaussian2Delliptical, (X, Y), pFit.ravel(), p0=(1, 1, 1))
                print("\tFit:\t\t a={:.2f}\t b={:.2f}\t c={:.2f}\t Hessian: {:.2f}".format(a, b, c, a * c - b**2))
                self.resLabels[i].setText("Fit: a={:.2f} b={:.2f} c={:.2f} Hessian: {:.2f}".format(a, b, c, a * c - b**2))

                tmpGaussianP = [self.maxima[i][0], self.maxima[i][1], self.maxima[i][2], a, b, c]
                self.gaussianParameters.append(tmpGaussianP)
            elif not checked and computed:
                self.maxima[i][3] = 0
                self.maxima[i][4] = 0
                j = 0
                find = False
                while j < len(self.gaussianParameters) and not find:
                    if self.gaussianParameters[j][0] == self.maxima[i][0] and self.gaussianParameters[j][1] == self.maxima[i][1]:
                        self.gaussianParameters.pop(j)
                        find = True
                    j += 1
                self.slides[i].hide()
                self.fitButtons[i].hide()
                self.distanceLabels[i].hide()
                self.resLabels[i].setText("")
                print("delete maximum number {}".format(i + 1))

        self.showHistogram()

    def showHistogram(self):
        # import scipy.ndimage

        # i = QLabel()
        # i.setPixmap(QtGui.QPixmap(self.hist))
        # self.grid.addWidget(i,1,1)
        # histogram = ImageLabel(qimage2ndarray.array2qimage(self.hist.reshape((self.BINS, self.BINS))))
        # self.grid.addWidget(histogram, 1, 1)

        f = Figure()  # create a matplotlib figure
        f.clf()
        # f.patch.set_facecolor("None")
        # f.patch.set_alpha(0.0)

        a = f.add_subplot(111)

        # a.patch.set_facecolor("None")
        # a.patch.set_alpha(0.0)
        # a.spines['bottom'].set_color(self.fontColor)
        # a.spines['top'].set_color(self.fontColor)
        # a.spines['right'].set_color(self.fontColor)
        # a.spines['left'].set_color(self.fontColor)
        # a.tick_params(axis='x', colors=self.fontColor)
        # a.tick_params(axis='y', colors=self.fontColor)
        # a.yaxis.label.set_color(self.fontColor)
        # a.xaxis.label.set_color(self.fontColor)
        # a.title.set_color(self.fontColor)

        tmp = self.hist.copy()
        tmp[self.hist <= 0] = numpy.nan
        tmp = numpy.log(tmp)
        extent = [self.greyLimitsCrop[0][0], self.greyLimitsCrop[0][1], self.greyLimitsCrop[1][0], self.greyLimitsCrop[1][1]]
        # aspect = float(extent[1]-extent[0]) / float(extent[3]-extent[2])
        aspect = 1.0
        a.imshow(tmp.T, extent=extent, aspect=aspect, origin='lower')
        a.set_xlabel(self.names[0], fontsize='xx-large')
        a.set_ylabel(self.names[1], fontsize='xx-large')
        for i, m in enumerate(self.maxima):
            x = m[0] * (extent[1] - extent[0]) / float(self.BINS) + extent[0]
            y = m[1] * (extent[3] - extent[2]) / float(self.BINS) + extent[2]
            r = m[3] * (extent[3] - extent[2]) / float(self.BINS)
            a.plot(x, y, 'r*')
            # a.annotate(i + 1, (x, y), color=self.fontColor)
            a.annotate(i + 1, (x, y))
            if m[3] > 0:
                a.add_artist(plt.Circle((x, y), r, color='r', fill=False))

        # histogram image widget
        self.plotWidget = FigureCanvas(f)
        self.plotWidget.setStyleSheet("background-color:transparent;")
        self.grid.addWidget(self.plotWidget, 1, 1, 3, 1)

    # def output(self):
    #     checkedBoxes = []
    #     for i in range(len(self.checkMaxima)):
    #         if self.checkMaxima[i].isChecked():
    #             checkedBoxes.append(self.maxima[i])
    #     return checkedBoxes

    def slideIndexedValChange(self, index):
        self.maxima[index][3] = self.slides[index].value()
        self.distanceLabels[index].setText(str(self.slides[index].value()))
        self.resLabels[index].setText("\tNeed to be fitted")
        self.showHistogram()

    def reFit(self, index):
        from scipy.optimize import curve_fit
        # for fitting
        GLOBALx = 0.0
        GLOBALy = 0.0
        GLOBALz = 0.0

        def computeLambda(a, b, c, x, xMean, y, yMean):
            return numpy.longfloat(0.5 * (a * (x - xMean)**2 + 2.0 * b * (x - xMean) * (y - yMean) + c * (y - yMean)**2))

        def gaussian2Delliptical(XY, a, b, c):
            # invert x and y on purpose to be consistent with H
            grid = numpy.array(numpy.meshgrid(XY[1], XY[0]))
            field = numpy.zeros(grid.shape[1:3])
            for ny in range(grid.shape[2]):
                y = grid[0, 0, ny]
                for nx in range(grid.shape[1]):
                    x = grid[1, nx, 0]
                    field[nx, ny] = float(GLOBALz) * numpy.exp(-computeLambda(a, b, c, x, GLOBALx, y, GLOBALy))
            return field.ravel()

        GLOBALx = self.maxima[index][0]
        GLOBALy = self.maxima[index][1]
        GLOBALz = self.maxima[index][2]
        print(index)
        fitDistance = self.maxima[index][3]
        pFit = self.hist.copy()
        for nf in range(pFit.shape[0]):
            for ng in range(pFit.shape[1]):
                dist = numpy.sqrt((nf - GLOBALx)**2.0 + (ng - GLOBALy)**2.0)  # cicrle
                if dist > fitDistance:
                    pFit[nf, ng] = 0.0

        X = numpy.linspace(0, self.BINS - 1, self.BINS)
        Y = numpy.linspace(0, self.BINS - 1, self.BINS)
        (a, b, c), _ = curve_fit(gaussian2Delliptical, (X, Y), pFit.ravel(), p0=(1, 1, 1))
        print("\tFit:\t\t a={:.2f}\t b={:.2f}\t c={:.2f}\t Hessian: {:.2f}".format(a, b, c, a * c - b**2))
        self.resLabels[index].setText("Fit: a={:.2f} b={:.2f} c={:.2f} Hessian: {:.2f}".format(a, b, c, a * c - b**2))
        self.resLabels[index].show()
        j = 0
        find = False
        while j < len(self.gaussianParameters) and not find:
            if self.gaussianParameters[j][0] == self.maxima[index][0] and self.gaussianParameters[j][1] == self.maxima[index][1]:
                self.gaussianParameters.pop(j)
                find = True
            j += 1
        tmpGaussianP = [self.maxima[index][0],
                        self.maxima[index][1], self.maxima[index][2], a, b, c]
        self.gaussianParameters.append(tmpGaussianP)


class PhaseDiagram(QWidget):
    def __init__(self, gaussianParameters, bins, jointHistogram, names):
        QWidget.__init__(self)

        # variables
        self.gaussianParameters = gaussianParameters
        self.jointHistogram = jointHistogram
        self.BINS = bins
        self.voxelCoverage = 1.0
        self.sigma = 1.0
        self.distanceType = 0
        self.names = names
        # display
        self.grid = QGridLayout(self)

        # do things
        self.findFullCoverage()  # it defines self.sigma so put it before sliders
        # self.computePhaseDiagram()

        self.selectDistanceType = QComboBox()
        self.selectDistanceType.addItems(["Maximum distance", "Mahalanobis"])
        self.selectDistanceType.currentIndexChanged.connect(self.changeDistanceType)
        # helper function to compute distances
        self.grid.addWidget(self.selectDistanceType, 2, 2)

    def distanceMax(self, x, y, gp):
        xG, yG, zG, a, b, c = gp
        if self.distanceType == 0:
            # maximum distance
            return (a * (x - xG)**2 + 2.0 * b * (x - xG) * (y - yG) + c * (y - yG)**2) - numpy.log(zG)
        else:
            # Mahalanobis distance
            return numpy.sqrt((a * (x - xG)**2 + 2.0 * b * (x - xG) * (y - yG) + c * (y - yG)**2))

    def changeDistanceType(self, i):
        self.distanceType = i
        self.findFullCoverage()

    def changeSigma(self):
        self.sigma = self.sigmaSlider.value() / 100.0
        self.computePhaseDiagram()

    def findFullCoverage(self):
        self.phase = numpy.zeros((self.BINS, self.BINS), dtype='<u1')
        self.voxelCoverage = 0.0
        self.sigma = 1
        while self.voxelCoverage <= 0.999:
            self.sigma += 10**int(numpy.log10(self.sigma))
            for xbin in range(self.BINS):
                x = (xbin + 0.5)
                for ybin in range(self.BINS):
                    y = (ybin + 0.5)
                    distances = numpy.array(
                        [self.distanceMax(x, y, gp) for gp in self.gaussianParameters])
                    i = numpy.argmin(distances)
                    distanceMin = distances[i]
                    if distanceMin < self.sigma:
                        self.phase[xbin, ybin] = i + 1

            self.voxelCoverage = self.jointHistogram[self.phase > 0].sum()
            print("Finding full coverage: sigma={}, coverage={}".format(
                self.sigma, self.voxelCoverage))

        self.sigmaSlider = QSlider(QtCore.Qt.Horizontal)
        self.sigmaSlider.setMinimum(1.0)
        # times 100 to increase slide precision
        self.sigmaSlider.setMaximum(self.sigma * 100.0)
        self.sigmaSlider.setValue(self.sigma * 100.0)
        self.sigmaSlider.valueChanged.connect(self.changeSigma)
        self.grid.addWidget(self.sigmaSlider, 2, 1)

        self.showPhaseDiagram()

    def computePhaseDiagram(self):
        self.phase = numpy.zeros((self.BINS, self.BINS), dtype='<u1')
        # define corresponding level
        for xbin in range(self.BINS):
            x = (xbin + 0.5)
            for ybin in range(self.BINS):
                y = (ybin + 0.5)
                distances = numpy.array(
                    [self.distanceMax(x, y, gp) for gp in self.gaussianParameters])
                i = numpy.argmin(distances)
                distanceMin = distances[i]
                if distanceMin < self.sigma:
                    self.phase[xbin, ybin] = i + 1

        self.voxelCoverage = self.jointHistogram[self.phase > 0].sum()

        self.showPhaseDiagram()

    def showPhaseDiagram(self):
        f = Figure()  # create a matplotlib figure
        a = f.add_subplot(111)
        np = len(self.gaussianParameters) + 1  # number of phases
        im = a.imshow(self.phase.T, origin='lower', extent=[0.0, self.BINS, 0.0, self.BINS], vmin=-0.5, vmax=np - 0.5, cmap=mpl.cm.get_cmap(cmapPhases, np))
        f.colorbar(im, ticks=numpy.arange(0, np))

        a.set_title("Phase diagram. Voxel coverage: {:.1f}%".format(self.voxelCoverage * 100))
        a.set_xlabel(self.names[0] + " grey levels", fontsize='xx-large')
        a.set_ylabel(self.names[1] + " grey levels", fontsize='xx-large')

        for i, gp in enumerate(self.gaussianParameters):
            a.plot(gp[0], gp[1], 'b*')
            a.annotate(i + 1, (gp[0], gp[1]), fontsize='xx-large')

        # histogram image widget
        self.plotWidget = FigureCanvas(f)
        self.grid.addWidget(self.plotWidget, 1, 1, 1, 2)


class FinalStep(QWidget):
    def __init__(self, images, crop, phaseDiagram, phi, GP, bins, greyLimitsCrop, binning, deformedImageName, names):
        import spam.helpers
        QWidget.__init__(self)
        self.images = images
        self.crop = crop
        self.phi = phi
        self.phaseDiagram = phaseDiagram
        self.binning = binning
        # This is the name of the output deformed image
        self.rootFileName = "".join(deformedImageName.split(".")[:-1])
        print(self.rootFileName)
        # The names of the two input files
        self.names = names

        # reorganize columns for spam.DIC.correlateGM.multimodalRegistration
        self.gaussianParameters = numpy.zeros_like(GP, dtype="<f8")
        self.gaussianParameters[:, 0] = numpy.array(GP)[:, 2]
        self.gaussianParameters[:, 1] = numpy.array(GP)[:, 0]
        self.gaussianParameters[:, 2] = numpy.array(GP)[:, 1]
        self.gaussianParameters[:, 3] = numpy.array(GP)[:, 3]
        self.gaussianParameters[:, 4] = numpy.array(GP)[:, 4]
        self.gaussianParameters[:, 5] = numpy.array(GP)[:, 5]
        self.BINS = bins

        # print("[FinalStep.__inti__] Image 0 is transformed by phi")
        # self.images[0] = spam.DIC.applyPhi(self.images[0], Phi=self.phi)

        self.greyLimitsCrop = greyLimitsCrop
        self.result = 0
        # self.greyLimitsOrig = greyLimitsOrig
        self.imagesCrop = []
        print("[FinalStep.__inti__] Image 0 is transformed by phi, cropped and rescaled -> saved in imagesCrop")
        # scale to 0-255
        #tmp = spam.DIC.applyPhi(self.images[0], Phi=self.phi)
        tmp = self.images[0]
        #self.imagesCrop.append(spam.helpers.rescaleToInteger(tmp[self.crop], scale=self.greyLimitsCrop[0], nBytes=1))
        self.imagesCrop.append(spam.helpers.rescaleToInteger(tmp, scale=self.greyLimitsCrop[0], nBytes=1))
        # divide into NBINS
        self.imagesCrop[0] = numpy.divide(self.imagesCrop[0], numpy.uint8(256 / self.BINS)).astype('<u1')

        print("[FinalStep.__inti__] Image 1 is cropped and rescaled -> saved in imagesCrop")
        # scale to 0-255
        tmp = self.images[1]
        #self.imagesCrop.append(spam.helpers.rescaleToInteger(tmp[self.crop], scale=self.greyLimitsCrop[1], nBytes=1))
        self.imagesCrop.append(spam.helpers.rescaleToInteger(tmp, scale=self.greyLimitsCrop[1], nBytes=1))
        # divide into NBINS
        self.imagesCrop[1] = numpy.divide(self.imagesCrop[1], numpy.uint8(256 / self.BINS)).astype('<u1')
        del tmp

        self.im2CropDef = spam.helpers.rescaleToInteger(spam.DIC.applyPhi(self.images[1], Phi=numpy.linalg.inv(self.phi)), scale=self.greyLimitsCrop[1], nBytes=1)
        self.im2CropDef = numpy.divide(self.im2CropDef, numpy.uint8(256 / self.BINS)).astype('<u1')

        self.grid = QGridLayout(self)
        startButton = QPushButton("Start correlation")
        startButton.clicked.connect(self.starCorrelation)
        self.grid.addWidget(startButton, 1, 1, 1, 3)
        self.automaticallySavedFiles = QLabel("Images saved: ")
        #self.label = QLabel("Save final phi in a tsv file")
        #self.nameEntry = QLineEdit("mmr-phi-final-bin{}.tsv".format(self.binning))
        #self.nameEntry = QLineEdit()
        self.resultLabel = QLabel()
        #self.saveButton = QPushButton("Save")
        #self.saveButton.clicked.connect(self.saveFinalResults)

        #  final step parameters and first rendering
        self.margin = 5
        margin = (slice(5, self.imagesCrop[0].shape[0] - 5),
                  slice(5, self.imagesCrop[0].shape[1] - 5),
                  slice(5, self.imagesCrop[0].shape[2] - 5))
        self.maxIterations = 10
        self.deltaPhiMin = 0.001
        middleSlice = self.imagesCrop[0][margin].shape[0] // 2

        self.viewerResiduals = QtImageViewer.QtImageViewer()
        self.viewerPhase = QtImageViewer.QtImageViewer()
        self.viewerIm1 = QtImageViewer.QtImageViewer()
        self.viewerIm2 = QtImageViewer.QtImageViewer()
        self.viewerCheckerBoard = QtImageViewer.QtImageViewer()

        # compute residuals
        print("[FinalStep.__inti__] Computing inital residuals")
        residualField = numpy.zeros_like(self.imagesCrop[0][margin], dtype="<f4")
        phaseField    = numpy.zeros_like(self.imagesCrop[0][margin], dtype="<u1")
        DICToolkit.computeGMresidualAndPhase(self.imagesCrop[0][margin],
                                             self.im2CropDef[margin],
                                             self.phaseDiagram,
                                             self.gaussianParameters, residualField, phaseField)

        self.viewerResiduals.setImage(qimage2ndarray.array2qimage(residualField[middleSlice, :, :], normalize=True))
        # self.viewerPhase.setImage(qimage2ndarray.array2qimage(phaseField[middleSlice, :, :], normalize=True))
        self.viewerIm1.setImage(qimage2ndarray.array2qimage(self.imagesCrop[0][margin][middleSlice, :, :], normalize=True))
        self.viewerIm2.setImage(qimage2ndarray.array2qimage(self.im2CropDef[margin][middleSlice, :, :], normalize=True))
        self.viewerCheckerBoard.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(self.imagesCrop[0][margin][middleSlice, :, :],
                                                                                      self.im2CropDef[margin][middleSlice, :, :]),
                                                                                      normalize=True))

        f = Figure()
        f.patch.set_alpha(0.0)
        NPHASES = self.gaussianParameters.shape[0]
        ax = f.add_subplot(111)
        ax.axis('off')
        ax.margins(0.0)
        im = ax.imshow(phaseField[phaseField.shape[0] // 2, :, :], vmin=-0.5, vmax=NPHASES + 0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES + 1))
        f.colorbar(im, ticks=numpy.arange(0, NPHASES + 1))
        self.canvas = FigureCanvas(f)
        self.grid.addWidget(self.canvas, 5, 2)

        im1Label = QLabel("Image 1")
        im2Label = QLabel("Image 2 (deformed)")
        residualLabel = QLabel("Residual field")
        phaseLabel = QLabel("Phase field")
        checkerBoardLabel = QLabel("CheckerBoard")
        selectotrGrid = QGridLayout()
        self.grid.addLayout(selectotrGrid, 0, 1, 1, 3)
        marginLabel = QLabel("Margin: ")
        self.marginEntry = QLineEdit("5")
        iterLabel = QLabel("Max iteration: ")
        self.iterEntry = QLineEdit("50")
        minPhiLabel = QLabel("Min delta Phi: ")
        self.minPhiEntry = QLineEdit("0.001")
        selectotrGrid.addWidget(marginLabel, 1, 1)
        selectotrGrid.addWidget(self.marginEntry, 1, 2)
        selectotrGrid.addWidget(iterLabel, 1, 3)
        selectotrGrid.addWidget(self.iterEntry, 1, 4)
        selectotrGrid.addWidget(minPhiLabel, 1, 5)
        selectotrGrid.addWidget(self.minPhiEntry, 1, 6)
        self.blankLabel1 = QLabel("")
        self.blankLabel2 = QLabel("")
        self.informationLabel = QLabel("")
        self.grid.addWidget(self.automaticallySavedFiles, 9, 1)
        self.grid.addWidget(self.blankLabel1, 10, 1)
        self.grid.addWidget(self.blankLabel2, 11, 1)
        #self.grid.addWidget(self.label, 10, 1)
        #self.grid.addWidget(self.nameEntry, 10, 2)
        #self.grid.addWidget(self.saveButton, 10, 3)
        self.grid.addWidget(self.resultLabel, 11, 2)
        self.grid.addWidget(residualLabel, 4, 1)
        self.grid.addWidget(phaseLabel, 4, 2)
        self.grid.addWidget(im1Label, 6, 1)
        self.grid.addWidget(im2Label, 6, 2)
        self.grid.addWidget(checkerBoardLabel, 4, 3)
        self.grid.addWidget(self.informationLabel, 8, 1, 1, 3)
        self.grid.addWidget(self.viewerResiduals, 5, 1)
        # self.grid.addWidget(self.viewerPhase, 5, 2)
        self.grid.addWidget(self.viewerIm1, 7, 1)
        self.grid.addWidget(self.viewerIm2, 7, 2)
        self.grid.addWidget(self.viewerCheckerBoard, 5, 3, 3, 1)
        #self.label.hide()
        #self.nameEntry.hide()
        #self.saveButton.hide()
        self.resultLabel.hide()
        self.automaticallySavedFiles.hide()

    def starCorrelation(self):
        from PyQt5 import QtTest

        self.automaticallySavedFiles.hide()
        #self.label.hide()
        #self.nameEntry.hide()
        #self.saveButton.hide()
        self.resultLabel.hide()

        # for matplotlib
        # plt.ion()

        # set variable that will be changeable in the interface
        if int(self.marginEntry.text()):
            self.margin = int(self.marginEntry.text())

        if int(self.iterEntry.text()):
            self.maxIterations = int(self.iterEntry.text())  # maximum iteration

        if float(self.minPhiEntry.text()):
            self.deltaPhiMin = float(self.minPhiEntry.text())

        m = self.margin  # margin
        maxIterations = self.maxIterations
        deltaPhiMin = self.deltaPhiMin

        # set local variables (can be removed later, it's just for sake of clarity)
        # Here we deform im1 There is no initial phi but imagesCrop[0] has been deformed previously from ereg
        im1 = self.imagesCrop[0]
        im2 = self.imagesCrop[1]
        BINS = self.BINS
        phaseDiagram = self.phaseDiagram
        gaussianParameters = self.gaussianParameters.astype('<f8')

        # phiCrop correspond to the transformation operator on the cropped imageself.
        # it will be added to the phi from ereg at the end

        # Phi (not self) will be the one we update in this function
        Phi = self.phi.copy()
        im2def = spam.DIC.applyPhi(im2, Phi=numpy.linalg.inv(Phi))

        # set margin to feed the transformed image
        margin = (slice(m, im1.shape[0] - m),
                  slice(m, im1.shape[1] - m),
                  slice(m, im1.shape[2] - m))
        print("[finalStep.startCorrelation] Margin set to {} pixels in every directions".format(m))

        # init loop variables
        iterations = 0
        returnStatus = 0
        deltaPhiNorm = 0.0

        # compute the joint histogram for the LogLikelyhood LL
        p, _, _ = numpy.histogram2d(im1[margin].ravel(),
                                    im2def[margin].ravel(),
                                    bins=BINS,
                                    range=[[0.0, BINS], [0.0, BINS]],
                                    normed=False, weights=None)
        LL = numpy.sum(numpy.log(p[numpy.where(p > 0)]))

        print("[finalStep.startCorrelation] Initial state        LL = {:0.2f}".format(LL))

        ### 2019-09-25 EA: Warining, this has changed a lot, now it's im1 which is moving consistent with
        ###   computeDICoperatorsGM, and so at the end of this function, PhiCrop is inversed.
        while (iterations <= maxIterations and deltaPhiNorm > deltaPhiMin) or iterations <= 1:
            # previousLL = LL  # need if divergence criterion

            # compute DIC operators
            M = numpy.zeros((12, 12), dtype='<f8')
            A = numpy.zeros((12),     dtype='<f8')
            im2defGradZ, im2defGradY, im2defGradX = numpy.gradient(im2def)

            # Compute operators
            DICToolkit.computeDICoperatorsGM(im1[margin].astype("<f4"),
                                             im2def[margin].astype("<f4"),
                                             im2defGradZ[margin].astype("<f4"),
                                             im2defGradY[margin].astype("<f4"),
                                             im2defGradX[margin].astype("<f4"),
                                             phaseDiagram.astype("<u1"),
                                             gaussianParameters.astype("<f8"),
                                             M, A)

            # compute deltaPhi
            try:
                deltaPhi = numpy.dot(numpy.linalg.inv(M), A)
            except numpy.linalg.linalg.LinAlgError:  # no cover
                # TODO: Calculate error for clean break.
                print('\tsingular M matrix')
                print('exiting')
                exit()

            # add deltaPhi to phi and compute current transformation
            deltaPhiNorm = numpy.linalg.norm(deltaPhi)
            deltaPhi = numpy.hstack([deltaPhi, numpy.zeros(4)]).reshape((4, 4))

            # In Roux X-N paper equation number 11
            Phi = numpy.dot(Phi, (numpy.eye(4) + deltaPhi))
            currentTransformation = spam.deformation.decomposePhi(Phi)

            # transform im1
            im2def = spam.DIC.applyPhi(im2, Phi=numpy.linalg.inv(Phi), interpolationOrder=1)

            # compute residuals
            residualField = numpy.zeros_like(im1[margin], dtype="<f4")
            phaseField    = numpy.zeros_like(im1[margin], dtype="<u1")
            DICToolkit.computeGMresidualAndPhase(im1[margin].astype("<f4"),
                                                 im2def[margin].astype("<f4"),
                                                 phaseDiagram.astype("<u1"),
                                                 gaussianParameters.astype("<f8"), residualField, phaseField)

            # iterate
            iterations += 1

            # recompute histogram and print
            p, _, _ = numpy.histogram2d(im1[margin].ravel(),
                                        im2def[margin].ravel(),
                                        bins=BINS,
                                        range=[[0.0, BINS], [0.0, BINS]],
                                        normed=False,
                                        weights=None)
            LL = numpy.sum(numpy.log(p[numpy.where(p > 0)]))
            print("[finalStep.startCorrelation] Iteration Number {:03d} ".format(iterations), end="")
            print("LL = {:0.2f} ".format(LL), end="")
            print("dPhi = {:0.4f} ".format(deltaPhiNorm), end="")
            print("Tr = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['t']), end="")
            print("Ro = {: .3f}, {: .3f}, {: .3f} ".format(*currentTransformation['r']), end="")
            print("Zo = {: .3f}, {: .3f}, {: .3f}".format(Phi[0, 0], Phi[1, 1], Phi[2, 2]))

            # plot
            self.informationLabel.setText("Gaussian Mixture iteration number {} "
                                          "|deltaPhi|={:.5f} \tT = [{: 2.4f} {: 2.4f} {:.4f}]\t"
                                          "R = [{: 2.4f} {: 2.4f} {: 2.4f}]\t"
                                          "Z = [{: 2.4f} {: 2.4f} {: 2.4f}]".format(iterations, deltaPhiNorm,
                                                                                    currentTransformation['t'][0],
                                                                                    currentTransformation['t'][1],
                                                                                    currentTransformation['t'][2],
                                                                                    currentTransformation['r'][0],
                                                                                    currentTransformation['r'][1],
                                                                                    currentTransformation['r'][2],
                                                                                    Phi[0, 0], Phi[1, 1], Phi[2, 2]))
            middleSlice = im1[margin].shape[0] // 2

            self.viewerResiduals.setImage(qimage2ndarray.array2qimage(residualField[middleSlice, :, :], normalize=True))
            self.viewerPhase.setImage(    qimage2ndarray.array2qimage(phaseField[middleSlice,    :, :], normalize=True))
            plt.clf()
            f = Figure()
            f.patch.set_alpha(0.0)
            NPHASES = self.gaussianParameters.shape[0]
            ax = f.add_subplot(111)
            ax.axis('off')
            ax.margins(0.0)
            im = ax.imshow(phaseField[phaseField.shape[0] // 2, :, :], vmin=-0.5, vmax=NPHASES + 0.5, cmap=mpl.cm.get_cmap(cmapPhases, NPHASES + 1))
            f.colorbar(im, ticks=numpy.arange(0, NPHASES + 1))
            self.canvas = FigureCanvas(f)
            self.grid.addWidget(self.canvas, 5, 2)

            self.viewerIm1.setImage(qimage2ndarray.array2qimage(im1[margin][middleSlice, :, :], normalize=True))
            self.viewerIm2.setImage(qimage2ndarray.array2qimage(im2def[margin][middleSlice, :, :], normalize=True))
            self.viewerCheckerBoard.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(im1[margin][middleSlice, :, :],
                                                                                          im2def[margin][middleSlice, :, :]),
                                                                                          normalize=True))
            #
            # tmp1 = spam.DIC.applyPhi(self.images[0], Phi=self.phi)
            # # tmp1 = spam.DIC.applyPhi(self.images[0], Phi=self.phi)
            # tmp2 = self.images[1]
            # middleSlice = tmp1.shape[0] // 2
            # self.viewerCheckerBoard.setImage(qimage2ndarray.array2qimage(cGM.checkerBoard(tmp1[middleSlice, :, :], tmp2[middleSlice, :, :]), normalize=True))
            QtTest.QTest.qWait(10)


        print("[finalStep.startCorrelation] End of the loop after {}/{} iterations: ".format(iterations, maxIterations), end="")
        print("dPhi = {:0.4f} (criterion at {}) ".format(deltaPhiNorm, deltaPhiMin))

        print("[finalStep.startCorrelation] Total transformation (eye registration + lucas and kanade on the crop): ")
        for k, v in spam.deformation.decomposePhi(Phi).items():
            print("[finalStep.startCorrelation] {}: {}".format(k, v))

        print("[finalStep.startCorrelation] Save deformed image: ", end="")
        fileName = self.rootFileName + "-registered.tif"
        im1Def = spam.DIC.applyPhi(self.images[0], Phi=Phi)
        tifffile.imsave(fileName, im1Def)
        dataSaved = [fileName]
        print("{}".format(fileName))

        # compute residuals
        print("[finalStep.startCorrelation] Compute residual and phase fields: ", end="")
        residualField = numpy.zeros_like(im1Def, dtype="<f4")
        phaseField = numpy.zeros_like(im1Def, dtype="<u1")

        im1Def = spam.helpers.rescaleToInteger(im1Def, scale=self.greyLimitsCrop[0], nBytes=1)
        im1Def = numpy.divide(im1Def, numpy.uint8(256 / self.BINS)).astype('<u1')
        im2 = spam.helpers.rescaleToInteger(self.images[1], scale=self.greyLimitsCrop[1], nBytes=1)
        im2 = numpy.divide(im2, numpy.uint8(256 / self.BINS)).astype('<u1')

        DICToolkit.computeGMresidualAndPhase(im1Def, im2, phaseDiagram, gaussianParameters, residualField, phaseField)
        fileName = self.rootFileName + "-mmr-phases-bin{}.tif".format(self.binning)
        tifffile.imsave(fileName, phaseField)
        dataSaved.append(fileName)
        print("{}, ".format(fileName), end="")

        fileName = self.rootFileName + "-mmr-residual-bin{}.tif".format(self.binning)
        tifffile.imsave(fileName, residualField)
        dataSaved.append(fileName)
        print("{}".format(fileName))

        # self.result = cGM.multimodalRegistration(
        #     self.images[0], self.images[1], self.phaseDiagram,
        #     self.gaussianParameters.astype('<f4'), BINS=self.BINS, verbose=True, INTERACTIVE=True, margin=5)
        self.result = {'transformation':  spam.deformation.decomposePhi(Phi),
                       'Phi':             Phi,
                       'returnStatus':    returnStatus,
                       'iterations':      iterations,
                       'residualField':   residualField,
                       'phaseField':      phaseField,
                       'deltaPhiNorm':    deltaPhiNorm}

        # 2021-02-11 EA and OS: as per issue #196: save final Phi TSV automatically
        fileName = self.rootFileName + "{}-{}-PhiFinal-bin{}.tsv".format(self.names[0][0:-4], self.names[1][0:-4], self.binning)
        TSVheader = "Zpos\tYpos\tXpos\tFzz\tFzy\tFzx\tZdisp\tFyz\tFyy\tFyx\tYdisp\tFxz\tFxy\tFxx\tXdisp\tbin\treturnStatus\tdeltaPhiNorm\titerations"
        centre = (numpy.array(self.images[0].shape)-1)/2.0
        output = numpy.array([[centre[0]], [centre[1]], [centre[2]],
                                [Phi[0, 0]], [Phi[0, 1]], [Phi[0, 2]],
                                [Phi[0, 3]], [Phi[1, 0]], [Phi[1, 1]],
                                [Phi[1, 2]], [Phi[1, 3]], [Phi[2, 0]],
                                [Phi[2, 1]], [Phi[2, 2]], [Phi[2, 3]],
                                [self.binning], [self.result['returnStatus']],
                                [self.result['deltaPhiNorm']], [self.result['iterations']]])
        numpy.savetxt(fileName, output.T, fmt='%.7f', delimiter='\t', newline='\n', comments='', header=TSVheader)
        #self.resultLabel.setText("Final Phi saved in: {}".format(os.path.join(os.getcwd(), fileName)))
        #self.resultLabel.setStyleSheet("QLabel {font-weight: bold; color: green;}")
        dataSaved.append(fileName)
        print("{}, ".format(fileName), end="")


        self.automaticallySavedFiles.setText("Data saved: {}".format(",\n\t ".join(dataSaved)))
        self.automaticallySavedFiles.setStyleSheet("QLabel {font-weight: bold; color: green;}")
        self.automaticallySavedFiles.show()
        #self.label.show()
        #self.nameEntry.show()
        #self.saveButton.show()
        self.resultLabel.show()


