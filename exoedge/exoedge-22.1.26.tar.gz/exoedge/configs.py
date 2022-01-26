# pylint: disable=W0141,W0110,C0103,W1202
import os
import threading
import json
import time
from murano_client.client import StoppableThread
from exoedge.channel import DataOutChannel
from exoedge import logger

LOG = logger.getLogger(__name__)


class ExoEdgeConfig(StoppableThread):
    """
        Base class for all config_* resources.
     """
    def __init__(self, **kwargs):
        StoppableThread.__init__(
            self,
            name=kwargs.get('name', self.__class__.__name__)
        )
        self._lock = threading.Lock()
        self.event_new_config = threading.Event()
        self.config = kwargs.get('config')
        self.config_file = kwargs.get('config_file')
        self.device = kwargs.get('device')
        assert self.device,\
            "{} constructor needs murano_client.client.Client object."\
            .format(self.__class__.__name__)
        self.acktime = 0.0

    def ack_config(self):
        """ ACK config to Murano. """
        with self._lock:
            status, result = self.device.ack(
                resource=self.resource,
                payload=json.dumps(self.config)
            )
            if not status:
                LOG.critical('Ack config failed', result)
            self.acktime = time.time()

    def set_config(self, config):
        """
            Update internal and local config.
            Set's event_new_config.
        """
        if isinstance(config, dict):
            LOG.critical(
                'Received new config:\n{}\n'
                .format(json.dumps(config, indent=2))
            )

            with self._lock:
                self.config = config
            self.write_local_config()
            self.ack_config()
            self.event_new_config.set()
        else:
            LOG.critical(
                'Not setting improper config:\n{}'
                .format(config)
            )

    def read_local_config(self):
        """
            Returns dictionary of config from local file
            if it exists.
        """
        infostr = 'READING LOCAL CONFIG_IO file: {}'.format(
            self.config_file)
        LOG.critical('\n{:-^80}\n'.format(infostr))

        if self.config_file:
            try:
                return json.load(open(self.config_file, 'r'))
            except IOError:
                raise NoLocalConfigFile(
                    'config_io file {} does not exist.'
                    .format(self.config_file))
            except ValueError:
                raise InvalidLocalConfigFile(
                    'config_io file contains invalid JSON: \n{}.'
                    .format(open(self.config_file, 'r').read()))
        else:
            raise NoLocalConfigFile('A local config_io file has not been set.')

    def write_local_config(self):
        """
            Writes the current contents of self.config to
            the configured local filename.
        """
        with self._lock:
            if isinstance(self.config_file, str):
                LOG.info(
                    "Writing {!r}:\n{}"
                    .format(self.config_file, json.dumps(self.config, indent=2))
                )
                with open(self.config_file, 'w') as __f:
                    json.dump(self.config, __f)
            else:
                raise InvalidConfigFileName(
                    "invalid config_file name: {}"
                    .format(self.config_file)
                )

