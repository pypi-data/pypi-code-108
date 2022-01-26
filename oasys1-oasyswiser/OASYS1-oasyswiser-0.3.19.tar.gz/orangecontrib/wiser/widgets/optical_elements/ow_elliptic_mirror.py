import numpy

from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui
from oasys.widgets import congruence

from syned.widget.widget_decorator import WidgetDecorator
from syned.beamline.shape import Ellipsoid

from LibWiser import Optics

from wofrywiser.beamline.beamline_elements import WiserOpticalElement

from orangecontrib.wiser.widgets.gui.ow_optical_element import OWOpticalElement
from orangecontrib.wiser.widgets.gui.ow_wise_widget import PositioningDirectivesPhrases


class OWEllipticMirror(OWOpticalElement, WidgetDecorator):
    name = "EllipticMirror"
    id = "EllipticMirror"
    description = "Elliptic Mirror"
    icon = "icons/ellipsoid_mirror.png"
    priority = 2

    OWOpticalElement.WhatWhereReferTo = Setting(PositioningDirectivesPhrases.Type.DistanceFromSource)

    oe_name = Setting("Elliptic mirror")

    f1 = Setting(0)
    f2 = Setting(0)

    def after_change_workspace_units(self):
        super(OWEllipticMirror, self).after_change_workspace_units()
        # I don't know why exactly, but the label displays correctly with the two lines commented
        # label = self.le_length.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")
        # label = self.le_f1.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")
        # label = self.le_f2.parent().layout().itemAt(0).widget()
        # label.setText(label.text() + " [" + self.workspace_units_label + "]")

    def check_fields(self):
        super(OWEllipticMirror, self).check_fields()

        self.f1 = congruence.checkStrictlyPositiveNumber(self.f1, "F1")
        self.f2 = congruence.checkStrictlyPositiveNumber(self.f2, "F2")

    def build_mirror_specific_gui(self, container_box):
        self.le_f1 = oasysgui.lineEdit(container_box, self, "f1", "F1 [m]", labelWidth=240, valueType=float, orientation="horizontal")
        self.le_f2 = oasysgui.lineEdit(container_box, self, "f2", "F2 [m]", labelWidth=240, valueType=float, orientation="horizontal")

    def get_native_optical_element(self):
        return Optics.MirrorElliptic(f1=self.f1,
                                     f2=self.f2,
                                     L=self.length,
                                     Alpha=numpy.deg2rad(self.alpha))

    def get_optical_element(self, native_optical_element):
         return WiserOpticalElement(name=self.oe_name,
                                    boundary_shape=None,
                                    native_CoreOptics=native_optical_element,
                                    native_PositioningDirectives=self.get_PositionDirectives())

    def receive_specific_syned_data(self, optical_element):
        p, q = optical_element._surface_shape.get_p_q(numpy.radians(self.alpha))

        self.f1 = numpy.round(p, 6)
        self.f2 = numpy.round(q, 6)

    def check_syned_shape(self, optical_element):
        if not isinstance(optical_element._surface_shape, Ellipsoid):
            raise Exception("Syned Data not correct: Mirror Surface Shape is not Elliptical")

from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
import sys

if __name__ == "__main__":
    a = QApplication(sys.argv)
    ow = OWEllipticMirror()
    ow.show()
    a.exec_()
    ow.saveSettings()