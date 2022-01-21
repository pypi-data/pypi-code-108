r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Manages a specific filter instance.
See the documentation for [/support/ems/filters](#/docs/support/support_ems_filters) for details on the various properties.
## Examples
### Retrieving a specific filter instance
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilter

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilter(name="no-info-debug-events")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
EmsFilter(
    {
        "name": "no-info-debug-events",
        "_links": {"self": {"href": "/api/support/ems/filters/no-info-debug-events"}},
        "rules": [
            {
                "index": 1,
                "type": "include",
                "message_criteria": {
                    "severities": "emergency,alert,error,notice",
                    "name_pattern": "*",
                    "_links": {
                        "related": {
                            "href": "/api/support/ems/messages?name=*&severity=emergency,alert,error,notice&snmp_trap_type=*"
                        }
                    },
                    "snmp_trap_types": "*",
                },
                "_links": {
                    "self": {
                        "href": "/api/support/ems/filters/no-info-debug-events/rules/1"
                    }
                },
            },
            {
                "index": 2,
                "type": "exclude",
                "message_criteria": {
                    "severities": "*",
                    "name_pattern": "*",
                    "_links": {
                        "related": {
                            "href": "/api/support/ems/messages?name=*&severity=*&snmp_trap_type=*"
                        }
                    },
                    "snmp_trap_types": "*",
                },
                "_links": {
                    "self": {
                        "href": "/api/support/ems/filters/no-info-debug-events/rules/2"
                    }
                },
            },
        ],
    }
)

```
</div>
</div>

### Updating an existing filter with a new rule
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilter

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilter(name="test-filter")
    resource.rules = [
        {
            "type": "include",
            "message_criteria": {"name_pattern": "wafl.*", "severities": "error"},
        }
    ]
    resource.patch()

```

### Deleting an existing filter
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilter

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilter(name="test-filter")
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


__all__ = ["EmsFilter", "EmsFilterSchema"]
__pdoc__ = {
    "EmsFilterSchema.resource": False,
    "EmsFilter.ems_filter_show": False,
    "EmsFilter.ems_filter_create": False,
    "EmsFilter.ems_filter_modify": False,
    "EmsFilter.ems_filter_delete": False,
}


class EmsFilterSchema(ResourceSchema):
    """The fields of the EmsFilter object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ems_filter. """

    name = fields.Str(
        data_key="name",
    )
    r""" Filter name

Example: snmp-traphost """

    rules = fields.List(fields.Nested("netapp_ontap.resources.ems_filter_rule.EmsFilterRuleSchema", unknown=EXCLUDE), data_key="rules")
    r""" Array of event filter rules on which to match. """

    system_defined = fields.Boolean(
        data_key="system_defined",
    )
    r""" Flag indicating system-defined filters.

Example: true """

    @property
    def resource(self):
        return EmsFilter

    gettable_fields = [
        "links",
        "name",
        "rules",
        "system_defined",
    ]
    """links,name,rules,system_defined,"""

    patchable_fields = [
        "name",
        "rules",
    ]
    """name,rules,"""

    postable_fields = [
        "name",
        "rules",
    ]
    """name,rules,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EmsFilter.get_collection(fields=field)]
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
            raise NetAppRestError("EmsFilter modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EmsFilter(Resource):
    """Allows interaction with EmsFilter objects on the host"""

    _schema = EmsFilterSchema
    _path = "/api/support/ems/filters"
    _keys = ["name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of event filters.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters`](#docs-support-support_ems_filters)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter show")
        def ems_filter_show(
            fields: List[Choices.define(["name", "system_defined", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of EmsFilter resources

            Args:
                name: Filter name
                system_defined: Flag indicating system-defined filters.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if system_defined is not None:
                kwargs["system_defined"] = system_defined
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return EmsFilter.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all EmsFilter resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["EmsFilter"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event filter.
### Recommended optional properties
* `new_name` - New string that uniquely identifies a filter.
* `rules` - New list of criteria used to match the filter with an event. The existing list is discarded.
### Related ONTAP commands
* `event filter rename`
* `event filter rule add`
* `event filter rule delete`
* `event filter rule reorder`

### Learn more
* [`DOC /support/ems/filters/{name}`](#docs-support-support_ems_filters_{name})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["EmsFilter"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["EmsFilter"], NetAppResponse]:
        r"""Creates an event filter.
### Required properties
* `name` - String that uniquely identifies the filter.
### Recommended optional properties
* `rules` - List of criteria which is used to match a filter with an event.
### Related ONTAP commands
* `event filter create`

### Learn more
* [`DOC /support/ems/filters`](#docs-support-support_ems_filters)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["EmsFilter"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event filter.
### Related ONTAP commands
* `event filter delete`

### Learn more
* [`DOC /support/ems/filters/{name}`](#docs-support-support_ems_filters_{name})"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of event filters.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters`](#docs-support-support_ems_filters)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an event filter.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters/{name}`](#docs-support-support_ems_filters_{name})"""
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
        r"""Creates an event filter.
### Required properties
* `name` - String that uniquely identifies the filter.
### Recommended optional properties
* `rules` - List of criteria which is used to match a filter with an event.
### Related ONTAP commands
* `event filter create`

### Learn more
* [`DOC /support/ems/filters`](#docs-support-support_ems_filters)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter create")
        async def ems_filter_create(
        ) -> ResourceTable:
            """Create an instance of a EmsFilter resource

            Args:
                links: 
                name: Filter name
                rules: Array of event filter rules on which to match.
                system_defined: Flag indicating system-defined filters.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if name is not None:
                kwargs["name"] = name
            if rules is not None:
                kwargs["rules"] = rules
            if system_defined is not None:
                kwargs["system_defined"] = system_defined

            resource = EmsFilter(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create EmsFilter: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event filter.
### Recommended optional properties
* `new_name` - New string that uniquely identifies a filter.
* `rules` - New list of criteria used to match the filter with an event. The existing list is discarded.
### Related ONTAP commands
* `event filter rename`
* `event filter rule add`
* `event filter rule delete`
* `event filter rule reorder`

### Learn more
* [`DOC /support/ems/filters/{name}`](#docs-support-support_ems_filters_{name})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter modify")
        async def ems_filter_modify(
        ) -> ResourceTable:
            """Modify an instance of a EmsFilter resource

            Args:
                name: Filter name
                query_name: Filter name
                system_defined: Flag indicating system-defined filters.
                query_system_defined: Flag indicating system-defined filters.
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_system_defined is not None:
                kwargs["system_defined"] = query_system_defined

            if name is not None:
                changes["name"] = name
            if system_defined is not None:
                changes["system_defined"] = system_defined

            if hasattr(EmsFilter, "find"):
                resource = EmsFilter.find(
                    **kwargs
                )
            else:
                resource = EmsFilter()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify EmsFilter: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event filter.
### Related ONTAP commands
* `event filter delete`

### Learn more
* [`DOC /support/ems/filters/{name}`](#docs-support-support_ems_filters_{name})"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter delete")
        async def ems_filter_delete(
        ) -> None:
            """Delete an instance of a EmsFilter resource

            Args:
                name: Filter name
                system_defined: Flag indicating system-defined filters.
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if system_defined is not None:
                kwargs["system_defined"] = system_defined

            if hasattr(EmsFilter, "find"):
                resource = EmsFilter.find(
                    **kwargs
                )
            else:
                resource = EmsFilter()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete EmsFilter: %s" % err)


