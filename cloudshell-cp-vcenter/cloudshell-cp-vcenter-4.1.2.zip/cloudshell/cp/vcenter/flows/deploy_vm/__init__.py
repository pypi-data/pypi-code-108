from __future__ import annotations

from .base_flow import AbstractVCenterDeployVMFlow
from .from_image import VCenterDeployVMFromImageFlow
from .from_linked_clone import VCenterDeployVMFromLinkedCloneFlow
from .from_template import VCenterDeployVMFromTemplateFlow
from .from_vm import VCenterDeployVMFromVMFlow

from cloudshell.cp.vcenter.models import deploy_app

DEPLOY_APP_TO_FLOW = (
    (deploy_app.VMFromVMDeployApp, VCenterDeployVMFromVMFlow),
    (deploy_app.VMFromImageDeployApp, VCenterDeployVMFromImageFlow),
    (deploy_app.VMFromTemplateDeployApp, VCenterDeployVMFromTemplateFlow),
    (deploy_app.VMFromLinkedCloneDeployApp, VCenterDeployVMFromLinkedCloneFlow),
)


def get_deploy_flow(request_action) -> type[AbstractVCenterDeployVMFlow]:
    da = request_action.deploy_app
    for deploy_class, deploy_flow in DEPLOY_APP_TO_FLOW:
        if isinstance(da, deploy_class):
            return deploy_flow
    raise NotImplementedError(f"Not supported deployment type {type(da)}")


__all__ = (
    VCenterDeployVMFromVMFlow,
    VCenterDeployVMFromImageFlow,
    VCenterDeployVMFromTemplateFlow,
    VCenterDeployVMFromLinkedCloneFlow,
    get_deploy_flow,
)
