from __future__ import annotations

import json
from datetime import datetime
from logging import Logger

import attr

from cloudshell.api.cloudshell_api import CloudShellAPISession
from cloudshell.shell.core.orchestration_save_restore import OrchestrationSaveRestore

from cloudshell.cp.vcenter.exceptions import BaseVCenterException, InvalidCommandParam
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


class InvalidOrchestrationType(BaseVCenterException):
    def __init__(self, type_: str):
        msg = f"Invalid orchestration type '{type_}', expect vcenter_snapshot"
        super().__init__(msg)


def _validate_dump_memory_param(dump_memory: str):
    expected_values = ("Yes", "No")
    if dump_memory not in ("Yes", "No"):
        raise InvalidCommandParam(
            param_name="save_memory",
            param_value=dump_memory,
            expected_values=expected_values,
        )


@attr.s(auto_attribs=True)
class SnapshotFlow:
    _resource_conf: VCenterResourceConfig
    _deployed_app: BaseVCenterDeployedApp
    _logger: Logger

    def __attrs_post_init__(self):
        self._si = SiHandler.from_config(self._resource_conf, self._logger)

    def _get_vm(self) -> VmHandler:
        dc = DcHandler.get_dc(self._resource_conf.default_datacenter, self._si)
        return dc.get_vm_by_uuid(self._deployed_app.vmdetails.uid)

    def get_snapshot_paths(self) -> str:
        vm = self._get_vm()
        paths = vm.get_snapshot_paths(self._logger)
        return json.dumps(paths)

    def save_snapshot(self, snapshot_name: str, dump_memory: str) -> str:
        _validate_dump_memory_param(dump_memory)
        vm = self._get_vm()
        dump_memory = dump_memory == "Yes"
        snapshot_path = vm.create_snapshot(snapshot_name, dump_memory, self._logger)
        return snapshot_path

    def restore_from_snapshot(
        self,
        cs_api: CloudShellAPISession,
        snapshot_path: str,
    ):
        vm = self._get_vm()
        vm.restore_from_snapshot(snapshot_path, self._logger)
        cs_api.SetResourceLiveStatus(self._deployed_app.name, "Offline", "Powered Off")

    def orchestration_save(self) -> str:
        snapshot_name = datetime.now().strftime("%y_%m_%d %H_%M_%S_%f")
        snapshot_path = self.save_snapshot(snapshot_name, dump_memory="No")
        type_ = "vcenter_snapshot"
        path = f"{type_}:{snapshot_path}"

        result = OrchestrationSaveRestore(
            self._logger, self._resource_conf.name
        ).prepare_orchestration_save_result(path)
        return result

    def orchestration_restore(self, artifacts_info: str, cs_api: CloudShellAPISession):
        result = OrchestrationSaveRestore(
            self._logger, self._resource_conf.name
        ).parse_orchestration_save_result(artifacts_info)
        type_, snapshot_path = result["path"].split(":", 1)
        if not type_ == "vcenter_snapshot":
            raise InvalidOrchestrationType(type_)

        self.restore_from_snapshot(cs_api, snapshot_path)

    def remove_snapshot(self, snapshot_name: str) -> None:
        vm = self._get_vm()
        vm.remove_snapshot(snapshot_name, self._logger)
