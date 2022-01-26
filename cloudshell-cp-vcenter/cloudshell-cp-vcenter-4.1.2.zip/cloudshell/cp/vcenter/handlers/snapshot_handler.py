from __future__ import annotations

from collections.abc import Generator

import attr
from pyVmomi import vim

from cloudshell.cp.vcenter.exceptions import BaseVCenterException
from cloudshell.cp.vcenter.handlers.vcenter_path import VcenterPath


class SnapshotNotFoundInSnapshotTree(BaseVCenterException):
    def __init__(self):
        super().__init__("Snapshot not found in snapshot tree")


def _yield_snapshot_handlers(
    snapshot_list, path: VcenterPath | None = None
) -> Generator[SnapshotHandler, None, None]:
    if not path:
        path = VcenterPath()

    for snapshot_tree in snapshot_list:
        new_path = path + snapshot_tree.name
        yield SnapshotHandler(snapshot_tree.snapshot, new_path)
        yield from _yield_snapshot_handlers(snapshot_tree.childSnapshotList, new_path)


def _get_snapshot_path(
    snapshot_list, snapshot, path: VcenterPath | None = None
) -> VcenterPath | None:
    if not path:
        path = VcenterPath()

    for snapshot_tree in snapshot_list:
        new_path = path + snapshot_tree.name
        if snapshot_tree.snapshot == snapshot:
            return new_path

        new_path = _get_snapshot_path(
            snapshot_tree.childSnapshotList, snapshot, new_path
        )
        if new_path:
            return new_path
        else:
            continue

    return None


@attr.s(auto_attribs=True)
class SnapshotHandler:
    _snapshot: vim.vm.Snapshot
    _path: VcenterPath | None = None

    @classmethod
    def get_vm_snapshot_by_path(cls, vm, path: VcenterPath) -> SnapshotHandler:
        for snapshot_handler in cls.yield_vm_snapshots(vm):
            if snapshot_handler.path == path:
                return snapshot_handler
        raise SnapshotNotFoundInSnapshotTree

    @classmethod
    def yield_vm_snapshots(cls, vm) -> Generator[SnapshotHandler, None, None]:
        if vm.snapshot:
            yield from _yield_snapshot_handlers(vm.snapshot.rootSnapshotList)

    @property
    def _root_snapshot_list(self):
        return self._snapshot.vm.snapshot.rootSnapshotList

    @property
    def name(self) -> str:
        return self.path.name

    @property
    def path(self) -> VcenterPath:
        if self._path is None:
            path = _get_snapshot_path(self._root_snapshot_list, self._snapshot)
            if not path:
                raise SnapshotNotFoundInSnapshotTree  # it shouldn't happen
            self._path = path
        return self._path

    def revert_to_snapshot_task(self):
        return self._snapshot.RevertToSnapshot_Task()

    def remove_snapshot_task(self):
        return self._snapshot.RemoveSnapshot_Task(removeChildren=True)
