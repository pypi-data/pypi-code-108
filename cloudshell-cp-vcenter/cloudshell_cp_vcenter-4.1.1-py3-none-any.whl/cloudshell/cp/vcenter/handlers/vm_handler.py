from __future__ import annotations

from contextlib import suppress
from datetime import datetime
from enum import Enum
from logging import Logger

from pyVmomi import vim

from cloudshell.cp.vcenter.common.vcenter.event_manager import EventManager
from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.cluster_handler import HostHandler
from cloudshell.cp.vcenter.handlers.config_spec_handler import ConfigSpecHandler
from cloudshell.cp.vcenter.handlers.custom_spec_handler import CustomSpecHandler
from cloudshell.cp.vcenter.handlers.datastore_handler import DatastoreHandler
from cloudshell.cp.vcenter.handlers.folder_handler import FolderHandler
from cloudshell.cp.vcenter.handlers.managed_entity_handler import ManagedEntityHandler
from cloudshell.cp.vcenter.handlers.network_handler import (
    DVPortGroupHandler,
    HostPortGroupNotFound,
    NetworkHandler,
    get_network_handler,
)
from cloudshell.cp.vcenter.handlers.resource_pool import ResourcePoolHandler
from cloudshell.cp.vcenter.handlers.snapshot_handler import (
    SnapshotHandler,
    SnapshotNotFoundInSnapshotTree,
)
from cloudshell.cp.vcenter.handlers.switch_handler import VSwitchHandler
from cloudshell.cp.vcenter.handlers.vcenter_path import VcenterPath
from cloudshell.cp.vcenter.handlers.virtual_device_handler import (
    is_virtual_disk,
    is_vnic,
)
from cloudshell.cp.vcenter.handlers.virtual_disk_handler import VirtualDiskHandler
from cloudshell.cp.vcenter.handlers.vnic_handler import (
    VnicHandler,
    VnicWithMacNotFound,
    VnicWithoutNetwork,
)
from cloudshell.cp.vcenter.utils.task_waiter import VcenterTaskWaiter
from cloudshell.cp.vcenter.utils.units_converter import BASE_10


class VmNotFound(BaseVCenterException):
    def __init__(
        self,
        entity: ManagedEntityHandler,
        uuid: str | None = None,
        name: str | None = None,
    ):
        self.entity = entity
        self.uuid = uuid
        self.name = name

        if not uuid and not name:
            raise ValueError("You should specify uuid or name")
        if uuid:
            msg = f"VM with the uuid {uuid} in the {entity} not found"
        else:
            msg = f"VM with the name {name} in the {entity} not found"
        super().__init__(msg)


class VMWareToolsNotInstalled(BaseVCenterException):
    def __init__(self, vm: VmHandler):
        self.vm = vm
        super().__init__(f"VMWare Tools are not installed or running on VM '{vm.name}'")


class DuplicatedSnapshotName(BaseVCenterException):
    def __init__(self, snapshot_name: str):
        self.snapshot_name = snapshot_name
        super().__init__(f"Snapshot with name '{snapshot_name}' already exists")


class SnapshotNotFoundByPath(BaseVCenterException):
    def __init__(self, snapshot_path: VcenterPath, vm: VmHandler):
        self.snapshot_path = snapshot_path
        self.vm = vm
        super().__init__(f"Snapshot with path '{snapshot_path}' not found for the {vm}")


class PowerState(Enum):
    ON = "poweredOn"
    OFF = "poweredOff"
    SUSPENDED = "suspended"


def _get_dc(entity):
    while not isinstance(entity.parent, vim.Datacenter):
        entity = entity.parent
    return entity.parent


