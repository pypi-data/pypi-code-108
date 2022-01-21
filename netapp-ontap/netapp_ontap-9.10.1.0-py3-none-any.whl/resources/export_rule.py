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


__all__ = ["ExportRule", "ExportRuleSchema"]
__pdoc__ = {
    "ExportRuleSchema.resource": False,
    "ExportRule.export_rule_show": False,
    "ExportRule.export_rule_create": False,
    "ExportRule.export_rule_modify": False,
    "ExportRule.export_rule_delete": False,
}


class ExportRuleSchema(ResourceSchema):
    """The fields of the ExportRule object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the export_rule. """

    allow_device_creation = fields.Boolean(
        data_key="allow_device_creation",
    )
    r""" Specifies whether or not device creation is allowed. """

    allow_suid = fields.Boolean(
        data_key="allow_suid",
    )
    r""" Specifies whether or not SetUID bits in SETATTR Op is to be honored. """

    anonymous_user = fields.Str(
        data_key="anonymous_user",
    )
    r""" User ID To Which Anonymous Users Are Mapped. """

    chown_mode = fields.Str(
        data_key="chown_mode",
        validate=enum_validation(['restricted', 'unrestricted']),
    )
    r""" Specifies who is authorized to change the ownership mode of a file.

Valid choices:

* restricted
* unrestricted """

    clients = fields.List(fields.Nested("netapp_ontap.models.export_clients.ExportClientsSchema", unknown=EXCLUDE), data_key="clients")
    r""" Array of client matches """

    index = Size(
        data_key="index",
    )
    r""" Index of the rule within the export policy. """

    ntfs_unix_security = fields.Str(
        data_key="ntfs_unix_security",
        validate=enum_validation(['fail', 'ignore']),
    )
    r""" NTFS export UNIX security options.

Valid choices:

* fail
* ignore """

    policy = fields.Nested("netapp_ontap.models.export_rule_policy.ExportRulePolicySchema", data_key="policy", unknown=EXCLUDE)
    r""" The policy field of the export_rule. """

    protocols = fields.List(fields.Str, data_key="protocols")
    r""" The protocols field of the export_rule. """

    ro_rule = fields.List(fields.Str, data_key="ro_rule")
    r""" Authentication flavors that the read-only access rule governs """

    rw_rule = fields.List(fields.Str, data_key="rw_rule")
    r""" Authentication flavors that the read/write access rule governs """

    superuser = fields.List(fields.Str, data_key="superuser")
    r""" Authentication flavors that the superuser security type governs """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the export_rule. """

    @property
    def resource(self):
        return ExportRule

    gettable_fields = [
        "links",
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "index",
        "ntfs_unix_security",
        "policy",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,index,ntfs_unix_security,policy,protocols,ro_rule,rw_rule,superuser,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "ntfs_unix_security",
        "policy",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
        "svm.name",
        "svm.uuid",
    ]
    """allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,ntfs_unix_security,policy,protocols,ro_rule,rw_rule,superuser,svm.name,svm.uuid,"""

    postable_fields = [
        "allow_device_creation",
        "allow_suid",
        "anonymous_user",
        "chown_mode",
        "clients",
        "ntfs_unix_security",
        "policy",
        "protocols",
        "ro_rule",
        "rw_rule",
        "superuser",
        "svm.name",
        "svm.uuid",
    ]
    """allow_device_creation,allow_suid,anonymous_user,chown_mode,clients,ntfs_unix_security,policy,protocols,ro_rule,rw_rule,superuser,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ExportRule.get_collection(fields=field)]
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
            raise NetAppRestError("ExportRule modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ExportRule(Resource):
    """Allows interaction with ExportRule objects on the host"""

    _schema = ExportRuleSchema
    _path = "/api/protocols/nfs/export-policies/{policy[id]}/rules"
    _keys = ["policy.id", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves export policy rules.
### Related ONTAP commands
* `vserver export-policy rule show`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export rule show")
        def export_rule_show(
            policy_id,
            allow_device_creation: Choices.define(_get_field_list("allow_device_creation"), cache_choices=True, inexact=True)=None,
            allow_suid: Choices.define(_get_field_list("allow_suid"), cache_choices=True, inexact=True)=None,
            anonymous_user: Choices.define(_get_field_list("anonymous_user"), cache_choices=True, inexact=True)=None,
            chown_mode: Choices.define(_get_field_list("chown_mode"), cache_choices=True, inexact=True)=None,
            index: Choices.define(_get_field_list("index"), cache_choices=True, inexact=True)=None,
            ntfs_unix_security: Choices.define(_get_field_list("ntfs_unix_security"), cache_choices=True, inexact=True)=None,
            protocols: Choices.define(_get_field_list("protocols"), cache_choices=True, inexact=True)=None,
            ro_rule: Choices.define(_get_field_list("ro_rule"), cache_choices=True, inexact=True)=None,
            rw_rule: Choices.define(_get_field_list("rw_rule"), cache_choices=True, inexact=True)=None,
            superuser: Choices.define(_get_field_list("superuser"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["allow_device_creation", "allow_suid", "anonymous_user", "chown_mode", "index", "ntfs_unix_security", "protocols", "ro_rule", "rw_rule", "superuser", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ExportRule resources

            Args:
                allow_device_creation: Specifies whether or not device creation is allowed.
                allow_suid: Specifies whether or not SetUID bits in SETATTR Op is to be honored.
                anonymous_user: User ID To Which Anonymous Users Are Mapped.
                chown_mode: Specifies who is authorized to change the ownership mode of a file.
                index: Index of the rule within the export policy. 
                ntfs_unix_security: NTFS export UNIX security options.
                protocols: 
                ro_rule: Authentication flavors that the read-only access rule governs 
                rw_rule: Authentication flavors that the read/write access rule governs 
                superuser: Authentication flavors that the superuser security type governs 
            """

            kwargs = {}
            if allow_device_creation is not None:
                kwargs["allow_device_creation"] = allow_device_creation
            if allow_suid is not None:
                kwargs["allow_suid"] = allow_suid
            if anonymous_user is not None:
                kwargs["anonymous_user"] = anonymous_user
            if chown_mode is not None:
                kwargs["chown_mode"] = chown_mode
            if index is not None:
                kwargs["index"] = index
            if ntfs_unix_security is not None:
                kwargs["ntfs_unix_security"] = ntfs_unix_security
            if protocols is not None:
                kwargs["protocols"] = protocols
            if ro_rule is not None:
                kwargs["ro_rule"] = ro_rule
            if rw_rule is not None:
                kwargs["rw_rule"] = rw_rule
            if superuser is not None:
                kwargs["superuser"] = superuser
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ExportRule.get_collection(
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
        """Returns a count of all ExportRule resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["ExportRule"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of an export policy rule to change an export policy rule's index or fields.
### Related ONTAP commands
* `vserver export-policy rule modify`
* `vserver export-policy rule setindex`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["ExportRule"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ExportRule"], NetAppResponse]:
        r"""Creates an export policy rule.
### Required properties
* `policy.id`  - Existing export policy for which to create an export rule.
* `clients.match`  - List of clients (hostnames, ipaddresses, netgroups, domains) to which the export rule applies.
* `ro_rule`  - Used to specify the security type for read-only access to volumes that use the export rule.
* `rw_rule`  - Used to specify the security type for read-write access to volumes that use the export rule.
### Default property values
If not specified in POST, the following default property values are assigned:
* `protocols` - _any_
* `anonymous_user` - _none_
* `superuser` - _any_
* `allow_device_creation` - _true_
* `ntfs_unix_security` - _fail_
* `chown_mode` - _restricted_
* `allow_suid` - _true_
### Related ONTAP commands
* `vserver export-policy rule create`
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
        records: Iterable["ExportRule"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy rule.
### Related ONTAP commands
* `vserver export-policy rule delete`
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
        r"""Retrieves export policy rules.
### Related ONTAP commands
* `vserver export-policy rule show`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an export policy rule
### Related ONTAP commands
* `vserver export-policy rule show`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
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
        r"""Creates an export policy rule.
### Required properties
* `policy.id`  - Existing export policy for which to create an export rule.
* `clients.match`  - List of clients (hostnames, ipaddresses, netgroups, domains) to which the export rule applies.
* `ro_rule`  - Used to specify the security type for read-only access to volumes that use the export rule.
* `rw_rule`  - Used to specify the security type for read-write access to volumes that use the export rule.
### Default property values
If not specified in POST, the following default property values are assigned:
* `protocols` - _any_
* `anonymous_user` - _none_
* `superuser` - _any_
* `allow_device_creation` - _true_
* `ntfs_unix_security` - _fail_
* `chown_mode` - _restricted_
* `allow_suid` - _true_
### Related ONTAP commands
* `vserver export-policy rule create`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export rule create")
        async def export_rule_create(
            policy_id,
            links: dict = None,
            allow_device_creation: bool = None,
            allow_suid: bool = None,
            anonymous_user: str = None,
            chown_mode: str = None,
            clients: dict = None,
            index: Size = None,
            ntfs_unix_security: str = None,
            policy: dict = None,
            protocols = None,
            ro_rule: List[str] = None,
            rw_rule: List[str] = None,
            superuser: List[str] = None,
            svm: dict = None,
        ) -> ResourceTable:
            """Create an instance of a ExportRule resource

            Args:
                links: 
                allow_device_creation: Specifies whether or not device creation is allowed.
                allow_suid: Specifies whether or not SetUID bits in SETATTR Op is to be honored.
                anonymous_user: User ID To Which Anonymous Users Are Mapped.
                chown_mode: Specifies who is authorized to change the ownership mode of a file.
                clients: Array of client matches
                index: Index of the rule within the export policy. 
                ntfs_unix_security: NTFS export UNIX security options.
                policy: 
                protocols: 
                ro_rule: Authentication flavors that the read-only access rule governs 
                rw_rule: Authentication flavors that the read/write access rule governs 
                superuser: Authentication flavors that the superuser security type governs 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if allow_device_creation is not None:
                kwargs["allow_device_creation"] = allow_device_creation
            if allow_suid is not None:
                kwargs["allow_suid"] = allow_suid
            if anonymous_user is not None:
                kwargs["anonymous_user"] = anonymous_user
            if chown_mode is not None:
                kwargs["chown_mode"] = chown_mode
            if clients is not None:
                kwargs["clients"] = clients
            if index is not None:
                kwargs["index"] = index
            if ntfs_unix_security is not None:
                kwargs["ntfs_unix_security"] = ntfs_unix_security
            if policy is not None:
                kwargs["policy"] = policy
            if protocols is not None:
                kwargs["protocols"] = protocols
            if ro_rule is not None:
                kwargs["ro_rule"] = ro_rule
            if rw_rule is not None:
                kwargs["rw_rule"] = rw_rule
            if superuser is not None:
                kwargs["superuser"] = superuser
            if svm is not None:
                kwargs["svm"] = svm

            resource = ExportRule(
                policy_id,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ExportRule: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of an export policy rule to change an export policy rule's index or fields.
### Related ONTAP commands
* `vserver export-policy rule modify`
* `vserver export-policy rule setindex`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export rule modify")
        async def export_rule_modify(
            policy_id,
            allow_device_creation: bool = None,
            query_allow_device_creation: bool = None,
            allow_suid: bool = None,
            query_allow_suid: bool = None,
            anonymous_user: str = None,
            query_anonymous_user: str = None,
            chown_mode: str = None,
            query_chown_mode: str = None,
            index: Size = None,
            query_index: Size = None,
            ntfs_unix_security: str = None,
            query_ntfs_unix_security: str = None,
            protocols=None,
            query_protocols=None,
            ro_rule: List[str] = None,
            query_ro_rule: List[str] = None,
            rw_rule: List[str] = None,
            query_rw_rule: List[str] = None,
            superuser: List[str] = None,
            query_superuser: List[str] = None,
        ) -> ResourceTable:
            """Modify an instance of a ExportRule resource

            Args:
                allow_device_creation: Specifies whether or not device creation is allowed.
                query_allow_device_creation: Specifies whether or not device creation is allowed.
                allow_suid: Specifies whether or not SetUID bits in SETATTR Op is to be honored.
                query_allow_suid: Specifies whether or not SetUID bits in SETATTR Op is to be honored.
                anonymous_user: User ID To Which Anonymous Users Are Mapped.
                query_anonymous_user: User ID To Which Anonymous Users Are Mapped.
                chown_mode: Specifies who is authorized to change the ownership mode of a file.
                query_chown_mode: Specifies who is authorized to change the ownership mode of a file.
                index: Index of the rule within the export policy. 
                query_index: Index of the rule within the export policy. 
                ntfs_unix_security: NTFS export UNIX security options.
                query_ntfs_unix_security: NTFS export UNIX security options.
                protocols: 
                query_protocols: 
                ro_rule: Authentication flavors that the read-only access rule governs 
                query_ro_rule: Authentication flavors that the read-only access rule governs 
                rw_rule: Authentication flavors that the read/write access rule governs 
                query_rw_rule: Authentication flavors that the read/write access rule governs 
                superuser: Authentication flavors that the superuser security type governs 
                query_superuser: Authentication flavors that the superuser security type governs 
            """

            kwargs = {}
            changes = {}
            if query_allow_device_creation is not None:
                kwargs["allow_device_creation"] = query_allow_device_creation
            if query_allow_suid is not None:
                kwargs["allow_suid"] = query_allow_suid
            if query_anonymous_user is not None:
                kwargs["anonymous_user"] = query_anonymous_user
            if query_chown_mode is not None:
                kwargs["chown_mode"] = query_chown_mode
            if query_index is not None:
                kwargs["index"] = query_index
            if query_ntfs_unix_security is not None:
                kwargs["ntfs_unix_security"] = query_ntfs_unix_security
            if query_protocols is not None:
                kwargs["protocols"] = query_protocols
            if query_ro_rule is not None:
                kwargs["ro_rule"] = query_ro_rule
            if query_rw_rule is not None:
                kwargs["rw_rule"] = query_rw_rule
            if query_superuser is not None:
                kwargs["superuser"] = query_superuser

            if allow_device_creation is not None:
                changes["allow_device_creation"] = allow_device_creation
            if allow_suid is not None:
                changes["allow_suid"] = allow_suid
            if anonymous_user is not None:
                changes["anonymous_user"] = anonymous_user
            if chown_mode is not None:
                changes["chown_mode"] = chown_mode
            if index is not None:
                changes["index"] = index
            if ntfs_unix_security is not None:
                changes["ntfs_unix_security"] = ntfs_unix_security
            if protocols is not None:
                changes["protocols"] = protocols
            if ro_rule is not None:
                changes["ro_rule"] = ro_rule
            if rw_rule is not None:
                changes["rw_rule"] = rw_rule
            if superuser is not None:
                changes["superuser"] = superuser

            if hasattr(ExportRule, "find"):
                resource = ExportRule.find(
                    policy_id,
                    **kwargs
                )
            else:
                resource = ExportRule(policy_id,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ExportRule: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy rule.
### Related ONTAP commands
* `vserver export-policy rule delete`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export rule delete")
        async def export_rule_delete(
            policy_id,
            allow_device_creation: bool = None,
            allow_suid: bool = None,
            anonymous_user: str = None,
            chown_mode: str = None,
            index: Size = None,
            ntfs_unix_security: str = None,
            protocols=None,
            ro_rule: List[str] = None,
            rw_rule: List[str] = None,
            superuser: List[str] = None,
        ) -> None:
            """Delete an instance of a ExportRule resource

            Args:
                allow_device_creation: Specifies whether or not device creation is allowed.
                allow_suid: Specifies whether or not SetUID bits in SETATTR Op is to be honored.
                anonymous_user: User ID To Which Anonymous Users Are Mapped.
                chown_mode: Specifies who is authorized to change the ownership mode of a file.
                index: Index of the rule within the export policy. 
                ntfs_unix_security: NTFS export UNIX security options.
                protocols: 
                ro_rule: Authentication flavors that the read-only access rule governs 
                rw_rule: Authentication flavors that the read/write access rule governs 
                superuser: Authentication flavors that the superuser security type governs 
            """

            kwargs = {}
            if allow_device_creation is not None:
                kwargs["allow_device_creation"] = allow_device_creation
            if allow_suid is not None:
                kwargs["allow_suid"] = allow_suid
            if anonymous_user is not None:
                kwargs["anonymous_user"] = anonymous_user
            if chown_mode is not None:
                kwargs["chown_mode"] = chown_mode
            if index is not None:
                kwargs["index"] = index
            if ntfs_unix_security is not None:
                kwargs["ntfs_unix_security"] = ntfs_unix_security
            if protocols is not None:
                kwargs["protocols"] = protocols
            if ro_rule is not None:
                kwargs["ro_rule"] = ro_rule
            if rw_rule is not None:
                kwargs["rw_rule"] = rw_rule
            if superuser is not None:
                kwargs["superuser"] = superuser

            if hasattr(ExportRule, "find"):
                resource = ExportRule.find(
                    policy_id,
                    **kwargs
                )
            else:
                resource = ExportRule(policy_id,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ExportRule: %s" % err)


