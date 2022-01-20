import zmq
import yaml
import logging
from pathlib import Path
from . import control_adapter as ctrl

def coordinate_daq_access(network_config: dict):
    """ a function run in a separate process that coordinates the access
    to the daq-system and target system so that the access is serialized
    and the daq interface is stabilized towards the datenraffinerie

    :network_config: the hostnames and ports of the target, daq-client and daq-server
    :returns: Nothing

    """
    logging.basicConfig(filename='daq_coordinator.log',
                        encoding='utf-8',
                        level=logging.DEBUG)
    logger = logging.getLogger('daq_coordinator')
    logger.debug('creating zmq context and socket')
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket_address = f"tcp://{network_config['daq_coordinator']['hostname']}:" +\
                     f"{network_config['daq_coordinator']['port']}"
    socket.bind(socket_address)
    logger.debug('bound to: %s' % socket_address)
    target = ctrl.TargetAdapter(network_config['target']['hostname'],
                                network_config['target']['port'])
    daq_system = ctrl.DAQSystem(network_config['server']['hostname'],
                                network_config['server']['port'],
                                network_config['client']['hostname'],
                                network_config['client']['port'])
    logger.debug('created the target and daq systems')
    while True:
        logger.debug('waiting for message')
        message = socket.recv()
        message_delimiter = message.find(b';')
        command = message[:message_delimiter]
        if command == b'measure':
            logger.debug('received message "measure"')
            if not target.has_default() and not daq_system.has_default():
                socket.send_string('error: no defaults loaded')
                continue
            config = yaml.safe_load(message[message_delimiter+1:].decode())
            logger.debug('Received Configuration:\n' + yaml.dump(config))
            daq_config = config['daq']
            target_config = config['target']
            target.configure(target_config, overlays_default=True)
            daq_system.configure(daq_config)
            measurement_data_path = Path('./measurement_data.raw')
            daq_system.take_data(measurement_data_path)
            with open(measurement_data_path, 'rb') as data_file:
                socket.send(data_file.read())
        elif command == b'load defaults':
            logger.debug('received message: %s' % command.decode())
            logger.debug('received default config:\n%s' %
                         message[message_delimiter+1:].decode())
            default_config = yaml.safe_load(
                    message[message_delimiter+1:].decode())
            target_default_config = default_config['target']
            daq_default_config = default_config['daq']
            target.load_default_config(target_default_config)
            daq_system.load_default_config(daq_default_config)
            socket.send_string('defaults loaded')
        else:
            logger.warning('invalid command message received: %s' %
                           command.decode())
            socket.send_string('invalid command')
