r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
FPolicy events configurations allow you to specify which file access is monitored. As part of an FPolicy event, you can configure the SVM for which the events are generated, the name of the event configuration, the protocol (cifs, nfsv3/nfsv4) for which the events are generated, the file operations which are monitored, and filters that can be used to filter the unwanted notification generation for a specified protocol and file operation.</br>
Each protocol has a set of supported file operations and filters. An SVM can have multiple events. A single FPolicy policy can have multiple FPolicy events.
## Examples
### Creating an FPolicy event for a CIFS protocol with all the supported file operations and filters
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e")
    resource.file_operations = {
        "close": True,
        "create": True,
        "create_dir": True,
        "delete": True,
        "delete_dir": True,
        "getattr": True,
        "open": True,
        "read": True,
        "rename": True,
        "rename_dir": True,
        "setattr": True,
        "write": True,
    }
    resource.filters = {
        "close_with_modification": True,
        "close_with_read": True,
        "close_without_modification": True,
        "first_read": True,
        "first_write": True,
        "monitor_ads": True,
        "offline_bit": True,
        "open_with_delete_intent": True,
        "open_with_write_intent": True,
        "write_with_size_change": True,
    }
    resource.name = "event_cifs"
    resource.protocol = "cifs"
    resource.volume_monitoring = True
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
FpolicyEvent(
    {
        "filters": {
            "offline_bit": True,
            "close_without_modification": True,
            "close_with_modification": True,
            "first_read": True,
            "open_with_write_intent": True,
            "close_with_read": True,
            "open_with_delete_intent": True,
            "first_write": True,
            "write_with_size_change": True,
            "monitor_ads": True,
        },
        "volume_monitoring": True,
        "protocol": "cifs",
        "file_operations": {
            "delete": True,
            "create_dir": True,
            "getattr": True,
            "close": True,
            "delete_dir": True,
            "rename": True,
            "create": True,
            "rename_dir": True,
            "setattr": True,
            "open": True,
            "write": True,
            "read": True,
        },
        "name": "event_cifs",
    }
)

```
</div>
</div>

---
### Creating an FPolicy event for an NFS protocol with all the supported file operations and filters
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e")
    resource.file_operations = {
        "create": True,
        "create_dir": True,
        "delete": True,
        "delete_dir": True,
        "link": True,
        "lookup": True,
        "read": True,
        "rename": True,
        "rename_dir": True,
        "setattr": True,
        "symlink": True,
        "write": True,
    }
    resource.filters = {"offline_bit": True, "write_with_size_change": True}
    resource.name = "event_nfsv3"
    resource.protocol = "nfsv3"
    resource.volume_monitoring = False
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
FpolicyEvent(
    {
        "filters": {"offline_bit": True, "write_with_size_change": True},
        "volume_monitoring": False,
        "protocol": "nfsv3",
        "file_operations": {
            "link": True,
            "delete": True,
            "create_dir": True,
            "lookup": True,
            "delete_dir": True,
            "rename": True,
            "create": True,
            "rename_dir": True,
            "setattr": True,
            "symlink": True,
            "write": True,
            "read": True,
        },
        "name": "event_nfsv3",
    }
)

```
</div>
</div>

