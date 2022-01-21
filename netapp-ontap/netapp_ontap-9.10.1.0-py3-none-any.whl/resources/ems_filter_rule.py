r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Manages a specific instance of a rule within a filter.
See the documentation for [/support/ems/filters](#/docs/support/support_ems_filters) for details on the various properties in a rule.
## Examples
### Retrieving a single instance of a rule
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilterRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilterRule("no-info-debug-events", index=1)
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
EmsFilterRule(
    {
        "index": 1,
        "type": "include",
        "message_criteria": {
            "severities": "emergency,alert,error,notice",
            "name_pattern": "*",
            "_links": {},
            "snmp_trap_types": "*",
        },
        "_links": {
            "self": {"href": "/api/support/ems/filters/no-info-debug-events/rules/1"}
        },
    }
)

```
</div>
</div>

### Updating an existing rule to use severity emergency
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilterRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilterRule("test-filter")
    resource.message_criteria = {"severities": "emergency"}
    resource.post(hydrate=True)
    print(resource)

```

### Deleting a rule from an existing filter
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsFilterRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = EmsFilterRule("test-filter", index=1)
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


__all__ = ["EmsFilterRule", "EmsFilterRuleSchema"]
__pdoc__ = {
    "EmsFilterRuleSchema.resource": False,
    "EmsFilterRule.ems_filter_rule_show": False,
    "EmsFilterRule.ems_filter_rule_create": False,
    "EmsFilterRule.ems_filter_rule_modify": False,
    "EmsFilterRule.ems_filter_rule_delete": False,
}


class EmsFilterRuleSchema(ResourceSchema):
    """The fields of the EmsFilterRule object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ems_filter_rule. """

    index = Size(
        data_key="index",
    )
    r""" Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.

Example: 1 """

    message_criteria = fields.Nested("netapp_ontap.models.ems_filter_rule_message_criteria.EmsFilterRuleMessageCriteriaSchema", data_key="message_criteria", unknown=EXCLUDE)
    r""" The message_criteria field of the ems_filter_rule. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['include', 'exclude']),
    )
    r""" Rule type

Valid choices:

* include
* exclude """

    @property
    def resource(self):
        return EmsFilterRule

    gettable_fields = [
        "links",
        "index",
        "message_criteria",
        "type",
    ]
    """links,index,message_criteria,type,"""

    patchable_fields = [
        "index",
        "message_criteria",
        "type",
    ]
    """index,message_criteria,type,"""

    postable_fields = [
        "index",
        "message_criteria",
        "type",
    ]
    """index,message_criteria,type,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EmsFilterRule.get_collection(fields=field)]
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
            raise NetAppRestError("EmsFilterRule modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EmsFilterRule(Resource):
    r""" Rule for an event filter """

    _schema = EmsFilterRuleSchema
    _path = "/api/support/ems/filters/{ems_filter[name]}/rules"
    _keys = ["ems_filter.name", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves event filter rules.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters/{name}/rules`](#docs-support-support_ems_filters_{name}_rules)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter rule show")
        def ems_filter_rule_show(
            name,
            index: Choices.define(_get_field_list("index"), cache_choices=True, inexact=True)=None,
            type: Choices.define(_get_field_list("type"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["index", "type", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of EmsFilterRule resources

            Args:
                index: Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.
                type: Rule type
            """

            kwargs = {}
            if index is not None:
                kwargs["index"] = index
            if type is not None:
                kwargs["type"] = type
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return EmsFilterRule.get_collection(
                name,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all EmsFilterRule resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["EmsFilterRule"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event filter rule.
### Recommended optional properties
* `message_criteria` - New criteria on which a rule is to match an event.
### Related ONTAP commands
* `event filter rule add`
* `event filter rule delete`

### Learn more
* [`DOC /support/ems/filters/{name}/rules/{index}`](#docs-support-support_ems_filters_{name}_rules_{index})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["EmsFilterRule"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["EmsFilterRule"], NetAppResponse]:
        r"""Creates an event filter rule.
### Required properties
* `message_criteria` - Criteria on which a rule is to match an event.
### Recommended optional properties
* `index` - One-based position index of the new rule.
### Related ONTAP commands
* `event filter rule add`

### Learn more
* [`DOC /support/ems/filters/{name}/rules`](#docs-support-support_ems_filters_{name}_rules)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["EmsFilterRule"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event filter rule.
### Related ONTAP commands
* `event filter rule delete`

### Learn more
* [`DOC /support/ems/filters/{name}/rules/{index}`](#docs-support-support_ems_filters_{name}_rules_{index})"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves event filter rules.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters/{name}/rules`](#docs-support-support_ems_filters_{name}_rules)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an event filter rule.
### Related ONTAP commands
* `event filter show`

### Learn more
* [`DOC /support/ems/filters/{name}/rules/{index}`](#docs-support-support_ems_filters_{name}_rules_{index})"""
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
        r"""Creates an event filter rule.
### Required properties
* `message_criteria` - Criteria on which a rule is to match an event.
### Recommended optional properties
* `index` - One-based position index of the new rule.
### Related ONTAP commands
* `event filter rule add`

### Learn more
* [`DOC /support/ems/filters/{name}/rules`](#docs-support-support_ems_filters_{name}_rules)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter rule create")
        async def ems_filter_rule_create(
            name,
            links: dict = None,
            index: Size = None,
            message_criteria: dict = None,
            type: str = None,
        ) -> ResourceTable:
            """Create an instance of a EmsFilterRule resource

            Args:
                links: 
                index: Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.
                message_criteria: 
                type: Rule type
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if index is not None:
                kwargs["index"] = index
            if message_criteria is not None:
                kwargs["message_criteria"] = message_criteria
            if type is not None:
                kwargs["type"] = type

            resource = EmsFilterRule(
                name,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create EmsFilterRule: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an event filter rule.
### Recommended optional properties
* `message_criteria` - New criteria on which a rule is to match an event.
### Related ONTAP commands
* `event filter rule add`
* `event filter rule delete`

### Learn more
* [`DOC /support/ems/filters/{name}/rules/{index}`](#docs-support-support_ems_filters_{name}_rules_{index})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter rule modify")
        async def ems_filter_rule_modify(
            name,
            index: Size = None,
            query_index: Size = None,
            type: str = None,
            query_type: str = None,
        ) -> ResourceTable:
            """Modify an instance of a EmsFilterRule resource

            Args:
                index: Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.
                query_index: Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.
                type: Rule type
                query_type: Rule type
            """

            kwargs = {}
            changes = {}
            if query_index is not None:
                kwargs["index"] = query_index
            if query_type is not None:
                kwargs["type"] = query_type

            if index is not None:
                changes["index"] = index
            if type is not None:
                changes["type"] = type

            if hasattr(EmsFilterRule, "find"):
                resource = EmsFilterRule.find(
                    name,
                    **kwargs
                )
            else:
                resource = EmsFilterRule(name,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify EmsFilterRule: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an event filter rule.
### Related ONTAP commands
* `event filter rule delete`

### Learn more
* [`DOC /support/ems/filters/{name}/rules/{index}`](#docs-support-support_ems_filters_{name}_rules_{index})"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems filter rule delete")
        async def ems_filter_rule_delete(
            name,
            index: Size = None,
            type: str = None,
        ) -> None:
            """Delete an instance of a EmsFilterRule resource

            Args:
                index: Rule index. Rules are evaluated in ascending order. If a rule's index order is not specified during creation, the rule is appended to the end of the list.
                type: Rule type
            """

            kwargs = {}
            if index is not None:
                kwargs["index"] = index
            if type is not None:
                kwargs["type"] = type

            if hasattr(EmsFilterRule, "find"):
                resource = EmsFilterRule.find(
                    name,
                    **kwargs
                )
            else:
                resource = EmsFilterRule(name,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete EmsFilterRule: %s" % err)


