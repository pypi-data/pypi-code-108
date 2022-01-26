import subprocess
from .errors import *
from .models import *
from .parser import Regrex

regrex = Regrex()


class ProcessContext:
    def __init__(self, process, output, error) -> None:
        self.returncode = process.returncode
        self.output = output
        self.error = error


class ClientManager:
    def __init__(self) -> None:
        self.hostname = 'localhost'

    def __execute(self, command) -> ProcessContext:
        """
        Returns an object of type ProcessContext
        """
        process = subprocess.Popen(
            command.split(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        out, err = process.communicate()
        return ProcessContext(process, out.decode(), err.decode())

    def create_network_interface(self, interface_name: str = 'VPN') -> bool:
        """
        Creates a network interface with the given interface name.

        The `interface_name` is always capitalised

        Returns `True` on successful creation of network interface.
        """
        if len(interface_name) < 1:
            raise InvalidParameterError(
                f'Length of interface_name must be greater than 0')
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD NicCreate {interface_name.upper()}')
        if command.returncode == 0:
            return True
        if command.returncode == 30:
            raise NonZeroExitCode(
                '[X] A Virtual Network Adapter with the specified name already exists. Specify a different name.'
            )
        elif command.returncode == 32:
            raise NonZeroExitCode(
                'You cannot use the specified name for a Virtual Network Adapter device. Use names like VPN, VPN2 and likewise.\nNote: VPN1 is reserved.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def delete_network_interface(self, interface_name: str = 'VPN') -> bool:
        """
        Deletes a network interface with the given interface name.

        The `interface_name` is always capitalised

        Returns `True` on successful deletion of network interface.
        """
        if len(interface_name) < 1:
            raise InvalidParameterError(
                f'Length of interface_name must be greater than 0')
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD NicDelete {interface_name.upper()}')
        if command.returncode == 0:
            return True
        if command.returncode == 29:
            raise NetworkInterfaceNotExistsError(
                '[X] A Virtual Network Adapter with the specified name doesn\'t exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def list_network_interface(self) -> list[NetworkInterface]:
        """
        Lists network interface associated with SoftEther VPN.
        """
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD NicList')
        network_interfaces = []
        if command.returncode == 0:
            for nic in regrex.nic_list.findall(command.output):
                network_interfaces.append(NetworkInterface(nic))
            return network_interfaces
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def create_account(self, account_name: str, hostname: str, port: int, hubname: str, username: str, network_interface_name: str) -> bool:
        """
        Creates an account with the given parameters.

        Returns `True` on successful creation of account.
        """
        if len(account_name) < 1 or len(hostname) < 1 or type(port) is not int or len(hubname) < 1 or len(username) < 1 or len(network_interface_name) < 1:
            raise InvalidParameterError(
                f'Length of arguements must be greater than 0 and port must be an integer')
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountCreate {account_name} /SERVER:{hostname}:{port} /HUB:{hubname} /USERNAME:{username} /NICNAME:{network_interface_name}')
        if command.returncode == 0:
            return True
        if command.returncode == 34:
            raise NonZeroExitCode(
                '[X] VPN Connection Setting with the specified name already exists.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def list_accounts(self) -> list[Accounts]:
        """
        Lists accounts associated with SoftEther VPN.
        """
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountList')
        accounts = []
        if command.returncode == 0:
            for nic in regrex.account_list.findall(command.output):
                accounts.append(Accounts(nic))
            return accounts
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def delete_account(self, account_name: str) -> bool:
        """
        Deletes an account with the given account name.

        Returns `True` on successful deletion of account.
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')
        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountDelete {account_name}')
        if command.returncode == 0:
            return True
        if command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] An account with the specified name doesn\'t exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def set_anomymous_authentication(self, account_name: str) -> bool:
        """
        Set User Authentication Type of VPN Connection Setting to Anonymous Authentication

        Use this to set the user auth type to [Anonymous Authentication] for when a VPN Connection Setting registered on the VPN Client is specified and that VPN Connection Setting connects to the VPN Server.
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')

        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountAnonymousSet {account_name}')
        if command.returncode == 0:
            return True
        if command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] The specified VPN Connection Setting (Account) does not exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def set_password_authentication(self, account_name: str, account_password: str, account_type: str) -> bool:
        """
        ## Purpose
        Set User Authentication Type of VPN Connection Setting to Password Authentication

        ## Description
        Use this to set the user auth type to Password Authentication for when a VPN Connection Setting registered on the VPN Client is specified and that VPN Connection Setting connects to the VPN Server. Specify Standard Password Authentication and RADIUS or NT Domain Authentication as the password authentication type.

        Parameter | Description
        --- | ---
        `account_name` | Specify the name of the VPN Connection Setting whose setting you want to change.
        `account_password` | Specify the password to use for password authentication. If this is not specified, a prompt will appear to input the password.
        `account_type` | Specify either "standard" (Standard Password Authentication) or "radius" (RADIUS or NT Domain Authentication) as the password authentication type.
        """
        if len(account_name) < 1 or len(account_password) < 1 or len(account_type) < 1:
            raise InvalidParameterError(
                f'Length of account_name or account_password or account_type must be greater than 0')
        if account_type not in ['standard', 'radius']:
            raise InvalidParameterError(
                f'account_type of "{account_type}" is invalid.')

        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountPasswordSet {account_name} /PASSWORD:{account_password} /TYPE:{account_type}')
        if command.returncode == 0:
            return True
        if command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] The specified VPN Connection Setting (Account) does not exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def account_connect(self, account_name: str) -> bool:
        """
        ## Purpose
        Start Connection to VPN Server using VPN Connection Setting
        ## Description
        Use this to specify a VPN Connection Setting registered on the VPN Client and start a connection to the VPN Server using that VPN Connection Setting. A VPN Connection Setting that has a connecting status or a connected status will continue to be connected to the VPN Server, or continue to attempt to connect to the VPN Server until the AccountDisconnect command is used to disconnect the connection (Note however, if the AccountRetrySet command is used to specify the number of retries, connection attempts will be aborted when the specified value is reached.)
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')

        command = self.__execute(
            f'vpncmd localhost /CLIENT /CMD AccountConnect {account_name}')
        if command.returncode == 0:
            return True
        elif command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] An account with the specified name doesn\'t exist.'
            )
        elif command.returncode == 35:
            raise AlreadyConnectedError(
                '[X] The specified VPN Connection Setting is currently connected.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def account_disconnect(self, account_name: str) -> bool:
        """
        ## Purpose
        Disconnect VPN Connection Setting During Connection
        ## Description
        Use this to specify a VPN Connection Setting that is registered on the VPN Client and that is either in the condition of connecting or is connected, and immediately disconnect it.
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')

        command = self.__execute(
            f'vpncmd {self.hostname} /CLIENT /CMD AccountDisconnect {account_name}')
        if command.returncode == 0:
            return True
        elif command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] An account with the specified name doesn\'t exist.'
            )
        elif command.returncode == 37:
            raise NotConnectedError(
                '[X] The specified VPN Connection Setting is not connected.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )

    def set_startup_account(self, account_name: str) -> bool:
        """
        ## Purpose
        Set VPN Connection Setting as Startup Connection
        ## Description
        Use this to specify a VPN Connection Setting registered on the VPN Client and set it as the startup connection. The VPN Connection Setting that is set as the startup connection will automatically start the connection process when the VPN Client service starts.
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')

        command = self.__execute(
            f'vpncmd {self.hostname} /CLIENT /CMD AccountStartupSet {account_name}')
        if command.returncode == 0:
            return True
        elif command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] An account with the specified name doesn\'t exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )
    def remove_startup_account(self, account_name: str) -> bool:
        """
        ## Purpose
        Remove Startup Connection of VPN Connection Setting
        ## Description
        When a VPN Connection Setting registered on the VPN Client is specified and that VPN Connection Setting is currently set as a startup connection, use this to delete the startup connection.
        """
        if len(account_name) < 1:
            raise InvalidParameterError(
                f'Length of account_name must be greater than 0')

        command = self.__execute(
            f'vpncmd {self.hostname} /CLIENT /CMD AccountStartupRemove {account_name}')
        if command.returncode == 0:
            return True
        elif command.returncode == 36:
            raise AccountDoesNotExistsError(
                '[X] An account with the specified name doesn\'t exist.'
            )
        else:
            print(command.output)
            raise NonZeroExitCode(
                'Unknown Error'
            )
