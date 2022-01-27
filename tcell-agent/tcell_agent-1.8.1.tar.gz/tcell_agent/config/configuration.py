# -*- coding: utf-8 -*-
# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals

_CONFIGURATION = None


def get_config():
    return _CONFIGURATION


def set_config(config):
    global _CONFIGURATION  # pylint: disable=global-statement
    _CONFIGURATION = config


class TCellAgentConfiguration(object):
    def __init__(self):
        self.enabled = True  # DEFAULT
        self.disabled_instrumentation = set()

    def load_ffi_config(self, config):
        first_app = config.get("applications", {}).get("first", {})
        self.api_key = first_app.get('api_key')
        self.app_id = first_app.get('app_id')
        self.reverse_proxy = first_app.get("reverse_proxy")
        self.reverse_proxy_ip_address_header = first_app.get("reverse_proxy_ip_address_header")

        self.disabled_instrumentation = set(config.get('disabled_instrumentation'))
        self.logging_options = config.get("log_config")
        self.fetch_policies_from_tcell = config.get("update_policy")

        endpoint_config = config.get("endpoint_config")
        self.tcell_api_url = endpoint_config.get("api_url")

        self.load_disabled_configuration()

    def load_disabled_configuration(self):
        self.instrument_django = ("django_auth" not in self.disabled_instrumentation) and self.enabled
