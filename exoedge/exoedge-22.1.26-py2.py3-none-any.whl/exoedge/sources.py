# pylint: disable=W1202,C0103
import sys
import threading
import time
from murano_client.client import StoppableThread, WatchQueue
from exoedge import logger

LOG = logger.getLogger(__name__)


class ExoEdgeClassicSource(object):
    def __init__(self, channel, module_function):
        self.channel = channel
        self.function = module_function
        self.interval = channel.protocol_config.sample_rate / 1000.0 # pylint: disable=E1101,
        self.timer = None

    def start_source(self):
        positionals = self.channel.protocol_config.app_specific_config.get('positionals')
        parameters = self.channel.protocol_config.app_specific_config.get('parameters')
        LOG.warning(
            "call_again: calling: {} with: {} and {}"
            .format(self.function, positionals, parameters)
        )
        try:
            self.timer = threading.Timer(
                self.interval,
                self.start_source
            )
            if positionals and parameters:
                res = self.function(
                    *positionals,
                    **parameters
                )
            elif positionals and not parameters:
                res = self.function(
                    *positionals
                )
            elif not positionals and parameters:
                res = self.function(
                    **parameters
                )
            else:
                res = self.function()

            self.channel.put_sample(res)

            self.timer.start()
        except Exception as exc:
            error_msg = "Stopping source! Calling {} raises: {}".format(
                self.function, exc)
            LOG.error(error_msg)
            self.channel.put_channel_error(error_msg)
            self.stop_source()

    def stop_source(self):
        LOG.critical("Stopping!")
        if self.timer:
            self.timer.cancel()


class DataOutQueueObject(object):
    def __init__(self, channel, data_out_value):
        self.channel = channel
        self.data_out_value = data_out_value

    def __repr__(self):
        return "<{}: {}>".format(self.channel.name, self.data_out_value)

class ExoEdgeSource(StoppableThread):
    """
        Template class for creating custom ExoEdge sources.

        To use this class, simply import and subclass it to gain access
        to the members and methods available.
    """
    _Q_DATA_OUT = WatchQueue()

    def __init__(self, **kwargs):
        """

        """
        t_kwargs = {}
        t_kwargs.update(name=kwargs.get('name') or self.__class__.__name__)
        if kwargs.get('group'):
            t_kwargs.update(group=kwargs.get('group'))
        if kwargs.get('target'):
            t_kwargs.update(target=kwargs.get('target'))
        if kwargs.get('args'):
            t_kwargs.update(args=kwargs.get('args'))
        if kwargs.get('kwargs'):
            t_kwargs.update(kwargs=kwargs.get('kwargs'))

        LOG.info("{} source thread kwargs: {}".format(self.__class__.__name__, t_kwargs))
        LOG.info("{} source other kwargs: {}".format(self.__class__.__name__, kwargs))

        super(ExoEdgeSource, self).__init__(**t_kwargs)
        self.setDaemon(True)

        # exoedge sources can have access to config_io
        self.config_io_thread = None

        # exoedge sources need access to config_applications
        self.config_applications_thread = None
        LOG.info("{} init complete.".format(str(self)))
        self.start_source = self.get_source

    def get_channels_by_application(self, application):
        """
            Function for iterating over all channels and
            compiiing a list of channels that are configured
            for
                config_io
                  .$(id)
                    .protocol_config
                      .application

            equal to the 'application' parameter.
        """
        channels_by_application = []
        if self.config_io_thread:
            for c in self.config_io_thread.channels.values():
                if c.protocol_config.application == application:
                    if c not in channels_by_application:
                        channels_by_application.append(c)
        return channels_by_application

    def get_channels_by_module(self, module):
        """
            Function for iterating over all channels and
            compiiing a list of channels that are configured
            for
                config_io
                  .$(id)
                    .protocol_config
                      .app_specific_config
                        .module

            equal to the 'module' parameter.
        """
        channels_by_module = []
        if self.config_io_thread:
            for c in self.config_io_thread.channels.values():
                if c.protocol_config.app_specific_config.get('module') == module:
                    if c not in channels_by_module:
                        channels_by_module.append(c)
        return channels_by_module

    def get_configured_applications(self):
        """
            If a value in config_applications is set or there is a local
            config_applications file, return the dictionary object.
        """
        if self.config_applications_thread and self.config_applications_thread.config:
            return self.config_applications_thread.config
        return {}

    def put_data_out(self, channel, data_out_value):
        self._Q_DATA_OUT.put(DataOutQueueObject(channel, data_out_value))

    def stop_source(self):
        LOG.warning("Stopping source: {}".format(self))
        self.stop()

    def get_source(self):
        """ Call this function atleast once to start the
        ExoEdgeSource thread. Call this function and assign
        to a variable to gain access to members and methods
        associated with this thread. """

        if not self.is_started():
            LOG.info("{} starting...".format(self.__class__.__name__))
            while not self.config_io_thread:
                for thread in threading.enumerate():
                    if thread.getName() == "ConfigIO":
                        self.config_io_thread = thread
                        break
                else:
                    LOG.critical("Waiting for config_io thread to start...")
                    time.sleep(0.25) # only executed if the inner loop did NOT break
            LOG.info("{} started.".format("ConfigIO"))
            while not self.config_applications_thread:
                for thread in threading.enumerate():
                    if thread.getName() == "ConfigApplications":
                        self.config_applications_thread = thread
                        break
                else:
                    LOG.critical("Waiting for config_applications thread to start...")
                    time.sleep(0.25) # only executed if the inner loop did NOT break
            LOG.info("{} started.".format("ConfigApplications"))
            super(ExoEdgeSource, self).start()

        LOG.warning("source: {} startup complete.".format(self.name))
        return self
