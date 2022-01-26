import numpy

from PyQt5.QtGui import QPalette, QColor, QFont

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wiser.util.wise_objects import WiserData, WiserPreInputData
from orangecontrib.wiser.widgets.gui.ow_wise_widget import WiserWidget


class OWFromOasysBeamlineToWiserBeamline(WiserWidget):
    name = "From Oasys Beamline To Wiser Beamline"
    id = "FromOasysBeamlineToWiserBeamline"
    description = "Gets Oasys beamline and returns a beamline element compatible with LibWiser"
    icon = "icons/oasys_to_libwiser.png"
    priority = 10
    category = ""
    keywords = ["libwiser", "converter"]

    inputs = [("Input", WiserData, "set_input")]

    selectIndex = None
    input_data = None

    def build_gui(self):

        main_box = oasysgui.widgetBox(self.controlArea, "Settings", orientation="vertical", width=self.CONTROL_AREA_WIDTH-5, height=100)

        oasysgui.lineEdit(main_box, self, "selectIndex", "Select Element Index", labelWidth=260, valueType=float, orientation="horizontal")

        gui.button(main_box, self, "Print beamline", callback=self.printBeamline, height=35)

    def printBeamline(self):
        print(self.GetWiserBeamline(self.input_data))#, self.selectIndex))

    def GetWiserBeamline(self, in_object, Index=None):
        '''
        Return the native WISER BeamlineElements
        '''

        wb = in_object.wise_beamline
        N = wb.get_propagation_elements_number()

        if Index is None:
            WiserOE = wb.get_wise_propagation_element(N - 1)
        else:
            WiserOE = wb.get_wise_propagation_element(Index)

        WiserBeamline = WiserOE.ParentContainer

        return WiserBeamline

    def check_fields(self):
        # self.selectIndex = congruence.checkPositiveNumber(self.selectIndex, "Element index")
        pass

    def do_wiser_beamline(self):
        wiser_beamline = self.input_data.duplicate().wise_beamline

        return wiser_beamline

    def do_wise_calculation(self):
        output_wavefront = self.input_data.wise_wavefront

        self.printBeamline()

        S = output_wavefront.wiser_computation_result.S
        E = output_wavefront.wiser_computation_result.Field
        I = abs(E) ** 2
        norm = max(I)
        norm = 1.0 if norm == 0.0 else norm
        I = I / norm

        # ------------------------------------------------------------

        data_to_plot = numpy.zeros((2, len(S)))
        data_to_plot[0, :] = S
        data_to_plot[1, :] = I
        # data_to_plot[2, :] = numpy.imag(E)

        return self.GetWiserBeamline(self.input_data), data_to_plot

    def extract_plot_data_from_calculation_output(self, calculation_output):
        return calculation_output[1]

    def extract_wise_data_from_calculation_output(self, calculation_output):
        return calculation_output[0]

    def getTitles(self):
        return ["Wavefront Intensity"]

    def getXTitles(self):
        return ["S"]

    def getYTitles(self):
        return ["Intensity [arbitrary units]"]

    def set_input(self, input_data):
        self.setStatusMessage("")
        if not input_data is None:
            try:
                if not input_data.wise_beamline is None:
                    self.input_data = input_data.duplicate()
                    if self.is_automatic_run:
                        self.compute()
                else:
                    raise ValueError("No wavefront is present in input data")
            except Exception as exception:
                QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
import sys

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWFromOasysBeamlineToWiserBeamline()
    ow.show()
    a.exec_()
    ow.saveSettings()