import os

from rox.core.consts import property_type
from rox.core.consts.build import Build


class DeviceProperties(object):
    def __init__(self, sdk_settings, rox_options):
        self.sdk_settings = sdk_settings
        self.rox_options = rox_options

    def get_all_properties(self):
        return {
            property_type.LIB_VERSION.name: self.lib_version,
            property_type.ROLLOUT_BUILD.name: '50', #TODO: fix the build number
            property_type.API_VERSION.name: Build.API_VERSION,
            property_type.APP_RELEASE.name: self.rox_options.version, #used for the version filter
            property_type.DISTINCT_ID.name: self.distinct_id,
            property_type.APP_KEY.name: self.sdk_settings.api_key,
            property_type.PLATFORM.name: Build.PLATFORM,
            property_type.DEV_MODE_SECRET.name: self.rox_options.dev_mode_key,
        }

    @property
    def rollout_environment(self):
        env = os.getenv('ROLLOUT_MODE', '')
        return env if env in ['QA', 'LOCAL'] else 'PRODUCTION'

    @property
    def lib_version(self):
        return '1.0.0'

    @property
    def rollout_key(self):
        return self.get_all_properties().get(property_type.APP_KEY.name, None)

    @property
    def distinct_id(self):
        return 'stam'
