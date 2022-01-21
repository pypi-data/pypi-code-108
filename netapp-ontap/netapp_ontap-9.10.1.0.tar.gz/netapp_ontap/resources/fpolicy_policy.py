r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The FPolicy policy acts as a container for different constituents of the FPolicy such as FPolicy events and the FPolicy engine. It also provides a platform for policy management functions, such as policy enabling and disabling. As part of FPolicy policy configuration, you can specifiy the name of policy, the SVM to which it belongs, the FPolicy events to monitor, the FPolicy engine to which the generated notifications are sent and the policy priority. FPolicy policy configuration also allows to you to configure the file access behaviour when the primary and secondary servers are down. Under such circumstances, if the "mandatory" field is set to true, file access is denied.</br>
Each FPolicy policy is associated with a scope which allows you to restrain the scope of the policy to specified storage objects such as volume, shares and export or to a set of file extensions such as .txt, .jpeg. An FPolicy policy can be configured to send notifications, to the FPolicy server or for native file blocking which uses the file extension specified in the policy scope. An SVM can have multiple FPolicy policies which can be enabled or disabled independently of each other.
## Examples
### Creating an FPolicy policy
Use the following API to create an FPolicy policy configuration. Note that the <i>return_records=true</i> query parameter used to obtain the newly created entry in the response.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34")
    resource.engine = {"name": "engine1"}
    resource.events = [{"name": "cifs"}, {"name": "nfs"}]
    resource.mandatory = True
    resource.name = "FPolicy_policy_0"
    resource.passthrough_read = True
    resource.privileged_user = "mydomain\testuser"
    resource.scope = {
        "exclude_export_policies": ["export_pol1"],
        "exclude_extension": ["txt", "png"],
        "exclude_shares": ["sh1"],
        "exclude_volumes": ["vol0"],
        "include_export_policies": ["export_pol10"],
        "include_extension": ["pdf"],
        "include_shares": ["sh2", "sh3"],
        "include_volumes": ["vol1", "vol2"],
    }
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
FpolicyPolicy(
    {
        "passthrough_read": True,
        "scope": {
            "exclude_export_policies": ["export_pol1"],
            "include_export_policies": ["export_pol10"],
            "include_extension": ["pdf"],
            "include_volumes": ["vol1", "vol2"],
            "include_shares": ["sh2", "sh3"],
            "exclude_extension": ["txt", "png"],
            "exclude_volumes": ["vol0"],
            "exclude_shares": ["sh1"],
        },
        "events": [{"name": "cifs"}, {"name": "nfs"}],
        "mandatory": True,
        "engine": {"name": "engine1"},
        "name": "FPolicy_policy_0",
        "privileged_user": "mydomain\\testuser",
    }
)

```
</div>
</div>

---
### Creating and enable an FPolicy policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34")
    resource.priority = 1
    resource.engine = {"name": "engine1"}
    resource.events = [{"name": "cifs"}, {"name": "nfs"}]
    resource.mandatory = True
    resource.name = "FPolicy_policy_on"
    resource.passthrough_read = False
    resource.scope = {
        "exclude_export_policies": ["export_pol1"],
        "exclude_extension": ["txt", "png"],
        "exclude_shares": ["sh1"],
        "exclude_volumes": ["vol0"],
        "include_export_policies": ["export_pol10"],
        "include_extension": ["pdf"],
        "include_shares": ["sh2", "sh3"],
        "include_volumes": ["vol1", "vol2"],
    }
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
FpolicyPolicy(
    {
        "passthrough_read": True,
        "priority": 1,
        "scope": {
            "exclude_export_policies": ["export_pol1"],
            "include_export_policies": ["export_pol10"],
            "include_extension": ["pdf"],
            "include_volumes": ["vol1", "vol2"],
            "include_shares": ["sh2", "sh3"],
            "exclude_extension": ["txt", "png"],
            "exclude_volumes": ["vol0"],
            "exclude_shares": ["sh1"],
        },
        "events": [{"name": "cifs"}, {"name": "nfs"}],
        "mandatory": True,
        "engine": {"name": "engine1"},
        "name": "FPolicy_policy_0",
        "privileged_user": "mydomain\\testuser",
    }
)

```
</div>
</div>

