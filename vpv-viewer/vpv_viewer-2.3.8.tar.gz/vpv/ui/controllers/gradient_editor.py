from __future__ import division
from PyQt5 import  QtCore
from PyQt5.QtWidgets import QDialog
from vpv.ui.views.ui_gradient_editor import Ui_GradientEditor
import pyqtgraph as pg

class GradientEditor(QDialog):
    sigFinished = QtCore.pyqtSignal(list)  # Emits the two chosen gradients

    def __init__(self, parent):
        super(GradientEditor, self).__init__(parent.mainwindow)
        self.ui = Ui_GradientEditor()
        self.ui.setupUi(self)
        self.ui.pushButtonOk.clicked.connect(self.on_ok)
        self.pos_editor = pg.GradientWidget()
        self.ui.gridLayout.addWidget(self.pos_editor, 0, 1)
        self.neg_editor = pg.GradientWidget()
        self.ui.gridLayout.addWidget(self.neg_editor, 1, 1)

    def on_ok(self):
        pos_cm = self.pos_editor.colorMap().color
        neg_cm = list(reversed(self.neg_editor.colorMap().color))
        self.sigFinished.emit([pos_cm, neg_cm])
        self.close()