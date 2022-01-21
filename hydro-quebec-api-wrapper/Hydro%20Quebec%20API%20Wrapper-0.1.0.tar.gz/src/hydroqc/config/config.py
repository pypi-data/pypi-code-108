"""Config helper.

This part of the code can probably be rewritten :)
"""

from schema import Schema, Optional
import yaml
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


CONFIG_SCHEMA = Schema({
    "ssl": {
        Optional("validate_ssl", default=True): bool,
    },
    "credentials": {
        "user": str,
        "password": str,
    },
    "formats": {
        Optional("datetime_format", default='%Y-%m-%d %H:%M:%S'): str,
    },
    "periods": {
        # Default peak periods as defined by HQ (as of winter 2021-2022)
        Optional("morning_peak_start", default="06:00:00"): str,
        Optional("morning_peak_end", default="09:00:00"): str,
        Optional("evening_peak_start", default="16:00:00"): str,
        Optional("evening_peak_end", default="20:00:00"): str,

        # Offset in hours to apply to the peak period start time to find the start
        # of the anchor period
        # Per HQ documentation (as of winter 2021-2022) it is 5 hours before the next peak
        Optional("anchor_start_offset", default=5): int,

        # Duration of the anchor period
        # Per HQ documentation (as of winter 2021-2022) it is a duration of 3 hours
        Optional("anchor_duration", default=3): int,

        # Data will be refreshed after 5mn (avoid killing hydro api)
        Optional("event_refresh_seconds", default=300): int,

        # Pre-heat offset
        # Will not be calculated if pre_heat_start_offset = 0
        Optional("pre_heat_start_offset", default=3): int,
        Optional("pre_heat_end_offset", default=0): int,
    }
})


class Config:
    """returns a config object."""

    def __init__(self, config_file='config/config.yaml'):
        """Config constructor."""
        self._configfile_path = config_file

        self._raw_config = self.read()
        self._validated_config = self.validate()

        self.validate_ssl = self._validated_config['ssl']['validate_ssl']
        self.user = self._validated_config['credentials']['user']
        self.password = self._validated_config['credentials']['password']
        self.datetime_format = self._validated_config['formats']['datetime_format']

    def read(self):
        """Read config file."""
        with open(self._configfile_path, 'rb') as fhy:
            config = yaml.load(fhy, Loader=Loader)
        return config

    def validate(self):
        """Validate config file."""
        return CONFIG_SCHEMA.validate(self._raw_config)