---
### Creating an FPolicy policy with the minimum required fields and a native engine
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34")
    resource.events = [{"name": "cifs"}, {"name": "nfs"}]
    resource.name = "pol_minimum_fields"
    resource.scope = {"include_volumes": ["vol1", "vol2"]}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
FpolicyPolicy(
    {
        "scope": {"include_volumes": ["vol1", "vol2"]},
        "events": [{"name": "cifs"}, {"name": "nfs"}],
        "name": "pol_minimum_fields",
    }
)

```
</div>
</div>

---
### Retrieving all the FPolicy policy configurations for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyPolicy.get_collection(
                "a00fac5d-0164-11e9-b64a-0050568eeb34", fields="*", return_timeout=15
            )
        )
    )

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "enabled": False,
            "scope": {
                "exclude_export_policies": ["export_pol1"],
                "include_export_policies": ["export_pol10"],
                "include_extension": ["pdf"],
                "include_volumes": ["vol1", "vol2"],
                "include_shares": ["sh2", "sh3"],
                "exclude_extension": ["txt", "png"],
                "exclude_volumes": ["vol0"],
                "exclude_shares": ["sh1"],
            },
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cifs"}, {"name": "nfs"}],
            "mandatory": True,
            "engine": {"name": "engine1"},
            "name": "pol0",
        }
    ),
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "priority": 1,
            "enabled": True,
            "scope": {
                "exclude_export_policies": ["export_pol1"],
                "include_export_policies": ["export_pol10"],
                "include_extension": ["pdf"],
                "include_volumes": ["vol1", "vol2"],
                "include_shares": ["sh2", "sh3"],
                "exclude_extension": ["txt", "png"],
                "exclude_volumes": ["vol0"],
                "exclude_shares": ["sh1"],
            },
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cifs"}, {"name": "nfs"}],
            "mandatory": True,
            "engine": {"name": "engine1"},
            "name": "FPolicy_policy_on",
        }
    ),
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "enabled": False,
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cluster"}],
            "mandatory": True,
            "engine": {"name": "native"},
            "name": "cluster_pol",
        }
    ),
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "enabled": False,
            "scope": {"include_volumes": ["vol1", "vol2"]},
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cifs"}, {"name": "nfs"}],
            "mandatory": True,
            "engine": {"name": "native"},
            "name": "pol_minimum_fields",
        }
    ),
]

```
</div>
</div>

---
### Retrieving all of the FPolicy policy configurations for the FPolicy engine "engine1" for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyPolicy.get_collection(
                "a00fac5d-0164-11e9-b64a-0050568eeb34",
                fields="*",
                return_timeout=15,
                **{"engine.name": "engine1"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
[
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "enabled": False,
            "scope": {
                "exclude_export_policies": ["export_pol1"],
                "include_export_policies": ["export_pol10"],
                "include_extension": ["pdf"],
                "exclude_extension": ["txt", "png"],
            },
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cifs"}, {"name": "nfs"}],
            "mandatory": True,
            "engine": {"name": "engine1"},
            "name": "pol0",
        }
    ),
    FpolicyPolicy(
        {
            "passthrough_read": False,
            "priority": 1,
            "enabled": True,
            "scope": {
                "exclude_export_policies": ["export_pol1"],
                "include_export_policies": ["export_pol10"],
                "include_extension": ["pdf"],
                "include_volumes": ["vol1", "vol2"],
                "include_shares": ["sh2", "sh3"],
                "exclude_extension": ["txt", "png"],
                "exclude_volumes": ["vol0"],
                "exclude_shares": ["sh1"],
            },
            "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
            "events": [{"name": "cifs"}, {"name": "nfs"}],
            "mandatory": True,
            "engine": {"name": "engine1"},
            "name": "FPolicy_policy_on",
        }
    ),
]

