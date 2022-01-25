# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/

__authors__ = ["H. Payno"]
__license__ = "MIT"
__date__ = "13/10/2021"

from orangewidget import gui
from orangewidget.widget import Output
from orangewidget.widget import OWBaseWidget
from orangewidget.settings import Setting
from tomwer.gui.cluster.slurm import SlurmSettingsWidget
from tomwer.core.cluster import SlurmClusterConfiguration
import tomwer.core.process.cluster.supervisor
import logging

_logger = logging.getLogger(__name__)


class SlurmClusterOW(OWBaseWidget, openclass=True):
    """
    Orange widget to define a slurm cluster as input of other
    widgets (based on nabu for now)
    """

    name = "slurm cluster"
    id = "orange.widgets.tomwer.cluster.SlurmClusterOW.SlurmClusterOW"
    description = "Let the user configure the cluster to be used."
    icon = "icons/slurm.svg"
    priority = 20
    keywords = ["tomography", "tomwer", "slurm", "cluster", "configuration"]

    want_main_area = True
    resizing_enabled = True
    compress_signal = False

    _static_input = Setting(dict())

    ewokstaskclass = tomwer.core.process.cluster.supervisor._SupervisorPlaceHolder

    class Outputs:
        data_out = Output(name="cluster_config", type=SlurmClusterConfiguration)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = gui.vBox(self.mainArea, self.name).layout()
        self._widget = SlurmSettingsWidget(parent=self)
        layout.addWidget(self._widget)

        if self._static_input != {}:
            self._widget.setConfiguration(self._static_input)

        # trigger the signal to avoid any user request
        self.Outputs.data_out.send(self.getConfiguration())

        # connect signal / slot
        self._widget.sigConfigChanged.connect(self._configurationChanged)

    def _configurationChanged(self):
        slurmClusterconfiguration = self.getConfiguration()
        self.Outputs.data_out.send(slurmClusterconfiguration)
        self._static_input = slurmClusterconfiguration.to_dict()

    def getConfiguration(self):
        return self._widget.getSlurmClusterConfiguration()
