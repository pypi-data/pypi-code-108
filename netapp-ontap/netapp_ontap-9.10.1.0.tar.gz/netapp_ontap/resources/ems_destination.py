r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Manages a specific instance of a destination. There are limits to the information that you can modify after a destination is created. For example, you cannot change a destination's type, but you can modify the underlying details of the type.
####
Note: The system defines default destinations that cannot be removed or modified. These destinations are specified by setting the "system_defined" field to "true".
####
See the documentation for [/support/ems/destinations](#/docs/support/support_ems_destinations) for details on the various properties in a destination.
## Examples
### Retrieving a specific destination instance
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsDestination

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsDestination(name="snmp-traphost")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
EmsDestination(
    {
        "filters": [
            {
                "name": "default-trap-events",
                "_links": {
                    "self": {"href": "/api/support/ems/filters/default-trap-events"}
                },
            }
        ],
        "type": "snmp",
        "destination": "",
        "name": "snmp-traphost",
        "_links": {"self": {"href": "/api/support/ems/destinations/snmp-traphost"}},
    }
)

```
</div>
</div>

### Updating an existing destination (change of email address)
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsDestination

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsDestination()
    resource.destination = "support@mycompany.com"
    resource.post(hydrate=True)
    print(resource)

```

### Deleting an existing destination
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsDestination

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsDestination(name="test-destination")
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


__all__ = ["EmsDestination", "EmsDestinationSchema"]
__pdoc__ = {
    "EmsDestinationSchema.resource": False,
    "EmsDestination.ems_destination_show": False,
    "EmsDestination.ems_destination_create": False,
    "EmsDestination.ems_destination_modify": False,
    "EmsDestination.ems_destination_delete": False,
}


class EmsDestinationSchema(ResourceSchema):
    """The fields of the EmsDestination object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ems_destination. """

    certificate = fields.Nested("netapp_ontap.models.ems_destination_certificate.EmsDestinationCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the ems_destination. """

    destination = fields.Str(
        data_key="destination",
    )
    r""" Event destination

Example: administrator@mycompany.com """

    filters = fields.List(fields.Nested("netapp_ontap.resources.ems_filter.EmsFilterSchema", unknown=EXCLUDE), data_key="filters")
    r""" The filters field of the ems_destination. """

    name = fields.Str(
        data_key="name",
    )
    r""" Destination name.  Valid in POST.

Example: Admin_Email """

    system_defined = fields.Boolean(
        data_key="system_defined",
    )
    r""" Flag indicating system-defined destinations.

Example: true """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['snmp', 'email', 'syslog', 'rest_api']),
    )
    r""" Type of destination. Valid in POST.

Valid choices:

* snmp
* email
* syslog
* rest_api """

    @property
    def resource(self):
        return EmsDestination

    gettable_fields = [
        "links",
        "certificate",
        "destination",
        "filters.links",
        "filters.name",
        "name",
        "system_defined",
        "type",
    ]
    """links,certificate,destination,filters.links,filters.name,name,system_defined,type,"""

    patchable_fields = [
        "certificate",
        "destination",
        "filters.name",
    ]
    """certificate,destination,filters.name,"""

    postable_fields = [
        "certificate",
        "destination",
        "filters.name",
        "name",
        "type",
    ]
    """certificate,destination,filters.name,name,type,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EmsDestination.get_collection(fields=field)]
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
            raise NetAppRestError("EmsDestination modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EmsDestination(Resource):
    """Allows interaction with EmsDestination objects on the host"""

    _schema = EmsDestinationSchema
    _path = "/api/support/ems/destinations"
    _keys = ["name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of event destinations.
### Related ONTAP commands
* `event notification destination show`
* `event notification show`

### Learn more
* [`DOC /support/ems/destinations`](#docs-support-support_ems_destinations)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems destination show")
        def ems_destination_show(
            fields: List[Choices.define(["destination", "name", "system_defined", "type", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of EmsDestination resources

            Args:
                destination: Event destination
                name: Destination name.  Valid in POST.
                system_defined: Flag indicating system-defined destinations.
                type: Type of destination. Valid in POST.
            """

            kwargs = {}
            if destination is not None:
                kwargs["destination"] = destination
            if name is not None:
                kwargs["name"] = name
            if system_defined is not None:
                kwargs["system_defined"] = system_defined
            if type is not None:
                kwargs["type"] = type
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return EmsDestination.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all EmsDestination resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["EmsDestination"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event destination.
### Recommended optional properties
* `filters.name` - New list of filters that should direct to this destination. The existing list is discarded.
* `certificate` - New certificate parameters when the destination type is `rest api`.
### Related ONTAP commands
* `event notification destination modify`
* `event notification modify`

### Learn more
* [`DOC /support/ems/destinations/{name}`](#docs-support-support_ems_destinations_{name})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["EmsDestination"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["EmsDestination"], NetAppResponse]:
        r"""Creates an event destination.
### Required properties
* `name` - String that uniquely identifies the destination.
* `type` - Type of destination that is to be created.
* `destination` - String that identifies the destination. The contents of this property changes depending on type.
### Recommended optional properties
* `filters.name` - List of filter names that should direct to this destination.
* `certificate` - When specifying a rest api destination, a client certificate can be provided.
### Related ONTAP commands
* `event notification destination create`
* `event notification create`

### Learn more
* [`DOC /support/ems/destinations`](#docs-support-support_ems_destinations)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["EmsDestination"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event destination.
### Related ONTAP commands
* `event notification destination delete`
* `event notification delete`

### Learn more
* [`DOC /support/ems/destinations/{name}`](#docs-support-support_ems_destinations_{name})"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of event destinations.
### Related ONTAP commands
* `event notification destination show`
* `event notification show`

### Learn more
* [`DOC /support/ems/destinations`](#docs-support-support_ems_destinations)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves event destinations.
### Related ONTAP commands
* `event notification destination show`
* `event notification show`

### Learn more
* [`DOC /support/ems/destinations/{name}`](#docs-support-support_ems_destinations_{name})"""
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
        r"""Creates an event destination.
### Required properties
* `name` - String that uniquely identifies the destination.
* `type` - Type of destination that is to be created.
* `destination` - String that identifies the destination. The contents of this property changes depending on type.
### Recommended optional properties
* `filters.name` - List of filter names that should direct to this destination.
* `certificate` - When specifying a rest api destination, a client certificate can be provided.
### Related ONTAP commands
* `event notification destination create`
* `event notification create`

### Learn more
* [`DOC /support/ems/destinations`](#docs-support-support_ems_destinations)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems destination create")
        async def ems_destination_create(
        ) -> ResourceTable:
            """Create an instance of a EmsDestination resource

            Args:
                links: 
                certificate: 
                destination: Event destination
                filters: 
                name: Destination name.  Valid in POST.
                system_defined: Flag indicating system-defined destinations.
                type: Type of destination. Valid in POST.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if certificate is not None:
                kwargs["certificate"] = certificate
            if destination is not None:
                kwargs["destination"] = destination
            if filters is not None:
                kwargs["filters"] = filters
            if name is not None:
                kwargs["name"] = name
            if system_defined is not None:
                kwargs["system_defined"] = system_defined
            if type is not None:
                kwargs["type"] = type

            resource = EmsDestination(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create EmsDestination: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event destination.
### Recommended optional properties
* `filters.name` - New list of filters that should direct to this destination. The existing list is discarded.
* `certificate` - New certificate parameters when the destination type is `rest api`.
### Related ONTAP commands
* `event notification destination modify`
* `event notification modify`

### Learn more
* [`DOC /support/ems/destinations/{name}`](#docs-support-support_ems_destinations_{name})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems destination modify")
        async def ems_destination_modify(
        ) -> ResourceTable:
            """Modify an instance of a EmsDestination resource

            Args:
                destination: Event destination
                query_destination: Event destination
                name: Destination name.  Valid in POST.
                query_name: Destination name.  Valid in POST.
                system_defined: Flag indicating system-defined destinations.
                query_system_defined: Flag indicating system-defined destinations.
                type: Type of destination. Valid in POST.
                query_type: Type of destination. Valid in POST.
            """

            kwargs = {}
            changes = {}
            if query_destination is not None:
                kwargs["destination"] = query_destination
            if query_name is not None:
                kwargs["name"] = query_name
            if query_system_defined is not None:
                kwargs["system_defined"] = query_system_defined
            if query_type is not None:
                kwargs["type"] = query_type

            if destination is not None:
                changes["destination"] = destination
            if name is not None:
                changes["name"] = name
            if system_defined is not None:
                changes["system_defined"] = system_defined
            if type is not None:
                changes["type"] = type

            if hasattr(EmsDestination, "find"):
                resource = EmsDestination.find(
                    **kwargs
                )
            else:
                resource = EmsDestination()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify EmsDestination: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event destination.
### Related ONTAP commands
* `event notification destination delete`
* `event notification delete`

### Learn more
* [`DOC /support/ems/destinations/{name}`](#docs-support-support_ems_destinations_{name})"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems destination delete")
        async def ems_destination_delete(
        ) -> None:
            """Delete an instance of a EmsDestination resource

            Args:
                destination: Event destination
                name: Destination name.  Valid in POST.
                system_defined: Flag indicating system-defined destinations.
                type: Type of destination. Valid in POST.
            """

            kwargs = {}
            if destination is not None:
                kwargs["destination"] = destination
            if name is not None:
                kwargs["name"] = name
            if system_defined is not None:
                kwargs["system_defined"] = system_defined
            if type is not None:
                kwargs["type"] = type

            if hasattr(EmsDestination, "find"):
                resource = EmsDestination.find(
                    **kwargs
                )
            else:
                resource = EmsDestination()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete EmsDestination: %s" % err)


