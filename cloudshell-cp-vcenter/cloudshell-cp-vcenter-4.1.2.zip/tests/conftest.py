import json
from unittest.mock import MagicMock, Mock

import pytest

from cloudshell.cp.core.cancellation_manager import CancellationContextManager
from cloudshell.cp.core.request_actions import GetVMDetailsRequestActions
from cloudshell.shell.core.driver_context import (
    AppContext,
    ConnectivityContext,
    ReservationContextDetails,
    ResourceCommandContext,
    ResourceContextDetails,
)

from cloudshell.cp.vcenter.constants import SHELL_NAME, STATIC_SHELL_NAME
from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.models.deployed_app import StaticVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig


@pytest.fixture()
def logger():
    return MagicMock()


@pytest.fixture()
def connectivity_context() -> ConnectivityContext:
    return ConnectivityContext(
        server_address="localhost",
        cloudshell_api_port="5000",
        quali_api_port="5001",
        admin_auth_token="token",
        cloudshell_version="2021.2",
        cloudshell_api_scheme="https",
    )


@pytest.fixture()
def resource_context_details() -> ResourceContextDetails:
    return ResourceContextDetails(
        id="id",
        name="name",
        fullname="fullname",
        type="type",
        address="192.168.1.2",
        model="model",
        family="family",
        description="",
        attributes={},
        app_context=AppContext("", ""),
        networks_info=None,
        shell_standard="",
        shell_standard_version="",
    )


@pytest.fixture()
def reservation_context_details() -> ReservationContextDetails:
    return ReservationContextDetails(
        environment_name="env name",
        environment_path="env path",
        domain="domain",
        description="",
        owner_user="user",
        owner_email="email",
        reservation_id="rid",
        saved_sandbox_name="name",
        saved_sandbox_id="id",
        running_user="user",
    )


@pytest.fixture()
def resource_command_context(
    connectivity_context, resource_context_details, reservation_context_details
) -> ResourceCommandContext:
    return ResourceCommandContext(
        connectivity_context, resource_context_details, reservation_context_details, []
    )


@pytest.fixture()
def cs_api():
    return MagicMock(DecryptPassword=lambda pswd: MagicMock(Value=pswd))


@pytest.fixture()
def cancellation_manager() -> CancellationContextManager:
    return CancellationContextManager(MagicMock(is_cancelled=False))


@pytest.fixture()
def resource_conf(resource_command_context, cs_api) -> VCenterResourceConfig:
    user = "user name"
    password = "password"
    default_datacenter = "default datacenter"
    default_dv_switch = "default dvSwitch"
    holding_network = "holding network"
    vm_cluster = "vm cluster"
    vm_resource_pool = "vm resource pool"
    vm_storage = "vm storage"
    saved_sandbox_storage = "saved sandbox storage"
    behavior_during_save = "behavior during save"
    vm_location = "vm location"
    shutdown_method = "soft"
    ovf_tool_path = "ovf tool path"
    reserved_networks = "10.1.0.0/24;10.1.1.0/24"
    execution_server_selector = "Execution Server Selector"
    promiscuous_mode = "true"

    a_name = VCenterResourceConfig.ATTR_NAMES
    get_full_a_name = lambda n: f"{SHELL_NAME}.{n}"  # noqa: E731
    resource_command_context.resource.attributes.update(
        {
            get_full_a_name(a_name.user): user,
            get_full_a_name(a_name.password): password,
            get_full_a_name(a_name.default_datacenter): default_datacenter,
            get_full_a_name(a_name.default_dv_switch): default_dv_switch,
            get_full_a_name(a_name.holding_network): holding_network,
            get_full_a_name(a_name.vm_cluster): vm_cluster,
            get_full_a_name(a_name.vm_resource_pool): vm_resource_pool,
            get_full_a_name(a_name.vm_storage): vm_storage,
            get_full_a_name(a_name.saved_sandbox_storage): saved_sandbox_storage,
            get_full_a_name(a_name.behavior_during_save): behavior_during_save,
            get_full_a_name(a_name.vm_location): vm_location,
            get_full_a_name(a_name.shutdown_method): shutdown_method,
            get_full_a_name(a_name.ovf_tool_path): ovf_tool_path,
            get_full_a_name(a_name.reserved_networks): reserved_networks,
            get_full_a_name(
                a_name.execution_server_selector
            ): execution_server_selector,
            get_full_a_name(a_name.promiscuous_mode): promiscuous_mode,
        }
    )
    conf = VCenterResourceConfig.from_context(
        context=resource_command_context,
        shell_name=SHELL_NAME,
        api=cs_api,
        supported_os=None,
    )

    return conf


