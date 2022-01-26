from __future__ import annotations

from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.cluster_handler import (
    ClusterHandler,
    ClusterHostNotFound,
    HostHandler,
)
from cloudshell.cp.vcenter.handlers.datastore_handler import (
    DatastoreHandler,
    DatastoreNotFound,
)
from cloudshell.cp.vcenter.handlers.folder_handler import FolderHandler
from cloudshell.cp.vcenter.handlers.managed_entity_handler import ManagedEntityHandler
from cloudshell.cp.vcenter.handlers.network_handler import (
    DVPortGroupHandler,
    NetworkHandler,
    NetworkNotFound,
    get_network_handler,
)
from cloudshell.cp.vcenter.handlers.resource_pool import (
    ResourcePoolHandler,
    ResourcePoolNotFound,
)
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.handlers.switch_handler import (
    DvSwitchHandler,
    DvSwitchNotFound,
)
from cloudshell.cp.vcenter.handlers.vcenter_path import VcenterPath
from cloudshell.cp.vcenter.handlers.vm_handler import VmHandler, VmNotFound


class DcNotFound(BaseVCenterException):
    def __init__(self, dc_name: str):
        self.dc_name = dc_name
        super().__init__(f"Datacenter with name '{dc_name}' not found.")


class DcHandler(ManagedEntityHandler):
    @classmethod
    def get_dc(cls, name: str, si: SiHandler) -> DcHandler:
        for vc_dc in si.find_items(vim.Datacenter):
            if vc_dc.name == name:
                return DcHandler(vc_dc, si)
        raise DcNotFound(name)

    def __str__(self):
        return f"Datacenter '{self.name}'"

    @property
    def networks(self) -> list[NetworkHandler | DVPortGroupHandler]:
        return [get_network_handler(net, self._si) for net in self._entity.network]

    @property
    def datastores(self) -> list[DatastoreHandler]:
        return [DatastoreHandler(store, self._si) for store in self._entity.datastore]

    def get_network(self, name: str) -> NetworkHandler | DVPortGroupHandler:
        for network in self.networks:
            if network.name == name:
                return network
        raise NetworkNotFound(self, name)

    def get_vm_by_uuid(self, uuid: str) -> VmHandler:
        vm = self._si.find_by_uuid(self._entity, uuid, vm_search=True)
        if not vm:
            raise VmNotFound(self, uuid=uuid)
        return VmHandler(vm, self._si)

    def get_vm_by_path(self, path: str | VcenterPath) -> VmHandler:
        if not isinstance(path, VcenterPath):
            path = VcenterPath(path)
        vm_name = path.pop()
        folder = self.get_vm_folder(path)
        vc_vm = folder.find_child(vm_name)
        if not vc_vm:
            raise VmNotFound(self, name=vm_name)
        return VmHandler(vc_vm, self._si)

    def get_vm_folder(self, path: str | VcenterPath) -> FolderHandler:
        vm_folder = FolderHandler(self._entity.vmFolder, self._si)
        if path:
            vm_folder = vm_folder.get_folder(path)
        return vm_folder

    def get_or_create_vm_folder(self, path: str | VcenterPath) -> FolderHandler:
        vm_folder = FolderHandler(self._entity.vmFolder, self._si)
        if path:
            vm_folder = vm_folder.get_or_create_folder(path)
        return vm_folder

    def get_cluster(self, name: str) -> ClusterHandler | HostHandler:
        for vc_cluster in self._si.find_items(
            [vim.ComputeResource, vim.ClusterComputeResource],
            container=self._entity.hostFolder,
        ):
            if vc_cluster.name == name:
                return ClusterHandler(vc_cluster, self._si)
        for vc_host in self._si.find_items(
            [vim.HostSystem], container=self._entity.hostFolder
        ):
            if vc_host.name == name:
                return HostHandler(vc_host, self._si)

        raise ClusterHostNotFound(self, name)

    def get_datastore(self, path: str | VcenterPath) -> DatastoreHandler:
        if not isinstance(path, VcenterPath):
            path = VcenterPath(path)

        datastore_name = path.pop()
        if path:
            entity = self.get_cluster(str(path))
        else:
            entity = self

        for datastore in entity.datastores:
            if datastore.name == datastore_name:
                return datastore
        raise DatastoreNotFound(entity, datastore_name)

    def get_dv_switch(self, path: VcenterPath | str) -> DvSwitchHandler:
        if not isinstance(path, VcenterPath):
            path = VcenterPath(path)
        dvs_name = path.pop()
        if path:
            entity = FolderHandler.get_folder_from_parent(self._entity, path, self._si)
        else:
            entity = FolderHandler(self._entity.networkFolder, self._si)

        for vc_dvs in entity.find_items(vim.dvs.VmwareDistributedVirtualSwitch):
            if vc_dvs.name == dvs_name:
                return DvSwitchHandler(vc_dvs, self._si)
        raise DvSwitchNotFound(self, dvs_name)

    def get_resource_pool(self, name: str) -> ResourcePoolHandler:
        for r_pool in self._si.find_items(
            vim.ResourcePool, container=self._entity.hostFolder
        ):
            if r_pool.name == name:
                return ResourcePoolHandler(r_pool, self._si)
        raise ResourcePoolNotFound(self, name)
