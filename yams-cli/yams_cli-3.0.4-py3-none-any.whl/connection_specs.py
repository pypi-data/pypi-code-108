#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from io import StringIO

log = logging.getLogger('yams-cli.connection-specs')

DEFAULT_SETTINGS = {
    'management-url': "TO_BE_FILLED",
    'access_key_id': "TO_BE_FILLED",
    'private_secret_key': "TO_BE_FILLED"
}


class ConnectionSpecs(object):

    def __init__(self, options):
        self._specs = {
            'management_url': options['management_url'],
            'fetch_url': options['fetch_url'],
            'api_version': options['api_version'],
            'jwt_algorithm': options['jwt_algorithm']
        }

    def get_connection_value(self, value):
        return self._specs[value]

    def dump_connection_specs(self):
        dump = StringIO()
        dump.write("management_url={}\n".format(self.get_connection_value('management_url')))
        dump.write("fetch_url={}\n".format(self.get_connection_value('fetch_url')))
        dump.write("api_version={}\n".format(self.get_connection_value('api_version')))
        dump.write("jwt_algorithm={}\n".format(self.get_connection_value('jwt_algorithm')))
        return dump.getvalue()

    @staticmethod
    def dump_profile(profile):
        dump = StringIO()
        profile.write(dump)
        return dump.getvalue()
