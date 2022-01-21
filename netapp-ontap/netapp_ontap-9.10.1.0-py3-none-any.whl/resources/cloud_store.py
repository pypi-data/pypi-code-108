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


__all__ = ["CloudStore", "CloudStoreSchema"]
__pdoc__ = {
    "CloudStoreSchema.resource": False,
    "CloudStore.cloud_store_show": False,
    "CloudStore.cloud_store_create": False,
    "CloudStore.cloud_store_modify": False,
    "CloudStore.cloud_store_delete": False,
}


class CloudStoreSchema(ResourceSchema):
    """The fields of the CloudStore object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cloud_store. """

    aggregate = fields.Nested("netapp_ontap.models.cloud_store_aggregate.CloudStoreAggregateSchema", data_key="aggregate", unknown=EXCLUDE)
    r""" The aggregate field of the cloud_store. """

    availability = fields.Str(
        data_key="availability",
        validate=enum_validation(['available', 'unavailable']),
    )
    r""" Availability of the object store.

Valid choices:

* available
* unavailable """

    mirror_degraded = fields.Boolean(
        data_key="mirror_degraded",
    )
    r""" This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool. """

    primary = fields.Boolean(
        data_key="primary",
    )
    r""" This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool. """

    target = fields.Nested("netapp_ontap.resources.cloud_target.CloudTargetSchema", data_key="target", unknown=EXCLUDE)
    r""" The target field of the cloud_store. """

    unavailable_reason = fields.Nested("netapp_ontap.models.cloud_store_unavailable_reason.CloudStoreUnavailableReasonSchema", data_key="unavailable_reason", unknown=EXCLUDE)
    r""" The unavailable_reason field of the cloud_store. """

    unreclaimed_space_threshold = Size(
        data_key="unreclaimed_space_threshold",
    )
    r""" Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.

Example: 20 """

    used = Size(
        data_key="used",
    )
    r""" The amount of object space used. Calculated every 5 minutes and cached. """

    @property
    def resource(self):
        return CloudStore

    gettable_fields = [
        "links",
        "aggregate",
        "availability",
        "mirror_degraded",
        "primary",
        "target.links",
        "target.name",
        "target.uuid",
        "unavailable_reason",
        "unreclaimed_space_threshold",
        "used",
    ]
    """links,aggregate,availability,mirror_degraded,primary,target.links,target.name,target.uuid,unavailable_reason,unreclaimed_space_threshold,used,"""

    patchable_fields = [
        "primary",
        "unavailable_reason",
        "unreclaimed_space_threshold",
    ]
    """primary,unavailable_reason,unreclaimed_space_threshold,"""

    postable_fields = [
        "aggregate",
        "primary",
        "target.name",
        "target.uuid",
        "unavailable_reason",
        "unreclaimed_space_threshold",
    ]
    """aggregate,primary,target.name,target.uuid,unavailable_reason,unreclaimed_space_threshold,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in CloudStore.get_collection(fields=field)]
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
            raise NetAppRestError("CloudStore modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class CloudStore(Resource):
    """Allows interaction with CloudStore objects on the host"""

    _schema = CloudStoreSchema
    _path = "/api/storage/aggregates/{aggregate[uuid]}/cloud-stores"
    _keys = ["aggregate.uuid", "target.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of cloud stores used by an aggregate.
### Related ONTAP commands
* `storage aggregate object-store show`
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud store show")
        def cloud_store_show(
            aggregate_uuid,
            availability: Choices.define(_get_field_list("availability"), cache_choices=True, inexact=True)=None,
            mirror_degraded: Choices.define(_get_field_list("mirror_degraded"), cache_choices=True, inexact=True)=None,
            primary: Choices.define(_get_field_list("primary"), cache_choices=True, inexact=True)=None,
            unreclaimed_space_threshold: Choices.define(_get_field_list("unreclaimed_space_threshold"), cache_choices=True, inexact=True)=None,
            used: Choices.define(_get_field_list("used"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["availability", "mirror_degraded", "primary", "unreclaimed_space_threshold", "used", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of CloudStore resources

            Args:
                availability: Availability of the object store.
                mirror_degraded: This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool.
                primary: This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool.
                unreclaimed_space_threshold: Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.
                used: The amount of object space used. Calculated every 5 minutes and cached.
            """

            kwargs = {}
            if availability is not None:
                kwargs["availability"] = availability
            if mirror_degraded is not None:
                kwargs["mirror_degraded"] = mirror_degraded
            if primary is not None:
                kwargs["primary"] = primary
            if unreclaimed_space_threshold is not None:
                kwargs["unreclaimed_space_threshold"] = unreclaimed_space_threshold
            if used is not None:
                kwargs["used"] = used
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return CloudStore.get_collection(
                aggregate_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all CloudStore resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["CloudStore"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cloud store specified by the UUID with the fields in the body. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store modify`
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["CloudStore"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["CloudStore"], NetAppResponse]:
        r"""Attaches an object store to an aggregate, or adds a second object store as a mirror.
### Required properties
* `target.uuid` or `target.name` - UUID or name of the cloud target.
### Recommended optional properties
* `primary` - _true_ if the object store is primary or _false_ if it is a mirror.
* `allow_flexgroups` - Allow attaching object store to an aggregate containing FlexGroup constituents.
* `check_only` - Validate only and do not add the cloud store.
### Default property values
* `primary` - _true_
* `allow_flexgroups` - _false_
* `check_only` - _false_
### Related ONTAP commands
* `storage aggregate object-store attach`
* `storage aggregate object-store mirror`
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
        records: Iterable["CloudStore"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes the specified cloud target from the aggregate. Only removal of a mirror is allowed. The primary cannot be removed. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store unmirror`
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of cloud stores used by an aggregate.
### Related ONTAP commands
* `storage aggregate object-store show`
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the cloud store for the aggregate using the specified cloud target UUID.
### Related ONTAP commands
* `storage aggregate object-store show`
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
        r"""Attaches an object store to an aggregate, or adds a second object store as a mirror.
### Required properties
* `target.uuid` or `target.name` - UUID or name of the cloud target.
### Recommended optional properties
* `primary` - _true_ if the object store is primary or _false_ if it is a mirror.
* `allow_flexgroups` - Allow attaching object store to an aggregate containing FlexGroup constituents.
* `check_only` - Validate only and do not add the cloud store.
### Default property values
* `primary` - _true_
* `allow_flexgroups` - _false_
* `check_only` - _false_
### Related ONTAP commands
* `storage aggregate object-store attach`
* `storage aggregate object-store mirror`
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud store create")
        async def cloud_store_create(
            aggregate_uuid,
            links: dict = None,
            aggregate: dict = None,
            availability: str = None,
            mirror_degraded: bool = None,
            primary: bool = None,
            target: dict = None,
            unavailable_reason: dict = None,
            unreclaimed_space_threshold: Size = None,
            used: Size = None,
        ) -> ResourceTable:
            """Create an instance of a CloudStore resource

            Args:
                links: 
                aggregate: 
                availability: Availability of the object store.
                mirror_degraded: This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool.
                primary: This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool.
                target: 
                unavailable_reason: 
                unreclaimed_space_threshold: Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.
                used: The amount of object space used. Calculated every 5 minutes and cached.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if aggregate is not None:
                kwargs["aggregate"] = aggregate
            if availability is not None:
                kwargs["availability"] = availability
            if mirror_degraded is not None:
                kwargs["mirror_degraded"] = mirror_degraded
            if primary is not None:
                kwargs["primary"] = primary
            if target is not None:
                kwargs["target"] = target
            if unavailable_reason is not None:
                kwargs["unavailable_reason"] = unavailable_reason
            if unreclaimed_space_threshold is not None:
                kwargs["unreclaimed_space_threshold"] = unreclaimed_space_threshold
            if used is not None:
                kwargs["used"] = used

            resource = CloudStore(
                aggregate_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create CloudStore: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cloud store specified by the UUID with the fields in the body. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store modify`
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud store modify")
        async def cloud_store_modify(
            aggregate_uuid,
            availability: str = None,
            query_availability: str = None,
            mirror_degraded: bool = None,
            query_mirror_degraded: bool = None,
            primary: bool = None,
            query_primary: bool = None,
            unreclaimed_space_threshold: Size = None,
            query_unreclaimed_space_threshold: Size = None,
            used: Size = None,
            query_used: Size = None,
        ) -> ResourceTable:
            """Modify an instance of a CloudStore resource

            Args:
                availability: Availability of the object store.
                query_availability: Availability of the object store.
                mirror_degraded: This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool.
                query_mirror_degraded: This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool.
                primary: This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool.
                query_primary: This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool.
                unreclaimed_space_threshold: Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.
                query_unreclaimed_space_threshold: Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.
                used: The amount of object space used. Calculated every 5 minutes and cached.
                query_used: The amount of object space used. Calculated every 5 minutes and cached.
            """

            kwargs = {}
            changes = {}
            if query_availability is not None:
                kwargs["availability"] = query_availability
            if query_mirror_degraded is not None:
                kwargs["mirror_degraded"] = query_mirror_degraded
            if query_primary is not None:
                kwargs["primary"] = query_primary
            if query_unreclaimed_space_threshold is not None:
                kwargs["unreclaimed_space_threshold"] = query_unreclaimed_space_threshold
            if query_used is not None:
                kwargs["used"] = query_used

            if availability is not None:
                changes["availability"] = availability
            if mirror_degraded is not None:
                changes["mirror_degraded"] = mirror_degraded
            if primary is not None:
                changes["primary"] = primary
            if unreclaimed_space_threshold is not None:
                changes["unreclaimed_space_threshold"] = unreclaimed_space_threshold
            if used is not None:
                changes["used"] = used

            if hasattr(CloudStore, "find"):
                resource = CloudStore.find(
                    aggregate_uuid,
                    **kwargs
                )
            else:
                resource = CloudStore(aggregate_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify CloudStore: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Removes the specified cloud target from the aggregate. Only removal of a mirror is allowed. The primary cannot be removed. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store unmirror`
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud store delete")
        async def cloud_store_delete(
            aggregate_uuid,
            availability: str = None,
            mirror_degraded: bool = None,
            primary: bool = None,
            unreclaimed_space_threshold: Size = None,
            used: Size = None,
        ) -> None:
            """Delete an instance of a CloudStore resource

            Args:
                availability: Availability of the object store.
                mirror_degraded: This field identifies if the mirror cloud store is in sync with the primary cloud store of a FabricPool.
                primary: This field indicates whether the cloud store is the primary cloud store of a mirrored FabricPool.
                unreclaimed_space_threshold: Usage threshold for reclaiming unused space in the cloud store. Valid values are 0 to 99. The default value depends on the provider type. This can be specified in PATCH but not POST.
                used: The amount of object space used. Calculated every 5 minutes and cached.
            """

            kwargs = {}
            if availability is not None:
                kwargs["availability"] = availability
            if mirror_degraded is not None:
                kwargs["mirror_degraded"] = mirror_degraded
            if primary is not None:
                kwargs["primary"] = primary
            if unreclaimed_space_threshold is not None:
                kwargs["unreclaimed_space_threshold"] = unreclaimed_space_threshold
            if used is not None:
                kwargs["used"] = used

            if hasattr(CloudStore, "find"):
                resource = CloudStore.find(
                    aggregate_uuid,
                    **kwargs
                )
            else:
                resource = CloudStore(aggregate_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete CloudStore: %s" % err)