```
</div>
</div>

---
### Retrieving a particular FPolicy policy configuration for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34", name="pol0")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
FpolicyPolicy(
    {
        "passthrough_read": False,
        "enabled": False,
        "scope": {
            "exclude_export_policies": ["export_pol1"],
            "include_export_policies": ["export_pol10"],
            "include_extension": ["pdf"],
            "include_volumes": ["vol1", "vol2"],
            "include_shares": ["sh2", "sh3"],
            "exclude_extension": ["txt", "png"],
            "exclude_volumes": ["vol0"],
            "exclude_shares": ["sh1"],
        },
        "svm": {"uuid": "a00fac5d-0164-11e9-b64a-0050568eeb34"},
        "events": [{"name": "cifs"}, {"name": "nfs"}],
        "mandatory": True,
        "engine": {"name": "engine1"},
        "name": "pol0",
    }
)

```
</div>
</div>

---
### Updating a particular FPolicy policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34", name="pol0")
    resource.engine = {"name": "native"}
    resource.events = [{"name": "cifs"}]
    resource.mandatory = False
    resource.scope = {"include_volumes": ["*"]}
    resource.patch()

```

---
### Enabling a particular FPolicy policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34", name="pol0")
    resource.enabled = True
    resource.priority = 3
    resource.patch()

```

---
### Disabling a particular FPolicy policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyPolicy("a00fac5d-0164-11e9-b64a-0050568eeb34", name="pol0")
    resource.enabled = True
    resource.patch()

```

---
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


__all__ = ["FpolicyPolicy", "FpolicyPolicySchema"]
__pdoc__ = {
    "FpolicyPolicySchema.resource": False,
    "FpolicyPolicy.fpolicy_policy_show": False,
    "FpolicyPolicy.fpolicy_policy_create": False,
    "FpolicyPolicy.fpolicy_policy_modify": False,
    "FpolicyPolicy.fpolicy_policy_delete": False,
}


class FpolicyPolicySchema(ResourceSchema):
    """The fields of the FpolicyPolicy object"""

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies if the policy is enabled on the SVM or not. If no value is
mentioned for this field but priority is set, then this policy will be enabled. """

    engine = fields.Nested("netapp_ontap.resources.fpolicy_engine.FpolicyEngineSchema", data_key="engine", unknown=EXCLUDE)
    r""" The engine field of the fpolicy_policy. """

    events = fields.List(fields.Nested("netapp_ontap.resources.fpolicy_event.FpolicyEventSchema", unknown=EXCLUDE), data_key="events")
    r""" The events field of the fpolicy_policy.

Example: ["event_nfs_close","event_open"] """

    mandatory = fields.Boolean(
        data_key="mandatory",
    )
    r""" Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances. """

    name = fields.Str(
        data_key="name",
    )
    r""" Specifies the name of the policy.

Example: fp_policy_1 """

    passthrough_read = fields.Boolean(
        data_key="passthrough_read",
    )
    r""" Specifies whether passthrough-read should be allowed for FPolicy servers
registered for the policy. Passthrough-read is a way to read data for
offline files without restoring the files to primary storage. Offline
files are files that have been moved to secondary storage. """

    priority = Size(
        data_key="priority",
        validate=integer_validation(minimum=1, maximum=10),
    )
    r""" Specifies the priority that is assigned to this policy. """

    privileged_user = fields.Str(
        data_key="privileged_user",
    )
    r""" Specifies the privileged user name for accessing files on the cluster
using a separate data channel with privileged access. The input for
this field should be in "domain\username" format.


Example: mydomain\testuser """

    scope = fields.Nested("netapp_ontap.models.fpolicy_policies_scope.FpolicyPoliciesScopeSchema", data_key="scope", unknown=EXCLUDE)
    r""" The scope field of the fpolicy_policy. """

    svm = fields.Nested("netapp_ontap.models.fpolicy_engine_svm.FpolicyEngineSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fpolicy_policy. """

    @property
    def resource(self):
        return FpolicyPolicy

    gettable_fields = [
        "enabled",
        "engine.links",
        "engine.name",
        "events",
        "mandatory",
        "name",
        "passthrough_read",
        "priority",
        "privileged_user",
        "scope",
        "svm",
    ]
    """enabled,engine.links,engine.name,events,mandatory,name,passthrough_read,priority,privileged_user,scope,svm,"""

    patchable_fields = [
        "enabled",
        "engine.name",
        "events",
        "mandatory",
        "passthrough_read",
        "priority",
        "privileged_user",
        "scope",
        "svm",
    ]
    """enabled,engine.name,events,mandatory,passthrough_read,priority,privileged_user,scope,svm,"""

    postable_fields = [
        "engine.name",
        "events",
        "mandatory",
        "name",
        "passthrough_read",
        "priority",
        "privileged_user",
        "scope",
        "svm",
    ]
    """engine.name,events,mandatory,name,passthrough_read,priority,privileged_user,scope,svm,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FpolicyPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("FpolicyPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FpolicyPolicy(Resource):
    """Allows interaction with FpolicyPolicy objects on the host"""

    _schema = FpolicyPolicySchema
    _path = "/api/protocols/fpolicy/{svm[uuid]}/policies"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the FPolicy policy configuration of an SVM. ONTAP allows the creation of a cluster level FPolicy policy that acts as a template for all the data SVMs belonging to the cluster. This cluster level FPolicy policy is also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy show`
