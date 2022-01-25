import sys
import os
from importlib import reload
from PySide2 import QtWidgets
from pymxs import runtime as rt
import datetime

# DO NOT SORT IMPORTS !!!!!!!!!!!!!
CIO_DIR = os.path.dirname(os.path.dirname(__file__))
sys.path.append(CIO_DIR)

# While in development, we reload everything.
if  os.environ.get("CONDUCTOR_MODE") == "dev":
    from ciomax import reloader
    reload(reloader)

from ciomax.preview_tab import PreviewTab
from ciomax.main_tab import MainTab
from ciomax.validation_tab import ValidationTab
from ciomax.response_tab import ResponseTab

from ciomax.store import ConductorStore
from ciopath.gpath import Path
from ciomax import render_scope
from ciotemplate.expander import Expander


BACKGROUND_COLOR = "rgb(48, 48, 48)"

# Ideally these override styles will be reinstated when we figure out how to detect light mode and
# make equivalents 


# STYLESHEET = """
# QLineEdit {{ background: {bg}; }}
# QSpinBox {{ background: {bg}; }}
# QListWidget {{ background: {bg}; }}
# QToolButton {{ border: none; }}
# QTextEdit {{ background: {bg}; }}""".format(
#     bg=BACKGROUND_COLOR
# )

STYLESHEET = """
QToolButton {{ border: none; }}
"""

class ConductorDialog(QtWidgets.QDialog):
    """
    Build the dialog as a child of the Max window.

    The dialog has:
    * A reference to the ConductorStore, where settings are persisted.
    * A reference to the RenderScope, which holds information about the renderer chosen when the
       dialog was instantiated or reset. RenderScope needs to know our available software, so it can
       only be created after a connection is established.
    * References to the 4 tabs:
        * Main - all the configuratin sections
        * Preview - resolved JSNON payload
        * Validation - Display pre submission warnngs etc.
        * Response - Display submission response, link to dash.
    """

    def __init__(self):
        QtWidgets.QDialog.__init__(self, QtWidgets.QWidget.find(rt.windows.getMAXHWND()))

        self.render_scope = None
        self.store = ConductorStore()
        self.screen_scale = self.logicalDpiX() / 96

        self.setStyleSheet(STYLESHEET)
        self.setWindowTitle("Conductor")
        self.layout = QtWidgets.QVBoxLayout()
        self.tab_widget = QtWidgets.QTabWidget()

        self.setLayout(self.layout)
        self.layout.addWidget(self.tab_widget)

        self.main_tab = MainTab(self)
        self.preview_tab = PreviewTab(self)
        self.validation_tab = ValidationTab(self)
        self.response_tab = ResponseTab(self)

        self.tab_widget.addTab(self.main_tab, "Configure")
        self.tab_widget.addTab(self.preview_tab, "Preview")
        self.tab_widget.addTab(self.validation_tab, "Validation")
        self.tab_widget.addTab(self.response_tab, "Response")

        self.tab_widget.setTabEnabled(2, False)
        self.tab_widget.setTabEnabled(3, False)

        self.main_tab.populate_from_store()
        self.configure_signals()

    def show_main_tab(self):
        self.tab_widget.setCurrentWidget(self.main_tab)

    def show_preview_tab(self):
        self.tab_widget.setCurrentWidget(self.preview_tab)

    def show_validation_tab(self):
        self.tab_widget.setTabEnabled(2, True)
        self.validation_tab.clear()
        self.tab_widget.setCurrentWidget(self.validation_tab)

    def show_response_tab(self):
        self.tab_widget.setTabEnabled(3, True)
        self.response_tab.clear()
        self.tab_widget.setCurrentWidget(self.response_tab)

    def configure_signals(self):
        self.tab_widget.currentChanged.connect(self.on_tab_change)

    def on_tab_change(self, index):
        """
        Handle tab change.

        If switching to the preview tab, resolve the submission payload.

        Args:
            index (int): the tab index
        """
        if index == 1:
            context = self.get_context()
            submission = self.main_tab.resolve(context, preview_only=True)
            self.preview_tab.populate(submission)
        if index != 2:
            self.tab_widget.setTabEnabled(2, False)

    def get_context(self):
        scenefile = rt.maxFilePath + rt.maxFileName
        if scenefile:
            scenefile = Path(scenefile).fslash()
            scenedir = os.path.dirname(scenefile)
            scenenamex, ext = os.path.splitext(os.path.basename(scenefile))
        else:
            scenefile = "/NOT_SAVED"
            scenedir = "/NOT_SAVED"
            scenenamex, ext = ("NOT_SAVED", "")
        scenename = "{}{}".format(scenenamex, ext)

        project = rt.pathConfig.getCurrentProjectFolder()
        if project:
            project = Path(project).fslash()
        else:
            project = "/NOT_SET"

        result = {
            "conductor": Path(CIO_DIR).fslash(),
            "scenefile": scenefile,
            "scenedir": scenedir,
            "scenenamex": scenenamex,
            "ext": ext,
            "scenename": scenename,
            "project": project,
            "renderer": str(self.render_scope),
            "timestamp": datetime.datetime.now().strftime("%y%m%d_%H%M%S"),
        }

        # Evaluate destination so we can use it as a token in other places.
        # User shouldn't use the destination token in the destination field itself.
        expander = Expander(safe=True, **result)
        result["destination"] = expander.evaluate(
            self.main_tab.section("GeneralSection").destination_component.field.text()
        )
        return result

    def set_render_scope(self):
        self.render_scope = render_scope.RenderScope.get()


def main():

    dlg = ConductorDialog()
    dlg.resize(600 * dlg.screen_scale, 800 * dlg.screen_scale)

    # exec_() causes the window to be modal. This means we don't have to manage
    # any communication between max and the dialog such as changes to the frame
    # range while the dialog is open.
    dlg.exec_()


if __name__ == "__main__":
    main()
