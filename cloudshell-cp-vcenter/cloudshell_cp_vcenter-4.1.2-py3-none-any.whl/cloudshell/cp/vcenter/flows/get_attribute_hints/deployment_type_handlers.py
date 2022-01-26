from __future__ import annotations

from abc import ABC, abstractmethod

from cloudshell.cp.vcenter import constants
from cloudshell.cp.vcenter.flows.get_attribute_hints import attribute_hints
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.models.DeployDataHolder import DeployDataHolder


class AbstractHintsHandler(ABC):
    @property
    @staticmethod
    @abstractmethod
    def DEPLOYMENT_PATH() -> str:
        pass

    @property
    @staticmethod
    @abstractmethod
    def ATTRIBUTES() -> tuple[type[attribute_hints.AbstractAttributeHint]]:
        pass

    def __init__(self, request: DeployDataHolder, dc: DcHandler):
        self._dc = dc
        self._request = request

    def prepare_hints(self) -> list[dict]:
        hints = []
        requested_attribute = next(
            (
                attr
                for attr in self.ATTRIBUTES
                if self._request.AttributeName.endswith(f".{attr.ATTR_NAME}")
            ),
            None,
        )
        if requested_attribute:
            return [requested_attribute(self._request, self._dc).prepare_hints()]
        return hints


class VMFromVMHintsHandler(AbstractHintsHandler):
    DEPLOYMENT_PATH = constants.VM_FROM_VM_DEPLOYMENT_PATH
    ATTRIBUTES = (
        attribute_hints.VcenterVMAttributeHint,
        attribute_hints.VMClusterAttributeHint,
        attribute_hints.VMStorageAttributeHint,
    )


class VMFromTemplateHintsHandler(AbstractHintsHandler):
    DEPLOYMENT_PATH = constants.VM_FROM_TEMPLATE_DEPLOYMENT_PATH
    ATTRIBUTES = (
        attribute_hints.VcenterTemplateAttributeHint,
        attribute_hints.VMClusterAttributeHint,
        attribute_hints.VMStorageAttributeHint,
    )


class VMFromLinkedCloneHintsHandler(AbstractHintsHandler):
    DEPLOYMENT_PATH = constants.VM_FROM_LINKED_CLONE_DEPLOYMENT_PATH
    ATTRIBUTES = (
        attribute_hints.VcenterVMAttributeHint,
        attribute_hints.VcenterVMSnapshotAttributeHint,
        attribute_hints.VMClusterAttributeHint,
        attribute_hints.VMStorageAttributeHint,
    )


class VMFromImageHintsHandler(AbstractHintsHandler):
    DEPLOYMENT_PATH = constants.VM_FROM_IMAGE_DEPLOYMENT_PATH
    ATTRIBUTES = (
        attribute_hints.VMClusterAttributeHint,
        attribute_hints.VMStorageAttributeHint,
    )


def get_handler(request: DeployDataHolder, dc: DcHandler) -> AbstractHintsHandler:
    handlers = (
        VMFromVMHintsHandler,
        VMFromTemplateHintsHandler,
        VMFromLinkedCloneHintsHandler,
        VMFromImageHintsHandler,
    )

    for handler in handlers:
        if request.DeploymentPath == handler.DEPLOYMENT_PATH:
            return handler(request, dc)

    raise Exception(
        f"Unable to process deployment path '{request.DeploymentPath}'. "
        f"It should be one of: {[handler.DEPLOYMENT_PATH for handler in handlers]}"
    )