* `fpolicy policy scope show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy policy show")
        def fpolicy_policy_show(
            svm_uuid,
            enabled: Choices.define(_get_field_list("enabled"), cache_choices=True, inexact=True)=None,
            mandatory: Choices.define(_get_field_list("mandatory"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            passthrough_read: Choices.define(_get_field_list("passthrough_read"), cache_choices=True, inexact=True)=None,
            priority: Choices.define(_get_field_list("priority"), cache_choices=True, inexact=True)=None,
            privileged_user: Choices.define(_get_field_list("privileged_user"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["enabled", "mandatory", "name", "passthrough_read", "priority", "privileged_user", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FpolicyPolicy resources

            Args:
                enabled: Specifies if the policy is enabled on the SVM or not. If no value is mentioned for this field but priority is set, then this policy will be enabled. 
                mandatory: Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances.
                name: Specifies the name of the policy.
                passthrough_read: Specifies whether passthrough-read should be allowed for FPolicy servers registered for the policy. Passthrough-read is a way to read data for offline files without restoring the files to primary storage. Offline files are files that have been moved to secondary storage. 
                priority: Specifies the priority that is assigned to this policy.
                privileged_user: Specifies the privileged user name for accessing files on the cluster using a separate data channel with privileged access. The input for this field should be in \"domain\\username\" format. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if mandatory is not None:
                kwargs["mandatory"] = mandatory
            if name is not None:
                kwargs["name"] = name
            if passthrough_read is not None:
                kwargs["passthrough_read"] = passthrough_read
            if priority is not None:
                kwargs["priority"] = priority
            if privileged_user is not None:
                kwargs["privileged_user"] = privileged_user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FpolicyPolicy.get_collection(
                svm_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FpolicyPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FpolicyPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a particular FPolicy policy configuration for a specified SVM. PATCH can be used to enable or disable the policy. When enabling a policy, you must specify the policy priority. The policy priority of the policy is not required when disabling the policy. If the policy is enabled, the FPolicy policy engine cannot be modified.
### Related ONTAP commands
* `fpolicy policy modify`
* `fpolicy policy scope modify`
* `fpolicy enable`
* `fpolicy disable`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FpolicyPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FpolicyPolicy"], NetAppResponse]:
        r"""Creates an FPolicy policy configuration for the specified SVM. To create an FPolicy policy, you must specify the policy scope and the FPolicy events to be monitored.
</br>Important notes:
* A single policy can monitor multiple events.
* An FPolicy engine is an optional field whose default value is set to native. A native engine can be used to simply block the file access based on the file extensions specified in the policy scope.
* To enable a policy, the policy priority  must be specified. If the priority is not specified, the policy is created but it is not enabled.
* The "mandatory" field, if set to true, blocks the file access when the primary or secondary FPolicy servers are down.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy policy.
* `events` - Name of the events to monitior.
* `name` - Name of the FPolicy policy.
* `scope` - Scope of the policy. Can be limited to exports, volumes, shares or file extensions.
* `priority`- Priority of the policy (ranging from 1 to 10).
### Default property values
* `mandatory` - _true_
* `engine` - _native_
### Related ONTAP commands
* `fpolicy policy scope create`
* `fpolicy policy create`
* `fpolicy enable`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
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
        records: Iterable["FpolicyPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a particular FPolicy policy configuration for a specified SVM. To delete a policy, you must first disable the policy.
### Related ONTAP commands
* `fpolicy policy scope delete`
* `fpolicy policy delete`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the FPolicy policy configuration of an SVM. ONTAP allows the creation of a cluster level FPolicy policy that acts as a template for all the data SVMs belonging to the cluster. This cluster level FPolicy policy is also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy show`
* `fpolicy policy scope show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a particular FPolicy policy configuration for a specified SVM. Cluster-level FPolicy policy configuration details cannot be retrieved for a data SVM.
### Related ONTAP commands
* `fpolicy policy show`
* `fpolicy policy scope show`
* `fpolicy show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
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
        r"""Creates an FPolicy policy configuration for the specified SVM. To create an FPolicy policy, you must specify the policy scope and the FPolicy events to be monitored.
</br>Important notes:
* A single policy can monitor multiple events.
* An FPolicy engine is an optional field whose default value is set to native. A native engine can be used to simply block the file access based on the file extensions specified in the policy scope.
* To enable a policy, the policy priority  must be specified. If the priority is not specified, the policy is created but it is not enabled.
* The "mandatory" field, if set to true, blocks the file access when the primary or secondary FPolicy servers are down.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy policy.
* `events` - Name of the events to monitior.
* `name` - Name of the FPolicy policy.
* `scope` - Scope of the policy. Can be limited to exports, volumes, shares or file extensions.
* `priority`- Priority of the policy (ranging from 1 to 10).
### Default property values
* `mandatory` - _true_
* `engine` - _native_
### Related ONTAP commands
* `fpolicy policy scope create`
* `fpolicy policy create`
* `fpolicy enable`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy policy create")
        async def fpolicy_policy_create(
            svm_uuid,
            enabled: bool = None,
            engine: dict = None,
            events: dict = None,
            mandatory: bool = None,
            name: str = None,
            passthrough_read: bool = None,
            priority: Size = None,
            privileged_user: str = None,
            scope: dict = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a FpolicyPolicy resource

            Args:
                enabled: Specifies if the policy is enabled on the SVM or not. If no value is mentioned for this field but priority is set, then this policy will be enabled. 
                engine: 
                events: 
                mandatory: Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances.
                name: Specifies the name of the policy.
                passthrough_read: Specifies whether passthrough-read should be allowed for FPolicy servers registered for the policy. Passthrough-read is a way to read data for offline files without restoring the files to primary storage. Offline files are files that have been moved to secondary storage. 
                priority: Specifies the priority that is assigned to this policy.
                privileged_user: Specifies the privileged user name for accessing files on the cluster using a separate data channel with privileged access. The input for this field should be in \"domain\\username\" format. 
                scope: 
                svm: 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if engine is not None:
                kwargs["engine"] = engine
            if events is not None:
                kwargs["events"] = events
            if mandatory is not None:
                kwargs["mandatory"] = mandatory
            if name is not None:
                kwargs["name"] = name
            if passthrough_read is not None:
                kwargs["passthrough_read"] = passthrough_read
            if priority is not None:
                kwargs["priority"] = priority
            if privileged_user is not None:
                kwargs["privileged_user"] = privileged_user
            if scope is not None:
                kwargs["scope"] = scope
            if svm is not None:
                kwargs["svm"] = svm

            resource = FpolicyPolicy(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FpolicyPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a particular FPolicy policy configuration for a specified SVM. PATCH can be used to enable or disable the policy. When enabling a policy, you must specify the policy priority. The policy priority of the policy is not required when disabling the policy. If the policy is enabled, the FPolicy policy engine cannot be modified.
### Related ONTAP commands
* `fpolicy policy modify`
* `fpolicy policy scope modify`
* `fpolicy enable`
* `fpolicy disable`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy policy modify")
        async def fpolicy_policy_modify(
            svm_uuid,
            enabled: bool = None,
            query_enabled: bool = None,
            mandatory: bool = None,
            query_mandatory: bool = None,
            name: str = None,
            query_name: str = None,
            passthrough_read: bool = None,
            query_passthrough_read: bool = None,
            priority: Size = None,
            query_priority: Size = None,
            privileged_user: str = None,
            query_privileged_user: str = None,
        ) -> ResourceTable:
            """Modify an instance of a FpolicyPolicy resource

            Args:
                enabled: Specifies if the policy is enabled on the SVM or not. If no value is mentioned for this field but priority is set, then this policy will be enabled. 
                query_enabled: Specifies if the policy is enabled on the SVM or not. If no value is mentioned for this field but priority is set, then this policy will be enabled. 
                mandatory: Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances.
                query_mandatory: Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances.
                name: Specifies the name of the policy.
                query_name: Specifies the name of the policy.
                passthrough_read: Specifies whether passthrough-read should be allowed for FPolicy servers registered for the policy. Passthrough-read is a way to read data for offline files without restoring the files to primary storage. Offline files are files that have been moved to secondary storage. 
                query_passthrough_read: Specifies whether passthrough-read should be allowed for FPolicy servers registered for the policy. Passthrough-read is a way to read data for offline files without restoring the files to primary storage. Offline files are files that have been moved to secondary storage. 
                priority: Specifies the priority that is assigned to this policy.
                query_priority: Specifies the priority that is assigned to this policy.
                privileged_user: Specifies the privileged user name for accessing files on the cluster using a separate data channel with privileged access. The input for this field should be in \"domain\\username\" format. 
                query_privileged_user: Specifies the privileged user name for accessing files on the cluster using a separate data channel with privileged access. The input for this field should be in \"domain\\username\" format. 
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_mandatory is not None:
                kwargs["mandatory"] = query_mandatory
            if query_name is not None:
                kwargs["name"] = query_name
            if query_passthrough_read is not None:
                kwargs["passthrough_read"] = query_passthrough_read
            if query_priority is not None:
                kwargs["priority"] = query_priority
            if query_privileged_user is not None:
                kwargs["privileged_user"] = query_privileged_user

            if enabled is not None:
                changes["enabled"] = enabled
            if mandatory is not None:
                changes["mandatory"] = mandatory
            if name is not None:
                changes["name"] = name
            if passthrough_read is not None:
                changes["passthrough_read"] = passthrough_read
            if priority is not None:
                changes["priority"] = priority
            if privileged_user is not None:
                changes["privileged_user"] = privileged_user

            if hasattr(FpolicyPolicy, "find"):
                resource = FpolicyPolicy.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyPolicy(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FpolicyPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a particular FPolicy policy configuration for a specified SVM. To delete a policy, you must first disable the policy.
### Related ONTAP commands
* `fpolicy policy scope delete`
* `fpolicy policy delete`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/policies`](#docs-NAS-protocols_fpolicy_{svm.uuid}_policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy policy delete")
        async def fpolicy_policy_delete(
            svm_uuid,
            enabled: bool = None,
            mandatory: bool = None,
            name: str = None,
            passthrough_read: bool = None,
            priority: Size = None,
            privileged_user: str = None,
        ) -> None:
            """Delete an instance of a FpolicyPolicy resource

            Args:
                enabled: Specifies if the policy is enabled on the SVM or not. If no value is mentioned for this field but priority is set, then this policy will be enabled. 
                mandatory: Specifies what action to take on a file access event in a case when all primary and secondary servers are down or no response is received from the FPolicy servers within a given timeout period. When this parameter is set to true, file access events will be denied under these circumstances.
                name: Specifies the name of the policy.
                passthrough_read: Specifies whether passthrough-read should be allowed for FPolicy servers registered for the policy. Passthrough-read is a way to read data for offline files without restoring the files to primary storage. Offline files are files that have been moved to secondary storage. 
                priority: Specifies the priority that is assigned to this policy.
                privileged_user: Specifies the privileged user name for accessing files on the cluster using a separate data channel with privileged access. The input for this field should be in \"domain\\username\" format. 
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if mandatory is not None:
                kwargs["mandatory"] = mandatory
            if name is not None:
                kwargs["name"] = name
            if passthrough_read is not None:
                kwargs["passthrough_read"] = passthrough_read
            if priority is not None:
                kwargs["priority"] = priority
            if privileged_user is not None:
                kwargs["privileged_user"] = privileged_user

            if hasattr(FpolicyPolicy, "find"):
                resource = FpolicyPolicy.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyPolicy(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FpolicyPolicy: %s" % err)


