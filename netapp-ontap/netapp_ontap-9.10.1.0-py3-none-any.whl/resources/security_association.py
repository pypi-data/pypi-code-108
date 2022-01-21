r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview

* Collection Get: GET security/ipsec/security-associations
* Instance Get: GET security/ipsec/security-associations/uuid
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


__all__ = ["SecurityAssociation", "SecurityAssociationSchema"]
__pdoc__ = {
    "SecurityAssociationSchema.resource": False,
    "SecurityAssociation.security_association_show": False,
    "SecurityAssociation.security_association_create": False,
    "SecurityAssociation.security_association_modify": False,
    "SecurityAssociation.security_association_delete": False,
}


class SecurityAssociationSchema(ResourceSchema):
    """The fields of the SecurityAssociation object"""

    cipher_suite = fields.Str(
        data_key="cipher_suite",
        validate=enum_validation(['suite_aescbc', 'suiteb_gcm256', 'suiteb_gmac256']),
    )
    r""" Cipher suite for the security association.

Valid choices:

* suite_aescbc
* suiteb_gcm256
* suiteb_gmac256 """

    ike = fields.Nested("netapp_ontap.models.security_association_ike.SecurityAssociationIkeSchema", data_key="ike", unknown=EXCLUDE)
    r""" The ike field of the security_association. """

    ipsec = fields.Nested("netapp_ontap.models.security_association_ipsec.SecurityAssociationIpsecSchema", data_key="ipsec", unknown=EXCLUDE)
    r""" The ipsec field of the security_association. """

    lifetime = Size(
        data_key="lifetime",
    )
    r""" Lifetime for the security association in seconds. """

    local_address = fields.Str(
        data_key="local_address",
    )
    r""" Local address of the security association. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the security_association. """

    policy_name = fields.Str(
        data_key="policy_name",
    )
    r""" Policy name for the security association. """

    remote_address = fields.Str(
        data_key="remote_address",
    )
    r""" Remote address of the security association. """

    scope = fields.Str(
        data_key="scope",
    )
    r""" The scope field of the security_association. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the security_association. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['ipsec', 'ike']),
    )
    r""" Type of security association, it can be IPsec or IKE (Internet Key Exchange).

Valid choices:

* ipsec
* ike """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier of the security association. """

    @property
    def resource(self):
        return SecurityAssociation

    gettable_fields = [
        "cipher_suite",
        "ike",
        "ipsec",
        "lifetime",
        "local_address",
        "node.links",
        "node.name",
        "node.uuid",
        "policy_name",
        "remote_address",
        "scope",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "uuid",
    ]
    """cipher_suite,ike,ipsec,lifetime,local_address,node.links,node.name,node.uuid,policy_name,remote_address,scope,svm.links,svm.name,svm.uuid,type,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityAssociation.get_collection(fields=field)]
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
            raise NetAppRestError("SecurityAssociation modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityAssociation(Resource):
    r""" Security association object for IPsec security association and IKE (Internet Key Exchange) security association. """

    _schema = SecurityAssociationSchema
    _path = "/api/security/ipsec/security-associations"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the IPsec and IKE (Internet Key Exchange) security associations.
### Related ONTAP commands
* `security ipsec show-ipsecsa`
* `security ipsec show-ikesa`

### Learn more
* [`DOC /security/ipsec/security-associations`](#docs-security-security_ipsec_security-associations)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security association show")
        def security_association_show(
            fields: List[Choices.define(["cipher_suite", "lifetime", "local_address", "policy_name", "remote_address", "scope", "type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SecurityAssociation resources

            Args:
                cipher_suite: Cipher suite for the security association.
                lifetime: Lifetime for the security association in seconds.
                local_address: Local address of the security association.
                policy_name: Policy name for the security association.
                remote_address: Remote address of the security association.
                scope: 
                type: Type of security association, it can be IPsec or IKE (Internet Key Exchange).
                uuid: Unique identifier of the security association.
            """

            kwargs = {}
            if cipher_suite is not None:
                kwargs["cipher_suite"] = cipher_suite
            if lifetime is not None:
                kwargs["lifetime"] = lifetime
            if local_address is not None:
                kwargs["local_address"] = local_address
            if policy_name is not None:
                kwargs["policy_name"] = policy_name
            if remote_address is not None:
                kwargs["remote_address"] = remote_address
            if scope is not None:
                kwargs["scope"] = scope
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SecurityAssociation.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SecurityAssociation resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the IPsec and IKE (Internet Key Exchange) security associations.
### Related ONTAP commands
* `security ipsec show-ipsecsa`
* `security ipsec show-ikesa`

### Learn more
* [`DOC /security/ipsec/security-associations`](#docs-security-security_ipsec_security-associations)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific IPsec or IKE (Internet Key Exchange) security association.
### Related ONTAP commands
* `security ipsec show-ipsecsa`
* `security ipsec show-ikesa`

### Learn more
* [`DOC /security/ipsec/security-associations`](#docs-security-security_ipsec_security-associations)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





