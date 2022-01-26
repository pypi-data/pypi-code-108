# pylint: disable=W0141,W0110,C0103,W1202
"""
ExoEdge ConfigApplications.
"""
import time
import threading
import json
from exoedge.configs import ExoEdgeConfig
from exoedge import logger
from exoedge.constants import DEFAULTS

LOG = logger.getLogger(__name__)


class ConfigApplications(ExoEdgeConfig, object):
    """
        Thread for maintaining the state of the of the
        config_applications resource according to the
        exoedge.configs.ExoEdgeConfig state machine.

        If an event_new_config is detected, this will
        force the ConfigIO thread to restart all channels.
    """
    resource = 'config_applications'
    def __init__(self, **kwargs):
        ExoEdgeConfig.__init__(
            self,
            name="ConfigApplications",
            device=kwargs.get('device'),
            config_file=kwargs.get(
                'config_applications_file',
                DEFAULTS['config_applications_file']
            )
        )
        self.restart_channels_event = kwargs.get('restart_channels_event')
        self.wait_timeout = float(kwargs.get('wait_timeout', 1.0))
        self.set_config(kwargs.get('config'))

    def run(self):
        """ Update ConfigApplications.

            Waits for a new config_applications event set by
            ConfigApplications.set_config_applications().

            When a new config_applications is recieved,
            the config_io 'event_new_config' event is set
            which restarts all channels.
        """
        LOG.debug('starting')

        while not self.is_stopped():
            if self.event_new_config.wait(timeout=0.5):
                self.restart_channels_event.set()
                self.event_new_config.clear()

        LOG.debug('exiting')


