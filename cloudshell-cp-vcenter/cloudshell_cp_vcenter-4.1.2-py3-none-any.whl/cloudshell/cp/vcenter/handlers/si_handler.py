from __future__ import annotations

from logging import Logger
from typing import Any

import attr
from pyVmomi import vim

from cloudshell.cp.vcenter.handlers.custom_spec_handler import (
    CustomSpecHandler,
    get_custom_spec_from_vim_spec,
)
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig
from cloudshell.cp.vcenter.utils.client_helpers import get_si


@attr.s(auto_attribs=True, slots=True, frozen=True)
class SiHandler:
    _si: vim.ServiceInstance

    @classmethod
    def from_config(cls, conf: VCenterResourceConfig, logger: Logger) -> SiHandler:
        return cls.connect(conf.address, conf.user, conf.password, logger)

    @classmethod
    def connect(cls, host: str, user: str, password: str, logger: Logger) -> SiHandler:
        logger.info("Initializing vCenter API client SI")
        si = get_si(host, user, password)
        return cls(si)

    @property
    def root_folder(self):
        return self._si.content.rootFolder

    @property
    def vc_version(self) -> str:
        return self._si.content.about.version

    @property
    def instance_uuid(self) -> str:
        return self._si.content.about.instanceUuid

    @property
    def vcenter_host(self) -> str:
        # noinspection PyUnresolvedReferences
        for item in self._si.content.setting.setting:
            if item.key == "VirtualCenter.FQDN":
                return item.value
        raise Exception("Unable to find vCenter host")

    def acquire_session_ticket(self) -> str:
        return self._si.content.sessionManager.AcquireCloneTicket()

    def find_items(self, vim_type, recursive=False, container=None) -> Any:
        container = container or self.root_folder
        if not isinstance(vim_type, list):
            vim_type = [vim_type]
        view = self._si.content.viewManager.CreateContainerView(
            container, vim_type, recursive
        )
        # noinspection PyUnresolvedReferences
        items = view.view
        # noinspection PyUnresolvedReferences
        view.DestroyView()
        return items

    def find_by_uuid(self, dc, uuid: str, vm_search) -> Any:
        return self._si.content.searchIndex.FindByUuid(dc, uuid, vmSearch=vm_search)

    def find_child(self, parent, name: str) -> Any:
        return self._si.content.searchIndex.FindChild(parent, name)

    def get_customization_spec(self, name: str) -> CustomSpecHandler | None:
        try:
            spec = self._si.content.customizationSpecManager.GetCustomizationSpec(name)
        except vim.fault.NotFound:
            return None

        custom_spec_handler = get_custom_spec_from_vim_spec(spec)
        return custom_spec_handler

    def duplicate_customization_spec(self, original_name: str, new_name: str):
        self._si.content.customizationSpecManager.DuplicateCustomizationSpec(
            name=original_name, newName=new_name
        )

    def overwrite_customization_spec(self, spec: CustomSpecHandler):
        self._si.content.customizationSpecManager.OverwriteCustomizationSpec(spec.spec)

    def create_customization_spec(self, spec: CustomSpecHandler):
        self._si.content.customizationSpecManager.CreateCustomizationSpec(spec.spec)

    def delete_customization_spec(self, name: str):
        try:
            self._si.content.customizationSpecManager.DeleteCustomizationSpec(name=name)
        except vim.fault.NotFound:
            pass

    def query_event(self, filter_spec: vim.event.EventFilterSpec):
        # noinspection PyUnresolvedReferences
        return self._si.content.eventManager.QueryEvent(filter_spec)
