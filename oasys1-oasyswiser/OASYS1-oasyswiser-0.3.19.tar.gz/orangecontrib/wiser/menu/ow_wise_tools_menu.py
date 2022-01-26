__author__ = 'labx'

from PyQt5.QtGui import QPalette, QColor

from orangecanvas.scheme.link import SchemeLink
from oasys.menus.menu import OMenu

from wofry.propagator.propagator import PropagationManager, PropagationMode
from wofrywiser.propagator.propagator1D.wise_propagator import WISE_APPLICATION

from orangecontrib.wiser.util.wise_util import showWarningMessage, showCriticalMessage
from orangecontrib.wiser.widgets.optical_elements.ow_detector import OWDetector

class WiseToolsMenu(OMenu):

    def __init__(self):
        super().__init__(name="WISEr Tools")

        self.openContainer()
        self.addContainer("Propagation Mode")
        self.addSubMenu("Element by Element")
        self.addSubMenu("Whole beamline at Detector")
        self.closeContainer()

        PropagationManager.Instance().set_propagation_mode(WISE_APPLICATION, PropagationMode.STEP_BY_STEP)

    def executeAction_1(self, action):
        try:
            PropagationManager.Instance().set_propagation_mode(WISE_APPLICATION, PropagationMode.STEP_BY_STEP)
            showWarningMessage("Propagation Mode: Element by Element")

            self.set_wise_live_propagation_mode()
        except Exception as exception:
            showCriticalMessage(exception.args[0])

    def executeAction_2(self, action):
        try:
            PropagationManager.Instance().set_propagation_mode(WISE_APPLICATION, PropagationMode.WHOLE_BEAMLINE)
            showWarningMessage("Propagation Mode: Whole beamline at Detector")

            self.set_wise_live_propagation_mode()
        except Exception as exception:
            showCriticalMessage(exception.args[0])
            raise exception

    def set_wise_live_propagation_mode(self):
        for node in self.canvas_main_window.current_document().scheme().nodes:
            widget = self.canvas_main_window.current_document().scheme().widget_for_node(node)

            if hasattr(widget, "wise_live_propagation_mode"):
                widget.set_wise_live_propagation_mode()
                if not isinstance(widget, OWDetector) and (PropagationManager.Instance().get_propagation_mode(WISE_APPLICATION) == PropagationMode.WHOLE_BEAMLINE):
                    widget.view_type = 0
                    widget.set_ViewType()

    #################################################################
    #
    # SCHEME MANAGEMENT
    #
    #################################################################

    def getWidgetFromNode(self, node):
        return self.canvas_main_window.current_document().scheme().widget_for_node(node)

    def createLinks(self, nodes):
        previous_node = None
        for node in nodes:
            if not (isinstance(node, str)) and not previous_node is None and not (isinstance(previous_node, str)):
                link = SchemeLink(source_node=previous_node, source_channel="Beam", sink_node=node, sink_channel="Input Beam")
                self.canvas_main_window.current_document().addLink(link=link)
            previous_node = node

    def getWidgetDesc(self, widget_name):
        return self.canvas_main_window.widget_registry.widget(widget_name)

    def createNewNode(self, widget_desc):
        return self.canvas_main_window.current_document().createNewNode(widget_desc)

    def createNewNodeAndWidget(self, widget_desc):
        messages = []

        try:
            node = self.createNewNode(widget_desc)
            widget = self.getWidgetFromNode(node)

            # here you can put values on the attrubutes

        except Exception as exception:
            messages.append(exception.args[0])

        return widget, node, messages
