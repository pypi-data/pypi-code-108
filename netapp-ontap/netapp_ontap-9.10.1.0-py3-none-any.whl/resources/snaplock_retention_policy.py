r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

An event retention policy consists of a policy-name and a retention-period. The policy can be applied to a single file or files in a directory. Only a user with the security login role vsadmin-snaplock can perform the operation. EBR policies cannot be applied to files under a Legal-Hold.
### Examples
1. Creates an EBR policy policy_name with a retention period of "10 years":
   <br/>
   ```
   POST "/api/storage/snaplock/event-retention/policies/" '{"name": "policy_name","retention_period": "P10Y"}'
   ```
   <br/>
2. Creates an EBR policy policy_name1 with a retention period of "infinite":
   <br/>
   ```
   POST "/api/storage/snaplock/event-retention/policies/" '{"name": "policy_name1","retention_period": "infinite"}'
   ```
   <br/>
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


__all__ = ["SnaplockRetentionPolicy", "SnaplockRetentionPolicySchema"]
__pdoc__ = {
    "SnaplockRetentionPolicySchema.resource": False,
    "SnaplockRetentionPolicy.snaplock_retention_policy_show": False,
    "SnaplockRetentionPolicy.snaplock_retention_policy_create": False,
    "SnaplockRetentionPolicy.snaplock_retention_policy_modify": False,
    "SnaplockRetentionPolicy.snaplock_retention_policy_delete": False,
}


