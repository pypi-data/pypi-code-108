r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Use Vscan to protect data from being compromised by viruses or other malicious code. Vscan combines best-in-class third party antivirus software with ONTAP features that give you the flexibility you need to control which files get scanned and when. Storage systems offload scanning operations to external servers hosting antivirus software from third party vendors. An Antivirus Connector on the external server handles communications between the storage system and the antivirus software.
## Examples
### Retrieving all of the Vscan configurations
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Vscan.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    Vscan(
        {
            "on_access_policies": [
                {
                    "mandatory": True,
                    "name": "default_CIFS",
                    "scope": {
                        "scan_readonly_volumes": False,
                        "include_extensions": ["*"],
                        "max_file_size": 2147483648,
                        "only_execute_access": False,
                        "scan_without_extension": True,
                    },
                    "enabled": True,
                },
                {
                    "mandatory": True,
                    "name": "on-access-test1",
                    "scope": {
                        "scan_readonly_volumes": False,
                        "include_extensions": ["mp*", "txt"],
                        "max_file_size": 10000,
                        "exclude_paths": ["\\dir"],
                        "only_execute_access": False,
                        "exclude_extensions": ["mp*", "txt"],
                        "scan_without_extension": True,
                    },
                    "enabled": False,
                },
                {
                    "mandatory": True,
                    "name": "on-access-test2",
                    "scope": {
                        "scan_readonly_volumes": False,
                        "include_extensions": ["mp*", "txt"],
                        "max_file_size": 10000,
                        "exclude_paths": ["\\dir"],
                        "only_execute_access": False,
                        "exclude_extensions": ["mp*", "txt"],
                        "scan_without_extension": True,
                    },
                    "enabled": False,
                },
            ],
            "on_demand_policies": [
                {
                    "scope": {
                        "include_extensions": ["vmdk", "mp*"],
                        "max_file_size": 10000,
                        "exclude_paths": ["/vol1"],
                        "exclude_extensions": ["mp3", "mp4"],
                        "scan_without_extension": True,
                    },
                    "log_path": "/vol1",
                    "scan_paths": ["/vol1"],
                    "name": "task-1",
                },
                {
                    "scope": {
                        "include_extensions": ["vmdk", "mp*"],
                        "max_file_size": 10000,
                        "exclude_paths": ["/vol2"],
                        "exclude_extensions": ["mp3", "mp4"],
                        "scan_without_extension": True,
                    },
                    "log_path": "/vol2",
                    "scan_paths": ["/vol1"],
                    "name": "task-2",
                },
            ],
            "enabled": True,
            "scanner_pools": [
                {
                    "role": "primary",
                    "cluster": {
                        "uuid": "0228714d-f268-11e8-8851-0050568e5298",
                        "name": "Cluster1",
                    },
                    "privileged_users": ["cifs\\u1", "cifs\\u2"],
                    "servers": ["1.1.1.1", "10.72.204.27"],
                    "name": "scanner-1",
                },
                {
                    "role": "primary",
                    "cluster": {
                        "uuid": "0228714d-f268-11e8-8851-0050568e5298",
                        "name": "Cluster1",
                    },
                    "privileged_users": ["cifs\\u1", "cifs\\u2"],
                    "servers": ["1.1.1.1", "10.72.204.27"],
                    "name": "scanner-2",
                },
            ],
            "svm": {"uuid": "03ce5c36-f269-11e8-8852-0050568e5298", "name": "vs1"},
        }
    ),
    Vscan(
        {
            "on_access_policies": [
                {
                    "mandatory": True,
                    "name": "default_CIFS",
                    "scope": {
                        "scan_readonly_volumes": False,
                        "include_extensions": ["*"],
                        "max_file_size": 2147483648,
                        "only_execute_access": False,
                        "scan_without_extension": True,
                    },
                    "enabled": True,
                },
                {
                    "mandatory": True,
                    "name": "ap1",
                    "scope": {
                        "scan_readonly_volumes": False,
                        "include_extensions": ["*"],
                        "max_file_size": 2147483648,
                        "only_execute_access": False,
                        "scan_without_extension": True,
                    },
                    "enabled": False,
                },
            ],
            "on_demand_policies": [
                {
                    "scope": {
                        "include_extensions": ["*"],
                        "max_file_size": 10737418240,
                        "scan_without_extension": True,
                    },
                    "log_path": "/vol1",
                    "scan_paths": ["/vol1"],
                    "name": "t1",
                }
            ],
            "enabled": False,
            "scanner_pools": [
                {
                    "role": "idle",
                    "privileged_users": ["cifs\\u1"],
                    "servers": ["1.1.1.1"],
                    "name": "sp2",
                }
            ],
            "svm": {"uuid": "24c2567a-f269-11e8-8852-0050568e5298", "name": "vs2"},
        }
    ),
]

