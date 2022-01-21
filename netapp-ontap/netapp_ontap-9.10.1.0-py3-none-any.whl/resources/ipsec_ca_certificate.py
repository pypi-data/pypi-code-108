r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The following APIs can be used to add/remove/retrieve the IPsec CA certficates:

* Creation Post: POST security/ipsec/ca-certificates
* Collection Get: GET security/ipsec/ca-certificates
* Instance Get: GET security/ipsec/ca-certificates/{certificate.uuid}
* Instance Delete: DELETE security/ipsec/ca-certificates/{certificate.uuid}
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


__all__ = ["IpsecCaCertificate", "IpsecCaCertificateSchema"]
__pdoc__ = {
    "IpsecCaCertificateSchema.resource": False,
    "IpsecCaCertificate.ipsec_ca_certificate_show": False,
    "IpsecCaCertificate.ipsec_ca_certificate_create": False,
    "IpsecCaCertificate.ipsec_ca_certificate_modify": False,
    "IpsecCaCertificate.ipsec_ca_certificate_delete": False,
}


class IpsecCaCertificateSchema(ResourceSchema):
    """The fields of the IpsecCaCertificate object"""

    certificate = fields.Nested("netapp_ontap.models.ipsec_ca_certificate_uuid.IpsecCaCertificateUuidSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the ipsec_ca_certificate. """

    scope = fields.Str(
        data_key="scope",
    )
    r""" The scope field of the ipsec_ca_certificate. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ipsec_ca_certificate. """

    @property
    def resource(self):
        return IpsecCaCertificate

    gettable_fields = [
        "certificate",
        "scope",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """certificate,scope,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "scope",
    ]
    """scope,"""

    postable_fields = [
        "certificate",
        "scope",
        "svm.name",
        "svm.uuid",
    ]
    """certificate,scope,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in IpsecCaCertificate.get_collection(fields=field)]
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
            raise NetAppRestError("IpsecCaCertificate modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class IpsecCaCertificate(Resource):
    """Allows interaction with IpsecCaCertificate objects on the host"""

    _schema = IpsecCaCertificateSchema
    _path = "/api/security/ipsec/ca-certificates"
    _keys = ["certificate.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of IPsec CA certificates configured for cluster and all SVMs.
### Related ONTAP commands
* `security ipsec ca-certificate show`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec ca certificate show")
        def ipsec_ca_certificate_show(
            fields: List[Choices.define(["scope", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of IpsecCaCertificate resources

            Args:
                scope: 
            """

            kwargs = {}
            if scope is not None:
                kwargs["scope"] = scope
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return IpsecCaCertificate.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all IpsecCaCertificate resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["IpsecCaCertificate"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["IpsecCaCertificate"], NetAppResponse]:
        r"""Add CA certificate to IPsec. The CA certificate should already be installed on the cluster prior to adding them to IPsec.
The CA certificate can be installed on the cluster using the /security/certificates endpoint.
The svm.uuid or svm.name should not be supplied for certificates that have a scope of cluster.
### Related ONTAP commands
* `security ipsec ca-certificate add`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["IpsecCaCertificate"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the IPsec CA certificate with the specified UUID from IPsec.
### Related ONTAP commands
* `security ipsec ca-certificate remove`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of IPsec CA certificates configured for cluster and all SVMs.
### Related ONTAP commands
* `security ipsec ca-certificate show`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific CA certificate configured for IPsec.
### Related ONTAP commands
* `security ipsec ca-certificate show`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
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
        r"""Add CA certificate to IPsec. The CA certificate should already be installed on the cluster prior to adding them to IPsec.
The CA certificate can be installed on the cluster using the /security/certificates endpoint.
The svm.uuid or svm.name should not be supplied for certificates that have a scope of cluster.
### Related ONTAP commands
* `security ipsec ca-certificate add`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec ca certificate create")
        async def ipsec_ca_certificate_create(
        ) -> ResourceTable:
            """Create an instance of a IpsecCaCertificate resource

            Args:
                certificate: 
                scope: 
                svm: 
            """

            kwargs = {}
            if certificate is not None:
                kwargs["certificate"] = certificate
            if scope is not None:
                kwargs["scope"] = scope
            if svm is not None:
                kwargs["svm"] = svm

            resource = IpsecCaCertificate(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create IpsecCaCertificate: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the IPsec CA certificate with the specified UUID from IPsec.
### Related ONTAP commands
* `security ipsec ca-certificate remove`

### Learn more
* [`DOC /security/ipsec/ca-certificates`](#docs-security-security_ipsec_ca-certificates)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec ca certificate delete")
        async def ipsec_ca_certificate_delete(
        ) -> None:
            """Delete an instance of a IpsecCaCertificate resource

            Args:
                scope: 
            """

            kwargs = {}
            if scope is not None:
                kwargs["scope"] = scope

            if hasattr(IpsecCaCertificate, "find"):
                resource = IpsecCaCertificate.find(
                    **kwargs
                )
            else:
                resource = IpsecCaCertificate()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete IpsecCaCertificate: %s" % err)