class SnaplockRetentionPolicySchema(ResourceSchema):
    """The fields of the SnaplockRetentionPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_retention_policy. """

    name = fields.Str(
        data_key="name",
    )
    r""" Specifies the EBR policy name """

    retention_period = fields.Str(
        data_key="retention_period",
    )
    r""" Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as "P<num>Y", "P<num>M", "P<num>D" respectively. For example "P10Y" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by "PT<num>H", "PT<num>M" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example "P1Y10M" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings "infinite" and "unspecified".

Example: P30M """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the snaplock_retention_policy. """

    @property
    def resource(self):
        return SnaplockRetentionPolicy

    gettable_fields = [
        "links",
        "name",
        "retention_period",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,name,retention_period,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "name",
        "retention_period",
        "svm.name",
        "svm.uuid",
    ]
    """name,retention_period,svm.name,svm.uuid,"""

    postable_fields = [
        "name",
        "retention_period",
        "svm.name",
        "svm.uuid",
    ]
    """name,retention_period,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockRetentionPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockRetentionPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockRetentionPolicy(Resource):
    """Allows interaction with SnaplockRetentionPolicy objects on the host"""

    _schema = SnaplockRetentionPolicySchema
    _path = "/api/storage/snaplock/event-retention/policies"
    _keys = ["policy.name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves all event retention policies for an SVM.
### Related ONTAP commands
* `snaplock event-retention policy show`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock retention policy show")
        def snaplock_retention_policy_show(
            fields: List[Choices.define(["name", "retention_period", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockRetentionPolicy resources

            Args:
                name: Specifies the EBR policy name
                retention_period: Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as \"P<num>Y\", \"P<num>M\", \"P<num>D\" respectively. For example \"P10Y\" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by \"PT<num>H\", \"PT<num>M\" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example \"P1Y10M\" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings \"infinite\" and \"unspecified\".
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if retention_period is not None:
                kwargs["retention_period"] = retention_period
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockRetentionPolicy.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockRetentionPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SnaplockRetentionPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the retention period of an Event Based Retention (EBR) policy.
### Related ONTAP commands
* `snaplock event-retention policy modify`
### Example
Updates the retention period of an EBR policy "policy_name":
<br/>
```
PATCH "/api/storage/snaplock/event-retention/policies/" '{"name": "policy_name","retention_period": "P20Y"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockRetentionPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockRetentionPolicy"], NetAppResponse]:
        r"""Creates an Event Based Retention (EBR) policy for an SVM. The input parameter retention_period expects the duration in ISO 8601 format or infinite.
### Required properties
* `name` - Event retention policy name.
* `retention_period` - Retention period of the EBR policy.
### Related ONTAP commands
* `snaplock event-retention policy create`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
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
        records: Iterable["SnaplockRetentionPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the specified Event Based Retention (EBR) policy.
### Related ONTAP commands
* `snaplock event-retention policy delete`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves all event retention policies for an SVM.
### Related ONTAP commands
* `snaplock event-retention policy show`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a list of attributes of the specified Event Based Retention (EBR) policy.
### Related ONTAP commands
* `snaplock event-retention policy show`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
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
        r"""Creates an Event Based Retention (EBR) policy for an SVM. The input parameter retention_period expects the duration in ISO 8601 format or infinite.
### Required properties
* `name` - Event retention policy name.
* `retention_period` - Retention period of the EBR policy.
### Related ONTAP commands
* `snaplock event-retention policy create`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock retention policy create")
        async def snaplock_retention_policy_create(
        ) -> ResourceTable:
            """Create an instance of a SnaplockRetentionPolicy resource

            Args:
                links: 
                name: Specifies the EBR policy name
                retention_period: Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as \"P<num>Y\", \"P<num>M\", \"P<num>D\" respectively. For example \"P10Y\" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by \"PT<num>H\", \"PT<num>M\" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example \"P1Y10M\" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings \"infinite\" and \"unspecified\".
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if name is not None:
                kwargs["name"] = name
            if retention_period is not None:
                kwargs["retention_period"] = retention_period
            if svm is not None:
                kwargs["svm"] = svm

            resource = SnaplockRetentionPolicy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockRetentionPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the retention period of an Event Based Retention (EBR) policy.
### Related ONTAP commands
* `snaplock event-retention policy modify`
### Example
Updates the retention period of an EBR policy "policy_name":
<br/>
```
PATCH "/api/storage/snaplock/event-retention/policies/" '{"name": "policy_name","retention_period": "P20Y"}'
```
<br/>
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock retention policy modify")
        async def snaplock_retention_policy_modify(
        ) -> ResourceTable:
            """Modify an instance of a SnaplockRetentionPolicy resource

            Args:
                name: Specifies the EBR policy name
                query_name: Specifies the EBR policy name
                retention_period: Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as \"P<num>Y\", \"P<num>M\", \"P<num>D\" respectively. For example \"P10Y\" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by \"PT<num>H\", \"PT<num>M\" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example \"P1Y10M\" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings \"infinite\" and \"unspecified\".
                query_retention_period: Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as \"P<num>Y\", \"P<num>M\", \"P<num>D\" respectively. For example \"P10Y\" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by \"PT<num>H\", \"PT<num>M\" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example \"P1Y10M\" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings \"infinite\" and \"unspecified\".
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_retention_period is not None:
                kwargs["retention_period"] = query_retention_period

            if name is not None:
                changes["name"] = name
            if retention_period is not None:
                changes["retention_period"] = retention_period

            if hasattr(SnaplockRetentionPolicy, "find"):
                resource = SnaplockRetentionPolicy.find(
                    **kwargs
                )
            else:
                resource = SnaplockRetentionPolicy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SnaplockRetentionPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the specified Event Based Retention (EBR) policy.
### Related ONTAP commands
* `snaplock event-retention policy delete`
### Learn more
* [`DOC /storage/snaplock/event-retention/policies`](#docs-snaplock-storage_snaplock_event-retention_policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock retention policy delete")
        async def snaplock_retention_policy_delete(
        ) -> None:
            """Delete an instance of a SnaplockRetentionPolicy resource

            Args:
                name: Specifies the EBR policy name
                retention_period: Specifies the retention period of an event based retention policy. The retention period value represents a duration and must be specified in the ISO-8601 duration format. The retention period can be in years, months, days, hours or minutes. A period specified for years, months and days is represented in the ISO-8601 format as \"P<num>Y\", \"P<num>M\", \"P<num>D\" respectively. For example \"P10Y\" represents a duration of 10 years. Similarly, a duration in hours, minutes is represented by \"PT<num>H\", \"PT<num>M\" respectively. The period string must contain only a single time element i.e. either years, months, days, hours or minutes. A duration which combines different periods is not supported, example \"P1Y10M\" is not supported. Apart from the duration specified in the ISO-8601 format, the retention period field also accepts the strings \"infinite\" and \"unspecified\".
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if retention_period is not None:
                kwargs["retention_period"] = retention_period

            if hasattr(SnaplockRetentionPolicy, "find"):
                resource = SnaplockRetentionPolicy.find(
                    **kwargs
                )
            else:
                resource = SnaplockRetentionPolicy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnaplockRetentionPolicy: %s" % err)


