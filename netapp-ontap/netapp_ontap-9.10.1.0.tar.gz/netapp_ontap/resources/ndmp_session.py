r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

You can use this API to manage diagnostic information on NDMP sessions belonging to a specific SVM in the case of SVM-scope or to a specific node in the case of node-scope.
### Examples
Retrieves NDMP session details under node-scope:
<br/>
```
GET "/api/protocols/ndmp/sessions/9b372ce7-3a4b-11e9-a7f8-0050568e3d73/2000"
```
<br/>
Retrieves NDMP session details under SVM-scope:
<br/>
```
GET "/api/protocols/ndmp/sessions/13bb2092-458b-11e9-9c06-0050568ea604/2000:4000"
```
<br/>
Deletes NDMP session details under node-scope:
<br/>
```
DELETE "/api/protocols/ndmp/sessions/9b372ce7-3a4b-11e9-a7f8-0050568e3d73/2000"
```
<br/>
Deletes NDMP session details under SVM-scope:
<br/>
```
DELETE "/api/protocols/ndmp/sessions/13bb2092-458b-11e9-9c06-0050568ea604/2000:4000"
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


__all__ = ["NdmpSession", "NdmpSessionSchema"]
__pdoc__ = {
    "NdmpSessionSchema.resource": False,
    "NdmpSession.ndmp_session_show": False,
    "NdmpSession.ndmp_session_create": False,
    "NdmpSession.ndmp_session_modify": False,
    "NdmpSession.ndmp_session_delete": False,
}


class NdmpSessionSchema(ResourceSchema):
    """The fields of the NdmpSession object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ndmp_session. """

    backup_engine = fields.Str(
        data_key="backup_engine",
        validate=enum_validation(['dump', 'smtape']),
    )
    r""" Indicates the NDMP backup engine.

Valid choices:

* dump
* smtape """

    client_address = fields.Str(
        data_key="client_address",
    )
    r""" Indicates the NDMP client address. """

    client_port = Size(
        data_key="client_port",
    )
    r""" Indicates the NDMP client port. """

    data = fields.Nested("netapp_ontap.models.ndmp_data.NdmpDataSchema", data_key="data", unknown=EXCLUDE)
    r""" Information about the NDMP data server. """

    data_path = fields.Str(
        data_key="data_path",
    )
    r""" Indicates the NDMP backup or restore path.

Example: /vserver1/vol1 """

    id = fields.Str(
        data_key="id",
    )
    r""" NDMP session identifier. """

    mover = fields.Nested("netapp_ontap.models.ndmp_mover.NdmpMoverSchema", data_key="mover", unknown=EXCLUDE)
    r""" Information about the NDMP mover. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the ndmp_session. """

    scsi = fields.Nested("netapp_ontap.models.ndmp_scsi.NdmpScsiSchema", data_key="scsi", unknown=EXCLUDE)
    r""" Information about the NDMP SCSI server. """

    source_address = fields.Str(
        data_key="source_address",
    )
    r""" Indicates the NDMP local address on which connection was established. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ndmp_session. """

    tape_device = fields.Str(
        data_key="tape_device",
    )
    r""" Indicates the NDMP tape device.

Example: nrst0a """

    tape_mode = fields.Str(
        data_key="tape_mode",
    )
    r""" Indicates the NDMP tape device mode of operation. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The NDMP node or SVM UUID based on whether NDMP is operating in node-scope or SVM-scope mode. """

    @property
    def resource(self):
        return NdmpSession

    gettable_fields = [
        "links",
        "backup_engine",
        "client_address",
        "client_port",
        "data",
        "data_path",
        "id",
        "mover",
        "node.links",
        "node.name",
        "node.uuid",
        "scsi",
        "source_address",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "tape_device",
        "tape_mode",
        "uuid",
    ]
    """links,backup_engine,client_address,client_port,data,data_path,id,mover,node.links,node.name,node.uuid,scsi,source_address,svm.links,svm.name,svm.uuid,tape_device,tape_mode,uuid,"""

    patchable_fields = [
        "backup_engine",
        "client_address",
        "client_port",
        "data",
        "data_path",
        "id",
        "mover",
        "node.name",
        "node.uuid",
        "scsi",
        "source_address",
        "svm.name",
        "svm.uuid",
        "tape_device",
        "tape_mode",
        "uuid",
    ]
    """backup_engine,client_address,client_port,data,data_path,id,mover,node.name,node.uuid,scsi,source_address,svm.name,svm.uuid,tape_device,tape_mode,uuid,"""

    postable_fields = [
        "backup_engine",
        "client_address",
        "client_port",
        "data",
        "data_path",
        "id",
        "mover",
        "node.name",
        "node.uuid",
        "scsi",
        "source_address",
        "svm.name",
        "svm.uuid",
        "tape_device",
        "tape_mode",
        "uuid",
    ]
    """backup_engine,client_address,client_port,data,data_path,id,mover,node.name,node.uuid,scsi,source_address,svm.name,svm.uuid,tape_device,tape_mode,uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NdmpSession.get_collection(fields=field)]
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
            raise NetAppRestError("NdmpSession modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NdmpSession(Resource):
    """Allows interaction with NdmpSession objects on the host"""

    _schema = NdmpSessionSchema
    _path = "/api/protocols/ndmp/sessions"
    _keys = ["owner.uuid", "session.id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of NDMP sessions. In the case of SVM-scope, if this API is executed on a data IP, it displays the list of NDMP sessions under the specified SVM; otherwise it displays the list of NDMP sessions for all the SVMs under the cluster. In the case of node-scope, it displays the list of NDMP sessions for all nodes.
### Related ONTAP commands
* `vserver services ndmp probe`
* `system services ndmp probe`
### Learn more
* [`DOC /protocols/ndmp/sessions`](#docs-ndmp-protocols_ndmp_sessions)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ndmp session show")
        def ndmp_session_show(
            fields: List[Choices.define(["backup_engine", "client_address", "client_port", "data_path", "id", "source_address", "tape_device", "tape_mode", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NdmpSession resources

            Args:
                backup_engine: Indicates the NDMP backup engine.
                client_address: Indicates the NDMP client address.
                client_port: Indicates the NDMP client port.
                data_path: Indicates the NDMP backup or restore path.
                id: NDMP session identifier.
                source_address: Indicates the NDMP local address on which connection was established.
                tape_device: Indicates the NDMP tape device.
                tape_mode: Indicates the NDMP tape device mode of operation.
                uuid: The NDMP node or SVM UUID based on whether NDMP is operating in node-scope or SVM-scope mode.
            """

            kwargs = {}
            if backup_engine is not None:
                kwargs["backup_engine"] = backup_engine
            if client_address is not None:
                kwargs["client_address"] = client_address
            if client_port is not None:
                kwargs["client_port"] = client_port
            if data_path is not None:
                kwargs["data_path"] = data_path
            if id is not None:
                kwargs["id"] = id
            if source_address is not None:
                kwargs["source_address"] = source_address
            if tape_device is not None:
                kwargs["tape_device"] = tape_device
            if tape_mode is not None:
                kwargs["tape_mode"] = tape_mode
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NdmpSession.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NdmpSession resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)



    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["NdmpSession"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific NDMP session.
### Related ONTAP commands
* `vserver services ndmp kill`
* `system services ndmp kill`
### Learn more
* [`DOC /protocols/ndmp/sessions`](#docs-ndmp-protocols_ndmp_sessions)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of NDMP sessions. In the case of SVM-scope, if this API is executed on a data IP, it displays the list of NDMP sessions under the specified SVM; otherwise it displays the list of NDMP sessions for all the SVMs under the cluster. In the case of node-scope, it displays the list of NDMP sessions for all nodes.
### Related ONTAP commands
* `vserver services ndmp probe`
* `system services ndmp probe`
### Learn more
* [`DOC /protocols/ndmp/sessions`](#docs-ndmp-protocols_ndmp_sessions)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the details of a specific NDMP session.
### Related ONTAP commands
* `vserver services ndmp probe`
* `system services ndmp probe`
### Learn more
* [`DOC /protocols/ndmp/sessions`](#docs-ndmp-protocols_ndmp_sessions)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)



    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific NDMP session.
### Related ONTAP commands
* `vserver services ndmp kill`
* `system services ndmp kill`
### Learn more
* [`DOC /protocols/ndmp/sessions`](#docs-ndmp-protocols_ndmp_sessions)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ndmp session delete")
        async def ndmp_session_delete(
        ) -> None:
            """Delete an instance of a NdmpSession resource

            Args:
                backup_engine: Indicates the NDMP backup engine.
                client_address: Indicates the NDMP client address.
                client_port: Indicates the NDMP client port.
                data_path: Indicates the NDMP backup or restore path.
                id: NDMP session identifier.
                source_address: Indicates the NDMP local address on which connection was established.
                tape_device: Indicates the NDMP tape device.
                tape_mode: Indicates the NDMP tape device mode of operation.
                uuid: The NDMP node or SVM UUID based on whether NDMP is operating in node-scope or SVM-scope mode.
            """

            kwargs = {}
            if backup_engine is not None:
                kwargs["backup_engine"] = backup_engine
            if client_address is not None:
                kwargs["client_address"] = client_address
            if client_port is not None:
                kwargs["client_port"] = client_port
            if data_path is not None:
                kwargs["data_path"] = data_path
            if id is not None:
                kwargs["id"] = id
            if source_address is not None:
                kwargs["source_address"] = source_address
            if tape_device is not None:
                kwargs["tape_device"] = tape_device
            if tape_mode is not None:
                kwargs["tape_mode"] = tape_mode
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(NdmpSession, "find"):
                resource = NdmpSession.find(
                    **kwargs
                )
            else:
                resource = NdmpSession()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NdmpSession: %s" % err)


