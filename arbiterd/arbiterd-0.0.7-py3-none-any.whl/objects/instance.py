# -*- coding: utf-8 -*-
# Copyright 2021 - 2021, Sean Mooney and the arbiterd contributors
# SPDX-License-Identifier: Apache-2.0
import collections
import typing as ty
from dataclasses import dataclass

from arbiterd.common import cpu
from arbiterd.common import libvirt
from defusedxml import ElementTree as ET

# TODO: extract this so it can be shared
CPUAffinity = collections.namedtuple(
    'CPUAffinity', ['vcpu', 'vcpupin', 'emulatorpin', 'iothreadpin'])


@dataclass
class Instance:
    """Class to model a nova instance"""

    name: ty.Optional[str] = None
    uuid: ty.Optional[str] = None  # TODO: define a uuid type for this.
    # libvirt_domain_name: ty.Optional[str] = None
    _domain: 'libvirt.virDomain' = None
    # TODO: expose this as a property and store the parsed xml
    _xml_str: ty.Optional[str] = None
    _xml: ty.Optional = None

    def __eq__(self, other: 'Instance') -> bool:
        if not isinstance(other, Instance):
            return False
        return self.uuid == other.uuid

    @property
    def xml_str(self) -> str:
        if self._xml_str is None:
            self._xml_str = self.domain.XMLDesc(0)
        return self._xml_str

    @property
    def xml(self) -> ET:
        if self._xml is None:
            self._xml = ET.fromstring(self.domain.XMLDesc(0))
        return self._xml

    @property
    def domain(self) -> 'libvirt.virDomain':
        if self._domain is None:
            if self.uuid:
                self._domain = libvirt.libvirt_obj.get_domain_by_uuid(
                    self.uuid)
                self.name = self._domain.name()
            elif self.name:
                self._domain = libvirt.libvirt_obj.get_domain_by_name(
                    self.name)
                self.uuid = self._domain.UUIDString()
            else:
                raise ValueError(
                    f'domain lookup failed, name or uuid must be set: {self}')
        return self._domain

    @property
    def is_nova_instance(self) -> bool:
        return 'nova:instance' in self.xml_str

    @classmethod
    def from_domain(cls, domain) -> 'Instance':
        return Instance(
            name=domain.name(), uuid=domain.UUIDString(), _domain=domain)

    @property
    def cpu_affinities(self) -> ty.List[int]:
        # used in openstack if you have vcpu_pin_set defined
        vcpu = self.xml.find('.//vcpu[@cpuset]')
        # used to pin or soft pin the instnece cpus
        vcpu_pin = self.xml.findall('.//vcpupin[@cpuset]')
        # used to pin the emulator threads
        emulator_pin = self.xml.find('.//emulatorpin[@cpuset]')
        # not used by openstack but used to allcoate io threads.
        io_pin = self.xml.findall('.//iothreadpin[@cpuset]')

        vcpu_set = cpu.parse_cpu_spec(vcpu.get('cpuset')) if vcpu else set()
        emulator_set = cpu.parse_cpu_spec(
            emulator_pin['cpuset']) if emulator_pin else set()
        return CPUAffinity(
            vcpu_set,
            {core for pinning in vcpu_pin for core in cpu.parse_cpu_spec(
                pinning.get('cpuset'))},
            emulator_set,
            {core for pinning in io_pin for core in cpu.parse_cpu_spec(
                pinning.get('cpuset'))}
        )
