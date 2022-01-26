import numpy

from PyQt5.QtGui import QPalette, QColor, QFont

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from orangecontrib.wiser.util.wise_objects import WiserData
from orangecontrib.wiser.widgets.gui.ow_wise_widget import WiserWidget

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D

from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagationElements
from wofrywiser.propagator.wavefront1D.wise_wavefront import WiserWavefront
from wofrywiser.beamline.beamline_elements import WiserBeamlineElement
from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from LibWiser import Foundation, Optics

class OWFromWofryWavefront1d(WiserWidget):
    name = "From Wofry Wavefront 1D"
    id = "FromWofryWavefront1d"
    description = "From Wofry Wavefront 1D"
    icon = "icons/from_wofry_wavefront_1d_new.png"
    priority = 10
    category = ""
    keywords = ["wise", "gaussian"]

    inputs = [("GenericWavefront1D", GenericWavefront1D, "set_input")]

    wofry_wavefront = None
    reset_phase = Setting(0)
    normalization_factor = Setting(1.0)
    deltaSource = Setting(0.0)
    number_of_points = Setting(5000)

    source_lambda = 0.0

    def build_gui(self):

        main_box = oasysgui.widgetBox(self.controlArea, "Wavefront Parameters", orientation="vertical", width=self.CONTROL_AREA_WIDTH-5, height=300)

        le = oasysgui.lineEdit(main_box, self, "source_lambda", "Wavelength [nm]", labelWidth=260, valueType=float, orientation="horizontal")
        le.setReadOnly(True)
        font = QFont(le.font())
        font.setBold(True)
        le.setFont(font)
        palette = QPalette(le.palette())
        palette.setColor(QPalette.Text, QColor('dark blue'))
        palette.setColor(QPalette.Base, QColor(243, 240, 140))
        le.setPalette(palette)

        gui.separator(main_box, height=5)

        gui.comboBox(main_box, self, "reset_phase", label="Reset Phase",
                                            items=["No", "Yes"], labelWidth=260, sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(main_box, self, "normalization_factor", "Normalization Factor", labelWidth=260, valueType=float, orientation="horizontal")

        gui.separator(main_box, height=5)

        le_deltaSource = oasysgui.lineEdit(main_box, self, "deltaSource", "Offset distance from source point [m]", labelWidth=260, valueType=float, orientation="horizontal")

        gui.separator(main_box, height=5)

        le_sampling = oasysgui.lineEdit(main_box, self, "number_of_points", "Number of Points (field will be resampled)", labelWidth=260, valueType=int, orientation="horizontal")


    def check_fields(self):
        self.source_lambda = congruence.checkStrictlyPositiveNumber(self.source_lambda, "Wavelength")
        self.deltaSource = congruence.checkPositiveNumber(self.deltaSource, "Offset distance from source point")

    def do_wise_calculation(self):
        rinorm = numpy.sqrt(self.normalization_factor/numpy.max(self.wofry_wavefront.get_intensity()))

        if self.reset_phase:
            electric_fields = self.wofry_wavefront.get_amplitude()*rinorm
        else:
            electric_fields = self.wofry_wavefront.get_amplitude()*rinorm * numpy.exp(1j*self.wofry_wavefront.get_phase())

        self.wofry_wavefront.set_complex_amplitude(electric_fields)

        data_to_plot = numpy.zeros((2, self.wofry_wavefront.size()))

        data_to_plot[0, :] = self.wofry_wavefront._electric_field_array.get_abscissas()#/self.workspace_units_to_m
        data_to_plot[1, :] = numpy.abs(self.wofry_wavefront._electric_field_array.get_values())**2

        return self.wofry_wavefront, WiserWavefront.fromGenericWavefront(self.wofry_wavefront), data_to_plot

    def getTitles(self):
        return ["Wavefront Intensity"]

    def getXTitles(self):
        return ["Z [" + self.workspace_units_label + "]"]

    def getYTitles(self):
        return ["Intensity [arbitrary units]"]

    def extract_plot_data_from_calculation_output(self, calculation_output):
        return calculation_output[2]

    def extract_wise_data_from_calculation_output(self, calculation_output):
        wofry_wavefront = calculation_output[0]
        wise_wavefront = calculation_output[1]

        wiser_beamline = WiserPropagationElements()
        wiser_beamline.add_beamline_element(WiserBeamlineElement(optical_element=get_virtual_source()))
        wiser_beamline.add_beamline_element(WiserBeamlineElement(optical_element=get_wavefront_source(wofry_wavefront, self.deltaSource)))
        s2 = wiser_beamline.get_wise_propagation_element(-1)
        s2.ComputationData = s2.CoreOptics.GetInitComputationData()
        s2.ComputationSettings.UseCustomSampling = True
        s2.NSamples = self.number_of_points

        return WiserData(wise_wavefront=wise_wavefront, wise_beamline=wiser_beamline)

    def set_input(self, input_data):
        self.setStatusMessage("")

        if not input_data is None:
            self.wofry_wavefront = input_data.duplicate()
            self.source_lambda = round(self.wofry_wavefront._wavelength*1e9, 4)

            if self.is_automatic_run: self.compute()

def get_dummy_source(wofry_wavefront):
    return Foundation.OpticalElement(Name="Wofry Source",
                                     IsSource=True,
                                     CoreOpticsElement=DummyElement(wofry_wavefront=wofry_wavefront),
                                     PositioningDirectives=Foundation.PositioningDirectives(ReferTo=Foundation.PositioningDirectives.ReferTo.AbsoluteReference,
                                                                                            XYCentre=[0.0, 0.0],
                                                                                            Angle=0.0))


def get_virtual_source():
    return WiserOpticalElement(name="Virtual source",
                               isSource=True,
                               native_CoreOptics=Optics.SourceVirtual(),
                               native_PositioningDirectives=Foundation.PositioningDirectives(ReferTo=Foundation.PositioningDirectives.ReferTo.AbsoluteReference,
                                                                                             XYCentre=[0.0, 0.0],
                                                                                             Angle=0.0))


def get_wavefront_source(wofry_wavefront, deltaSource):
    mesh_x = wofry_wavefront.get_abscissas()

    return WiserOpticalElement(name="Wavefront Source",
                               isSource=False,
                               native_CoreOptics=Optics.SourceWavefront(Lambda=wofry_wavefront.get_wavelength(),
                                                                        L=numpy.abs(mesh_x[0]) + numpy.abs(mesh_x[-1]),
                                                                        Field=wofry_wavefront.get_amplitude() * numpy.exp(1j*wofry_wavefront.get_phase()),
                                                                        Orientation = Optics.OPTICS_ORIENTATION.ISOTROPIC),
                               native_PositioningDirectives=Foundation.PositioningDirectives(ReferTo=Foundation.PositioningDirectives.ReferTo.Source,
                                                                                             PlaceWhat='centre',
                                                                                             PlaceWhere='centre',
                                                                                             Distance=deltaSource))

class DummyElement(Optics.SourceGaussian):
    def __init__(self, wofry_wavefront=GenericWavefront1D()):
        self.wofry_wavefront = wofry_wavefront

        wavelength = wofry_wavefront.get_wavelength()
        waist0 = fwhm(wofry_wavefront.get_abscissas(), wofry_wavefront.get_intensity())*numpy.sqrt(2)/1.66

        print("WAIST", waist0)

        super(DummyElement, self).__init__(Lambda=wavelength, Waist0=waist0)

    def EvalField_XYSelf(self, z = numpy.array(None) , r = numpy.array(None)):
        electric_fields = self.wofry_wavefront.get_interpolated_complex_amplitudes(r)
        #electric_fields = self.wofry_wavefront.get_interpolated_amplitudes(r)

        return electric_fields*super(DummyElement, self).EvalField_XYSelf(z, r)

from scipy.interpolate import splrep, sproot, splev

class MultiplePeaks(Exception): pass
class NoPeaksFound(Exception): pass

def fwhm(x, y, k=3):
    """
    Determine full-with-half-maximum of a peaked set of points, x and y.

    Assumes that there is only one peak present in the datasset.  The function
    uses a spline interpolation of order k.
    """

    half_max = numpy.max(y)/2.0
    s = splrep(x, y - half_max, k=k)
    roots = sproot(s)

    if len(roots) > 2:
        raise MultiplePeaks("The dataset appears to have multiple peaks, and "
                "thus the FWHM can't be determined.")
    elif len(roots) < 2:
        raise NoPeaksFound("No proper peaks were found in the data set; likely "
                "the dataset is flat (e.g. all zeros).")
    else:
        return abs(roots[1] - roots[0])


