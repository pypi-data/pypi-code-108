r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


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


__all__ = ["IgroupNested", "IgroupNestedSchema"]
__pdoc__ = {
    "IgroupNestedSchema.resource": False,
    "IgroupNested.igroup_nested_show": False,
    "IgroupNested.igroup_nested_create": False,
    "IgroupNested.igroup_nested_modify": False,
    "IgroupNested.igroup_nested_delete": False,
}


class IgroupNestedSchema(ResourceSchema):
    """The fields of the IgroupNested object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the igroup_nested. """

    igroup = fields.Nested("netapp_ontap.models.igroup_nested_igroup.IgroupNestedIgroupSchema", data_key="igroup", unknown=EXCLUDE)
    r""" The igroup field of the igroup_nested. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=96),
    )
    r""" The name of the initiator group.


Example: igroup1 """

    records = fields.List(fields.Nested("netapp_ontap.models.igroup_nested_no_records.IgroupNestedNoRecordsSchema", unknown=EXCLUDE), data_key="records")
    r""" An array of initiator groups specified to add multiple nested initiator groups to an initiator group in a single API call. Not allowed when the `name` property is used. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the initiator group.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IgroupNested

    gettable_fields = [
        "links",
        "igroup",
        "name",
        "uuid",
    ]
    """links,igroup,name,uuid,"""

    patchable_fields = [
        "igroup",
        "name",
        "records",
        "uuid",
    ]
    """igroup,name,records,uuid,"""

    postable_fields = [
        "igroup",
        "name",
        "records",
        "uuid",
    ]
    """igroup,name,records,uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in IgroupNested.get_collection(fields=field)]
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
            raise NetAppRestError("IgroupNested modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class IgroupNested(Resource):
    """Allows interaction with IgroupNested objects on the host"""

    _schema = IgroupNestedSchema
    _path = "/api/protocols/san/igroups/{igroup[uuid]}/igroups"
    _keys = ["igroup.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves nested initiator groups of an initiator group.
This API only reports the nested initiator groups that are direct
children of the initiator group. Further nested initiator groups are
reported by their direct parent initiator group.
### Related ONTAP commands
* `lun igroup show`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="igroup nested show")
        def igroup_nested_show(
            igroup_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of IgroupNested resources

            Args:
                name: The name of the initiator group. 
                uuid: The unique identifier of the initiator group. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return IgroupNested.get_collection(
                igroup_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all IgroupNested resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["IgroupNested"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["IgroupNested"], NetAppResponse]:
        r"""Adds one or more nested initiator groups to an initiator group. A single
nested initiator group can be added by directly specifying the name or
UUID. Multiple nested initiator groups can be added by specifying the
names or UUIDs in the records array. Nested initiator groups cannot be
added to an initiator group that already directly contains initiators.
### Required properties
* `name` and/or `uuid` or `records` - Nested initiator groups to add to the initiator group.
### Related ONTAP commands
* `lun igroup add`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
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
        records: Iterable["IgroupNested"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes a nested initiator group from an initiator group. This API does
not delete the nested initiator group itself. It removes the relationship
between a parent and child initiator group.
This API only supports removal of initiator groups owned directly by the
initiator group. Further nested initiator groups must be removed from the
direct parent initiator group.
### Related ONTAP commands
* `lun igroup remove`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves nested initiator groups of an initiator group.
This API only reports the nested initiator groups that are direct
children of the initiator group. Further nested initiator groups are
reported by their direct parent initiator group.
### Related ONTAP commands
* `lun igroup show`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a nested initiator group of an initiator group.
This API only reports the nested initiator groups that are direct
children of the initiator group. Further nested initiator groups are
reported by their direct parent initiator group.
### Related ONTAP commands
* `lun igroup show`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
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
        r"""Adds one or more nested initiator groups to an initiator group. A single
nested initiator group can be added by directly specifying the name or
UUID. Multiple nested initiator groups can be added by specifying the
names or UUIDs in the records array. Nested initiator groups cannot be
added to an initiator group that already directly contains initiators.
### Required properties
* `name` and/or `uuid` or `records` - Nested initiator groups to add to the initiator group.
### Related ONTAP commands
* `lun igroup add`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="igroup nested create")
        async def igroup_nested_create(
            igroup_uuid,
            links: dict = None,
            igroup: dict = None,
            name: str = None,
            records: dict = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a IgroupNested resource

            Args:
                links: 
                igroup: 
                name: The name of the initiator group. 
                records: An array of initiator groups specified to add multiple nested initiator groups to an initiator group in a single API call. Not allowed when the `name` property is used. 
                uuid: The unique identifier of the initiator group. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if igroup is not None:
                kwargs["igroup"] = igroup
            if name is not None:
                kwargs["name"] = name
            if records is not None:
                kwargs["records"] = records
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = IgroupNested(
                igroup_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create IgroupNested: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes a nested initiator group from an initiator group. This API does
not delete the nested initiator group itself. It removes the relationship
between a parent and child initiator group.
This API only supports removal of initiator groups owned directly by the
initiator group. Further nested initiator groups must be removed from the
direct parent initiator group.
### Related ONTAP commands
* `lun igroup remove`
### Learn more
* [`DOC /protocols/san/igroups`](#docs-SAN-protocols_san_igroups)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="igroup nested delete")
        async def igroup_nested_delete(
            igroup_uuid,
            name: str = None,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a IgroupNested resource

            Args:
                name: The name of the initiator group. 
                uuid: The unique identifier of the initiator group. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(IgroupNested, "find"):
                resource = IgroupNested.find(
                    igroup_uuid,
                    **kwargs
                )
            else:
                resource = IgroupNested(igroup_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete IgroupNested: %s" % err)


