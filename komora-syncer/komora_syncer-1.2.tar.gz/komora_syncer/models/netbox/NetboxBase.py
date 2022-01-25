from komora_syncer.connections.NetboxConnection import NetboxConnection

import logging
logger = logging.getLogger(__name__)

class NetboxBase:
    def __init__(self):
        self.netbox = NetboxConnection()
        self.netbox.open()