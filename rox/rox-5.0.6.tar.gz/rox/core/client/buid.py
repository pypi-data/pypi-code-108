import hashlib
import json

from rox.core.consts import property_type
from rox.core.utils import md5_generator

class BUID:
    BUID_GENERATORS = [
        property_type.PLATFORM,
        property_type.APP_KEY,
        property_type.LIB_VERSION,
        property_type.API_VERSION
    ]

    def __init__(self, sdk_settings, device_properties):
        self.sdk_settings = sdk_settings
        self.device_properties = device_properties
        self.buid = None

    def get_value(self):
        properties = self.device_properties.get_all_properties()
        buid_md5 = md5_generator.generate(properties, BUID.BUID_GENERATORS)

        self.buid = buid_md5
        return self.buid

    def get_query_string_parts(self):
        return {
            property_type.BUID.name: self.get_value()
        }

    def get_latest_buid(self):
        return self.buid

    def __str__(self):
        return self.buid