```
</div>
</div>

### Retrieving all Vscan configurations for a particular SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan(**{"svm.uuid": "24c2567a-f269-11e8-8852-0050568e5298"})
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Vscan(
    {
        "on_access_policies": [
            {
                "mandatory": True,
                "name": "default_CIFS",
                "scope": {
                    "scan_readonly_volumes": False,
                    "include_extensions": ["*"],
                    "max_file_size": 2147483648,
                    "only_execute_access": False,
                    "scan_without_extension": True,
                },
                "enabled": True,
            },
            {
                "mandatory": True,
                "name": "ap1",
                "scope": {
                    "scan_readonly_volumes": False,
                    "include_extensions": ["*"],
                    "max_file_size": 2147483648,
                    "only_execute_access": False,
                    "scan_without_extension": True,
                },
                "enabled": False,
            },
        ],
        "on_demand_policies": [
            {
                "scope": {
                    "include_extensions": ["*"],
                    "max_file_size": 10737418240,
                    "scan_without_extension": True,
                },
                "log_path": "/vol1",
                "scan_paths": ["/vol1"],
                "name": "t1",
            }
        ],
        "enabled": False,
        "scanner_pools": [
            {
                "role": "idle",
                "privileged_users": ["cifs\\u1"],
                "servers": ["1.1.1.1"],
                "name": "sp2",
            }
        ],
        "svm": {"uuid": "24c2567a-f269-11e8-8852-0050568e5298", "name": "vs2"},
    }
)

```
</div>
</div>

