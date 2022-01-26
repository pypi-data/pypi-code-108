class NetworkInterface:
    def __init__(self, nic_info: tuple) -> None:
        self.adapter_name = nic_info[0]
        self.status = nic_info[1]
        self.mac_address = nic_info[2]
        self.version = nic_info[3]

class Accounts:
    def __init__(self, connection_settings) -> None:
        self.name = connection_settings[0]
        self.status = connection_settings[1]
        self.hostname = connection_settings[2]
        self.virtual_hub = connection_settings[3]
        self.adapter_name = connection_settings[4]