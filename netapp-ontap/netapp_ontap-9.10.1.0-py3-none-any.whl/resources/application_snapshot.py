r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Applications support Snapshot copies across all member storage elements. These Snapshot copies can be created and restored at any time or as scheduled. Most applications have hourly Snapshot copies enabled by default, unless the RPO setting is overridden during the creation of the application. An application Snapshot copy can be flagged as either _application consistent_, or _crash consistent_. From an ONTAP perspective, there is no difference between these two consistency types. These types are available for record keeping so that Snapshot copies taken after the application is quiesced (application consistent) can be tracked separately from those Snapshot copies taken without first quiescing the application (crash consistent). By default, all application Snapshot copies are flagged to be _crash consistent_, and Snapshot copies taken at a scheduled time are also considered _crash consistent_.<br/>
The functionality provided by these APIs is not integrated with the host application. Snapshot copies have limited value without host coordination, so the use of the SnapCenter Backup Management suite is recommended to ensure correct interaction between host applications and ONTAP.
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


__all__ = ["ApplicationSnapshot", "ApplicationSnapshotSchema"]
__pdoc__ = {
    "ApplicationSnapshotSchema.resource": False,
    "ApplicationSnapshot.application_snapshot_show": False,
    "ApplicationSnapshot.application_snapshot_create": False,
    "ApplicationSnapshot.application_snapshot_modify": False,
    "ApplicationSnapshot.application_snapshot_delete": False,
}


