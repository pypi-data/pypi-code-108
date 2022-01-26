#!/usr/bin/env python
# -*- coding: utf-8 -*-
from injector import Module, provider, Injector, singleton
from yams_cli.profile import Profile
from yams_cli.connection_specs import ConnectionSpecs

from yams_cli.logic.core.http_client import HttpClient
from yams_cli.logic.core.manager import Manager
from yams_cli.logic.dispatcher import Dispatcher


class YamsModule(Module):
    def __init__(self, options):
        self._options = options

    @singleton
    @provider
    def profile_provider(self) -> Profile:
        is_configure = self._options['command'] == 'configure'
        return Profile(self._options['profile'], is_configure)

    @singleton
    @provider
    def connection_specs_provider(self) -> ConnectionSpecs:
        return ConnectionSpecs(self._options)

    @singleton
    @provider
    def http_clientProvider(self) -> HttpClient:
        return HttpClient(self.connection_specs_provider(), self.profile_provider())

    @singleton
    @provider
    def manager_provider(self) -> Manager:
        return Manager(self.connection_specs_provider(), self.http_clientProvider())

    @singleton
    @provider
    def dispatcher_provider(self) -> Dispatcher:
        return Dispatcher(self.manager_provider(), self.profile_provider())


def get_injector(options):
    return Injector([YamsModule(options)])
