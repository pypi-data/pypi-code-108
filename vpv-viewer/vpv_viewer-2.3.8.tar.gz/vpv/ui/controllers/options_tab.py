
from PyQt5 import QtGui, QtCore
from vpv.ui.views.ui_options_tab import Ui_options
from vpv.utils.appdata import AppData


"""
A widget that allows the setting of some global options. The widget is added as a tab on the data manager
tab widget
"""


class OptionsTab(QtGui.QWidget):
    flip_signal = QtCore.pyqtSignal()
    toggle_filter_widget_signal = QtCore.pyqtSignal()

    def __init__(self, mainwindow, appdata: AppData):
        super(OptionsTab, self).__init__(mainwindow)
        self.ui = Ui_options()
        self.ui.setupUi(self)

        self.ui.checkBoxAxialFlipx.stateChanged.connect(self.on_axial_flipx)
        self.ui.checkBoxAxialFlipY.stateChanged.connect(self.on_axial_flipy)
        self.ui.checkBoxAxialFlipZ.stateChanged.connect(self.on_axial_flipz)

        self.ui.checkBoxCoronalFlipX.stateChanged.connect(self.on_coronal_flipx)
        self.ui.checkBoxCoronalFlipY.stateChanged.connect(self.on_coronal_flipy)
        self.ui.checkBoxCoronalFlipZ.stateChanged.connect(self.on_coronal_flipz)

        self.ui.checkBoxSagittalFlipX.stateChanged.connect(self.on_sagittal_flipx)
        self.ui.checkBoxSagittalFlipY.stateChanged.connect(self.on_sagittal_flipy)
        self.ui.checkBoxSagittalFlipZ.stateChanged.connect(self.on_sagittal_flipz)

        self.all_flip_check_boxes = [
            self.ui.checkBoxAxialFlipx,
            self.ui.checkBoxAxialFlipY,
            self.ui.checkBoxAxialFlipZ,
            self.ui.checkBoxCoronalFlipX,
            self.ui.checkBoxCoronalFlipY,
            self.ui.checkBoxCoronalFlipZ,
            self.ui.checkBoxSagittalFlipX,
            self.ui.checkBoxSagittalFlipY,
            self.ui.checkBoxSagittalFlipZ
        ]
        self.impc_flip_boxes = [
            self.ui.checkBoxAxialFlipZ,
            self.ui.checkBoxAxialFlipY,
            self.ui.checkBoxCoronalFlipZ
        ]

        self.ui.checkBoxImpcView.clicked.connect(self.on_impc_view)

        self.appdata = appdata

        self.ui.pushButtonFilterLabels.clicked.connect(self.toggle_filter_widget_signal)

    # def filter_label(self):
    #     input_ = self.ui.lineEditShowLabel.text()
    #     labels = input_.split(' ')
    #     try:
    #         labels = [int(x) for x in labels]
    #     except (TypeError, ValueError):
    #         labels = [0] # Reset the filtering
    #     self.filter_label_signal.emit(labels)

    def set_orientations(self):
        """
        Load the orientation-specific flip state stored in the appdata
        """
        if not self.appdata:
            return

        self.flips = self.appdata.get_flips()

        axial= self.flips['axial']
        coronal = self.flips['coronal']
        sagittal = self.flips['sagittal']

        self.ui.checkBoxAxialFlipx.setChecked(axial['x'])

        self.ui.checkBoxAxialFlipY.setChecked(axial['y'])

        self.ui.checkBoxAxialFlipZ.setChecked(axial['z'])

        self.ui.checkBoxCoronalFlipX.setChecked(coronal['x'])

        self.ui.checkBoxCoronalFlipY.setChecked(coronal['y'])

        self.ui.checkBoxCoronalFlipZ.setChecked(coronal['z'])

        self.ui.checkBoxSagittalFlipX.setChecked(sagittal['x'])

        self.ui.checkBoxSagittalFlipY.setChecked(sagittal['y'])

        self.ui.checkBoxSagittalFlipZ.setChecked(sagittal['z'])

        self.ui.checkBoxImpcView.setChecked(self.flips['impc_view'])

        self.on_impc_view(self.flips['impc_view'])

    def on_impc_view(self, checked: bool):
        """
        IMPC view is a series of flips to make the data look like as agreed.
        Uncheck all and set agred on flips
        """
        self.flips['impc_view'] = checked
        if checked:
            for box in self.all_flip_check_boxes:
                if box not in self.impc_flip_boxes:
                    box.setEnabled(False)
                    box.setChecked(False)
                else:
                    box.setEnabled(True)
                    box.setChecked(True)

        else:
            for box in self.all_flip_check_boxes:
                box.setEnabled(True)

        self.flip_signal.emit()

    def on_axial_flipx(self, checked: int):
        self.flips['axial']['x'] = bool(checked)
        self.flip_signal.emit()

    def on_axial_flipy(self, checked: int):
        self.flips['axial']['y'] = bool(checked)
        self.flip_signal.emit()

    def on_axial_flipz(self, checked: int):
        self.flips['axial']['z'] = bool(checked)
        self.flip_signal.emit()

    def on_coronal_flipx(self, checked: int):
        self.flips['coronal']['x'] = bool(checked)
        self.flip_signal.emit()

    def on_coronal_flipy(self, checked: int):
        self.flips['coronal']['y'] = bool(checked)
        self.flip_signal.emit()

    def on_coronal_flipz(self, checked: int):
        self.flips['coronal']['z'] = bool(checked)
        self.flip_signal.emit()

    def on_sagittal_flipx(self, checked: int):
        self.flips['sagittal']['x'] = bool(checked)
        self.flip_signal.emit()

    def on_sagittal_flipy(self, checked: int):
        self.flips['sagittal']['y'] = bool(checked)
        self.flip_signal.emit()

    def on_sagittal_flipz(self, checked: int):
        self.flips['sagittal']['z'] = bool(checked)
        self.flip_signal.emit()

