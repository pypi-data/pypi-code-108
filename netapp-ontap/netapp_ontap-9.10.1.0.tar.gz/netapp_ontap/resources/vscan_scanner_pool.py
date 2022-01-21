r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A scanner-pool defines the Vscan servers and privileged users that can connect to SVMs and a scanner policy or role determines whether a scanner-pool is active. You can configure a scanner-pool to be used on the local cluster or any other cluster in an MCC/DR setup.
## Examples
### Retrieving all fields for all scanner-pools of an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            VscanScannerPool.get_collection("<svm-uuid>", fields="*", return_timeout=15)
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    VscanScannerPool(
        {
            "role": "primary",
            "svm": {"uuid": "0e2f7c91-f227-11e8-9601-0050568ecc06"},
            "privileged_users": ["cifs\\u1", "cifs\\u2"],
            "servers": ["1.1.1.1", "10.72.204.27"],
            "name": "scanner-1",
        }
    ),
    VscanScannerPool(
        {
            "role": "secondary",
            "svm": {"uuid": "0e2f7c91-f227-11e8-9601-0050568ecc06"},
            "privileged_users": ["cifs\\u1", "cifs\\u2"],
            "servers": ["1.1.1.1", "10.72.204.27"],
            "name": "scanner-2",
        }
    ),
]

```
</div>
</div>

### Retrieving all scanner-pools with *role* set as *secondary*
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            VscanScannerPool.get_collection(
                "<svm-uuid>", role="secondary", fields="*", return_timeout=15
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    VscanScannerPool(
        {
            "role": "secondary",
            "cluster": {
                "uuid": "0933f9b5-f226-11e8-9601-0050568ecc06",
                "name": "Cluster3",
            },
            "svm": {"uuid": "0e2f7c91-f227-11e8-9601-0050568ecc06", "name": "vs1"},
            "privileged_users": ["cifs\\u1", "cifs\\u2"],
            "servers": ["1.1.1.1", "10.72.204.27"],
            "name": "scanner-2",
        }
    )
]

```
</div>
</div>

### Retrieving the specified scanner-pool associated with an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool(
        "0e2f7c91-f227-11e8-9601-0050568ecc06", name="scanner-1"
    )
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
VscanScannerPool(
    {
        "role": "primary",
        "cluster": {"uuid": "0933f9b5-f226-11e8-9601-0050568ecc06", "name": "Cluster3"},
        "svm": {"uuid": "0e2f7c91-f227-11e8-9601-0050568ecc06", "name": "vs1"},
        "privileged_users": ["cifs\\u1", "cifs\\u2"],
        "servers": ["1.1.1.1", "10.72.204.27"],
        "name": "scanner-1",
    }
)

```
</div>
</div>

### Creating a scanner-pool for an SVM with all fields specified
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool("b103be27-17b8-11e9-b451-0050568ecd85")
    resource.cluster = {
        "name": "Cluster1",
        "uuid": "ab746d77-17b7-11e9-b450-0050568ecd85",
    }
    resource.name = "test-scanner"
    resource.privileged_users = ["cifs\\u1", "cifs\\u2"]
    resource.role = "primary"
    resource.servers = ["1.1.1.1", "10.72.204.27"]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
VscanScannerPool(
    {
        "role": "primary",
        "cluster": {"uuid": "ab746d77-17b7-11e9-b450-0050568ecd85", "name": "Cluster1"},
        "privileged_users": ["cifs\\u1", "cifs\\u2"],
        "servers": ["1.1.1.1", "10.72.204.27"],
        "name": "test-scanner",
    }
)

```
</div>
</div>

### Creating a scanner-pool for an SVM with an unspecified role and cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool("b103be27-17b8-11e9-b451-0050568ecd85")
    resource.name = "test-scanner-1"
    resource.privileged_users = ["cifs\\u1", "cifs\\u2"]
    resource.servers = ["1.1.1.1", "10.72.204.27"]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
VscanScannerPool(
    {
        "privileged_users": ["cifs\\u1", "cifs\\u2"],
        "servers": ["1.1.1.1", "10.72.204.27"],
        "name": "test-scanner-1",
    }
)

```
</div>
</div>

### Updating a scanner-pool for an SVM with all of the fields specified
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool(
        "0e2f7c91-f227-11e8-9601-0050568ecc06", name="test-scanner-1"
    )
    resource.cluster = {
        "name": "Cluster3",
        "uuid": "0933f9b5-f226-11e8-9601-0050568ecc06",
    }
    resource.privileged_users = ["cifs\\u1", "cifs\\u2"]
    resource.role = "secondary"
    resource.servers = ["1.1.1.1", "10.72.204.27"]
    resource.patch()

```