class ApplicationSnapshotSchema(ResourceSchema):
    """The fields of the ApplicationSnapshot object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the application_snapshot. """

    application = fields.Nested("netapp_ontap.models.application_snapshot_application.ApplicationSnapshotApplicationSchema", data_key="application", unknown=EXCLUDE)
    r""" The application field of the application_snapshot. """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=255),
    )
    r""" Comment. Valid in POST. """

    components = fields.List(fields.Nested("netapp_ontap.models.application_snapshot_components.ApplicationSnapshotComponentsSchema", unknown=EXCLUDE), data_key="components")
    r""" The components field of the application_snapshot. """

    consistency_type = fields.Str(
        data_key="consistency_type",
        validate=enum_validation(['crash', 'application']),
    )
    r""" Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST.

Valid choices:

* crash
* application """

    create_time = fields.Str(
        data_key="create_time",
    )
    r""" Creation time """

    is_partial = fields.Boolean(
        data_key="is_partial",
    )
    r""" A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy. """

    name = fields.Str(
        data_key="name",
    )
    r""" The Snapshot copy name. Valid in POST. """

    svm = fields.Nested("netapp_ontap.models.application_component_svm.ApplicationComponentSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the application_snapshot. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The Snapshot copy UUID. Valid in URL. """

    @property
    def resource(self):
        return ApplicationSnapshot

    gettable_fields = [
        "links",
        "application",
        "comment",
        "components",
        "consistency_type",
        "create_time",
        "is_partial",
        "name",
        "svm",
        "uuid",
    ]
    """links,application,comment,components,consistency_type,create_time,is_partial,name,svm,uuid,"""

    patchable_fields = [
        "application",
        "comment",
        "consistency_type",
        "name",
        "svm",
    ]
    """application,comment,consistency_type,name,svm,"""

    postable_fields = [
        "application",
        "comment",
        "consistency_type",
        "name",
        "svm",
    ]
    """application,comment,consistency_type,name,svm,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ApplicationSnapshot.get_collection(fields=field)]
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
            raise NetAppRestError("ApplicationSnapshot modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ApplicationSnapshot(Resource):
    """Allows interaction with ApplicationSnapshot objects on the host"""

    _schema = ApplicationSnapshotSchema
    _path = "/api/application/applications/{application[uuid]}/snapshots"
    _keys = ["application.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves Snapshot copies of an application.
### Query examples
The following query returns all Snapshot copies from May 4, 2017 EST. For readability, the colon (`:`) is left in this example. For an actual call, they should be escaped as `%3A`.<br/><br/>
```
GET /application/applications/{application.uuid}/snapshots?create_time=2017-05-04T00:00:00-05:00..2017-05-04T23:59:59-05:00
```
<br/>The following query returns all Snapshot copies that have been flagged as _application consistent_.<br/><br/>
```
GET /application/applications/{application.uuid}/snapshots?consistency_type=application
```
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application snapshot show")
        def application_snapshot_show(
            application_uuid,
            comment: Choices.define(_get_field_list("comment"), cache_choices=True, inexact=True)=None,
            consistency_type: Choices.define(_get_field_list("consistency_type"), cache_choices=True, inexact=True)=None,
            create_time: Choices.define(_get_field_list("create_time"), cache_choices=True, inexact=True)=None,
            is_partial: Choices.define(_get_field_list("is_partial"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["comment", "consistency_type", "create_time", "is_partial", "name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ApplicationSnapshot resources

            Args:
                comment: Comment. Valid in POST.
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST.
                create_time: Creation time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: The Snapshot copy name. Valid in POST.
                uuid: The Snapshot copy UUID. Valid in URL.
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

            return ApplicationSnapshot.get_collection(
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
        """Returns a count of all ApplicationSnapshot resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["ApplicationSnapshot"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ApplicationSnapshot"], NetAppResponse]:
        r"""Creates a Snapshot copy of the application.
### Required properties
* `name`
### Recommended optional properties
* `consistency_type` - Track whether this snapshot is _application_ or _crash_ consistent.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
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
        records: Iterable["ApplicationSnapshot"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Delete a Snapshot copy of an application
### Query examples
Individual Snapshot copies can be destroyed with no query parameters, or a range of Snapshot copies can be destroyed at one time using a query.<br/>
The following query deletes all application Snapshot copies created before May 4, 2017<br/><br/>
```
DELETE /application/applications/{application.uuid}/snapshots?create_time=<2017-05-04T00:00:00-05:00
```

### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Snapshot copies of an application.
### Query examples
The following query returns all Snapshot copies from May 4, 2017 EST. For readability, the colon (`:`) is left in this example. For an actual call, they should be escaped as `%3A`.<br/><br/>
```
GET /application/applications/{application.uuid}/snapshots?create_time=2017-05-04T00:00:00-05:00..2017-05-04T23:59:59-05:00
```
<br/>The following query returns all Snapshot copies that have been flagged as _application consistent_.<br/><br/>
```
GET /application/applications/{application.uuid}/snapshots?consistency_type=application
```
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
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
* [`GET /application/applications/{uuid}/snapshots`](#operations-application-application_snapshot_create)
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
        r"""Creates a Snapshot copy of the application.
### Required properties
* `name`
### Recommended optional properties
* `consistency_type` - Track whether this snapshot is _application_ or _crash_ consistent.
### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)
* [`DOC /application`](#docs-application-overview)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application snapshot create")
        async def application_snapshot_create(
            application_uuid,
            links: dict = None,
            application: dict = None,
            comment: str = None,
            components: dict = None,
            consistency_type: str = None,
            create_time: str = None,
            is_partial: bool = None,
            name: str = None,
            svm: dict = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a ApplicationSnapshot resource

            Args:
                links: 
                application: 
                comment: Comment. Valid in POST.
                components: 
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST.
                create_time: Creation time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: The Snapshot copy name. Valid in POST.
                svm: 
                uuid: The Snapshot copy UUID. Valid in URL.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if application is not None:
                kwargs["application"] = application
            if comment is not None:
                kwargs["comment"] = comment
            if components is not None:
                kwargs["components"] = components
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

            resource = ApplicationSnapshot(
                application_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ApplicationSnapshot: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Delete a Snapshot copy of an application
### Query examples
Individual Snapshot copies can be destroyed with no query parameters, or a range of Snapshot copies can be destroyed at one time using a query.<br/>
The following query deletes all application Snapshot copies created before May 4, 2017<br/><br/>
```
DELETE /application/applications/{application.uuid}/snapshots?create_time=<2017-05-04T00:00:00-05:00
```

### Learn more
* [`DOC /application/applications/{application.uuid}/snapshots`](#docs-application-application_applications_{application.uuid}_snapshots)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application snapshot delete")
        async def application_snapshot_delete(
            application_uuid,
            comment: str = None,
            consistency_type: str = None,
            create_time: str = None,
            is_partial: bool = None,
            name: str = None,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a ApplicationSnapshot resource

            Args:
                comment: Comment. Valid in POST.
                consistency_type: Consistency type. This is for categorization purposes only. A Snapshot copy should not be set to 'application consistent' unless the host application is quiesced for the Snapshot copy. Valid in POST.
                create_time: Creation time
                is_partial: A partial Snapshot copy means that not all volumes in an application component were included in the Snapshot copy.
                name: The Snapshot copy name. Valid in POST.
                uuid: The Snapshot copy UUID. Valid in URL.
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

            if hasattr(ApplicationSnapshot, "find"):
                resource = ApplicationSnapshot.find(
                    application_uuid,
                    **kwargs
                )
            else:
                resource = ApplicationSnapshot(application_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ApplicationSnapshot: %s" % err)

    def restore(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Restore an application snapshot<br/>
Restoring an application Snapshot copy reverts all storage elements in the Snapshot copy to the state in which the Snapshot copy was in when the Snapshot copy was taken. This restoration does not apply to access settings that might have changed since the Snapshot copy was created.
### Learn more
* [`DOC /application`](#docs-application-overview)
* [`Asynchronous operations`](#Synchronous_and_asynchronous_operations)
"""
        return super()._action(
            "restore", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    restore.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)

