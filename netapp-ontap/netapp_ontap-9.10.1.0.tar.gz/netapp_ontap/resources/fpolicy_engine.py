r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The FPolicy engine allows you to configure the external servers to which the file access notifications are sent. As part of FPolicy engine configuration, you can configure the server(s) to which the notification is sent, an optional set of secondary server(s) to which the notification is sent in the case of the primary server(s) failure, the port number for FPolicy application and the type of the engine, synchronous or asynchronous. </br>
For the synchronous engine, ONTAP will wait for a response from the FPolicy application before it allows the operation. With an asynchronous engine, ONTAP proceeds with the operation processing after sending the notification to the FPolicy application. An engine can belong to multiple FPolicy policies.
## Examples
### Creating an FPolicy engine
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEngine("4f643fb4-fd21-11e8-ae49-0050568e2c1e")
    resource.name = "engine0"
    resource.port = 9876
    resource.primary_servers = ["10.132.145.22", "10.140.101.109"]
    resource.secondary_servers = ["10.132.145.20", "10.132.145.21"]
    resource.type = "synchronous"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
FpolicyEngine(
    {
        "type": "synchronous",
        "port": 9876,
        "primary_servers": ["10.132.145.22", "10.140.101.109"],
        "secondary_servers": ["10.132.145.20", "10.132.145.21"],
        "name": "engine0",
    }
)

```
</div>
</div>

---
### Creating an FPolicy engine with the minimum required fields
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEngine("4f643fb4-fd21-11e8-ae49-0050568e2c1e")
    resource.name = "engine0"
    resource.port = 9876
    resource.primary_servers = ["10.132.145.22", "10.140.101.109"]
    resource.type = "synchronous"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
FpolicyEngine(
    {
        "type": "synchronous",
        "port": 9876,
        "primary_servers": ["10.132.145.22", "10.140.101.109"],
        "name": "engine0",
    }
)

```
</div>
</div>

