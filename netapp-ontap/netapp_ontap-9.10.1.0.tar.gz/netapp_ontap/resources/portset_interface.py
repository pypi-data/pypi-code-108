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


__all__ = ["PortsetInterface", "PortsetInterfaceSchema"]
__pdoc__ = {
    "PortsetInterfaceSchema.resource": False,
    "PortsetInterface.portset_interface_show": False,
    "PortsetInterface.portset_interface_create": False,
    "PortsetInterface.portset_interface_modify": False,
    "PortsetInterface.portset_interface_delete": False,
}


class PortsetInterfaceSchema(ResourceSchema):
    """The fields of the PortsetInterface object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the portset_interface. """

    fc = fields.Nested("netapp_ontap.resources.fc_interface.FcInterfaceSchema", data_key="fc", unknown=EXCLUDE)
    r""" The fc field of the portset_interface. """

    ip = fields.Nested("netapp_ontap.resources.ip_interface.IpInterfaceSchema", data_key="ip", unknown=EXCLUDE)
    r""" The ip field of the portset_interface. """

    portset = fields.Nested("netapp_ontap.models.portset_interface_portset.PortsetInterfacePortsetSchema", data_key="portset", unknown=EXCLUDE)
    r""" The portset field of the portset_interface. """

    records = fields.List(fields.Nested("netapp_ontap.models.portset_interface_no_records.PortsetInterfaceNoRecordsSchema", unknown=EXCLUDE), data_key="records")
    r""" An array of network interfaces specified to add multiple interfaces to a portset in a single API call. Valid in POST only and not allowed when the `fc` or `ip` property is used. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the network interface.


Example: 4ea7a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return PortsetInterface

    gettable_fields = [
        "links",
        "fc.links",
        "fc.name",
        "fc.uuid",
        "fc.wwpn",
        "ip.links",
        "ip.ip",
        "ip.name",
        "ip.uuid",
        "portset",
        "uuid",
    ]
    """links,fc.links,fc.name,fc.uuid,fc.wwpn,ip.links,ip.ip,ip.name,ip.uuid,portset,uuid,"""

    patchable_fields = [
        "portset",
    ]
    """portset,"""

    postable_fields = [
        "fc.name",
        "fc.uuid",
        "ip.ip",
        "ip.name",
        "ip.uuid",
        "portset",
        "records",
    ]
    """fc.name,fc.uuid,ip.ip,ip.name,ip.uuid,portset,records,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in PortsetInterface.get_collection(fields=field)]
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
            raise NetAppRestError("PortsetInterface modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class PortsetInterface(Resource):
    """Allows interaction with PortsetInterface objects on the host"""

    _schema = PortsetInterfaceSchema
    _path = "/api/protocols/san/portsets/{portset[uuid]}/interfaces"
    _keys = ["portset.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves interfaces of a portset.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset interface show")
        def portset_interface_show(
            portset_uuid,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of PortsetInterface resources

            Args:
                uuid: The unique identifier of the network interface. 
            """

            kwargs = {}
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return PortsetInterface.get_collection(
                portset_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all PortsetInterface resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["PortsetInterface"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["PortsetInterface"], NetAppResponse]:
        r"""Adds one or more interfaces to a portset.
### Required properties
* `fc`, `ip` or `records` - Network interface(s) to add to the portset.
### Related ONTAP commands
* `lun portset add`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
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
        records: Iterable["PortsetInterface"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a network interface from a portset.
### Related ONTAP commands
* `lun portset remove`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves interfaces of a portset.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a network interface of a portset.
### Related ONTAP commands
* `lun portset show`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
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
        r"""Adds one or more interfaces to a portset.
### Required properties
* `fc`, `ip` or `records` - Network interface(s) to add to the portset.
### Related ONTAP commands
* `lun portset add`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset interface create")
        async def portset_interface_create(
            portset_uuid,
            links: dict = None,
            fc: dict = None,
            ip: dict = None,
            portset: dict = None,
            records: dict = None,
            uuid: str = None,
        ) -> ResourceTable:
            """Create an instance of a PortsetInterface resource

            Args:
                links: 
                fc: 
                ip: 
                portset: 
                records: An array of network interfaces specified to add multiple interfaces to a portset in a single API call. Valid in POST only and not allowed when the `fc` or `ip` property is used. 
                uuid: The unique identifier of the network interface. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if fc is not None:
                kwargs["fc"] = fc
            if ip is not None:
                kwargs["ip"] = ip
            if portset is not None:
                kwargs["portset"] = portset
            if records is not None:
                kwargs["records"] = records
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = PortsetInterface(
                portset_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create PortsetInterface: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a network interface from a portset.
### Related ONTAP commands
* `lun portset remove`
### Learn more
* [`DOC /protocols/san/portsets`](#docs-SAN-protocols_san_portsets)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="portset interface delete")
        async def portset_interface_delete(
            portset_uuid,
            uuid: str = None,
        ) -> None:
            """Delete an instance of a PortsetInterface resource

            Args:
                uuid: The unique identifier of the network interface. 
            """

            kwargs = {}
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(PortsetInterface, "find"):
                resource = PortsetInterface.find(
                    portset_uuid,
                    **kwargs
                )
            else:
                resource = PortsetInterface(portset_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete PortsetInterface: %s" % err)


