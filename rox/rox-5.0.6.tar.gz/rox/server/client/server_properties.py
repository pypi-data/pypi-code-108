import uuid

from rox.core.client.device_properties import DeviceProperties
import rox


class ServerProperties(DeviceProperties):
    def __init__(self, sdk_settings, rox_options):
        super(ServerProperties, self).__init__(sdk_settings, rox_options)
        self._distinct_id = str(uuid.uuid4())

    @property
    def distinct_id(self):
        return self._distinct_id

    @property
    def lib_version(self):
        return rox.__version__
