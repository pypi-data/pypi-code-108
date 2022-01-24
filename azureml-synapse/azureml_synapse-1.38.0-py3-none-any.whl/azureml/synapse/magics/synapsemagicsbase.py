# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Module for Synapse magic base class."""

import atexit

from IPython.core.magic import magics_class, Magics
from hdijupyterutils.ipythondisplay import IpythonDisplay
from sparkmagic.utils.sparklogger import SparkLog

from .. import telemetryutils, utils
from ..synapsesession import SynapseSession


@magics_class
class SynapseMagicBase(Magics):
    """Base class of the Synapse magic."""

    def __init__(self, shell):
        """Create the magic instance.

        :param shell: the shell object within which the magic will be hosted
        """
        super(SynapseMagicBase, self).__init__(shell)
        self.logger = SparkLog("SynapseMagic")
        self.ipython_display = IpythonDisplay()
        self.active_session = None
        atexit.register(self._stop_session)

    def show_error(self, msg: str):
        """Show errors.

        :param msg: the error message
        :type msg: str
        """
        utils.send_error(msg)

    def _start_session(self, subscription_id, resource_group, workspace, sparkpool,
                       properties, wslocation, timeout, start_timeout=300):
        assert self.active_session is None
        assert workspace is not None
        assert sparkpool is not None
        assert properties is not None

        self.active_session = SynapseSession(subscription_id, resource_group, workspace, sparkpool, properties,
                                             timeout, self.ipython_display, wslocation)
        try:
            self.active_session.start(start_timeout)
        except Exception:
            self.active_session = None
            raise

    def _stop_session(self):
        try:
            if self.active_session is not None:
                self.active_session.delete()
        except Exception as ex:
            self.logger.error("Close session failed {}".format(ex))
        finally:
            self.active_session = None

    def execute(self, cell, kind: str):
        """Execute the spark code in the cell.

        :param cell: the notebook cell
        :param kind: the spark language used in the cell
        :type kind: str
        """
        if not cell:
            self.show_error("No code to submit")
            return

        if self.active_session is None:
            self.show_error("No active session. Please run '%synapse start' to start a new session.")
            return
        if not self.active_session.can_submit():
            self.show_error(
                "Session is {}. Please run '%synapse stop' to stop it and then '%synapse start' to start a new one."
                .format(self.active_session.status))
            return

        extra = {'kind': kind, 'synapse_session_guid': str(self.active_session.guid)}
        telemetryutils.log_activity('azureml.synapse.run', custom_dimensions=extra, logger_name="run",
                                    func=self.active_session.execute, args=(cell, kind))
