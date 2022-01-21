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


__all__ = ["ExportClient", "ExportClientSchema"]
__pdoc__ = {
    "ExportClientSchema.resource": False,
    "ExportClient.export_client_show": False,
    "ExportClient.export_client_create": False,
    "ExportClient.export_client_modify": False,
    "ExportClient.export_client_delete": False,
}


class ExportClientSchema(ResourceSchema):
    """The fields of the ExportClient object"""

    match = fields.Str(
        data_key="match",
    )
    r""" Client Match Hostname, IP Address, Netgroup, or Domain.
You can specify the match as a string value in any of the
          following formats:

* As a hostname; for instance, host1
* As an IPv4 address; for instance, 10.1.12.24
* As an IPv6 address; for instance, fd20:8b1e:b255:4071::100:1
* As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24
* As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64
* As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0
* As a netgroup, with the netgroup name preceded by the @ character; for instance, @eng
* As a domain name preceded by the . character; for instance, .example.com


Example: 0.0.0.0/0 """

    policy = fields.Nested("netapp_ontap.models.export_client_policy.ExportClientPolicySchema", data_key="policy", unknown=EXCLUDE)
    r""" The policy field of the export_client. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the export_client. """

    @property
    def resource(self):
        return ExportClient

    gettable_fields = [
        "index",
        "match",
        "policy",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """index,match,policy,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "match",
        "policy",
        "svm.name",
        "svm.uuid",
    ]
    """match,policy,svm.name,svm.uuid,"""

    postable_fields = [
        "match",
        "policy",
        "svm.name",
        "svm.uuid",
    ]
    """match,policy,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ExportClient.get_collection(fields=field)]
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
            raise NetAppRestError("ExportClient modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ExportClient(Resource):
    """Allows interaction with ExportClient objects on the host"""

    _schema = ExportClientSchema
    _path = "/api/protocols/nfs/export-policies/{policy[id]}/rules/{export_rule[index]}/clients"
    _keys = ["policy.id", "export_rule.index", "match"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves export policy rule clients.
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export client show")
        def export_client_show(
            index,
            policy_id,
            match: Choices.define(_get_field_list("match"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["match", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ExportClient resources

            Args:
                match: Client Match Hostname, IP Address, Netgroup, or Domain. You can specify the match as a string value in any of the           following formats: * As a hostname; for instance, host1 * As an IPv4 address; for instance, 10.1.12.24 * As an IPv6 address; for instance, fd20:8b1e:b255:4071::100:1 * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a netgroup, with the netgroup name preceded by the @ character; for instance, @eng * As a domain name preceded by the . character; for instance, .example.com 
            """

            kwargs = {}
            if match is not None:
                kwargs["match"] = match
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ExportClient.get_collection(
                index,
                policy_id,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ExportClient resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["ExportClient"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ExportClient"], NetAppResponse]:
        r"""Creates an export policy rule client
### Required properties
* `policy.id` - Existing export policy that contains export policy rules for the client being added.
* `index`  - Existing export policy rule for which to create an export client.
* `match`  - Base name for the export policy client.
### Related ONTAP commands
* `vserver export-policy rule add-clientmatches`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
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
        records: Iterable["ExportClient"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy client
### Related ONTAP commands
* `vserver export-policy rule remove-clientmatches`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves export policy rule clients.
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)


    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates an export policy rule client
### Required properties
* `policy.id` - Existing export policy that contains export policy rules for the client being added.
* `index`  - Existing export policy rule for which to create an export client.
* `match`  - Base name for the export policy client.
### Related ONTAP commands
* `vserver export-policy rule add-clientmatches`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export client create")
        async def export_client_create(
            index,
            policy_id,
            match: str = None,
            policy: dict = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a ExportClient resource

            Args:
                match: Client Match Hostname, IP Address, Netgroup, or Domain. You can specify the match as a string value in any of the           following formats: * As a hostname; for instance, host1 * As an IPv4 address; for instance, 10.1.12.24 * As an IPv6 address; for instance, fd20:8b1e:b255:4071::100:1 * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a netgroup, with the netgroup name preceded by the @ character; for instance, @eng * As a domain name preceded by the . character; for instance, .example.com 
                policy: 
                svm: 
            """

            kwargs = {}
            if match is not None:
                kwargs["match"] = match
            if policy is not None:
                kwargs["policy"] = policy
            if svm is not None:
                kwargs["svm"] = svm

            resource = ExportClient(
                index,
                policy_id,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ExportClient: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy client
### Related ONTAP commands
* `vserver export-policy rule remove-clientmatches`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export client delete")
        async def export_client_delete(
            index,
            policy_id,
            match: str = None,
        ) -> None:
            """Delete an instance of a ExportClient resource

            Args:
                match: Client Match Hostname, IP Address, Netgroup, or Domain. You can specify the match as a string value in any of the           following formats: * As a hostname; for instance, host1 * As an IPv4 address; for instance, 10.1.12.24 * As an IPv6 address; for instance, fd20:8b1e:b255:4071::100:1 * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a netgroup, with the netgroup name preceded by the @ character; for instance, @eng * As a domain name preceded by the . character; for instance, .example.com 
            """

            kwargs = {}
            if match is not None:
                kwargs["match"] = match

            if hasattr(ExportClient, "find"):
                resource = ExportClient.find(
                    index,
                    policy_id,
                    **kwargs
                )
            else:
                resource = ExportClient(index,policy_id,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ExportClient: %s" % err)


