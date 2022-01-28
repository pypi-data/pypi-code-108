import os

from netmiko import ConnectHandler
from halo import Halo


def ping_from_switch(coninfo: dict, ip_list: list[str]) -> None:
    """
    Pings list of IPs from switch. Used primarily for populating ARP table.
    :param coninfo: Dictionary of connection info
    :param ip_list: List of IP addresses to ping
    :return: None
    """
    spinner = Halo(spinner='dots')
    spinner.start(f'\nConnecting to {coninfo["ip"]}')
    connection = ConnectHandler(**coninfo)
    spinner.succeed()
    spinner.stop()
    for ip in ip_list:
        spinner.start(f'\nPinging {ip} from switch {coninfo["ip"]}')
        connection.send_command(f'ping {ip}')
        spinner.succeed()
        spinner.stop()
    connection.disconnect()


def run_commands(coninfo: dict, commands: list[str]) -> None:
    """
    Cycles through a list of commands to run on a switch
    :param coninfo: Dictionary with connecion info
    :param commands: Command to run on switch
    :return: None
    """
    spinner = Halo(spinner='dots')
    spinner.start(f'Connecting to {coninfo["ip"]}')
    connection = ConnectHandler(**coninfo)
    spinner.succeed()
    spinner.stop()
    for command in commands:
        spinner.start(f'\nRunning "{command}" on switch at {coninfo["ip"]}. This might take a bit.')
        return_data = connection.send_command(command)
        spinner.succeed()
        spinner.stop()
        command = command.replace(' ', '_').replace('-', '_')
        spinner.start(f'\nWriting {command} to switch_{command}/{coninfo["ip"]}')
        if not os.path.exists(f'switch_{command}'):
            os.mkdir(f'switch_{command}')
        with open(f'switch_{command}/{coninfo["ip"]}', 'w+') as f:
            f.write(return_data)
        spinner.succeed(f'\nCommand "show {command}" on {coninfo["ip"]} completed and written to switch_{command}/{coninfo["ip"]}')
        spinner.stop()
    spinner.start(f'\nClosing connection to {coninfo["ip"]}')
    connection.disconnect()
    spinner.succeed()
    spinner.stop()
