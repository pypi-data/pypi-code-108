import yaml
import functools

from gtunrealdevice.config import Data
from gtunrealdevice.exceptions import WrapperError
from gtunrealdevice.exceptions import DevicesInfoError
from gtunrealdevice.exceptions import URDeviceConnectionError
from gtunrealdevice.exceptions import URDeviceOfflineError


def check_active_device(func):
    """Wrapper for URDevice methods.
    Parameters
    ----------
    func (function): a callable function

    Returns
    -------
    function: a wrapper function

    Raises
    ------
    WrapperError: if decorator is used incorrectly
    """
    @functools.wraps(func)
    def wrapper_func(*args, **kwargs):
        """A Wrapper Function"""
        if args:
            device = args[0]
            if isinstance(device, URDevice):
                if device.is_connected:
                    result = func(*args, **kwargs)
                    return result
                else:
                    fmt = '{} device is offline.'
                    raise URDeviceOfflineError(fmt.format(device.name))
            else:
                fmt = 'Using invalid decorator for this instance "{}"'
                raise WrapperError(fmt.format(type(device)))
        else:
            raise WrapperError('Using invalid decorator')
    return wrapper_func


class DevicesData(dict):
    """Devices Data class

    Raises
    ------
    DevicesInfoError: raise exception if devices_info_file contains invalid format
    """
    def __init__(self):
        super().__init__()
        if not Data.is_devices_info_file_exist():
            Data.create_devices_info_file()
        with open(Data.devices_info_filename) as fh:
            data = yaml.load(fh, Loader=yaml.SafeLoader)
            if isinstance(data, dict):
                self.update(data)
            else:
                fmt = '{} file has an invalid format.  Check with developer.'
                raise DevicesInfoError(fmt.format(Data.devices_info_filename))


DEVICES_DATA = DevicesData()


class URDevice:
    """Unreal Device class

    Attributes
    ----------
    address (str): an address of device
    name (str): name of device
    kwargs (dict): keyword arguments

    Properties
    ----------
    is_connected -> bool

    Methods
    -------
    connect(**kwargs) -> bool
    disconnect(**kwargs) -> bool
    execute(cmdline, **kwargs) -> str
    configure(config, **kwargs) -> str

    Raises
    ------
    URDeviceConnectionError: raise exception if device can not connect
    """
    def __init__(self, address, name='', **kwargs):
        self.address = str(address).strip()
        self.name = str(name).strip() or self.address
        self.__dict__.update(**kwargs)
        self._is_connected = False
        self.data = None

    @property
    def is_connected(self):
        """Return device connection status"""
        return self._is_connected

    def connect(self, **kwargs):
        """Connect GT Unreal Device

        Parameters
        ----------
        kwargs (dict): keyword arguments

        Returns
        -------
        bool: connection status
        """
        if self.is_connected:
            return self.is_connected

        if self.address in DEVICES_DATA:
            self.data = DEVICES_DATA.get(self.address)
            self._is_connected = True
            if kwargs.get('showed', True):
                login_result = self.data.get('login')
                print(login_result)
            return self.is_connected
        else:
            fmt = '{} is unavailable for connection.'
            raise URDeviceConnectionError(fmt.format(self.name))

    def disconnect(self, **kwargs):
        """Disconnect GT Unreal Device

        Parameters
        ----------
        kwargs (dict): keyword arguments

        Returns
        -------
        bool: disconnection status
        """
        self._is_connected = False
        if kwargs.get('showed', True):
            msg = '{} is disconnected.'.format(self.name)
            print(msg)
        return self._is_connected

    @check_active_device
    def execute(self, cmdline, **kwargs):
        """Execute command line for GT Unreal Device

        Parameters
        ----------
        cmdline (str): command line
        kwargs (dict): keyword arguments

        Returns
        -------
        str: output of a command line
        """

        data = self.data.get('cmdlines')
        if hasattr(self, 'testcase'):
            data = self.data.get('testcases').get(self.testcase, data)

        no_output = '*** "{}" does not have output ***'.format(cmdline)
        output = data.get(cmdline, self.data.get('cmdlines').get(cmdline, no_output))
        if kwargs.get('showed', True):
            print(output)
        return output

    @check_active_device
    def configure(self, config, **kwargs):
        """Configure GT Unreal Device

        Parameters
        ----------
        config (str): configuration data for device
        kwargs (dict): keyword arguments

        Returns
        -------
        str: result of configuration
        """
        result = self.data.get(config, '')
        if kwargs.get('showed', True):
            print(result)
        return result


def create(address, name='', **kwargs):
    """Create GT Unreal Device instance

    Parameters
    ----------
    address (str): address of device
    name (str): device name
    kwargs (dict): keyword arguments

    Returns
    -------
    URDevice: GT Unreal Device instance.
    """
    device = URDevice(address, name=name, **kwargs)
    return device


def connect(device, **kwargs):
    """Connect GT Unreal Device

    Parameters
    ----------
    kwargs (dict): keyword arguments

    Returns
    -------
    bool: connection status
    """
    result = device.connect(**kwargs)
    return result


def disconnect(device, **kwargs):
    """Disconnect GT Unreal Device

    Parameters
    ----------
    kwargs (dict): keyword arguments

    Returns
    -------
    bool: disconnection status
    """
    result = device.disconnect(**kwargs)
    return result


def execute(device, cmdline, **kwargs):
    """Execute command line for GT Unreal Device

    Parameters
    ----------
    cmdline (str): command line
    kwargs (dict): keyword arguments

    Returns
    -------
    str: output of a command line
    """
    output = device.execute(cmdline, **kwargs)
    return output


def configure(device, config, **kwargs):
    """Configure GT Unreal Device

    Parameters
    ----------
    config (str): configuration data for device
    kwargs (dict): keyword arguments

    Returns
    -------
    str: result of configuration
    """
    result = device.configure(config, **kwargs)
    return result
