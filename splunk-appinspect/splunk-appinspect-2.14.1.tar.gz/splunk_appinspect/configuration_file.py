# Copyright 2019 Splunk Inc. All rights reserved.
"""Splunk conf file abstraction base module"""
import re


class NoSectionError(Exception):
    """Exception raised when a specified section is not found."""


class NoOptionError(Exception):
    """Exception raised when a specified option is not found in the specified section."""


class DuplicateSectionError(Exception):
    """Exception raised if add_section() is called with the name of a section that is already present."""


class ConfigurationSetting(object):
    def __init__(self, name, value=str, header=None, lineno=None):
        self.name = name
        self.value = value
        self.header = [] if header is None else header
        self.lineno = lineno


class ConfigurationSection(object):
    def __init__(self, name, header=None, lineno=None):
        self.name = name
        self.header = [] if header is None else header
        self.lineno = lineno
        self.options = dict()

    def add_option(self, name, value, header=None, lineno=None):
        self.options[name] = ConfigurationSetting(
            name, value, header=header, lineno=lineno
        )

    def has_option(self, optname):
        return optname in self.options

    def has_setting_with_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key, _ in iter(self.options.items()):
            if re.search(setting_key_regex_object, key):
                return True
        return False

    def get_option(self, optname):
        if optname in self.options:
            return self.options[optname]

        error_output = f"No option '{optname}' exists in section '{self.name}'"
        raise NoOptionError(error_output)

    def settings(self):
        for key, _ in iter(self.options.items()):
            yield self.options[key]

    def settings_with_key_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for key, value in iter(self.options.items()):
            if re.search(setting_key_regex_object, key):
                yield value

    def items(self):
        return [
            (property_name, configuration_setting.value, configuration_setting.lineno)
            for (property_name, configuration_setting) in iter(self.options.items())
        ]


class ConfigurationFile(object):
    def __init__(self):
        self.headers = []
        self.sects = dict()
        self.errors = []

    def set_main_headers(self, header):
        self.headers = header

    def add_error(self, error, lineno, section):
        self.errors.append((error, lineno, section))

    def get(self, sectionname, key):
        if self.has_section(sectionname):
            option = self.sects[sectionname].get_option(key)
            if option is not None:
                return option.value

            error_output = (
                "The option does not exist in the section "
                f" searched. Section: {key}"
                f" Option: '{sectionname}'"
            )
            raise NoOptionError(error_output)
        else:
            raise NoSectionError(f"No section '{sectionname}' exists")

    def add_section(self, sectionname, header=None, lineno=None):
        section = ConfigurationSection(sectionname, header=header, lineno=lineno)
        self.sects[sectionname] = section
        return section

    def has_option(self, sectionname, key):
        return self.has_section(sectionname) and self.get_section(
            sectionname
        ).has_option(key)

    def has_section(self, sectionname):
        return sectionname in self.sects

    def get_section(self, sectionname):
        if sectionname in self.sects:
            return self.sects[sectionname]

        raise NoSectionError(f"No such section: {sectionname}")

    def section_names(self):
        return self.sects.keys()

    def sections(self):
        for _, value in iter(self.sects.items()):
            yield value

    # Returns only sections that have a property that matches a regex pattern
    def sections_with_setting_key_pattern(self, setting_key_regex_pattern):
        setting_key_regex_object = re.compile(setting_key_regex_pattern, re.IGNORECASE)
        for _, value in iter(self.sects.items()):
            for setting in value.settings():
                if re.search(setting_key_regex_object, setting.name):
                    yield value

    def items(self, sectionname):
        return self.get_section(sectionname).items()

    def build_lookup(self):
        """Build a dictionary from a config file where { sect => [options ...] }."""
        return {
            sect: [option for option in self.sects[sect].options] for sect in self.sects
        }
