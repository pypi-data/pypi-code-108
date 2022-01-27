
from vpv.ui.views.ui_consoletab import Ui_console
from PyQt5 import QtCore, QtGui
# from pyqtgraph import console
from vpv.common import Layers
import skimage
import scipy
import SimpleITK as sitk



import os
os.environ['QT_API'] = 'pyqt'
import sip
sip.setapi("QString", 2)
sip.setapi("QVariant", 2)
from PyQt5.QtGui  import *
from PyQt5.QtWidgets import QWidget
# Import the console machinery from ipython

from qtconsole.rich_jupyter_widget import RichJupyterWidget
from qtconsole.inprocess import QtInProcessKernelManager
from IPython.lib import guisupport

class Console(QWidget):
    console_command_executed = QtCore.pyqtSignal()

    def __init__(self, mainwindow, vpv):
        super(Console, self).__init__(mainwindow)
        self.ui = Ui_console()
        self.ui.setupUi(self)
        self.vpv = vpv
        variables = {
             "vpv_viewer": self.vpv,
             "current_volume": self.current_volume,
             "volume_ids": self.volume_ids,
             "get_volume": self.get_volume,
             "print_process_id": print_process_id
        }

        widget = ExampleWidget(variables, parent=vpv)
        self.ui.mainLayout.addWidget(widget)

    def activate_tab(self):
        pass

    def current_volume(self):
        return self.vpv.current_view.layers[Layers.vol1]

    def volume_ids(self):
        return self.vpv.model.volume_id_list()

    def get_volume(self, id_):
        return self.vpv.model.getvol(id_)._arr_data

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Enter:
            print('event')
            self.vpv.on_console_enter_pressesd()


class QIPythonWidget(RichJupyterWidget):
    """ Convenience class for a live IPython console widget.
    We can replace the standard banner using the customBanner argument"""

    def __init__(self, customBanner='VPV console', parent=None, *args,**kwargs):
        if customBanner!=None: self.banner=customBanner
        super(QIPythonWidget, self).__init__(*args,**kwargs)
        self.kernel_manager = kernel_manager = QtInProcessKernelManager()
        kernel_manager.start_kernel()
        kernel_manager.kernel.gui = 'qt4'
        self.kernel_client = kernel_client = self._kernel_manager.client()
        kernel_client.namespace = parent
        kernel_client.start_channels()

        def stop():
            kernel_client.stop_channels()
            kernel_manager.shutdown_kernel()
            guisupport.get_app_qt4().exit()
        self.exit_requested.connect(stop)

    def pushVariables(self, variableDict):
        """ Given a dictionary containing name / value pairs, push those variables to the IPython console widget """
        self.kernel_manager.kernel.shell.push(variableDict)

    def clearTerminal(self):
        """ Clears the terminal """
        self._control.clear()

    def printText(self, text):
        """ Prints some plain text to the console """
        self._append_plain_text(text)

    # def executeCommand(self, command):
    #     """ Execute a command in the frame of the console widget """
    #
    #     a = self._execute(command, False)
    #     print(a)


class ExampleWidget(QWidget):
    """ Main GUI Widget including a button and IPython Console widget inside vertical layout """
    def __init__(self, variables, parent=None):
        super(ExampleWidget, self).__init__(None)
        layout = QVBoxLayout(self)
        self.button = QPushButton('Another widget')
        ipyConsole = QIPythonWidget(parent=parent)
        #layout.addWidget(self.button)
        layout.addWidget(ipyConsole)
        # This allows the variable foo and method print_process_id to be accessed from the ipython console
        ipyConsole.pushVariables(variables)
        ipyConsole.printText("""Some functions to use. See docs for a full list:
        current_volume(): gets the the currently selected volume as a numpy array
        volume_ids(): gets a list of all available volume ids
        get_volume(volume_id): gets a volume as a numpy array
        """)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return:
            print('event')
            self.parent.on_console_enter_pressesd

def print_process_id():
    print('Process ID is:', os.getpid())