---
### Retrieving all of the FPolicy event configurations for a specified SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            FpolicyEvent.get_collection(
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
    FpolicyEvent(
        {
            "filters": {
                "setattr_with_modify_time_change": False,
                "setattr_with_sacl_change": False,
                "setattr_with_creation_time_change": False,
                "setattr_with_dacl_change": False,
                "setattr_with_size_change": False,
                "offline_bit": False,
                "setattr_with_access_time_change": False,
                "setattr_with_mode_change": False,
                "close_without_modification": False,
                "close_with_modification": False,
                "exclude_directory": False,
                "first_read": False,
                "open_with_write_intent": False,
                "close_with_read": True,
                "open_with_delete_intent": False,
                "setattr_with_allocation_size_change": False,
                "first_write": False,
                "setattr_with_group_change": False,
                "write_with_size_change": False,
                "setattr_with_owner_change": False,
                "monitor_ads": False,
            },
            "volume_monitoring": False,
            "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
            "protocol": "cifs",
            "file_operations": {
                "link": False,
                "delete": False,
                "create_dir": False,
                "getattr": False,
                "lookup": False,
                "close": True,
                "delete_dir": False,
                "rename": False,
                "create": False,
                "rename_dir": False,
                "setattr": False,
                "symlink": False,
                "open": False,
                "write": False,
                "read": False,
            },
            "name": "cluster",
        }
    ),
    FpolicyEvent(
        {
            "filters": {
                "setattr_with_modify_time_change": False,
                "setattr_with_sacl_change": False,
                "setattr_with_creation_time_change": False,
                "setattr_with_dacl_change": False,
                "setattr_with_size_change": False,
                "offline_bit": True,
                "setattr_with_access_time_change": False,
                "setattr_with_mode_change": False,
                "close_without_modification": True,
                "close_with_modification": True,
                "exclude_directory": False,
                "first_read": True,
                "open_with_write_intent": True,
                "close_with_read": True,
                "open_with_delete_intent": True,
                "setattr_with_allocation_size_change": False,
                "first_write": True,
                "setattr_with_group_change": False,
                "write_with_size_change": True,
                "setattr_with_owner_change": False,
                "monitor_ads": True,
            },
            "volume_monitoring": True,
            "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
            "protocol": "cifs",
            "file_operations": {
                "link": False,
                "delete": True,
                "create_dir": True,
                "getattr": True,
                "lookup": False,
                "close": True,
                "delete_dir": True,
                "rename": True,
                "create": True,
                "rename_dir": True,
                "setattr": True,
                "symlink": False,
                "open": True,
                "write": True,
                "read": True,
            },
            "name": "event_cifs",
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific FPolicy event configuration for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="event_cifs")
    resource.get(fields="*", return_timeout=15)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
FpolicyEvent(
    {
        "filters": {
            "setattr_with_modify_time_change": False,
            "setattr_with_sacl_change": False,
            "setattr_with_creation_time_change": False,
            "setattr_with_dacl_change": False,
            "setattr_with_size_change": False,
            "offline_bit": True,
            "setattr_with_access_time_change": False,
            "setattr_with_mode_change": False,
            "close_without_modification": True,
            "close_with_modification": True,
            "exclude_directory": False,
            "first_read": True,
            "open_with_write_intent": True,
            "close_with_read": True,
            "open_with_delete_intent": True,
            "setattr_with_allocation_size_change": False,
            "first_write": True,
            "setattr_with_group_change": False,
            "write_with_size_change": True,
            "setattr_with_owner_change": False,
            "monitor_ads": True,
        },
        "volume_monitoring": True,
        "svm": {"uuid": "4f643fb4-fd21-11e8-ae49-0050568e2c1e"},
        "protocol": "cifs",
        "file_operations": {
            "link": False,
            "delete": True,
            "create_dir": True,
            "getattr": True,
            "lookup": False,
            "close": True,
            "delete_dir": True,
            "rename": True,
            "create": True,
            "rename_dir": True,
            "setattr": True,
            "symlink": False,
            "open": True,
            "write": True,
            "read": True,
        },
        "name": "event_cifs",
    }
)

```
</div>
</div>

---
### Updating a specific FPolicy event configuration for a specified SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="event_cifs")
    resource.file_operations = {"close": False, "create": False, "read": True}
    resource.filters = {
        "close_with_modification": False,
        "close_with_read": False,
        "close_without_modification": False,
    }
    resource.protocol = "cifs"
    resource.volume_monitoring = False
    resource.patch()

```

---
### Deleting a specific FPolicy event configuration for a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FpolicyEvent

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FpolicyEvent("4f643fb4-fd21-11e8-ae49-0050568e2c1e", name="event_cifs")
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


__all__ = ["FpolicyEvent", "FpolicyEventSchema"]
__pdoc__ = {
    "FpolicyEventSchema.resource": False,
    "FpolicyEvent.fpolicy_event_show": False,
    "FpolicyEvent.fpolicy_event_create": False,
    "FpolicyEvent.fpolicy_event_modify": False,
    "FpolicyEvent.fpolicy_event_delete": False,
}


class FpolicyEventSchema(ResourceSchema):
    """The fields of the FpolicyEvent object"""

    file_operations = fields.Nested("netapp_ontap.models.fpolicy_event_file_operations.FpolicyEventFileOperationsSchema", data_key="file_operations", unknown=EXCLUDE)
    r""" The file_operations field of the fpolicy_event. """

    filters = fields.Nested("netapp_ontap.models.fpolicy_event_filters.FpolicyEventFiltersSchema", data_key="filters", unknown=EXCLUDE)
    r""" The filters field of the fpolicy_event. """

    name = fields.Str(
        data_key="name",
    )
    r""" Specifies the name of the FPolicy event.

Example: event_nfs_close """

    protocol = fields.Str(
        data_key="protocol",
        validate=enum_validation(['cifs', 'nfsv3', 'nfsv4']),
    )
    r""" Protocol for which event is created. If you specify protocol, then you
must also specify a valid value for the file operation parameters.
  The value of this parameter must be one of the following:

    * cifs  - for the CIFS protocol.
    * nfsv3 - for the NFSv3 protocol.
    * nfsv4 - for the NFSv4 protocol.


Valid choices:

* cifs
* nfsv3
* nfsv4 """

    svm = fields.Nested("netapp_ontap.models.fpolicy_engine_svm.FpolicyEngineSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the fpolicy_event. """

    volume_monitoring = fields.Boolean(
        data_key="volume_monitoring",
    )
    r""" Specifies whether volume operation monitoring is required. """

    @property
    def resource(self):
        return FpolicyEvent

    gettable_fields = [
        "file_operations",
        "filters",
        "name",
        "protocol",
        "svm",
        "volume_monitoring",
    ]
    """file_operations,filters,name,protocol,svm,volume_monitoring,"""

    patchable_fields = [
        "file_operations",
        "filters",
        "protocol",
        "svm",
        "volume_monitoring",
    ]
    """file_operations,filters,protocol,svm,volume_monitoring,"""

    postable_fields = [
        "file_operations",
        "filters",
        "name",
        "protocol",
        "svm",
        "volume_monitoring",
    ]
    """file_operations,filters,name,protocol,svm,volume_monitoring,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FpolicyEvent.get_collection(fields=field)]
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
            raise NetAppRestError("FpolicyEvent modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FpolicyEvent(Resource):
    r""" The information that a FPolicy process needs to determine what file access operations to monitor and for which of the monitored events notifications should be sent to the external FPolicy server. """

    _schema = FpolicyEventSchema
    _path = "/api/protocols/fpolicy/{svm[uuid]}/events"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FPolicy event configurations for all events for a specified SVM. ONTAP allows the creation of cluster-level FPolicy events that act as a template for all the data SVMs belonging to the cluster. These cluster-level FPolicy events are also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy event show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy event show")
        def fpolicy_event_show(
            svm_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            protocol: Choices.define(_get_field_list("protocol"), cache_choices=True, inexact=True)=None,
            volume_monitoring: Choices.define(_get_field_list("volume_monitoring"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "protocol", "volume_monitoring", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FpolicyEvent resources

            Args:
                name: Specifies the name of the FPolicy event.
                protocol: Protocol for which event is created. If you specify protocol, then you must also specify a valid value for the file operation parameters.   The value of this parameter must be one of the following:     * cifs  - for the CIFS protocol.     * nfsv3 - for the NFSv3 protocol.     * nfsv4 - for the NFSv4 protocol. 
                volume_monitoring: Specifies whether volume operation monitoring is required.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if volume_monitoring is not None:
                kwargs["volume_monitoring"] = volume_monitoring
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FpolicyEvent.get_collection(
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
        """Returns a count of all FpolicyEvent resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FpolicyEvent"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific FPolicy event configuration for an SVM. A cluster-level FPolicy event configuration cannot be modified for a data SVM through REST. When the file operations and filters fields are modified, the previous values are retained and new values are added to the list of previous values. To remove a particular file operation or filter, set its value to false in the request.
### Related ONTAP commands
* `fpolicy policy event modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["FpolicyEvent"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["FpolicyEvent"], NetAppResponse]:
        r"""Creates an FPolicy event configuration for a specified SVM. FPolicy event creation is allowed only on data SVMs. When a protocol is specified, you must specify a file operation or a file operation and filters.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy event.
* `name` - Name of the FPolicy event.
### Recommended optional properties
* `file-operations` - List of file operations to monitor.
* `protocol` - Protocol for which the file operations should be monitored.
* `filters` - List of filters for the specified file operations.
### Default property values
If not specified in POST, the following default property values are assigned:
* `file_operations.*` - _false_
* `filters.*` - _false_
* `volume-monitoring` - _false_
### Related ONTAP commands
* `fpolicy policy event create`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
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
        records: Iterable["FpolicyEvent"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific FPolicy event configuration for an SVM. A cluster-level FPolicy event configuration cannot be modified for a data SVM through REST. An FPolicy event that is attached to an FPolicy policy cannot be deleted.
### Related ONTAP commands
* `fpolicy policy event delete`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FPolicy event configurations for all events for a specified SVM. ONTAP allows the creation of cluster-level FPolicy events that act as a template for all the data SVMs belonging to the cluster. These cluster-level FPolicy events are also retrieved for the specified SVM.
### Related ONTAP commands
* `fpolicy policy event show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific FPolicy event configuration for an SVM. A cluster-level FPolicy event configuration cannot be retrieved for a data SVM through a REST API.
### Related ONTAP commands
* `fpolicy policy event show`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
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
        r"""Creates an FPolicy event configuration for a specified SVM. FPolicy event creation is allowed only on data SVMs. When a protocol is specified, you must specify a file operation or a file operation and filters.
### Required properties
* `svm.uuid` - Existing SVM in which to create the FPolicy event.
* `name` - Name of the FPolicy event.
### Recommended optional properties
* `file-operations` - List of file operations to monitor.
* `protocol` - Protocol for which the file operations should be monitored.
* `filters` - List of filters for the specified file operations.
### Default property values
If not specified in POST, the following default property values are assigned:
* `file_operations.*` - _false_
* `filters.*` - _false_
* `volume-monitoring` - _false_
### Related ONTAP commands
* `fpolicy policy event create`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy event create")
        async def fpolicy_event_create(
            svm_uuid,
            file_operations: dict = None,
            filters: dict = None,
            name: str = None,
            protocol: str = None,
            svm: dict = None,
            volume_monitoring: bool = None,
        ) -> ResourceTable:
            """Create an instance of a FpolicyEvent resource

            Args:
                file_operations: 
                filters: 
                name: Specifies the name of the FPolicy event.
                protocol: Protocol for which event is created. If you specify protocol, then you must also specify a valid value for the file operation parameters.   The value of this parameter must be one of the following:     * cifs  - for the CIFS protocol.     * nfsv3 - for the NFSv3 protocol.     * nfsv4 - for the NFSv4 protocol. 
                svm: 
                volume_monitoring: Specifies whether volume operation monitoring is required.
            """

            kwargs = {}
            if file_operations is not None:
                kwargs["file_operations"] = file_operations
            if filters is not None:
                kwargs["filters"] = filters
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if svm is not None:
                kwargs["svm"] = svm
            if volume_monitoring is not None:
                kwargs["volume_monitoring"] = volume_monitoring

            resource = FpolicyEvent(
                svm_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create FpolicyEvent: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific FPolicy event configuration for an SVM. A cluster-level FPolicy event configuration cannot be modified for a data SVM through REST. When the file operations and filters fields are modified, the previous values are retained and new values are added to the list of previous values. To remove a particular file operation or filter, set its value to false in the request.
### Related ONTAP commands
* `fpolicy policy event modify`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy event modify")
        async def fpolicy_event_modify(
            svm_uuid,
            name: str = None,
            query_name: str = None,
            protocol: str = None,
            query_protocol: str = None,
            volume_monitoring: bool = None,
            query_volume_monitoring: bool = None,
        ) -> ResourceTable:
            """Modify an instance of a FpolicyEvent resource

            Args:
                name: Specifies the name of the FPolicy event.
                query_name: Specifies the name of the FPolicy event.
                protocol: Protocol for which event is created. If you specify protocol, then you must also specify a valid value for the file operation parameters.   The value of this parameter must be one of the following:     * cifs  - for the CIFS protocol.     * nfsv3 - for the NFSv3 protocol.     * nfsv4 - for the NFSv4 protocol. 
                query_protocol: Protocol for which event is created. If you specify protocol, then you must also specify a valid value for the file operation parameters.   The value of this parameter must be one of the following:     * cifs  - for the CIFS protocol.     * nfsv3 - for the NFSv3 protocol.     * nfsv4 - for the NFSv4 protocol. 
                volume_monitoring: Specifies whether volume operation monitoring is required.
                query_volume_monitoring: Specifies whether volume operation monitoring is required.
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_protocol is not None:
                kwargs["protocol"] = query_protocol
            if query_volume_monitoring is not None:
                kwargs["volume_monitoring"] = query_volume_monitoring

            if name is not None:
                changes["name"] = name
            if protocol is not None:
                changes["protocol"] = protocol
            if volume_monitoring is not None:
                changes["volume_monitoring"] = volume_monitoring

            if hasattr(FpolicyEvent, "find"):
                resource = FpolicyEvent.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyEvent(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FpolicyEvent: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific FPolicy event configuration for an SVM. A cluster-level FPolicy event configuration cannot be modified for a data SVM through REST. An FPolicy event that is attached to an FPolicy policy cannot be deleted.
### Related ONTAP commands
* `fpolicy policy event delete`
### Learn more
* [`DOC /protocols/fpolicy/{svm.uuid}/events`](#docs-NAS-protocols_fpolicy_{svm.uuid}_events)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="fpolicy event delete")
        async def fpolicy_event_delete(
            svm_uuid,
            name: str = None,
            protocol: str = None,
            volume_monitoring: bool = None,
        ) -> None:
            """Delete an instance of a FpolicyEvent resource

            Args:
                name: Specifies the name of the FPolicy event.
                protocol: Protocol for which event is created. If you specify protocol, then you must also specify a valid value for the file operation parameters.   The value of this parameter must be one of the following:     * cifs  - for the CIFS protocol.     * nfsv3 - for the NFSv3 protocol.     * nfsv4 - for the NFSv4 protocol. 
                volume_monitoring: Specifies whether volume operation monitoring is required.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if volume_monitoring is not None:
                kwargs["volume_monitoring"] = volume_monitoring

            if hasattr(FpolicyEvent, "find"):
                resource = FpolicyEvent.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = FpolicyEvent(svm_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete FpolicyEvent: %s" % err)


