# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import configparser
import functools
import typing as ty

from arbiterd.common import cpu


@functools.lru_cache
def parse_nova_conf(nova_conf: str) -> configparser.ConfigParser:
    config = configparser.ConfigParser(interpolation=None)
    config.read(nova_conf)
    return config


def get_string(
        conf: configparser.ConfigParser, section, option, default=None,
        strip=True
) -> str:

    data = conf.get(section, option, fallback=default)
    if data is not None and strip:
        data = data.strip('"').strip('\'')
    return data


def get_dedicated_cpus(nova_conf: str) -> ty.Set[int]:
    nova = parse_nova_conf(nova_conf)
    data = get_string(nova, 'compute', 'cpu_dedicated_set')
    if data is None:
        return set()
    return cpu.parse_cpu_spec(data)


def get_shared_cpus(nova_conf: str) -> ty.Set[int]:
    nova = parse_nova_conf(nova_conf)
    data = get_string(nova, 'compute', 'cpu_shared_set')
    if data is None:
        return set()
    return cpu.parse_cpu_spec(data)
