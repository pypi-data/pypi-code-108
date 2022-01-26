import numpy

from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QRect

from orangewidget.settings import Setting
from orangewidget import gui

from oasys.widgets import gui as oasysgui
from oasys.widgets.widget import AutomaticWidget

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from wofrywiser.propagator.wavefront1D.wise_wavefront import WiserWavefront

from orangecontrib.wiser.util.wise_objects import WiserData

class OWWiseSourceToWofryWavefront1d(AutomaticWidget):
    name = "Wiser Wavefront To Wofry Wavefront 1D"
    id = "toWofryWavefront1D"
    description = "Wiser Wavefront To Wofry Wavefront 1D"
    icon = "icons/wf_to_wofry_wavefront_1d_new.png"
    priority = 11
    category = ""
    keywords = ["wise", "gaussian"]

    inputs = [("WiserData", WiserData, "set_input")]

    outputs = [{"name":"GenericWavefront1D",
                "type":GenericWavefront1D,
                "doc":"GenericWavefront1D",
                "id":"GenericWavefront1D"}]

    MAX_WIDTH = 420
    MAX_HEIGHT = 200
    CONTROL_AREA_WIDTH = 410

    want_main_area = 0

    input_data = None

    def __init__(self):
        super().__init__()

        geom = QApplication.desktop().availableGeometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.MAX_WIDTH)),
                               round(min(geom.height()*0.95, self.MAX_HEIGHT))))

        self.setMinimumHeight(self.geometry().height())
        self.setMinimumWidth(self.geometry().width())
        self.setMaximumHeight(self.geometry().height())
        self.setMaximumWidth(self.geometry().width())

        self.controlArea.setFixedWidth(self.MAX_WIDTH-10)
        self.controlArea.setFixedHeight(self.MAX_HEIGHT-10)

        main_box = oasysgui.widgetBox(self.controlArea, "Wiser Wavefront to Wofry Wavefront Converter", orientation="vertical", width=self.CONTROL_AREA_WIDTH-5, height=100)

        gui.button(main_box, self, "Compute", height=40, callback=self.compute)

    def compute(self):
        if not self.input_data is None:
            try:
                self.send("GenericWavefront1D", self.input_data.wise_wavefront.toGenericWavefront())
            except Exception as exception:
                QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

                #raise exception

    def set_input(self, input_data):
        self.setStatusMessage("")

        if not input_data is None:
            try:
                if not input_data.wise_wavefront is None:
                    
                    self.input_data = input_data

                    if self.is_automatic_execution:
                        self.compute()
                else:
                    raise ValueError("No wavefront is present in input data")
            except Exception as exception:
                QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

                #raise exception