---
### Retrieving an FPolicy engine configuration for a particular SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyEngine.get_collection(
                "4f643fb4-fd21-11e8-ae49-0050568e2c1e", fields="*", return_timeout=15
            )
        )
    )

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    FpolicyEngine(
        {
            "type": "synchronous",
            "port": 9876,
            "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
            "primary_servers": ["10.20.20.10"],
            "name": "cifs",
        }
    ),
    FpolicyEngine(
        {
            "type": "synchronous",
            "port": 9876,
            "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
            "primary_servers": ["10.23.140.64", "10.140.101.109"],
            "secondary_servers": ["10.132.145.20", "10.132.145.22"],
            "name": "nfs",
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific FPolicy engine configuration for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEngine("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="cifs")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
FpolicyEngine(
    {
        "type": "synchronous",
        "port": 9876,
        "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
        "primary_servers": ["10.20.20.10"],
        "name": "cifs",
    }
)

```
</div>
</div>

---
### Updating an FPolicy engine for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEngine("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="cifs")
    resource.port = 6666
    resource.secondary_servers = ["10.132.145.20", "10.132.145.21"]
    resource.type = "synchronous"
    resource.patch()

```

---
### Updating all the attributes of a specific FPolicy engine for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEngine

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEngine("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="cifs")
    resource.port = 9876
    resource.primary_servers = ["10.132.145.20", "10.140.101.109"]
    resource.secondary_servers = ["10.132.145.23", "10.132.145.21"]
    resource.type = "synchronous"
    resource.patch()

```

---
### Deleting a specific FPolicy engine for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="cifs")
    resource.delete()

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


__all__ = ["FpolicyEngine", "FpolicyEngineSchema"]
__pdoc__ = {
    "FpolicyEngineSchema.resource": False,
    "FpolicyEngine.fpolicy_engine_show": False,
    "FpolicyEngine.fpolicy_engine_create": False,
    "FpolicyEngine.fpolicy_engine_modify": False,
    "FpolicyEngine.fpolicy_engine_delete": False,
}


class FpolicyEngineSchema(ResourceSchema):
    """The fields of the FpolicyEngine object"""

    name = fields.Str(
        data_key="name",
    )
    r""" Specifies the name to assign to the external server configuration.

Example: fp_ex_eng """

    port = Size(
        data_key="port",
    )
    r""" Port number of the FPolicy server application.

Example: 9876 """

    primary_servers = fields.List(fields.Str, data_key="primary_servers")
    r""" The primary_servers field of the fpolicy_engine.

Example: ["10.132.145.20","10.140.101.109"] """

    secondary_servers = fields.List(fields.Str, data_key="secondary_servers")
    r""" The secondary_servers field of the fpolicy_engine.

Example: ["10.132.145.20","10.132.145.21"] """

    svm = fields.Nested("netapp_ontap.models.fpolicy_engine_svm.FpolicyEngineSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fpolicy_engine. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['synchronous', 'asynchronous']),
    )
    r""" The notification mode determines what ONTAP does after sending notifications to FPolicy servers.
  The possible values are:

    * synchronous  - After sending a notification, wait for a response from the FPolicy server.
    * asynchronous - After sending a notification, file request processing continues.


Valid choices:

* synchronous
* asynchronous """

    @property
    def resource(self):
        return FpolicyEngine

    gettable_fields = [
        "name",
        "port",
        "primary_servers",
        "secondary_servers",
        "svm",
        "type",
    ]
    """name,port,primary_servers,secondary_servers,svm,type,"""

    patchable_fields = [
        "port",
        "primary_servers",
        "secondary_servers",
        "svm",
        "type",
    ]
    """port,primary_servers,secondary_servers,svm,type,"""

    postable_fields = [
        "name",
        "port",
        "primary_servers",
        "secondary_servers",
        "svm",
        "type",
    ]
    """name,port,primary_servers,secondary_servers,svm,type,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FpolicyEngine.get_collection(fields=field)]
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
            raise NetAppRestError("FpolicyEngine modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FpolicyEngine(Resource):
    r""" The engine defines how ONTAP makes and manages connections to external FPolicy servers. """

    _schema = FpolicyEngineSchema
    _path = "/api/protocols/fpolicy/{svm[uuid]}/engines"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FPolicy engine configurations of all the engines for a specified SVM. ONTAP allows creation of cluster-level FPolicy engines that act as a template for all the SVMs belonging to the cluster. These cluster-level FPolicy engines are also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy external-engine show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy engine show")
        def fpolicy_engine_show(
            svm_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            port: Choices.define(_get_field_list("port"), cache_choices=True, inexact=True)=None,
            primary_servers: Choices.define(_get_field_list("primary_servers"), cache_choices=True, inexact=True)=None,
            secondary_servers: Choices.define(_get_field_list("secondary_servers"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "port", "primary_servers", "secondary_servers", "type", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FpolicyEngine resources

            Args:
                name: Specifies the name to assign to the external server configuration.
                port: Port number of the FPolicy server application.
                primary_servers: 
                secondary_servers: 
                type: The notification mode determines what ONTAP does after sending notifications to FPolicy servers.   The possible values are:     * synchronous  - After sending a notification, wait for a response from the FPolicy server.     * asynchronous - After sending a notification, file request processing continues. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if primary_servers is not None:
                kwargs["primary_servers"] = primary_servers
            if secondary_servers is not None:
                kwargs["secondary_servers"] = secondary_servers
            if type is not None:
                kwargs["type"] = type
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FpolicyEngine.get_collection(
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
        """Returns a count of all FpolicyEngine resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FpolicyEngine"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific FPolicy engine configuration of an SVM. Modification of an FPolicy engine that is attached to one or more enabled FPolicy policies is not allowed.
### Related ONTAP commands
* `fpolicy policy external-engine modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FpolicyEngine"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FpolicyEngine"], NetAppResponse]:
        r"""Creates an FPolicy engine configuration for a specified SVM. FPolicy engine creation is allowed only on data SVMs.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy engine.
* `name` - Name of external engine.
* `port` - Port number of the FPolicy server application.
* `primary_servers` - List of primary FPolicy servers to which the node will send notifications.
### Recommended optional properties
* `secondary_servers` - It is recommended to configure secondary FPolicy server to which the node will send notifications when the primary server is down.
### Default property values
* `type` - _synchronous_
### Related ONTAP commands
* `fpolicy policy external-engine create`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
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
        records: Iterable["FpolicyEngine"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the FPolicy external engine configuration. Deletion of an FPolicy engine that is attached to one or more FPolicy policies is not allowed.
### Related ONTAP commands
* `fpolicy policy external-engine modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FPolicy engine configurations of all the engines for a specified SVM. ONTAP allows creation of cluster-level FPolicy engines that act as a template for all the SVMs belonging to the cluster. These cluster-level FPolicy engines are also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy external-engine show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a particular FPolicy engine configuration of a specifed SVM. A cluster-level FPolicy engine configuration cannot be retrieved for a data SVM.
### Related ONTAP commands
* `fpolicy policy external-engine show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
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
        r"""Creates an FPolicy engine configuration for a specified SVM. FPolicy engine creation is allowed only on data SVMs.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy engine.
* `name` - Name of external engine.
* `port` - Port number of the FPolicy server application.
* `primary_servers` - List of primary FPolicy servers to which the node will send notifications.
### Recommended optional properties
* `secondary_servers` - It is recommended to configure secondary FPolicy server to which the node will send notifications when the primary server is down.
### Default property values
* `type` - _synchronous_
### Related ONTAP commands
* `fpolicy policy external-engine create`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy engine create")
        async def fpolicy_engine_create(
            svm_uuid,
            name: str = None,
            port: Size = None,
            primary_servers = None,
            secondary_servers = None,
            svm: dict = None,
            type: str = None,
        ) -> ResourceTable:
            """Create an instance of a FpolicyEngine resource

            Args:
                name: Specifies the name to assign to the external server configuration.
                port: Port number of the FPolicy server application.
                primary_servers: 
                secondary_servers: 
                svm: 
                type: The notification mode determines what ONTAP does after sending notifications to FPolicy servers.   The possible values are:     * synchronous  - After sending a notification, wait for a response from the FPolicy server.     * asynchronous - After sending a notification, file request processing continues. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if primary_servers is not None:
                kwargs["primary_servers"] = primary_servers
            if secondary_servers is not None:
                kwargs["secondary_servers"] = secondary_servers
            if svm is not None:
                kwargs["svm"] = svm
            if type is not None:
                kwargs["type"] = type

            resource = FpolicyEngine(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FpolicyEngine: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific FPolicy engine configuration of an SVM. Modification of an FPolicy engine that is attached to one or more enabled FPolicy policies is not allowed.
### Related ONTAP commands
* `fpolicy policy external-engine modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy engine modify")
        async def fpolicy_engine_modify(
            svm_uuid,
            name: str = None,
            query_name: str = None,
            port: Size = None,
            query_port: Size = None,
            primary_servers=None,
            query_primary_servers=None,
            secondary_servers=None,
            query_secondary_servers=None,
            type: str = None,
            query_type: str = None,
        ) -> ResourceTable:
            """Modify an instance of a FpolicyEngine resource

            Args:
                name: Specifies the name to assign to the external server configuration.
                query_name: Specifies the name to assign to the external server configuration.
                port: Port number of the FPolicy server application.
                query_port: Port number of the FPolicy server application.
                primary_servers: 
                query_primary_servers: 
                secondary_servers: 
                query_secondary_servers: 
                type: The notification mode determines what ONTAP does after sending notifications to FPolicy servers.   The possible values are:     * synchronous  - After sending a notification, wait for a response from the FPolicy server.     * asynchronous - After sending a notification, file request processing continues. 
                query_type: The notification mode determines what ONTAP does after sending notifications to FPolicy servers.   The possible values are:     * synchronous  - After sending a notification, wait for a response from the FPolicy server.     * asynchronous - After sending a notification, file request processing continues. 
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_port is not None:
                kwargs["port"] = query_port
            if query_primary_servers is not None:
                kwargs["primary_servers"] = query_primary_servers
            if query_secondary_servers is not None:
                kwargs["secondary_servers"] = query_secondary_servers
            if query_type is not None:
                kwargs["type"] = query_type

            if name is not None:
                changes["name"] = name
            if port is not None:
                changes["port"] = port
            if primary_servers is not None:
                changes["primary_servers"] = primary_servers
            if secondary_servers is not None:
                changes["secondary_servers"] = secondary_servers
            if type is not None:
                changes["type"] = type

            if hasattr(FpolicyEngine, "find"):
                resource = FpolicyEngine.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyEngine(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FpolicyEngine: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the FPolicy external engine configuration. Deletion of an FPolicy engine that is attached to one or more FPolicy policies is not allowed.
### Related ONTAP commands
* `fpolicy policy external-engine modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/engines`](#docs-NAS-protocols_fpolicy_{svm.uuid}_engines)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy engine delete")
        async def fpolicy_engine_delete(
            svm_uuid,
            name: str = None,
            port: Size = None,
            primary_servers=None,
            secondary_servers=None,
            type: str = None,
        ) -> None:
            """Delete an instance of a FpolicyEngine resource

            Args:
                name: Specifies the name to assign to the external server configuration.
                port: Port number of the FPolicy server application.
                primary_servers: 
                secondary_servers: 
                type: The notification mode determines what ONTAP does after sending notifications to FPolicy servers.   The possible values are:     * synchronous  - After sending a notification, wait for a response from the FPolicy server.     * asynchronous - After sending a notification, file request processing continues. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if primary_servers is not None:
                kwargs["primary_servers"] = primary_servers
            if secondary_servers is not None:
                kwargs["secondary_servers"] = secondary_servers
            if type is not None:
                kwargs["type"] = type

            if hasattr(FpolicyEngine, "find"):
                resource = FpolicyEngine.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyEngine(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FpolicyEngine: %s" % err)


