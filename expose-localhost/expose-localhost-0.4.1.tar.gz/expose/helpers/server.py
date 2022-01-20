import sys
from select import select
from socket import socket
from threading import Thread
from time import sleep
from typing import Union

import requests
from paramiko import AutoAddPolicy, RSAKey, SSHClient
from paramiko.channel import Channel
from paramiko.transport import Transport

from expose.helpers.auxiliary import sleeper
from expose.helpers.logger import LOGGER


def join(value: Union[tuple, list, str], separator: str = ':') -> str:
    """Uses ``.join`` to squash a list or tuple using a separator.

    Args:
        value: Value to be squashed.
        separator: Separator to be used to squash.

    Returns:
        str:
        A squashed string.
    """
    return separator.join(map(str, value))


def print_warning(port: int) -> None:
    """Prints a message on screen to run an app or api on the specific port.

    Args:
        port: Port number.
    """
    sys.stdout.write(f'\rRun an application on the port {port} to start tunneling.')
    sleep(5)
    sys.stdout.flush()
    sys.stdout.write('\r')


class Server:
    """Initiates ``Server`` object to create an SSH session to configure the server and intiate the tunneling.

    >>> Server

    **Reverse SSH Port Forwarding**

    Specifies that the given port on the remote server host is to be forwarded to the given host and port on the
    local side. So, instead of your machine doing a simple SSH, the server does an SSH and through the port
    forwarding makes sure that you can SSH back to the server machine.
    """

    def __init__(self, hostname: str, pem_file: str, username: str = "ubuntu"):
        """Instantiates the session using RSAKey generated from a ``***.pem`` file.

        Args:
            hostname: Hostname of the server to connect to.
            pem_file: Takes the .pem filename to authenticate.
            username: Takes the username of the server to authenticate.
        """
        pem_key = RSAKey.from_private_key_file(filename=pem_file)
        self.ssh_client = SSHClient()
        self.ssh_client.load_system_host_keys()
        self.ssh_client.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh_client.connect(hostname=hostname, username=username, pkey=pem_key)

    def run_interactive_ssh(self, commands: dict) -> bool:
        """Authenticates remote server using a ``*.pem`` file and runs interactive ssh commands using ``paramiko``.

        Args:
            commands: Takes a dictionary of commands as keys and the post command idle time as the values.

        Returns:
            bool:
            Returns a boolean flag if all commands were successful.
        """
        for command in commands:
            LOGGER.info(f"Executing {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            if output := stdout.read().decode('utf-8').strip():
                LOGGER.info(output)
            if error := stderr.read().decode("utf-8").strip():
                if error.startswith('debconf:') or 'could not get lock' in error.lower():
                    LOGGER.warning(error)
                else:
                    LOGGER.error(error)
                    self.ssh_client.close()
                    return False
            sleeper(sleep_time=commands[command])
        return True

    def server_write(self, data: dict) -> None:
        """Writes data into files.

        Args:
            data: Takes a dictionary of key-value pair filename and content.
        """
        ftp = self.ssh_client.open_sftp()
        for filename, content in data.items():
            if not filename.startswith("/"):
                filename = f"/home/ubuntu/{filename}"
            file = ftp.file(filename=filename, mode='w')
            file.write(content)
            file.flush()
        ftp.close()

    def _handler(self, channel: Channel, port: int) -> None:
        """Creates a socket and handles TCP IO on the channel created.

        Args:
            channel: Channel for Transport.
            port: Port number on which the socket should connect.
        """
        socket_ = socket()
        try:
            socket_.connect(('localhost', port))
        except Exception as error:
            LOGGER.error(f"Forwarding request to localhost:{port} failed: {error}")
            self.ssh_client.close()
            return

        LOGGER.info(f"Connection open "
                    f"{join(channel.origin_addr)} → {join(channel.getpeername())} → {join(channel.origin_addr)}")
        while True:
            read, write, execute = select([socket_, channel], [], [])
            if socket_ in read:
                if not (data := socket_.recv(1024)):
                    break
                channel.send(data)
            if channel in read:
                if not (data := channel.recv(1024)):
                    break
                socket_.send(data)
        channel.close()
        socket_.close()
        LOGGER.info(f"Connection closed from {join(channel.origin_addr)}")

    def initiate_tunnel(self, port: int) -> None:
        """Initiates port forwarding using ``Transport`` which creates a channel.

        Args:
            port: Port number on which the channel has to be
        """
        while True:
            try:
                response = requests.get(f'http://localhost:{port}')
                if response.ok:
                    LOGGER.info(f'Application is running on port: {port}')
                    break
            except requests.exceptions.ConnectionError:
                print_warning(port=port)
            else:
                print_warning(port=port)
        LOGGER.info("Awaiting connection...")
        transport: Transport = self.ssh_client.get_transport()
        transport.request_port_forward(address="localhost", port=8080)
        try:
            while True:
                if not (channel := transport.accept(timeout=1000)):
                    continue
                Thread(target=self._handler, args=[channel, port], daemon=True).start()
        except KeyboardInterrupt:
            LOGGER.info("Tunneling interrupted")
        LOGGER.info(f"Stopping reverse tunneling on {join(transport.getpeername())}")
        if host_keys := self.ssh_client.get_host_keys().keys():
            LOGGER.info(f"Closing SSH connection on {host_keys[0]}")
        else:
            LOGGER.info(f"Closing SSH connection on {join(transport.getpeername())}")
        transport.cancel_port_forward(address="localhost", port=8080)
        self.ssh_client.close()