class ConfigWatcher(StoppableThread):
    """
       This diagram illustrates that ExoEdge will continuously monitor
       configuration resources (e.g. config_io, config_applications)
       for updates. The order of precedence is that the remote config
       is first, then local configs. If using ExoEdge when is it to
       be configured with a local config, then it is imperative that
       it connects for the first time where the config resource has
       no value (i.e. it has never been set by ExoSense).

            +-----------------+
            |   while true    |
            +-----------------+
                     |
        +----------------------------<------------+
        |            v                            ^
        |       +----|---+         +--------+     |
        |       | Remote |   N     | Local  | N   |
        ^       | Config |------->-| Config |-->--+
        |       |   ?    |         |   ?    |     ^
        |       +----|---+         +----|---+     |
        |            | Y                | Y       |
        |            |                  v         |
        |            |             +----|---+     |
        |            |             | mtime  |     |
        |            |             |   >    | N   |
        |            |             | acktime|-->--+
        |            |             |   ?    |
        |            |             +----|---+
        |            |                  |
        |            v                  v
        |       +----|---+         +----|---+
        |       | ACK    |         | use    |
        |       | Config |       Y | local  |
        |       |        |<--------| config |
        |       +----|---+         +--------+
        |            |
        |            v
        |     +------|------+
        |     |acktime = now|
        |     +------|------+
        |            |
        |            v
        |        +---|--+
        |        |write |
        ^        |local |
        |        |config|
        |        +---|--+
        |            |
        +--<---------+

    """
    def __init__(self, **kwargs):
        StoppableThread.__init__(self, name='ConfigWatcher')
        self.config_mgrs = {e.name: e for e in kwargs.get('config_mgr_list')}
        self.device = kwargs.get('device')

    def start(self):
        """
            Starts all config manager threads.
        """
        for mgr in self.config_mgrs.values():
            mgr.start()
        super(ConfigWatcher, self).start()

    def stop(self):
        """
            Stops all config manager threads.
        """
        for mgr in self.config_mgrs.values():
            mgr.stop()
        super(ConfigWatcher, self).stop()

    def handle_command(self, inbound, payload):
        LOG.info("ACKing data_out: {}".format(inbound))
        status, result = self.device.ack(
            resource=inbound.resource,
            payload=inbound.payload
        )
        if not status:
            LOG.critical('Ack data_out failed', result)

        LOG.warning("Got data_out: {}".format(inbound))
        for name, value in payload.items():
            LOG.debug("Searching for channel: {}".format(name))
            channel = self.config_mgrs['ConfigIO'].channels.get(name)
            if isinstance(channel, DataOutChannel):
                LOG.info(
                    "Executing data_out {}: {}"
                    .format(name, value)
                )
                channel.execute(value)
            else:
                error_msg = "Channel '{}' not defined as a control channel.".format(name)
                LOG.info(error_msg)
                LOG.debug("\n{}\n".format(channel))

    def check_inbound_queue(self):
        # Check inbound queue for remote config or control command
        inbound = self.device.watch(timeout=1.0)

        if inbound:
            try:
                payload = json.loads(inbound.payload)
            except ValueError:
                LOG.critical(
                    'ERROR: `{}` has invalid JSON payload: {}'
                    .format(inbound, inbound.payload))

            # Match to appropriate manager
            for mgr in self.config_mgrs.values():
                if inbound.resource == mgr.resource:
                    mgr.set_config(payload)
                elif inbound.resource == 'data_out':
                    self.handle_command(inbound, payload)
        else:
            LOG.debug('No remote configs or commands.')

    def run(self):
        """
            Process remote and local configs for all config
            manager threads.

            Process data_out control data.
        """
        # Give a moment for the watch threads to spin up
        time.sleep(1)

        # Init - check inbound once per mgr, ensuring all cloud-staged changes are processed
        for mgr in self.config_mgrs:
            self.check_inbound_queue()

        while not self.is_stopped():
            # 1st check for remote configs or commands
            self.check_inbound_queue()

            # 2nd check local configs
            LOG.debug('Checking local configs.')
            for mgr in self.config_mgrs.values():
                if not isinstance(mgr, ExoEdgeConfig):
                    continue
                LOG.debug(
                    'Checking for local {}: {}'
                    .format(mgr.name, mgr.config_file)
                )
                if not os.path.exists(mgr.config_file):
                    LOG.info(
                        "Config file does not exist: {}"
                        .format(mgr.config_file)
                    )
                    continue
                if os.path.getmtime(mgr.config_file) > mgr.acktime:
                    config = mgr.read_local_config()
                    if config:
                        LOG.critical(
                            'Found new local {}: {}'
                            .format(mgr.name, mgr.config_file)
                        )
                        mgr.set_config(config)
                    else:
                        LOG.debug(
                            "Failed to load new local {}: {}"
                            .format(mgr.name, mgr.config_file)
                        )
                else:
                    LOG.debug("Config '{}' already ACK'ed.".format(mgr.name))

class ExoEdgeException(Exception):
    """ Base exception class for ExoEdge. """
    pass

class NoLocalConfigFile(ExoEdgeException):
    """ ExoEdge Exception: local config file not found. """
    pass

class InvalidLocalConfigFile(ExoEdgeException):
    """ ExoEdge Exception: local config file cannot be parsed. """
    pass

class InvalidConfigFileName(ExoEdgeException):
    """ ExoEdge Exception: local config file has invalid name. """
    pass