@pytest.fixture()
def si() -> SiHandler:
    _si = Mock()
    return SiHandler(_si)


@pytest.fixture()
def dc(si, resource_conf) -> DcHandler:
    return DcHandler.get_dc(resource_conf.default_datacenter, si)


@pytest.fixture()
def static_deployed_app(cs_api) -> StaticVCenterDeployedApp:
    vm_name = "vm folder/vm-name"
    vcenter_name = "vcenter"
    vm_uuid = "uuid"
    requests = {
        "items": [
            {
                "appRequestJson": {
                    "name": "win-static",
                    "description": None,
                    "logicalResource": {
                        "family": None,
                        "model": None,
                        "driver": None,
                        "description": None,
                        "attributes": [],
                    },
                    "deploymentService": {
                        "cloudProviderName": None,
                        "name": "win-static",
                        "model": STATIC_SHELL_NAME,
                        "driver": STATIC_SHELL_NAME,
                        "attributes": [
                            {
                                "name": f"{STATIC_SHELL_NAME}.VM Name",
                                "value": vm_name,
                            },
                            {
                                "name": f"{STATIC_SHELL_NAME}.vCenter Resource Name",
                                "value": vcenter_name,
                            },
                            {
                                "name": f"{STATIC_SHELL_NAME}.User",
                                "value": "",
                            },
                            {
                                "name": f"{STATIC_SHELL_NAME}.Password",
                                "value": "",
                            },
                            {
                                "name": f"{STATIC_SHELL_NAME}.Public IP",
                                "value": "",
                            },
                            {"name": "Execution Server Selector", "value": ""},
                        ],
                    },
                },
                "deployedAppJson": {
                    "name": "win-static",
                    "family": "CS_GenericAppFamily",
                    "model": f"{STATIC_SHELL_NAME}",
                    "address": "192.168.1.2",
                    "attributes": [
                        {
                            "name": f"{STATIC_SHELL_NAME}.VM Name",
                            "value": vm_name,
                        },
                        {
                            "name": f"{STATIC_SHELL_NAME}.vCenter Resource Name",
                            "value": vcenter_name,
                        },
                        {
                            "name": f"{STATIC_SHELL_NAME}.User",
                            "value": "",
                        },
                        {
                            "name": f"{STATIC_SHELL_NAME}.Password",
                            "value": "",
                        },
                        {
                            "name": f"{STATIC_SHELL_NAME}.Public IP",
                            "value": "",
                        },
                        {"name": "Execution Server Selector", "value": ""},
                    ],
                    "vmdetails": {
                        "id": "6132ff9e-379b-4e73-918d-b7e0b7bc93d5",
                        "cloudProviderId": "d4d679c6-3049-4e55-9e64-8692a3400b6a",
                        "uid": vm_uuid,
                        "vmCustomParams": [],
                    },
                },
            }
        ]
    }
    requests = json.dumps(requests)

    GetVMDetailsRequestActions.register_deployment_path(StaticVCenterDeployedApp)
    actions = GetVMDetailsRequestActions.from_request(requests, cs_api)
    return actions.deployed_apps[0]
