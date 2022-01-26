#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import stat
import logging
import configparser

from os.path import isfile
from configparser import NoSectionError
from io import StringIO

log = logging.getLogger('yams-cli.profile')


class Profile(object):
    """
    Read and parse the credentials file. The credentials file format is:
    ---------------
    [default]
    tenant_id = TENANT_ID
    access_key_id = ACCESS_KEY_ID
    private_secret_key = RSA_KEY
    -----------------
    """

    def __init__(self, profile_name, is_configure=False):
        """
        :param profile_name: String. Name of the profile into credentials file.
        :param is_configure: Boolean. When true, cli is being executed in configuration mode.
        """
        self._profile = configparser.ConfigParser()
        self._profile_name = profile_name.upper()
        self._profile_file = os.path.expanduser(os.path.join('~', '.yams', 'credentials'))

        if self._profile_name == 'DEFAULT':
            log.error("Profile name '{}' not allowed in {}. Aborting".format(self._profile_name, self._profile_file))
            sys.exit(1)

        log.debug('Loading profile file: {}'.format(self._profile_file))
        if isfile(self._profile_file):
            self._profile.read(self._profile_file)
            # When not configuring with cli, if the section/option doesn't exist, abort.
            if not is_configure:
                if not self._profile.has_section(self._profile_name):
                    log.error("Profile '{}' not found in {}. Aborting".format(self._profile_name, self._profile_file))
                    sys.exit(1)

                if (not self._profile.has_option(self._profile_name, 'tenant_id') or
                        not self._profile.has_option(self._profile_name, 'access_key_id') or
                        not self._profile.has_option(self._profile_name, 'private_secret_key')):
                    log.error(
                        "Profile '{}' has not required sections [tenant_id, access_key_id, private_secret_key]. Aborting".format(
                            self._profile_name))
                    sys.exit(1)
        else:
            if not is_configure:
                log.error("Profile file '{}' does not exist. Execute configure command to create it. Aborting".format(
                    self._profile_file))
                sys.exit(1)

    @property
    def profile(self):
        return self._profile

    def create_credentials_file_if_needed(self):
        if os.path.exists(self._profile_file):
            return False

        directory = os.path.expanduser(os.path.join('~', '.yams'))
        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.exists(self._profile_file):
            flags = os.O_WRONLY | os.O_CREAT
            mode = stat.S_IRUSR | stat.S_IWUSR
            file_descriptor = os.open(self._profile_file, flags, mode)
            self._profile.write(file_descriptor)
            os.close(file_descriptor)

        return True

    def create_profile(self, tenant_id, access_key_id, private_secret_key):
        """ Creates a new profile into the configuration file.
        :param tenant_id: id of the tenant 
        :param access_key_id: access id valid for tenant
        :param private_secret_key: 
        :return:
        """
        # if profile is not default and does not exist yet, create it
        if not self._profile.has_section(self._profile_name):
            self._profile.add_section(self._profile_name)

        self._profile.set(self._profile_name, 'tenant_id', tenant_id)
        self._profile.set(self._profile_name, 'access_key_id', access_key_id)
        self._profile.set(self._profile_name, 'private_secret_key', private_secret_key)

        with open(self._profile_file, 'w') as cf:
            self._profile.write(cf)

    def get_profile_value_or_none(self, value):
        if not self._profile.has_section(self._profile_name):
            return None
        if not self._profile.has_option(self._profile_name, value):
            return None
        return self._profile.get(self._profile_name, value)

    def get_profile_value(self, value):
        try:
            return self._profile.get(self._profile_name, value)
        except NoSectionError:
            log.error("Profile value '{}' not found in '{}'. Aborting".format(value, self._profile_name))
            sys.exit(1)

    @staticmethod
    def dump_profile(profile):
        dump = StringIO()
        profile.write(dump)
        return dump.getvalue()
