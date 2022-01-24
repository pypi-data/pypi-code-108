"""
Congregate - GitLab instance migration utility

Copyright (c) 2022 - GitLab
"""

import os
import json
from re import sub, split
from configparser import ConfigParser, ParsingError
from gitlab_ps_utils.string_utils import deobfuscate


class BaseConfig(object):
    def __init__(self, path=None):
        config_path = path
        self.config = ConfigParser()
        if not os.path.exists(config_path):
            print("WARNING: No configuration found. Configuring empty file {}".format(
                config_path))
            with open(config_path, "w") as f:
                self.config.write(f)
        try:
            self.config.read(config_path)
        except ParsingError as pe:
            print("Failed to parse configuration, with error:\n{}".format(pe))
            raise SystemExit() from pe

    def option_exists(self, section, option):
        return self.config.has_option(
            section, option) and self.config.get(section, option)

    def prop(self, section, option, default=None, obfuscated=False):
        if self.option_exists(section, option):
            if not obfuscated:
                return self.config.get(section, option)
            return deobfuscate(self.config.get(section, option))
        return default

    def prop_lower(self, section, option, default=None):
        if self.option_exists(section, option):
            return self.config.get(section, option).lower()
        return default

    def prop_int(self, section, option, default=None):
        """
            Returns configuration property string casted to an int
        """
        if self.option_exists(section, option):
            return self.config.getint(section, option)
        return default

    def prop_bool(self, section, option, default=None):
        """
            Returns configuration property string casted to a bool
        """
        if self.option_exists(section, option):
            return self.config.getboolean(section, option)
        return default

    def prop_list(self, section, option, default=None):
        """
            Returns configuration property string as a list.

            For example, a configuration property stored as '[hello, world, how, are you]'
            will be returned as ["hello", "world", "how", "are", "you"]
        """
        if self.option_exists(section, option):
            return split(r', |,', sub(r'\[|\]|\"\"\"', '', self.config.get(section, option)))
        return default

    def prop_array(self, section, option, default=None, obfuscated=False):
        """
            Comma separated string values
        """
        if self.option_exists(section, option):
            props = [p.strip(" ")
                     for p in self.config.get(section, option).split(",")]
            if not obfuscated:
                return props
            return [deobfuscate(p) for p in props]
        return default

    def prop_dict(self, section, option, default=None):
        """
            Returns configuration property JSON string as a dictionary
        """
        if self.option_exists(section, option):
            return json.loads(self.config.get(section, option))
        return default

    def as_obj(self):
        """
        Return entire config object (setter)
        """
        return self.config

    def as_dict(self):
        """
        Return entire config as dictionary (copy)
        """
        d = dict(self.config._sections)
        for k in d:
            d[k] = dict(self.config._defaults, **d[k])
            d[k].pop('__name__', None)
        return d
