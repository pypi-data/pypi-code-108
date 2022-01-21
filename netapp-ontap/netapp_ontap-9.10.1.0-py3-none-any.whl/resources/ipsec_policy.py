r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The following operations are supported:

* Collection Get: GET security/ipsec/policies
* Creation Post: POST security/ipsec/policies
* Instance Get: GET security/ipsec/policies/uuid
* Instance Patch: PATCH security/ipsec/policies/uuid
* Instance Delete: DELETE security/ipsec/policies/uuid
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


__all__ = ["IpsecPolicy", "IpsecPolicySchema"]
__pdoc__ = {
    "IpsecPolicySchema.resource": False,
    "IpsecPolicy.ipsec_policy_show": False,
    "IpsecPolicy.ipsec_policy_create": False,
    "IpsecPolicy.ipsec_policy_modify": False,
    "IpsecPolicy.ipsec_policy_delete": False,
}


class IpsecPolicySchema(ResourceSchema):
    """The fields of the IpsecPolicy object"""

    action = fields.Str(
        data_key="action",
        validate=enum_validation(['bypass', 'discard', 'esp_transport', 'esp_udp']),
    )
    r""" Action for the IPsec policy.

Valid choices:

* bypass
* discard
* esp_transport
* esp_udp """

    authentication_method = fields.Str(
        data_key="authentication_method",
        validate=enum_validation(['none', 'psk', 'pki']),
    )
    r""" Authentication method for the IPsec policy.

Valid choices:

* none
* psk
* pki """

    certificate = fields.Nested("netapp_ontap.resources.security_certificate.SecurityCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the ipsec_policy. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Indicates whether or not the policy is enabled. """

    ipspace = fields.Nested("netapp_ontap.resources.ipspace.IpspaceSchema", data_key="ipspace", unknown=EXCLUDE)
    r""" The ipspace field of the ipsec_policy. """

    local_endpoint = fields.Nested("netapp_ontap.models.ipsec_endpoint.IpsecEndpointSchema", data_key="local_endpoint", unknown=EXCLUDE)
    r""" The local_endpoint field of the ipsec_policy. """

    local_identity = fields.Str(
        data_key="local_identity",
    )
    r""" Local Identity """

    name = fields.Str(
        data_key="name",
    )
    r""" IPsec policy name. """

    protocol = fields.Str(
        data_key="protocol",
    )
    r""" Lower layer protocol to be covered by the IPsec policy.

Example: 17 """

    remote_endpoint = fields.Nested("netapp_ontap.models.ipsec_endpoint.IpsecEndpointSchema", data_key="remote_endpoint", unknown=EXCLUDE)
    r""" The remote_endpoint field of the ipsec_policy. """

    remote_identity = fields.Str(
        data_key="remote_identity",
    )
    r""" Remote Identity """

    scope = fields.Str(
        data_key="scope",
    )
    r""" The scope field of the ipsec_policy. """

    secret_key = fields.Str(
        data_key="secret_key",
        validate=len_validation(minimum=18, maximum=128),
    )
    r""" Pre-shared key for IKE negotiation. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ipsec_policy. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier of the IPsec policy.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return IpsecPolicy

    gettable_fields = [
        "authentication_method",
        "certificate.links",
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "ipspace.links",
        "ipspace.name",
        "ipspace.uuid",
        "local_endpoint",
        "local_identity",
        "name",
        "protocol",
        "remote_endpoint",
        "remote_identity",
        "scope",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """authentication_method,certificate.links,certificate.name,certificate.uuid,enabled,ipspace.links,ipspace.name,ipspace.uuid,local_endpoint,local_identity,name,protocol,remote_endpoint,remote_identity,scope,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "authentication_method",
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "ipspace.name",
        "ipspace.uuid",
        "local_endpoint",
        "local_identity",
        "name",
        "protocol",
        "remote_endpoint",
        "remote_identity",
        "scope",
        "svm.name",
        "svm.uuid",
    ]
    """authentication_method,certificate.name,certificate.uuid,enabled,ipspace.name,ipspace.uuid,local_endpoint,local_identity,name,protocol,remote_endpoint,remote_identity,scope,svm.name,svm.uuid,"""

    postable_fields = [
        "action",
        "authentication_method",
        "certificate.name",
        "certificate.uuid",
        "enabled",
        "ipspace.name",
        "ipspace.uuid",
        "local_endpoint",
        "local_identity",
        "name",
        "protocol",
        "remote_endpoint",
        "remote_identity",
        "scope",
        "secret_key",
        "svm.name",
        "svm.uuid",
    ]
    """action,authentication_method,certificate.name,certificate.uuid,enabled,ipspace.name,ipspace.uuid,local_endpoint,local_identity,name,protocol,remote_endpoint,remote_identity,scope,secret_key,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in IpsecPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("IpsecPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class IpsecPolicy(Resource):
    r""" IPsec policy object. """

    _schema = IpsecPolicySchema
    _path = "/api/security/ipsec/policies"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of IPsec policies.
### Related ONTAP commands
* `security ipsec policy show`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec policy show")
        def ipsec_policy_show(
            fields: List[Choices.define(["action", "authentication_method", "enabled", "local_identity", "name", "protocol", "remote_identity", "scope", "secret_key", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of IpsecPolicy resources

            Args:
                action: Action for the IPsec policy.
                authentication_method: Authentication method for the IPsec policy.
                enabled: Indicates whether or not the policy is enabled.
                local_identity: Local Identity
                name: IPsec policy name.
                protocol: Lower layer protocol to be covered by the IPsec policy.
                remote_identity: Remote Identity
                scope: 
                secret_key: Pre-shared key for IKE negotiation.
                uuid: Unique identifier of the IPsec policy.
            """

            kwargs = {}
            if action is not None:
                kwargs["action"] = action
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if enabled is not None:
                kwargs["enabled"] = enabled
            if local_identity is not None:
                kwargs["local_identity"] = local_identity
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if remote_identity is not None:
                kwargs["remote_identity"] = remote_identity
            if scope is not None:
                kwargs["scope"] = scope
            if secret_key is not None:
                kwargs["secret_key"] = secret_key
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return IpsecPolicy.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all IpsecPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["IpsecPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific IPsec policy.
### Related ONTAP commands
* `security ipsec policy modify`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["IpsecPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["IpsecPolicy"], NetAppResponse]:
        r"""Creates an IPsec policy.
### Related ONTAP commands
* `security ipsec policy create`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["IpsecPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific IPsec policy.
### Related ONTAP commands
* `security ipsec policy delete`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of IPsec policies.
### Related ONTAP commands
* `security ipsec policy show`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific IPsec policy.
### Related ONTAP commands
* `security ipsec policy show`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
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
        r"""Creates an IPsec policy.
### Related ONTAP commands
* `security ipsec policy create`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec policy create")
        async def ipsec_policy_create(
        ) -> ResourceTable:
            """Create an instance of a IpsecPolicy resource

            Args:
                action: Action for the IPsec policy.
                authentication_method: Authentication method for the IPsec policy.
                certificate: 
                enabled: Indicates whether or not the policy is enabled.
                ipspace: 
                local_endpoint: 
                local_identity: Local Identity
                name: IPsec policy name.
                protocol: Lower layer protocol to be covered by the IPsec policy.
                remote_endpoint: 
                remote_identity: Remote Identity
                scope: 
                secret_key: Pre-shared key for IKE negotiation.
                svm: 
                uuid: Unique identifier of the IPsec policy.
            """

            kwargs = {}
            if action is not None:
                kwargs["action"] = action
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if certificate is not None:
                kwargs["certificate"] = certificate
            if enabled is not None:
                kwargs["enabled"] = enabled
            if ipspace is not None:
                kwargs["ipspace"] = ipspace
            if local_endpoint is not None:
                kwargs["local_endpoint"] = local_endpoint
            if local_identity is not None:
                kwargs["local_identity"] = local_identity
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if remote_endpoint is not None:
                kwargs["remote_endpoint"] = remote_endpoint
            if remote_identity is not None:
                kwargs["remote_identity"] = remote_identity
            if scope is not None:
                kwargs["scope"] = scope
            if secret_key is not None:
                kwargs["secret_key"] = secret_key
            if svm is not None:
                kwargs["svm"] = svm
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = IpsecPolicy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create IpsecPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a specific IPsec policy.
### Related ONTAP commands
* `security ipsec policy modify`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec policy modify")
        async def ipsec_policy_modify(
        ) -> ResourceTable:
            """Modify an instance of a IpsecPolicy resource

            Args:
                action: Action for the IPsec policy.
                query_action: Action for the IPsec policy.
                authentication_method: Authentication method for the IPsec policy.
                query_authentication_method: Authentication method for the IPsec policy.
                enabled: Indicates whether or not the policy is enabled.
                query_enabled: Indicates whether or not the policy is enabled.
                local_identity: Local Identity
                query_local_identity: Local Identity
                name: IPsec policy name.
                query_name: IPsec policy name.
                protocol: Lower layer protocol to be covered by the IPsec policy.
                query_protocol: Lower layer protocol to be covered by the IPsec policy.
                remote_identity: Remote Identity
                query_remote_identity: Remote Identity
                scope: 
                query_scope: 
                secret_key: Pre-shared key for IKE negotiation.
                query_secret_key: Pre-shared key for IKE negotiation.
                uuid: Unique identifier of the IPsec policy.
                query_uuid: Unique identifier of the IPsec policy.
            """

            kwargs = {}
            changes = {}
            if query_action is not None:
                kwargs["action"] = query_action
            if query_authentication_method is not None:
                kwargs["authentication_method"] = query_authentication_method
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_local_identity is not None:
                kwargs["local_identity"] = query_local_identity
            if query_name is not None:
                kwargs["name"] = query_name
            if query_protocol is not None:
                kwargs["protocol"] = query_protocol
            if query_remote_identity is not None:
                kwargs["remote_identity"] = query_remote_identity
            if query_scope is not None:
                kwargs["scope"] = query_scope
            if query_secret_key is not None:
                kwargs["secret_key"] = query_secret_key
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if action is not None:
                changes["action"] = action
            if authentication_method is not None:
                changes["authentication_method"] = authentication_method
            if enabled is not None:
                changes["enabled"] = enabled
            if local_identity is not None:
                changes["local_identity"] = local_identity
            if name is not None:
                changes["name"] = name
            if protocol is not None:
                changes["protocol"] = protocol
            if remote_identity is not None:
                changes["remote_identity"] = remote_identity
            if scope is not None:
                changes["scope"] = scope
            if secret_key is not None:
                changes["secret_key"] = secret_key
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(IpsecPolicy, "find"):
                resource = IpsecPolicy.find(
                    **kwargs
                )
            else:
                resource = IpsecPolicy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify IpsecPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a specific IPsec policy.
### Related ONTAP commands
* `security ipsec policy delete`

### Learn more
* [`DOC /security/ipsec/policies`](#docs-security-security_ipsec_policies)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec policy delete")
        async def ipsec_policy_delete(
        ) -> None:
            """Delete an instance of a IpsecPolicy resource

            Args:
                action: Action for the IPsec policy.
                authentication_method: Authentication method for the IPsec policy.
                enabled: Indicates whether or not the policy is enabled.
                local_identity: Local Identity
                name: IPsec policy name.
                protocol: Lower layer protocol to be covered by the IPsec policy.
                remote_identity: Remote Identity
                scope: 
                secret_key: Pre-shared key for IKE negotiation.
                uuid: Unique identifier of the IPsec policy.
            """

            kwargs = {}
            if action is not None:
                kwargs["action"] = action
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if enabled is not None:
                kwargs["enabled"] = enabled
            if local_identity is not None:
                kwargs["local_identity"] = local_identity
            if name is not None:
                kwargs["name"] = name
            if protocol is not None:
                kwargs["protocol"] = protocol
            if remote_identity is not None:
                kwargs["remote_identity"] = remote_identity
            if scope is not None:
                kwargs["scope"] = scope
            if secret_key is not None:
                kwargs["secret_key"] = secret_key
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(IpsecPolicy, "find"):
                resource = IpsecPolicy.find(
                    **kwargs
                )
            else:
                resource = IpsecPolicy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete IpsecPolicy: %s" % err)


