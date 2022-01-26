import sys
import numpy
from scipy.stats import norm
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from PyQt5.QtGui import QPalette, QColor, QFont

from LibWiser import Optics
import LibWiser.FermiSource as Fermi
from LibWiser.Foundation import PositioningDirectives

from wofrywiser.propagator.propagator1D.wise_propagator import WiserPropagationElements

from wofrywiser.beamline.beamline_elements import WiserBeamlineElement, WiserOpticalElement

from orangecontrib.wiser.util.wise_objects import WiserData
from orangecontrib.wiser.widgets.gui.ow_wise_widget import WiserWidget, ElementType, PositioningDirectivesPhrases


class PositioningDirectivesSource:
    class Type:
        Custom = 'Absolute'

    class Orientation:
        Isotropic = 'Isotropic'
        Horizontal = 'Horizontal'
        Vertical = 'Vertical'
        Any = 'Any'

positioning_directives_what = [PositioningDirectives.What.Centre,
                               PositioningDirectives.What.UpstreamFocus,
                               PositioningDirectives.What.DownstreamFocus]

positioning_directives_where = [PositioningDirectives.Where.Centre,
                                PositioningDirectives.Where.UpstreamFocus,
                                PositioningDirectives.Where.DownstreamFocus]

positioning_directives_refer_to = [PositioningDirectives.ReferTo.AbsoluteReference,
                                   PositioningDirectives.ReferTo.UpstreamElement,
                                   PositioningDirectives.ReferTo.DownstreamElement,
                                   PositioningDirectives.ReferTo.DoNotMove,
                                   PositioningDirectives.ReferTo.Source]

positioning_directives_which_angle = [Optics.TypeOfAngle.GrazingNominal,
                                      Optics.TypeOfAngle.InputNominal,
                                      Optics.TypeOfAngle.OutputNominal,
                                      Optics.TypeOfAngle.SelfFrameOfReference,
                                      Optics.TypeOfAngle.NormalAbsolute,
                                      Optics.TypeOfAngle.TangentAbsolute]

positioning_directives_source = [PositioningDirectivesSource.Type.Custom]

positioning_directives_orientation = [PositioningDirectivesPhrases.Orientation.Isotropic,
                                      PositioningDirectivesPhrases.Orientation.Horizontal,
                                      PositioningDirectivesPhrases.Orientation.Vertical,
                                      PositioningDirectivesPhrases.Orientation.Any]

