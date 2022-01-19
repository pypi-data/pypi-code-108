"""
    lager.gateway.commands

    Gateway commands
"""
import click
from ..config import read_config_file, write_config_file

@click.group(name='set')
def setter():
    """
        Lager setter commands
    """
    pass

@setter.group()
def default():
    """
        Set defaults
    """
    pass

@default.command()
@click.argument('gateway_id')
def gateway(gateway_id):
    """
        Set default gateway
    """
    config = read_config_file()
    config.set('LAGER', 'gateway_id', gateway_id)
    write_config_file(config)

@default.command()
@click.argument('device_path')
def serial_device(device_path):
    """
        Set default serial device path
    """
    config = read_config_file()
    config.set('LAGER', 'serial_device', device_path)
    write_config_file(config)
