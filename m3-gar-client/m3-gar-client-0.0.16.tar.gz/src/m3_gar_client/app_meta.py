# coding: utf-8
from __future__ import absolute_import
from __future__ import unicode_literals

import warnings

import m3_gar_client


def register_actions():
    if m3_gar_client.config:
        m3_gar_client.config.backend.register_packs()
    else:
        warnings.warn("Не указана конфигурация m3-gar, паки пакета не будут инициализированы")