class OWGaussianSource1d(WiserWidget):
    name = "GaussianSource1d"
    id = "GaussianSource1d"
    description = "GaussianSource1d"
    icon = "icons/gaussian_source_1d.png"
    priority = 1
    category = ""
    keywords = ["wise", "gaussian"]

    use_small_displacements = Setting(0)
    rotation = Setting(0.0)
    transverse = Setting(0.0)
    longitudinal = Setting(0.0)

    WhatWhereReferTo = Setting(PositioningDirectivesPhrases.Type.Custom)
    ReferTo = Setting(PositioningDirectives.ReferTo.AbsoluteReference)
    What = Setting(PositioningDirectives.What.Centre)
    Where = Setting(PositioningDirectives.Where.Centre)

    source_name = Setting("Gaussian Source")
    rayleigh_range = Setting(0.)

    source_lambda = Setting(10)
    XYCentre_checked = Setting(1)
    source_m2 = Setting(1.)

    waist_calculation = Setting(0)
    source_waist = Setting(180)

    def build_gui(self):

        main_box = oasysgui.widgetBox(self.controlArea, "Gaussian Source 1D Input Parameters", orientation="vertical", width=self.CONTROL_AREA_WIDTH-5)

        source_box = oasysgui.widgetBox(main_box, "Source Settings", orientation="vertical", width=self.CONTROL_AREA_WIDTH-25)

        oasysgui.lineEdit(source_box, self, "source_name", "Source Name", labelWidth=120, valueType=str, orientation="horizontal")

        self.le_source_wl = oasysgui.lineEdit(source_box, self, "source_lambda", "Wavelength [nm]", labelWidth=260, valueType=float, orientation="horizontal", callback=self.set_WaistCalculation)
        self.le_source_m2 = oasysgui.lineEdit(source_box, self, "source_m2", "M\u00B2", labelWidth=260, valueType=float, orientation="horizontal")

        gui.comboBox(source_box, self, "waist_calculation", label="Preset Waist",
                     items=["None", "Fermi FEL1-like", "Fermi FEL2-like", "Fermi Auto"], labelWidth=260,
                     callback=self.set_WaistCalculation, sendSelectedValue=False, orientation="horizontal")

        self.le_source_waist = oasysgui.lineEdit(source_box, self, "source_waist", "Waist [um]", labelWidth=260, valueType=float, orientation="horizontal")


        self.position_box = oasysgui.tabWidget(main_box)#, "Position Settings", orientation="vertical", width=self.CONTROL_AREA_WIDTH-25)
        self.position_box.setFixedWidth(self.CONTROL_AREA_WIDTH-25)

        self.tab_pos = oasysgui.createTabPage(self.position_box, "Position")
        self.tab_dis = oasysgui.createTabPage(self.position_box, "Displacement")

        self.build_positioning_directive_box(container_box=self.tab_pos,
                                             width=self.CONTROL_AREA_WIDTH-25,
                                             element_type=ElementType.SOURCE)

        # displacement_box = oasysgui.widgetBox(self.tab_dis, "Small Displacements", orientation="vertical", width=self.CONTROL_AREA_WIDTH-50)

        gui.comboBox(self.tab_dis, self, "use_small_displacements", label="Small Displacements",
                     items=["No", "Yes"], labelWidth=260,
                     callback=self.set_UseSmallDisplacement, sendSelectedValue=False, orientation="horizontal")

        self.use_small_displacements_box       = oasysgui.widgetBox(self.tab_dis, "", addSpace=True, orientation="vertical", height=150, width=self.CONTROL_AREA_WIDTH-40)
        self.use_small_displacements_box_empty = oasysgui.widgetBox(self.tab_dis, "", addSpace=True, orientation="vertical", height=150, width=self.CONTROL_AREA_WIDTH-40)

        oasysgui.lineEdit(self.use_small_displacements_box, self, "rotation", "Rotation [deg]", labelWidth=260, valueType=float, orientation="horizontal")
        self.le_transverse = oasysgui.lineEdit(self.use_small_displacements_box, self, "transverse", "Transverse displacement [m]", labelWidth=260, valueType=float, orientation="horizontal")
        self.le_longitudinal = oasysgui.lineEdit(self.use_small_displacements_box, self, "longitudinal", "Longitudinal displacement [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_UseSmallDisplacement()


    def set_WaistCalculation(self):
        if self.source_lambda > 0.0:
            self.source_waist = round(Fermi.Waist0E(self.source_lambda, str( self.waist_calculation)) / 1e-6, 8) / 2.

    def set_UseSmallDisplacement(self):
        self.use_small_displacements_box.setVisible(self.use_small_displacements == 1)
        self.use_small_displacements_box_empty.setVisible(self.use_small_displacements == 0)

    def after_change_workspace_units(self):
        super(OWGaussianSource1d, self).after_change_workspace_units()

        # if hasattr(self, "le_transverse"):
        #     label = self.le_transverse.parent().layout().itemAt(0).widget()
        #     label.setText(label.text() + " [" + self.workspace_units_label + "]")
        #
        # if hasattr(self, "le_longitudinal"):
        #     label = self.le_longitudinal.parent().layout().itemAt(0).widget()
        #     label.setText(label.text() + " [" + self.workspace_units_label + "]")

        # self.source_lambda = self.source_lambda / self.workspace_units_to_m
        # self.source_waist = self.source_waist / self.workspace_units_to_m

        # label = self.le_source_wl.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")

        # label = self.le_source_waist.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")

    def check_fields(self):
        self.source_lambda = congruence.checkStrictlyPositiveNumber(self.source_lambda, "Wavelength")
        self.source_waist = congruence.checkStrictlyPositiveNumber(self.source_waist, "Waist")

    def do_wiser_beamline(self):
        raise Exception("Nothing to apply. Source is the first element of the beamline.")

    def do_wise_calculation(self):
        position_directives = self.get_PositionDirectives()
        position_directives.WhichAngle = Optics.TypeOfAngle.SelfFrameOfReference
        position_directives.Angle = 0.0

        wise_source = WiserOpticalElement(name=self.source_name,
                                          boundary_shape=None,
                                          native_CoreOptics=Optics.SourceGaussian(self.source_lambda*1e-9,
                                                                                  self.source_waist*1e-6,
                                                                                  M2=self.source_m2),
                                          isSource=True,
                                          native_PositioningDirectives=position_directives)

        if self.use_small_displacements == 1:
            wise_source.native_optical_element.CoreOptics.ComputationSettings.UseSmallDisplacements = True  # serve per traslare/ruotare l'EO
            wise_source.native_optical_element.CoreOptics.SmallDisplacements.Rotation = numpy.deg2rad(self.rotation)
            wise_source.native_optical_element.CoreOptics.SmallDisplacements.Trans = self.transverse  # Transverse displacement (rispetto al raggio uscente, magari faremo scegliere)
            wise_source.native_optical_element.CoreOptics.SmallDisplacements.Long = self.longitudinal  # Longitudinal displacement (idem)
        else:
            wise_source.native_optical_element.CoreOptics.ComputationSettings.UseSmallDisplacements = False

        z = wise_source.native_optical_element.CoreOptics.RayleighRange # [metres]
        x = 4. * wise_source.native_optical_element.CoreOptics.Fwhm(z)
        self.rayleigh_range = z

        data_to_plot = numpy.zeros((2, 201))

        sigma = self.source_waist * 1e-6 / 2.
        mu = 0.0 if self.XYCentre_checked else self.YCentre

        data_to_plot[0, :] = numpy.linspace(-x + mu, mu + x, 201)
        data_to_plot[1, :] = wise_source.native_optical_element.CoreOptics.Amplitude(data_to_plot[0, :], z)

        return wise_source, data_to_plot

    def getTitles(self):
        return ["Gaussian source intensity at Rayleigh range ($z_R$ = {:.3f} [m])".format(self.rayleigh_range)]

    def getXTitles(self):
        return ["Y"]

    def getXUnits(self):
        return ["m"]

    def getYTitles(self):
        return ["Intensity [arbitrary units]"]

    def extract_plot_data_from_calculation_output(self, calculation_output):
        return calculation_output[1]

    def extract_wise_data_from_calculation_output(self, calculation_output):
        beamline = WiserPropagationElements()
        beamline.add_beamline_element(WiserBeamlineElement(optical_element=calculation_output[0]))

        return WiserData(wise_wavefront=None, wise_beamline=beamline)

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
import sys

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWGaussianSource1d()
    ow.show()
    a.exec_()
    ow.saveSettings()