### Updating the "role" of a scanner-pool for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool(
        "0e2f7c91-f227-11e8-9601-0050568ecc06", name="test-scanner-1"
    )
    resource.cluster = {
        "name": "Cluster3",
        "uuid": "0933f9b5-f226-11e8-9601-0050568ecc06",
    }
    resource.role = "primary"
    resource.patch()

```

### Deleting a scanner-pool for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VscanScannerPool

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VscanScannerPool(
        "0e2f7c91-f227-11e8-9601-0050568ecc06", name="test-scanner-1"
    )
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


__all__ = ["VscanScannerPool", "VscanScannerPoolSchema"]
__pdoc__ = {
    "VscanScannerPoolSchema.resource": False,
    "VscanScannerPool.vscan_scanner_pool_show": False,
    "VscanScannerPool.vscan_scanner_pool_create": False,
    "VscanScannerPool.vscan_scanner_pool_modify": False,
    "VscanScannerPool.vscan_scanner_pool_delete": False,
}


class VscanScannerPoolSchema(ResourceSchema):
    """The fields of the VscanScannerPool object"""

    cluster = fields.Nested("netapp_ontap.resources.cluster.ClusterSchema", data_key="cluster", unknown=EXCLUDE)
    r""" The cluster field of the vscan_scanner_pool. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=256),
    )
    r""" Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), "_", "-" and ".".

Example: scanner-1 """

    privileged_users = fields.List(fields.Str, data_key="privileged_users")
    r""" Specifies a list of privileged users. A valid form of privileged user-name is "domain-name\user-name". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.

Example: ["cifs\\u1","cifs\\u2"] """

    role = fields.Str(
        data_key="role",
        validate=enum_validation(['primary', 'secondary', 'idle']),
    )
    r""" Specifies the role of the scanner pool. The possible values are:

  * primary   - Always active.
  * secondary - Active only when none of the primary external virus-scanning servers are connected.
  * idle      - Always inactive.


Valid choices:

* primary
* secondary
* idle """

    servers = fields.List(fields.Str, data_key="servers")
    r""" Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.

Example: ["1.1.1.1","10.72.204.27","vmwin204-27.fsct.nb"] """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the vscan_scanner_pool. """

    @property
    def resource(self):
        return VscanScannerPool

    gettable_fields = [
        "cluster.links",
        "cluster.name",
        "cluster.uuid",
        "name",
        "privileged_users",
        "role",
        "servers",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.links,cluster.name,cluster.uuid,name,privileged_users,role,servers,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "cluster.name",
        "cluster.uuid",
        "privileged_users",
        "role",
        "servers",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.name,cluster.uuid,privileged_users,role,servers,svm.name,svm.uuid,"""

    postable_fields = [
        "cluster.name",
        "cluster.uuid",
        "name",
        "privileged_users",
        "role",
        "servers",
        "svm.name",
        "svm.uuid",
    ]
    """cluster.name,cluster.uuid,name,privileged_users,role,servers,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in VscanScannerPool.get_collection(fields=field)]
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
            raise NetAppRestError("VscanScannerPool modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class VscanScannerPool(Resource):
    r""" Scanner pool is a set of attributes which are used to validate and manage connections between clustered ONTAP and external virus-scanning server, or "Vscan server". """

    _schema = VscanScannerPoolSchema
    _path = "/api/protocols/vscan/{svm[uuid]}/scanner-pools"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the Vscan scanner-pool configuration of an SVM.
### Related ONTAP commands
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan scanner-pool servers show`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan scanner pool show")
        def vscan_scanner_pool_show(
            svm_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            privileged_users: Choices.define(_get_field_list("privileged_users"), cache_choices=True, inexact=True)=None,
            role: Choices.define(_get_field_list("role"), cache_choices=True, inexact=True)=None,
            servers: Choices.define(_get_field_list("servers"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "privileged_users", "role", "servers", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of VscanScannerPool resources

            Args:
                name: Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), \"_\", \"-\" and \".\".
                privileged_users: Specifies a list of privileged users. A valid form of privileged user-name is \"domain-name\\user-name\". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.
                role: Specifies the role of the scanner pool. The possible values are:   * primary   - Always active.   * secondary - Active only when none of the primary external virus-scanning servers are connected.   * idle      - Always inactive. 
                servers: Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if privileged_users is not None:
                kwargs["privileged_users"] = privileged_users
            if role is not None:
                kwargs["role"] = role
            if servers is not None:
                kwargs["servers"] = servers
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return VscanScannerPool.get_collection(
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
        """Returns a count of all VscanScannerPool resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["VscanScannerPool"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Vscan scanner-pool configuration of an SVM.<br/>
Important notes:
* Along with servers and privileged-users, the role of a scanner-pool can also be updated with the cluster on which a scanner-pool is allowed.
* If role is specified and cluster isn't, then role is applied to the local cluster.
### Related ONTAP commands
* `vserver vscan scanner-pool modify`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan scanner-pool privileged-users remove`
* `vserver vscan scanner-pool servers remove`
* `vserver vscan scanner-pool servers add`
### Learn more
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
        records: Iterable["VscanScannerPool"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["VscanScannerPool"], NetAppResponse]:
        r"""Creates a Vscan scanner-pool configuration for a specified SVM. You can create a scanner-pool with all fields specified or only mandatory fields specified.<br/>
Important notes:
* A scanner-pool must have servers and privileged users specified.
* If the role or cluster is not specified, the scanner-pool is created on the local cluster with the role set as primary.
*`Only one of the fields cluster-uuid or cluster-name is required.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Vscan configuration.
* `name` - Scanner-pool name.
* `privileged_users` - List of privileged users.
* `servers` - List of server IP addresses or FQDNs.
### Recommended optional properties
* `role` - Setting a role for a scanner-pool is recommended.
* `cluster` - Passing the cluster name or UUID (or both) in a multi-cluster environment is recommended.
### Default property values
If not specified in POST, the following default property values are assigned:
* `role` - _primary_
* `cluster.name` - Local cluster name.
* `cluster.uuid` - Local cluster UUID.
### Related ONTAP commands
* `vserver vscan scanner-pool create`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan scanner-pool servers add`
### Learn more
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
        records: Iterable["VscanScannerPool"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Vscan scanner-pool configuration.<br/>
Important notes:
* The Vscan scanner-pool DELETE endpoint deletes all of the Vscan scanner-pools for a specified SVM.
* If a Vscan is enabled, it requires at least one scanner-pool to be in the active state. Therefore, disable Vscan on the specified SVM so all the scanner-pools configured on that SVM can be deleted.
### Related ONTAP commands
* `vserver vscan scanner-pool delete`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the Vscan scanner-pool configuration of an SVM.
### Related ONTAP commands
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan scanner-pool servers show`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the configuration of a specified scanner-pool of an SVM.
### Related ONTAP commands
* `vserver vscan scanner-pool show`
* `vserver vscan scanner-pool privileged-users show`
* `vserver vscan scanner-pool servers show`
### Learn more
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
        r"""Creates a Vscan scanner-pool configuration for a specified SVM. You can create a scanner-pool with all fields specified or only mandatory fields specified.<br/>
Important notes:
* A scanner-pool must have servers and privileged users specified.
* If the role or cluster is not specified, the scanner-pool is created on the local cluster with the role set as primary.
*`Only one of the fields cluster-uuid or cluster-name is required.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the Vscan configuration.
* `name` - Scanner-pool name.
* `privileged_users` - List of privileged users.
* `servers` - List of server IP addresses or FQDNs.
### Recommended optional properties
* `role` - Setting a role for a scanner-pool is recommended.
* `cluster` - Passing the cluster name or UUID (or both) in a multi-cluster environment is recommended.
### Default property values
If not specified in POST, the following default property values are assigned:
* `role` - _primary_
* `cluster.name` - Local cluster name.
* `cluster.uuid` - Local cluster UUID.
### Related ONTAP commands
* `vserver vscan scanner-pool create`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan scanner-pool servers add`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan scanner pool create")
        async def vscan_scanner_pool_create(
            svm_uuid,
            cluster: dict = None,
            name: str = None,
            privileged_users = None,
            role: str = None,
            servers = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a VscanScannerPool resource

            Args:
                cluster: 
                name: Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), \"_\", \"-\" and \".\".
                privileged_users: Specifies a list of privileged users. A valid form of privileged user-name is \"domain-name\\user-name\". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.
                role: Specifies the role of the scanner pool. The possible values are:   * primary   - Always active.   * secondary - Active only when none of the primary external virus-scanning servers are connected.   * idle      - Always inactive. 
                servers: Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.
                svm: 
            """

            kwargs = {}
            if cluster is not None:
                kwargs["cluster"] = cluster
            if name is not None:
                kwargs["name"] = name
            if privileged_users is not None:
                kwargs["privileged_users"] = privileged_users
            if role is not None:
                kwargs["role"] = role
            if servers is not None:
                kwargs["servers"] = servers
            if svm is not None:
                kwargs["svm"] = svm

            resource = VscanScannerPool(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create VscanScannerPool: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Vscan scanner-pool configuration of an SVM.<br/>
Important notes:
* Along with servers and privileged-users, the role of a scanner-pool can also be updated with the cluster on which a scanner-pool is allowed.
* If role is specified and cluster isn't, then role is applied to the local cluster.
### Related ONTAP commands
* `vserver vscan scanner-pool modify`
* `vserver vscan scanner-pool apply-policy`
* `vserver vscan scanner-pool privileged-users add`
* `vserver vscan scanner-pool privileged-users remove`
* `vserver vscan scanner-pool servers remove`
* `vserver vscan scanner-pool servers add`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan scanner pool modify")
        async def vscan_scanner_pool_modify(
            svm_uuid,
            name: str = None,
            query_name: str = None,
            privileged_users=None,
            query_privileged_users=None,
            role: str = None,
            query_role: str = None,
            servers=None,
            query_servers=None,
        ) -> ResourceTable:
            """Modify an instance of a VscanScannerPool resource

            Args:
                name: Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), \"_\", \"-\" and \".\".
                query_name: Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), \"_\", \"-\" and \".\".
                privileged_users: Specifies a list of privileged users. A valid form of privileged user-name is \"domain-name\\user-name\". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.
                query_privileged_users: Specifies a list of privileged users. A valid form of privileged user-name is \"domain-name\\user-name\". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.
                role: Specifies the role of the scanner pool. The possible values are:   * primary   - Always active.   * secondary - Active only when none of the primary external virus-scanning servers are connected.   * idle      - Always inactive. 
                query_role: Specifies the role of the scanner pool. The possible values are:   * primary   - Always active.   * secondary - Active only when none of the primary external virus-scanning servers are connected.   * idle      - Always inactive. 
                servers: Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.
                query_servers: Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_privileged_users is not None:
                kwargs["privileged_users"] = query_privileged_users
            if query_role is not None:
                kwargs["role"] = query_role
            if query_servers is not None:
                kwargs["servers"] = query_servers

            if name is not None:
                changes["name"] = name
            if privileged_users is not None:
                changes["privileged_users"] = privileged_users
            if role is not None:
                changes["role"] = role
            if servers is not None:
                changes["servers"] = servers

            if hasattr(VscanScannerPool, "find"):
                resource = VscanScannerPool.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = VscanScannerPool(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify VscanScannerPool: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Vscan scanner-pool configuration.<br/>
Important notes:
* The Vscan scanner-pool DELETE endpoint deletes all of the Vscan scanner-pools for a specified SVM.
* If a Vscan is enabled, it requires at least one scanner-pool to be in the active state. Therefore, disable Vscan on the specified SVM so all the scanner-pools configured on that SVM can be deleted.
### Related ONTAP commands
* `vserver vscan scanner-pool delete`
### Learn more
* [`DOC /protocols/vscan/{svm.uuid}/scanner-pools`](#docs-NAS-protocols_vscan_{svm.uuid}_scanner-pools)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vscan scanner pool delete")
        async def vscan_scanner_pool_delete(
            svm_uuid,
            name: str = None,
            privileged_users=None,
            role: str = None,
            servers=None,
        ) -> None:
            """Delete an instance of a VscanScannerPool resource

            Args:
                name: Specifies the name of the scanner pool. Scanner pool name can be up to 256 characters long and is a string that can only contain any combination of ASCII-range alphanumeric characters a-z, A-Z, 0-9), \"_\", \"-\" and \".\".
                privileged_users: Specifies a list of privileged users. A valid form of privileged user-name is \"domain-name\\user-name\". Privileged user-names are stored and treated as case-insensitive strings. Virus scanners must use one of the registered privileged users for connecting to clustered Data ONTAP for exchanging virus-scanning protocol messages and to access file for scanning, remedying and quarantining operations.
                role: Specifies the role of the scanner pool. The possible values are:   * primary   - Always active.   * secondary - Active only when none of the primary external virus-scanning servers are connected.   * idle      - Always inactive. 
                servers: Specifies a list of IP addresses or FQDN for each Vscan server host names which are allowed to connect to clustered ONTAP.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if privileged_users is not None:
                kwargs["privileged_users"] = privileged_users
            if role is not None:
                kwargs["role"] = role
            if servers is not None:
                kwargs["servers"] = servers

            if hasattr(VscanScannerPool, "find"):
                resource = VscanScannerPool.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = VscanScannerPool(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete VscanScannerPool: %s" % err)