class VmHandler(ManagedEntityHandler):
    _entity: vim.VirtualMachine

    def __str__(self):
        return f"VM '{self.name}'"

    @property
    def uuid(self) -> str:
        return self._entity.config.uuid

    @property
    def networks(self) -> list[NetworkHandler | DVPortGroupHandler]:
        return [get_network_handler(net, self._si) for net in self._entity.network]

    @property
    def gv_port_groups(self) -> list[DVPortGroupHandler]:
        return list(filter(lambda x: isinstance(x, DVPortGroupHandler), self.networks))

    @property
    def vnics(self) -> list[VnicHandler]:
        return list(map(VnicHandler, filter(is_vnic, self._get_devices())))

    @property
    def disks(self) -> list[VirtualDiskHandler]:
        return list(
            map(VirtualDiskHandler, filter(is_virtual_disk, self._get_devices()))
        )

    @property
    def host(self) -> HostHandler:
        return HostHandler(self._entity.runtime.host, self._si)

    @property
    def disk_size(self) -> int:
        return sum(map(lambda d: d.capacity_in_bytes, self.disks))

    @property
    def num_cpu(self) -> int:
        return self._entity.summary.config.numCpu

    @property
    def memory_size(self) -> int:
        return self._entity.summary.config.memorySizeMB * BASE_10 * BASE_10

    @property
    def guest_os(self) -> str:
        return self._entity.summary.config.guestFullName

    @property
    def guest_id(self) -> str | None:
        return self._entity.guest.guestId

    @property
    def current_snapshot(self) -> SnapshotHandler | None:
        if not self._entity.snapshot:
            return None
        return SnapshotHandler(self._entity.snapshot.currentSnapshot)

    @property
    def path(self) -> VcenterPath:
        """Path from DC.vmFolder."""
        dc = _get_dc(self._entity)

        path = VcenterPath(self.name)
        folder = self._entity.parent
        while folder != dc.vmFolder:
            path = VcenterPath(folder.name) + path
            folder = folder.parent
        return path

    @property
    def power_state(self) -> PowerState:
        return PowerState(self._entity.summary.runtime.powerState)

    @property
    def _moId(self) -> str:
        # avoid using this property
        return self._entity._moId

    @property
    def _wsdl_name(self) -> str:
        return self._entity._wsdlName

    def _get_devices(self):
        return self._entity.config.hardware.device

    def create_vnic(self) -> VnicHandler:
        try:
            vnic_type = self.vnics[0].vnic_type
            vnic = VnicHandler.create_new(vnic_type)
        except IndexError:
            vnic = VnicHandler.create_new()
        return vnic

    def get_network_from_vnic(
        self, vnic: VnicHandler
    ) -> NetworkHandler | DVPortGroupHandler:
        try:
            vc_network = vnic.vc_network
            network = NetworkHandler(vc_network, self._si)
        except ValueError:
            for pg in self.gv_port_groups:
                with suppress(ValueError):
                    if pg.key == vnic.port_group_key:
                        network = pg
                        break
            else:
                raise VnicWithoutNetwork

        return network

    def connect_vnic_to_port_group(
        self,
        vnic: VnicHandler,
        port_group: DVPortGroupHandler,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        nic_spec = vnic.create_spec_for_connection_port_group(port_group)
        config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
        task = self._entity.ReconfigVM_Task(config_spec)
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def connect_vnic_to_network(
        self,
        vnic: VnicHandler,
        network: NetworkHandler,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        nic_spec = vnic.create_spec_for_connection_network(network)
        config_spec = vim.vm.ConfigSpec(deviceChange=[nic_spec])
        task = self._entity.ReconfigVM_Task(config_spec)
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def get_vnic_by_mac(self, mac_address: str, logger: Logger) -> VnicHandler:
        logger.info(f"Searching for vNIC of the {self} with mac {mac_address}")
        for vnic in self.vnics:
            if vnic.mac_address.lower() == mac_address.lower():
                return vnic
        raise VnicWithMacNotFound(mac_address, self)

    def get_network_vlan_id(self, network: NetworkHandler | DVPortGroupHandler) -> int:
        if isinstance(network, DVPortGroupHandler):
            pg = network
        else:
            for pg in self.host.port_groups:
                if pg.name == network.name:
                    break
            else:
                raise HostPortGroupNotFound(self, network.name)
        return pg.vlan_id

    def get_v_switch(self, name: str) -> VSwitchHandler:
        return self.host.get_v_switch(name)

    def validate_guest_tools_installed(self):
        if self._entity.guest.toolsStatus != vim.vm.GuestInfo.ToolsStatus.toolsOk:
            raise VMWareToolsNotInstalled(self)

    def power_on(self, logger: Logger, task_waiter: VcenterTaskWaiter | None = None):
        if self.power_state is PowerState.ON:
            logger.info("VM already powered on")
        else:
            logger.info(f"Powering on the {self}")
            task = self._entity.PowerOn()
            task_waiter = task_waiter or VcenterTaskWaiter(logger)
            task_waiter.wait_for_task(task)

    def power_off(
        self, soft: bool, logger: Logger, task_waiter: VcenterTaskWaiter | None = None
    ):
        if self.power_state is PowerState.OFF:
            logger.info("VM already powered off")
        else:
            logger.info(f"Powering off the {self}")
            if soft:
                self.validate_guest_tools_installed()
                self._entity.ShutdownGuest()  # do not return task
            else:
                task = self._entity.PowerOff()
                task_waiter = task_waiter or VcenterTaskWaiter(logger)
                task_waiter.wait_for_task(task)

    def add_customization_spec(
        self,
        spec: CustomSpecHandler,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ):
        task = self._entity.CustomizeVM_Task(spec.spec.spec)
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def wait_for_customization_ready(self, begin_time: datetime, logger: Logger):
        logger.info(f"Checking for the {self} OS customization events")
        em = EventManager()
        em.wait_for_vm_os_customization_start_event(
            self._si, self._entity, logger=logger, event_start_time=begin_time
        )

        logger.info(f"Waiting for the {self} OS customization event to be proceeded")
        em.wait_for_vm_os_customization_end_event(
            self._si, self._entity, logger=logger, event_start_time=begin_time
        )

    def reconfigure_vm(
        self,
        config_spec: ConfigSpecHandler,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ):
        spec = config_spec.get_spec_for_vm(self._entity)
        task = self._entity.ReconfigVM_Task(spec)
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def create_snapshot(
        self,
        snapshot_name: str,
        dump_memory: bool,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> str:
        if self.current_snapshot:
            new_snapshot_path = self.current_snapshot.path + snapshot_name
            try:
                SnapshotHandler.get_vm_snapshot_by_path(self._entity, new_snapshot_path)
            except SnapshotNotFoundInSnapshotTree:
                pass
            else:
                raise DuplicatedSnapshotName(snapshot_name)
        else:
            new_snapshot_path = VcenterPath(snapshot_name)

        logger.info(f"Creating a new snapshot for {self} with path {new_snapshot_path}")
        quiesce = True
        task = self._entity.CreateSnapshot(
            snapshot_name, "Created by CloudShell vCenterShell", dump_memory, quiesce
        )
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

        return str(new_snapshot_path)

    def restore_from_snapshot(
        self,
        snapshot_path: str | VcenterPath,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ):
        logger.info(f"Restore {self} from the snapshot '{snapshot_path}'")
        snapshot = self.get_snapshot_by_path(snapshot_path)
        task = snapshot.revert_to_snapshot_task()
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def remove_snapshot(
        self,
        snapshot_path: str | VcenterPath,
        logger: Logger,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> None:
        logger.info(f"Removing snapshot '{snapshot_path}' from the {self}")
        snapshot = self.get_snapshot_by_path(snapshot_path)
        task = snapshot.remove_snapshot_task()
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def get_snapshot_by_path(self, snapshot_path: str | VcenterPath) -> SnapshotHandler:
        if not isinstance(snapshot_path, VcenterPath):
            snapshot_path = VcenterPath(snapshot_path)

        try:
            snapshot = SnapshotHandler.get_vm_snapshot_by_path(
                self._entity, snapshot_path
            )
        except SnapshotNotFoundInSnapshotTree:
            raise SnapshotNotFoundByPath(snapshot_path, self)
        return snapshot

    def get_snapshot_paths(self, logger: Logger) -> list[str]:
        logger.info(f"Getting snapshots for the {self}")
        return [str(s.path) for s in SnapshotHandler.yield_vm_snapshots(self._entity)]

    def delete(self, logger: Logger, task_waiter: VcenterTaskWaiter | None = None):
        logger.info(f"Deleting the {self}")
        task = self._entity.Destroy_Task()
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        task_waiter.wait_for_task(task)

    def clone_vm(
        self,
        vm_name: str,
        vm_storage: DatastoreHandler,
        vm_folder: FolderHandler,
        logger: Logger,
        vm_resource_pool: ResourcePoolHandler | None = None,
        snapshot: SnapshotHandler | None = None,
        config_spec: ConfigSpecHandler | None = None,
        task_waiter: VcenterTaskWaiter | None = None,
    ) -> VmHandler:
        logger.info(f"Cloning the {self} to the new VM '{vm_name}'")
        clone_spec = vim.vm.CloneSpec(powerOn=False)
        placement = vim.vm.RelocateSpec()
        placement.datastore = vm_storage._entity
        if vm_resource_pool:
            placement.pool = vm_resource_pool._entity
        if snapshot:
            clone_spec.snapshot = snapshot._snapshot
            clone_spec.template = False
            placement.diskMoveType = "createNewChildDiskBacking"
        clone_spec.location = placement

        task = self._entity.Clone(
            folder=vm_folder._entity, name=vm_name, spec=clone_spec
        )
        task_waiter = task_waiter or VcenterTaskWaiter(logger)
        new_vc_vm = task_waiter.wait_for_task(task)
        new_vm = VmHandler(new_vc_vm, self._si)

        if config_spec:
            new_vm.reconfigure_vm(config_spec, logger, task_waiter)
        return new_vm
