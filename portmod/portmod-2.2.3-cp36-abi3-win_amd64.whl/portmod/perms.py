# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

"""
Module that provides a function to aid construction of safe
wrapper libraries around unsafe system libraries
"""
from types import SimpleNamespace
from typing import List, Optional


class Permissions(SimpleNamespace):
    def __init__(
        self,
        copy: Optional["Permissions"] = None,
        *,
        rw_paths: List[str] = [],
        ro_paths: List[str] = [],
        global_read: Optional[bool] = None,
        network: Optional[bool] = None,
        tmp: Optional[str] = None,
    ):
        if copy:
            self.rw_paths: List[str] = copy.rw_paths
            self.ro_paths: List[str] = copy.ro_paths
            self.global_read: Optional[bool] = copy.global_read
            self.network: Optional[bool] = copy.network
            self.tmp: Optional[str] = copy.tmp
        else:
            self.global_read = False
            self.network = False
            self.rw_paths = []
            self.ro_paths = []
            self.tmp = None

        self.rw_paths.extend(rw_paths)
        self.ro_paths.extend(ro_paths)
        if global_read is not None:
            self.global_read = global_read
        if network is not None:
            self.network = network
        if tmp is not None:
            self.tmp = tmp
