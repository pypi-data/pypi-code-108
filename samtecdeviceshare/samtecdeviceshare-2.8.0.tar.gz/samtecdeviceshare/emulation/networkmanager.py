from typing import List, Any

class Connection:
    pass

class Device:
    DeviceType: int = 2

class ActiveConnection:
    State: int = 2

class Settings:

    @classmethod
    def ListConnections(cls):
        return []

    @classmethod
    def AddConnection(cls, settings):
        pass

class NetworkManager:

    @classmethod
    def GetDevices(cls):
        return []

    ActiveConnections: List[Any] = []

    @classmethod
    def ActivateConnection(cls, *args, **kwargs):
        return ActiveConnection()

    @classmethod
    def GetDeviceByIpIface(cls, iface):
        return None

NM_DEVICE_STATE_ACTIVATED = 100
NM_DEVICE_STATE_IP_CHECK = 80
NM_DEVICE_STATE_IP_CONFIG = 70
NM_DEVICE_STATE_FAILED = 120
NM_DEVICE_STATE_UNAVAILABLE = 20
NM_DEVICE_STATE_UNMANAGED = 10
NM_DEVICE_TYPE_ETHERNET = 1
NM_DEVICE_TYPE_WIFI = 2

NM_ACTIVE_CONNECTION_STATE_ACTIVATED = 2

# @classmethod
# def nm_state(cls):
#     pass
