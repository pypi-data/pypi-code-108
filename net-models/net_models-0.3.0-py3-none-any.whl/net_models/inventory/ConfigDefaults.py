import dataclasses
from pydantic import Extra
from pydantic.typing import Literal
from net_models.models import BaseNetModel


__all__ = [
    'ConfigDefaults',
    'CiscoIosCatalystDefaults',
    'CiscoIosSPConfigDefaults'
]

class ConfigDefaults(BaseNetModel):
    _registry = {}

    class Config:
        extra = Extra.ignore

    def __init_subclass__(cls, **kwargs):
        device_type = kwargs.pop('device_type', None)
        if device_type is not None:
            cls._registry[device_type] = cls
        super().__init_subclass__(**kwargs)

    def __new__(cls, **kwargs):
        device_type = kwargs.pop('device_type', None)
        subclass = None
        if device_type is not None:
            subclass = cls._registry.get(device_type, None)
        if subclass is None:
            subclass = cls
        obj = object.__new__(subclass)
        obj.__init__(**kwargs)
        return obj

    # Base Fields
    INCLUDE_DEFAULTS: bool = False
    PLATFORM_CDP_DEFAULT_ON: bool = None
    PLATFORM_LLDP_DEFAULT_ON: bool = None
    INTERFACES_DEFAULT_NO_SHUTDOWN: bool = None
    INTERFACES_DEFAULT_CDP_ENABLED: bool = None
    INTERFACES_DEFAULT_LLDP_ENABLED: bool = None
    INTERFACE_DEFAULT_MODE: Literal['switched', 'routed'] = None


class CiscoIosCatalystDefaults(ConfigDefaults, device_type='cisco_ios_catalyst'):

    PLATFORM_CDP_DEFAULT_ON = True
    PLATFORM_LLDP_DEFAULT_ON = False
    INTERFACES_DEFAULT_NO_SHUTDOWN = True
    INTERFACES_DEFAULT_CDP_ENABLED = True
    INTERFACES_DEFAULT_LLDP_ENABLED = False
    INTERFACE_DEFAULT_MODE: Literal['switched', 'routed'] = 'switched'

class CiscoIosSPConfigDefaults(ConfigDefaults, device_type='cisco_ios_sp'):

    PLATFORM_CDP_DEFAULT_ON = False
    PLATFORM_LLDP_DEFAULT_ON = False
    INTERFACES_DEFAULT_NO_SHUTDOWN = False
    INTERFACES_DEFAULT_CDP_ENABLED = False
    INTERFACES_DEFAULT_LLDP_ENABLED = False
    INTERFACE_DEFAULT_MODE: Literal['switched', 'routed'] = 'routed'


if __name__ == '__main__':

    test = ConfigDefault(device_type='cisco_ios_catalyst')
    print(test)