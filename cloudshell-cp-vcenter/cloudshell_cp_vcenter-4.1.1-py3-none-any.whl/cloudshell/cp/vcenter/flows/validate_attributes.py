from logging import Logger

import jsonpickle

from cloudshell.cp.core.request_actions.models import (
    ValidateAttributes,
    ValidateAttributesResponse,
)

from cloudshell.cp.vcenter.actions.validation import ValidationActions
from cloudshell.cp.vcenter.constants import (
    VM_FROM_IMAGE_DEPLOYMENT_PATH,
    VM_FROM_LINKED_CLONE_DEPLOYMENT_PATH,
    VM_FROM_TEMPLATE_DEPLOYMENT_PATH,
    VM_FROM_VM_DEPLOYMENT_PATH,
)
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.models.base_deployment_app import (
    VCenterDeploymentAppAttributeNames,
    VCenterVMFromCloneDeployAppAttributeNames,
    VCenterVMFromImageDeploymentAppAttributeNames,
    VCenterVMFromTemplateDeploymentAppAttributeNames,
    VCenterVMFromVMDeploymentAppAttributeNames,
)
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


def validate_attributes(
    resource_conf: VCenterResourceConfig, request: str, logger: Logger
) -> str:
    deployment_path_to_fn = {
        VM_FROM_VM_DEPLOYMENT_PATH: _validate_app_from_vm,
        VM_FROM_TEMPLATE_DEPLOYMENT_PATH: _validate_app_from_template,
        VM_FROM_LINKED_CLONE_DEPLOYMENT_PATH: _validate_app_from_clone,
        VM_FROM_IMAGE_DEPLOYMENT_PATH: _validate_app_from_image,
    }
    si = SiHandler.from_config(resource_conf, logger)
    action = ValidateAttributes.from_request(request)
    validator = ValidationActions(si, resource_conf, logger)
    _validate_common(action, validator)

    fn = deployment_path_to_fn[action.deployment_path]
    fn(action, validator)

    result = ValidateAttributesResponse(action.actionId)
    return jsonpickle.encode(result, unpicklable=False)


def _validate_common(action: ValidateAttributes, validator: ValidationActions):
    a_names = VCenterDeploymentAppAttributeNames
    vm_location = action.get(a_names.vm_location)
    vm_cluster = action.get(a_names.vm_cluster)
    vm_storage = action.get(a_names.vm_storage)

    validator.validate_base_app_attrs(
        vm_cluster=vm_cluster, vm_storage=vm_storage, vm_location=vm_location
    )
    validator.validate_base_app_dc_objects(
        vm_cluster=vm_cluster, vm_storage=vm_storage, vm_location=vm_location
    )


def _validate_app_from_vm(action: ValidateAttributes, validator: ValidationActions):
    a_names = VCenterVMFromVMDeploymentAppAttributeNames
    validator.validate_app_from_vm(action.get(a_names.vcenter_vm))


def _validate_app_from_template(
    action: ValidateAttributes, validator: ValidationActions
):
    a_names = VCenterVMFromTemplateDeploymentAppAttributeNames
    validator.validate_app_from_template(action.get(a_names.vcenter_template))


def _validate_app_from_clone(action: ValidateAttributes, validator: ValidationActions):
    a_names = VCenterVMFromCloneDeployAppAttributeNames
    validator.validate_app_from_clone(
        action.get(a_names.vcenter_vm), action.get(a_names.vcenter_vm_snapshot)
    )


def _validate_app_from_image(action: ValidateAttributes, validator: ValidationActions):
    a_names = VCenterVMFromImageDeploymentAppAttributeNames
    validator.validate_app_from_image(action.get(a_names.vcenter_image))