### Creating a Vscan configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan()
    resource.enabled = True
    resource.on_access_policies = [
        {
            "enabled": True,
            "mandatory": True,
            "name": "on-access-test",
            "scope": {
                "exclude_extensions": ["mp*", "txt"],
                "exclude_paths": ["\\vol"],
                "include_extensions": ["mp*", "txt"],
                "max_file_size": 21474,
                "only_execute_access": False,
                "scan_readonly_volumes": False,
                "scan_without_extension": True,
            },
        }
    ]
    resource.on_demand_policies = [
        {
            "log_path": "/vol",
            "name": "task-1",
            "scan_paths": ["/vol"],
            "schedule": {
                "name": "daily",
                "uuid": "d4984822-17b7-11e9-b450-0050568ecd85",
            },
            "scope": {
                "exclude_extensions": ["mp3", "mp4"],
                "exclude_paths": ["/vol"],
                "include_extensions": ["vmdk", "mp*"],
                "max_file_size": 10737,
                "scan_without_extension": True,
            },
        }
    ]
    resource.scanner_pools = [
        {
            "cluster": {
                "name": "Cluster1",
                "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
            },
            "name": "scanner-1",
            "privileged_users": ["cifs\\u1", "cifs\\u2"],
            "role": "primary",
            "servers": ["1.1.1.1", "10.72.204.27"],
        }
    ]
    resource.svm = {"name": "vs1", "uuid": "b103be27-17b8-11e9-b451-0050568ecd85"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Vscan(
    {
        "on_access_policies": [
            {
                "mandatory": True,
                "name": "on-access-test",
                "scope": {
                    "scan_readonly_volumes": False,
                    "include_extensions": ["mp*", "txt"],
                    "max_file_size": 21474,
                    "exclude_paths": ["\\vol"],
                    "only_execute_access": False,
                    "exclude_extensions": ["mp*", "txt"],
                    "scan_without_extension": True,
                },
                "enabled": True,
            }
        ],
        "on_demand_policies": [
            {
                "schedule": {
                    "uuid": "d4984822-17b7-11e9-b450-0050568ecd85",
                    "name": "daily",
                },
                "scope": {
                    "include_extensions": ["vmdk", "mp*"],
                    "max_file_size": 10737,
                    "exclude_paths": ["//"],
                    "exclude_extensions": ["mp3", "mp4"],
                    "scan_without_extension": True,
                },
                "log_path": "/vol",
                "scan_paths": ["/vol"],
                "name": "task-1",
            }
        ],
        "enabled": True,
        "scanner_pools": [
            {
                "role": "primary",
                "cluster": {
                    "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
                    "name": "Cluster1",
                },
                "privileged_users": ["cifs\\u1", "cifs\\u2"],
                "servers": ["1.1.1.1", "10.72.204.27"],
                "name": "scanner-1",
            }
        ],
        "svm": {"uuid": "b103be27-17b8-11e9-b451-0050568ecd85", "name": "vs1"},
    }
)

```
</div>
</div>

### Creating multiple Vscan scanner-pools for the specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan()
    resource.scanner_pools = [
        {
            "cluster": {
                "name": "Cluster1",
                "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
            },
            "name": "scanner-1",
            "privileged_users": ["cifs\\u1", "cifs\\u2"],
            "role": "primary",
            "servers": ["1.1.1.1", "10.72.204.27"],
        },
        {
            "cluster": {
                "name": "Cluster1",
                "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
            },
            "name": "scanner-2",
            "privileged_users": ["cifs\\u3", "cifs\\u4"],
            "role": "primary",
            "servers": ["1.1.1.5", "10.72.3.27"],
        },
    ]
    resource.svm = {"name": "vs1", "uuid": "b103be27-17b8-11e9-b451-0050568ecd85"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Vscan(
    {
        "scanner_pools": [
            {
                "role": "primary",
                "cluster": {
                    "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
                    "name": "Cluster1",
                },
                "privileged_users": ["cifs\\u1", "cifs\\u2"],
                "servers": ["1.1.1.1", "10.72.204.27"],
                "name": "scanner-1",
            },
            {
                "role": "primary",
                "cluster": {
                    "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
                    "name": "Cluster1",
                },
                "privileged_users": ["cifs\\u3", "cifs\\u4"],
                "servers": ["1.1.1.5", "10.72.3.27"],
                "name": "scanner-2",
            },
        ],
        "svm": {"uuid": "b103be27-17b8-11e9-b451-0050568ecd85", "name": "vs1"},
    }
)

```
</div>
</div>

### Creating multiple Vscan On-access policies for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan()
    resource.on_access_policies = [
        {
            "enabled": False,
            "mandatory": True,
            "name": "on-access-test11",
            "scope": {
                "exclude_extensions": ["mp*", "txt"],
                "exclude_paths": ["\\vol"],
                "include_extensions": ["mp*", "txt"],
                "max_file_size": 214748,
                "only_execute_access": False,
                "scan_readonly_volumes": False,
                "scan_without_extension": True,
            },
        },
        {
            "enabled": False,
            "mandatory": True,
            "name": "on-access-test10",
            "scope": {
                "exclude_extensions": ["mp*", "txt"],
                "exclude_paths": ["\\vol"],
                "include_extensions": ["mp*", "txt"],
                "max_file_size": 21474,
                "only_execute_access": False,
                "scan_readonly_volumes": False,
                "scan_without_extension": True,
            },
        },
    ]
    resource.svm = {"name": "vs1", "uuid": "b103be27-17b8-11e9-b451-0050568ecd85"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
Vscan(
    {
        "on_access_policies": [
            {
                "mandatory": True,
                "name": "on-access-test11",
                "scope": {
                    "scan_readonly_volumes": False,
                    "include_extensions": ["mp*", "txt"],
                    "max_file_size": 214748,
                    "exclude_paths": ["\\vol"],
                    "only_execute_access": False,
                    "exclude_extensions": ["mp*", "txt"],
                    "scan_without_extension": True,
                },
                "enabled": False,
            },
            {
                "mandatory": True,
                "name": "on-access-test10",
                "scope": {
                    "scan_readonly_volumes": False,
                    "include_extensions": ["mp*", "txt"],
                    "max_file_size": 21474,
                    "exclude_paths": ["\\vol"],
                    "only_execute_access": False,
                    "exclude_extensions": ["mp*", "txt"],
                    "scan_without_extension": True,
                },
                "enabled": False,
            },
        ],
        "svm": {"uuid": "b103be27-17b8-11e9-b451-0050568ecd85", "name": "vs1"},
    }
)

```
</div>
</div>

### Creating multiple Vscan On-demand policies for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan()
    resource.on_demand_policies = [
        {
            "log_path": "/vol",
            "name": "task-1",
            "scan_paths": ["/vol"],
            "schedule": {
                "name": "daily",
                "uuid": "d4984822-17b7-11e9-b450-0050568ecd85",
            },
            "scope": {
                "exclude_extensions": ["mp3", "mp4"],
                "exclude_paths": ["/vol1"],
                "include_extensions": ["vmdk", "mp*"],
                "max_file_size": 107374,
                "scan_without_extension": True,
            },
        },
        {
            "log_path": "/vol",
            "name": "task-2",
            "scan_paths": ["/vol"],
            "scope": {
                "exclude_extensions": ["mp3", "mp4"],
                "exclude_paths": ["/vol1"],
                "include_extensions": ["vmdk", "mp*"],
                "max_file_size": 107374,
                "scan_without_extension": True,
            },
        },
    ]
    resource.svm = {"name": "vs1", "uuid": "b103be27-17b8-11e9-b451-0050568ecd85"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
Vscan(
    {
        "on_demand_policies": [
            {
                "schedule": {
                    "uuid": "d4984822-17b7-11e9-b450-0050568ecd85",
                    "name": "daily",
                },
                "scope": {
                    "include_extensions": ["vmdk", "mp*"],
                    "max_file_size": 107374,
                    "exclude_paths": ["/vol1"],
                    "exclude_extensions": ["mp3", "mp4"],
                    "scan_without_extension": True,
                },
                "log_path": "/vol",
                "scan_paths": ["/vol"],
                "name": "task-1",
            },
            {
                "scope": {
                    "include_extensions": ["vmdk", "mp*"],
                    "max_file_size": 107374,
                    "exclude_paths": ["/vol1"],
                    "exclude_extensions": ["mp3", "mp4"],
                    "scan_without_extension": True,
                },
                "log_path": "/vol",
                "scan_paths": ["/vol"],
                "name": "task-2",
            },
        ],
        "svm": {"uuid": "b103be27-17b8-11e9-b451-0050568ecd85", "name": "vs1"},
    }
)

```
</div>
</div>

### Enabling Vscan for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan(**{"svm.uuid": "03ce5c36-f269-11e8-8852-0050568e5298"})
    resource.enabled = True
    resource.patch()

```

### Clearing the Vscan cache for the specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan(**{"svm.uuid": "03ce5c36-f269-11e8-8852-0050568e5298"})
    resource.cache_clear = True
    resource.patch()

```

### Deleting the Vscan configuration for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Vscan

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Vscan(**{"svm.uuid": "03ce5c36-f269-11e8-8852-0050568e5298"})
    resource.delete()

```

"""

import asyncio
from datetime import datetime
import inspect
from typing import Callable, Iterable, List, Optional, Union

try:
    RECLINE_INSTALLED = False
    import recline
    from recline.arg_types.choices import Choices
    from recline.commands import ClicheCommandError
    from netapp_ontap.resource_table import ResourceTable
    RECLINE_INSTALLED = True
except ImportError:
    pass

from marshmallow import fields, EXCLUDE  # type: ignore

import netapp_ontap
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size
from netapp_ontap import NetAppResponse, HostConnection
from netapp_ontap.validations import enum_validation, len_validation, integer_validation
from netapp_ontap.error import NetAppRestError


__all__ = ["Vscan", "VscanSchema"]
__pdoc__ = {
    "VscanSchema.resource": False,
    "Vscan.vscan_show": False,
    "Vscan.vscan_create": False,
    "Vscan.vscan_modify": False,
    "Vscan.vscan_delete": False,
}


class VscanSchema(ResourceSchema):
    """The fields of the Vscan object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the vscan. """

    cache_clear = fields.Boolean(
        data_key="cache_clear",
    )
    r""" Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether or not Vscan is enabled on the SVM. """

    on_access_policies = fields.List(fields.Nested("netapp_ontap.resources.vscan_on_access.VscanOnAccessSchema", unknown=EXCLUDE), data_key="on_access_policies")
    r""" The on_access_policies field of the vscan. """

    on_demand_policies = fields.List(fields.Nested("netapp_ontap.models.vscan_on_demand_policy.VscanOnDemandPolicySchema", unknown=EXCLUDE), data_key="on_demand_policies")
    r""" The on_demand_policies field of the vscan. """

    scanner_pools = fields.List(fields.Nested("netapp_ontap.models.scanner_pool.ScannerPoolSchema", unknown=EXCLUDE), data_key="scanner_pools")
    r""" The scanner_pools field of the vscan. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the vscan. """

    @property
    def resource(self):
        return Vscan

    gettable_fields = [
        "links",
        "enabled",
        "on_access_policies",
        "on_demand_policies",
        "scanner_pools",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,enabled,on_access_policies,on_demand_policies,scanner_pools,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "cache_clear",
        "enabled",
    ]
    """cache_clear,enabled,"""

    postable_fields = [
        "enabled",
        "on_access_policies",
        "on_demand_policies",
        "scanner_pools",
        "svm.name",
        "svm.uuid",
    ]
    """enabled,on_access_policies,on_demand_policies,scanner_pools,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Vscan.get_collection(fields=field)]
    return getter

async def _wait_for_job(response: NetAppResponse) -> None:
    """Examine the given response. If it is a job, asynchronously wait for it to
    complete. While polling, prints the current status message of the job.
    """

    if not response.is_job:
        return
    from netapp_ontap.resources import Job
    job = Job(**response.http_response.json()["job"])
    while True:
        job.get(fields="state,message")
        if hasattr(job, "message"):
            print("[%s]: %s" % (job.state, job.message))
        if job.state == "failure":
            raise NetAppRestError("Vscan modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Vscan(Resource):
    r""" Vscan can be used to protect data from being compromised by viruses or other malicious code. This combines best-in-class third-party antivirus software with ONTAP features that give you the flexibility you need to control which files get scanned and when. Storage systems offload scanning operations to external servers hosting antivirus software from thirdparty vendors. An Antivirus Connector on the external server handles communications between the storage system and the antivirus software. """

    _schema = VscanSchema
    _path = "/api/protocols/vscan"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the Vscan configuration.
This includes scanner-pools, On-Access policies, On-Demand policies, and information about whether a Vscan is enabled or disabled on an SVM.<br/>
Important notes:
* You can enable only one Vscan configuration at a time for an SVM.
* You can only query using `svm.uuid` or `svm.name`.
### Related ONTAP commands
* `vserver vscan show`
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool servers show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan on-access-policy show`
* `vserver vscan on-access-policy file-ext-to-exclude show`
* `vserver vscan on-access-policy file-ext-to-include show`
* `vserver vscan on-access-policy paths-to-exclude show`
* `vserver vscan on-demand-task show`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan show")
        def vscan_show(
            fields: List[Choices.define(["cache_clear", "enabled", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Vscan resources

            Args:
                cache_clear: Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only
                enabled: Specifies whether or not Vscan is enabled on the SVM.
            """

            kwargs = {}
            if cache_clear is not None:
                kwargs["cache_clear"] = cache_clear
            if enabled is not None:
                kwargs["enabled"] = enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Vscan.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Vscan resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Vscan"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Vscan configuration of an SVM. Allows you to either enable or disable a Vscan, and allows you to clear the Vscan cache that stores the past scanning data for an SVM.<br/>
Important note:
* The Vscan PATCH endpoint does not allow you to modify scanner-pools, On-Demand policies or On-Access policies. Those modifications can only be done through their respective endpoints.
### Related ONTAP commands
* `vserver vscan enable`
* `vserver vscan disable`
* `vserver vscan reset`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Vscan"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Vscan"], NetAppResponse]:
        r"""Creates a Vscan configuration, which includes a list of scanner-pools, Vscan On-Access policies and Vscan On-Demand policies. Defines whether the Vscan configuration you create is enabled or disabled for a specified SVM.<br/>
Important notes:
* You can enable only one Vscan configuration at a time for an SVM.
* There needs to be at least one active scanner-pool and one enabled On-Access policy to enable Vscan successfully.
* By default, a Vscan is enabled when it’s created.
* By default, the Vscan On-Access policies created from this endpoint are in the disabled state. You can use the On-Access policy PATCH endpoint to enable a particular On-Access policy. In ONTAP 9.6, only one Vscan On-Access policy can be enabled and only one Vscan On-Demand policy can be scheduled on an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Vscan configuration.
### Recommended optional properties
* `scanner_pools` - There must be at least one active scanner-pool for Vscan configuration. Created either through Vscan POST operation or scanner-pools POST operation.
### Default property values
If not specified in POST, the following default property value is assigned:
* `enabled` - _true_
### Related ONTAP commands
* `vserver vscan enable`
* `vserver vscan scanner-pool create`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool servers add`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan on-access-policy create`
* `vserver vscan on-access-policy file-ext-to-exclude add`
* `vserver vscan on-access-policy file-ext-to-include add`
* `vserver vscan on-access-policy paths-to-exclude add`
* `vserver vscan on-demand-task create`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Vscan"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Vscan configuration.<br/>
Important notes:
* The Vscan DELETE endpoint deletes all of the Vscan configuration of an SVM. It first disables the Vscan and then deletes all of the SVM scanner-pools, On-Access policies, and On-Demand policies.
* Disable the active Vscan On-Access policy on an SVM before performing the Vscan delete operation on that SVM.
### Related ONTAP commands
* `vserver vscan scanner-pool delete`
* `vserver vscan on-access-policy delete`
* `vserver vscan on-demand-policy delete`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the Vscan configuration.
This includes scanner-pools, On-Access policies, On-Demand policies, and information about whether a Vscan is enabled or disabled on an SVM.<br/>
Important notes:
* You can enable only one Vscan configuration at a time for an SVM.
* You can only query using `svm.uuid` or `svm.name`.
### Related ONTAP commands
* `vserver vscan show`
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool servers show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan on-access-policy show`
* `vserver vscan on-access-policy file-ext-to-exclude show`
* `vserver vscan on-access-policy file-ext-to-include show`
* `vserver vscan on-access-policy paths-to-exclude show`
* `vserver vscan on-demand-task show`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the Vscan configuration for a specified SVM.
This includes scanner-pools, On-Access policies, On-Demand policies, and information about whether a Vscan is enabled or disabled on an SVM.<br/>
Important note:
* You can enable only one Vscan configuration at a time for an SVM.
### Related ONTAP commands
* `vserver vscan show`
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool servers show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan on-access-policy show`
* `vserver vscan on-access-policy file-ext-to-exclude show`
* `vserver vscan on-access-policy file-ext-to-include show`
* `vserver vscan on-access-policy paths-to-exclude show`
* `vserver vscan on-demand-task show`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a Vscan configuration, which includes a list of scanner-pools, Vscan On-Access policies and Vscan On-Demand policies. Defines whether the Vscan configuration you create is enabled or disabled for a specified SVM.<br/>
Important notes:
* You can enable only one Vscan configuration at a time for an SVM.
* There needs to be at least one active scanner-pool and one enabled On-Access policy to enable Vscan successfully.
* By default, a Vscan is enabled when it’s created.
* By default, the Vscan On-Access policies created from this endpoint are in the disabled state. You can use the On-Access policy PATCH endpoint to enable a particular On-Access policy. In ONTAP 9.6, only one Vscan On-Access policy can be enabled and only one Vscan On-Demand policy can be scheduled on an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Vscan configuration.
### Recommended optional properties
* `scanner_pools` - There must be at least one active scanner-pool for Vscan configuration. Created either through Vscan POST operation or scanner-pools POST operation.
### Default property values
If not specified in POST, the following default property value is assigned:
* `enabled` - _true_
### Related ONTAP commands
* `vserver vscan enable`
* `vserver vscan scanner-pool create`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool servers add`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan on-access-policy create`
* `vserver vscan on-access-policy file-ext-to-exclude add`
* `vserver vscan on-access-policy file-ext-to-include add`
* `vserver vscan on-access-policy paths-to-exclude add`
* `vserver vscan on-demand-task create`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan create")
        async def vscan_create(
        ) -> ResourceTable:
            """Create an instance of a Vscan resource

            Args:
                links: 
                cache_clear: Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only
                enabled: Specifies whether or not Vscan is enabled on the SVM.
                on_access_policies: 
                on_demand_policies: 
                scanner_pools: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if cache_clear is not None:
                kwargs["cache_clear"] = cache_clear
            if enabled is not None:
                kwargs["enabled"] = enabled
            if on_access_policies is not None:
                kwargs["on_access_policies"] = on_access_policies
            if on_demand_policies is not None:
                kwargs["on_demand_policies"] = on_demand_policies
            if scanner_pools is not None:
                kwargs["scanner_pools"] = scanner_pools
            if svm is not None:
                kwargs["svm"] = svm

            resource = Vscan(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Vscan: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Vscan configuration of an SVM. Allows you to either enable or disable a Vscan, and allows you to clear the Vscan cache that stores the past scanning data for an SVM.<br/>
Important note:
* The Vscan PATCH endpoint does not allow you to modify scanner-pools, On-Demand policies or On-Access policies. Those modifications can only be done through their respective endpoints.
### Related ONTAP commands
* `vserver vscan enable`
* `vserver vscan disable`
* `vserver vscan reset`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan modify")
        async def vscan_modify(
        ) -> ResourceTable:
            """Modify an instance of a Vscan resource

            Args:
                cache_clear: Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only
                query_cache_clear: Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only
                enabled: Specifies whether or not Vscan is enabled on the SVM.
                query_enabled: Specifies whether or not Vscan is enabled on the SVM.
            """

            kwargs = {}
            changes = {}
            if query_cache_clear is not None:
                kwargs["cache_clear"] = query_cache_clear
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled

            if cache_clear is not None:
                changes["cache_clear"] = cache_clear
            if enabled is not None:
                changes["enabled"] = enabled

            if hasattr(Vscan, "find"):
                resource = Vscan.find(
                    **kwargs
                )
            else:
                resource = Vscan()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Vscan: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Vscan configuration.<br/>
Important notes:
* The Vscan DELETE endpoint deletes all of the Vscan configuration of an SVM. It first disables the Vscan and then deletes all of the SVM scanner-pools, On-Access policies, and On-Demand policies.
* Disable the active Vscan On-Access policy on an SVM before performing the Vscan delete operation on that SVM.
### Related ONTAP commands
* `vserver vscan scanner-pool delete`
* `vserver vscan on-access-policy delete`
* `vserver vscan on-demand-policy delete`
### Learn more
* [`DOC /protocols/vscan`](#docs-NAS-protocols_vscan)
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan delete")
        async def vscan_delete(
        ) -> None:
            """Delete an instance of a Vscan resource

            Args:
                cache_clear: Discards the cached information of the files that have been successfully scanned. Once the cache is cleared, files are scanned again when they are accessed. PATCH only
                enabled: Specifies whether or not Vscan is enabled on the SVM.
            """

            kwargs = {}
            if cache_clear is not None:
                kwargs["cache_clear"] = cache_clear
            if enabled is not None:
                kwargs["enabled"] = enabled

            if hasattr(Vscan, "find"):
                resource = Vscan.find(
                    **kwargs
                )
            else:
                resource = Vscan()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Vscan: %s" % err)


