# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import importlib
import typing as ty

libvirt = None

LIBVIRT_URI = 'qemu:///system'

libvirt_obj = None


def init_libvirt():
    global libvirt_obj
    if libvirt_obj is None:
        libvirt_obj = Libvirt()


class Libvirt(object):

    def __init__(self, uri: str = None) -> None:
        super().__init__()
        self.import_libvirt()
        self.uri = uri or LIBVIRT_URI
        self.conn = self.get_connection()

    def import_libvirt(self):
        global libvirt
        if libvirt is None:
            libvirt = importlib.import_module('libvirt')

    def get_connection(self) -> ty.Optional:
        try:
            return libvirt.openReadOnly('qemu:///system')
        except libvirt.libvirtError:
            return None

    def list_domains(self) -> ty.Iterable:
        return self.conn.listAllDomains(0)

    def get_domain_by_name(self, name: str) -> 'libvirt.virDomain':
        return self.conn.lookupByName(name)

    def get_domain_by_uuid(self, uuid: str) -> 'libvirt.virDomain':
        return self.conn.lookupByUUIDString(uuid)
