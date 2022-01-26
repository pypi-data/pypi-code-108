import json

from cloudshell.cp.core.request_actions import GetVMDetailsRequestActions

from cloudshell.cp.vcenter.constants import STATIC_SHELL_NAME
from cloudshell.cp.vcenter.models.deployed_app import StaticVCenterDeployedApp


def test_static_deploy_app(cs_api):
    vm_name = "vm folder/vm-name"
    vcenter_name = "vcenter"
    vm_uuid = "uuid"
    requests = {
        "items": [
            {
                "appRequestJson": "",
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

    assert actions.deployed_app is None
    assert actions.deployed_apps
    assert len(actions.deployed_apps) == 1
    deployed_app = actions.deployed_apps[0]
    assert isinstance(deployed_app, StaticVCenterDeployedApp)
    assert deployed_app.vm_name == vm_name
    assert deployed_app.vcenter_resource_name == vcenter_name
    assert deployed_app.vmdetails.uid == vm_uuid
