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


__all__ = ["ApplicationComponentSnapshot", "ApplicationComponentSnapshotSchema"]
__pdoc__ = {
    "ApplicationComponentSnapshotSchema.resource": False,
    "ApplicationComponentSnapshot.application_component_snapshot_show": False,
    "ApplicationComponentSnapshot.application_component_snapshot_create": False,
    "ApplicationComponentSnapshot.application_component_snapshot_modify": False,
    "ApplicationComponentSnapshot.application_component_snapshot_delete": False,
}


class ApplicationComponentSnapshotSchema(ResourceSchema):
    """The fields of the ApplicationComponentSnapshot object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the application_component_snapshot. """

    application = fields.Nested("netapp_ontap.models.application_component_snapshot_application.ApplicationComponentSnapshotApplicationSchema", data_key="application", unknown=EXCLUDE)
    r""" The application field of the application_component_snapshot. """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=255),
    )
    r""" Comment. Valid in POST """

    component = fields.Nested("netapp_ontap.models.application_component_snapshot_component.ApplicationComponentSnapshotComponentSchema", data_key="component", unknown=EXCLUDE)
    r""" The component field of the application_component_snapshot. """

    consistency_type = fields.Str(
        data_key="consistency_type",
        validate=enum_validation(['crash', 'application']),
    )
    r""" Consistency Type. This is for categorization only. A Snapshot copy should not be set to application consistent unless the host application is quiesced for the Snapshot copy. Valid in POST

Valid choices:

* crash
* application """

    create_time = fields.Str(
        data_key="create_time",
    )
    r""" Creation Time """

    is_partial = fields.Boolean(
        data_key="is_partial",
    )
    r""" A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy. """

    name = fields.Str(
        data_key="name",
    )
    r""" Snapshot copy name. Valid in POST """

    svm = fields.Nested("netapp_ontap.models.application_component_snapshot_svm.ApplicationComponentSnapshotSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the application_component_snapshot. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Snapshot copy UUID. Valid in URL """

    @property
    def resource(self):
        return ApplicationComponentSnapshot

    gettable_fields = [
        "links",
        "application",
        "comment",
        "component",
        "consistency_type",
        "create_time",
        "is_partial",
        "name",
        "svm",
        "uuid",
    ]
    """links,application,comment,component,consistency_type,create_time,is_partial,name,svm,uuid,"""

    patchable_fields = [
        "application",
        "comment",
        "component",
        "consistency_type",
        "name",
        "svm",
    ]
    """application,comment,component,consistency_type,name,svm,"""

    postable_fields = [
        "application",
        "comment",
        "component",
        "consistency_type",
        "name",
        "svm",
    ]
    """application,comment,component,consistency_type,name,svm,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ApplicationComponentSnapshot.get_collection(fields=field)]
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
            raise NetAppRestError("ApplicationComponentSnapshot modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ApplicationComponentSnapshot(Resource):
    """Allows interaction with ApplicationComponentSnapshot objects on the host"""

    _schema = ApplicationComponentSnapshotSchema
    _path = "/api/application/applications/{application[uuid]}/components/{component[uuid]}/snapshots"
    _keys = ["application.uuid", "component.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves Snapshot copies of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_collection_get)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application component snapshot show")
        def application_component_snapshot_show(
            component_uuid,
            application_uuid,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            consistency_type: Choices.define(_get_field_list("consistency_type"), cache_choices=True, inexact=True)=None,
            create_time: Choices.define(_get_field_list("create_time"), cache_choices=True, inexact=True)=None,
            is_partial: Choices.define(_get_field_list("is_partial"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["comment", "consistency_type", "create_time", "is_partial", "name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ApplicationComponentSnapshot resources

            Args:
                comment: Comment. Valid in POST
                consistency_type: Consistency Type. This is for categorization only. A Snapshot copy should not be set to application consistent unless the host application is quiesced for the Snapshot copy. Valid in POST
                create_time: Creation Time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: Snapshot copy name. Valid in POST
                uuid: Snapshot copy UUID. Valid in URL
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ApplicationComponentSnapshot.get_collection(
                component_uuid,
                application_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ApplicationComponentSnapshot resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["ApplicationComponentSnapshot"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ApplicationComponentSnapshot"], NetAppResponse]:
        r"""Creates a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
### Required properties
* `name`
### Recommended optional properties
* `consistency_type` - Track whether this snapshot is _application_ or _crash_ consistent.
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_create)
* [`DOC /application`](#docs-application-overview)
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
        records: Iterable["ApplicationComponentSnapshot"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Delete a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`DELETE /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_delete)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Snapshot copies of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_collection_get)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieve a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_get)
* [`DOC /application`](#docs-application-overview)
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
        r"""Creates a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
### Required properties
* `name`
### Recommended optional properties
* `consistency_type` - Track whether this snapshot is _application_ or _crash_ consistent.
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_create)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application component snapshot create")
        async def application_component_snapshot_create(
            component_uuid,
            application_uuid,
            links: dict = None,
            application: dict = None,
            comment: str = None,
            component: dict = None,
            consistency_type: str = None,
            create_time: str = None,
            is_partial: bool = None,
            name: str = None,
            svm: dict = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a ApplicationComponentSnapshot resource

            Args:
                links: 
                application: 
                comment: Comment. Valid in POST
                component: 
                consistency_type: Consistency Type. This is for categorization only. A Snapshot copy should not be set to application consistent unless the host application is quiesced for the Snapshot copy. Valid in POST
                create_time: Creation Time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: Snapshot copy name. Valid in POST
                svm: 
                uuid: Snapshot copy UUID. Valid in URL
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if application is not None:
                kwargs["application"] = application
            if comment is not None:
                kwargs["comment"] = comment
            if component is not None:
                kwargs["component"] = component
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if name is not None:
                kwargs["name"] = name
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = ApplicationComponentSnapshot(
                component_uuid,
                application_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ApplicationComponentSnapshot: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Delete a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`DELETE /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_delete)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application component snapshot delete")
        async def application_component_snapshot_delete(
            component_uuid,
            application_uuid,
            comment: str = None,
            consistency_type: str = None,
            create_time: str = None,
            is_partial: bool = None,
            name: str = None,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a ApplicationComponentSnapshot resource

            Args:
                comment: Comment. Valid in POST
                consistency_type: Consistency Type. This is for categorization only. A Snapshot copy should not be set to application consistent unless the host application is quiesced for the Snapshot copy. Valid in POST
                create_time: Creation Time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: Snapshot copy name. Valid in POST
                uuid: Snapshot copy UUID. Valid in URL
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_type is not None:
                kwargs["consistency_type"] = consistency_type
            if create_time is not None:
                kwargs["create_time"] = create_time
            if is_partial is not None:
                kwargs["is_partial"] = is_partial
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(ApplicationComponentSnapshot, "find"):
                resource = ApplicationComponentSnapshot.find(
                    component_uuid,
                    application_uuid,
                    **kwargs
                )
            else:
                resource = ApplicationComponentSnapshot(component_uuid,application_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ApplicationComponentSnapshot: %s" % err)

    def restore(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Restore a Snapshot copy of an application component.<br/>
This endpoint is only supported for Maxdata template applications.<br/>
Component Snapshot copies are essentially more granular application Snapshot copies. There is no difference beyond the scope of the operation.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`POST /application/applications/{application.uuid}/snapshots/{uuid}/restore`](#operations-application-application_snapshot_restore)
* [`DOC /application`](#docs-application-overview)
* [`Asynchronous operations`](#Synchronous_and_asynchronous_operations)
"""
        return super()._action(
            "restore", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    restore.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)

