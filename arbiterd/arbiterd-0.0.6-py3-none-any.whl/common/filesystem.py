# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import functools
import logging
import os
import typing as ty

SYS = '/sys'
SYSFS = 'sysfs'
MTAB = '/etc/mtab'
ETC = '/etc'

LOG = logging.getLogger(__name__)


@functools.lru_cache
def get_sys_fs_mount() -> str:
    """find the default sysfs mount point"""
    try:
        if os.path.exists(MTAB):
            with open(MTAB, mode='r') as mtab:
                mounts: ty.Set[str] = set()
                for line in mtab.readlines():
                    segments = line.split()
                    if segments[0] == SYSFS:
                        mounts.add(segments[1])
                    else:
                        return SYS
                return sorted(mounts, key=lambda path: len(path))[0]
    except OSError:
        # TODO: add logging
        pass
    return SYS


@functools.lru_cache
def get_etc_fs_mount() -> str:
    return ETC


def read_sys(path: str, default: str = None) -> ty.Optional[str]:
    sys = get_sys_fs_mount()
    try:
        with open(os.path.join(sys, path), mode='r') as data:
            return data.read()
    except (OSError, ValueError) as e:
        LOG.debug(e)
    return default


def readlines_sys(path: str) -> ty.List[str]:
    sys = get_sys_fs_mount()
    try:
        with open(os.path.join(sys, path), mode='r') as data:
            return data.readlines()
    except (OSError, ValueError) as e:
        LOG.debug(e)
    return []


def write_sys(path: str, data: str = None) -> ty.Optional[str]:
    sys = get_sys_fs_mount()
    try:
        with open(os.path.join(sys, path), mode='w') as fd:
            fd.write(data)
    except (OSError, ValueError) as e:
        LOG.debug(e)
