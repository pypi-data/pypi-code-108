r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

##  Examples
### Retrieving the Kerberos interface configuration details
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(KerberosInterface.get_collection()))

```

### Updating the Kerberos interface configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosInterface

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = KerberosInterface(
        **{"interface.uuid": "e62936de-7342-11e8-9eb4-0050568be2b7"}
    )
    resource.enabled = True
    resource.spn = "nfs/datalif1-vsim3-d1.sim.netapp.com@NFS-NSR-W01.RTP.NETAPP.COM"
    resource.user = "administrator"
    resource.password = "Hello123!"
    resource.patch()

```

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


__all__ = ["KerberosInterface", "KerberosInterfaceSchema"]
__pdoc__ = {
    "KerberosInterfaceSchema.resource": False,
    "KerberosInterface.kerberos_interface_show": False,
    "KerberosInterface.kerberos_interface_create": False,
    "KerberosInterface.kerberos_interface_modify": False,
    "KerberosInterface.kerberos_interface_delete": False,
}


class KerberosInterfaceSchema(ResourceSchema):
    """The fields of the KerberosInterface object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the kerberos_interface. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies if Kerberos is enabled. """

    encryption_types = fields.List(fields.Str, data_key="encryption_types")
    r""" The encryption_types field of the kerberos_interface. """

    interface = fields.Nested("netapp_ontap.resources.ip_interface.IpInterfaceSchema", data_key="interface", unknown=EXCLUDE)
    r""" The interface field of the kerberos_interface. """

    keytab_uri = fields.Str(
        data_key="keytab_uri",
    )
    r""" Load keytab from URI """

    organizational_unit = fields.Str(
        data_key="organizational_unit",
    )
    r""" Organizational unit """

    password = fields.Str(
        data_key="password",
    )
    r""" Account creation password """

    spn = fields.Str(
        data_key="spn",
    )
    r""" Service principal name. Valid in PATCH. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the kerberos_interface. """

    user = fields.Str(
        data_key="user",
    )
    r""" Account creation user name """

    @property
    def resource(self):
        return KerberosInterface

    gettable_fields = [
        "links",
        "enabled",
        "encryption_types",
        "interface.links",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "spn",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,enabled,encryption_types,interface.links,interface.ip,interface.name,interface.uuid,spn,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "enabled",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "keytab_uri",
        "organizational_unit",
        "password",
        "spn",
        "svm.name",
        "svm.uuid",
        "user",
    ]
    """enabled,interface.ip,interface.name,interface.uuid,keytab_uri,organizational_unit,password,spn,svm.name,svm.uuid,user,"""

    postable_fields = [
        "enabled",
        "interface.ip",
        "interface.name",
        "interface.uuid",
        "keytab_uri",
        "organizational_unit",
        "password",
        "spn",
        "svm.name",
        "svm.uuid",
        "user",
    ]
    """enabled,interface.ip,interface.name,interface.uuid,keytab_uri,organizational_unit,password,spn,svm.name,svm.uuid,user,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in KerberosInterface.get_collection(fields=field)]
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
            raise NetAppRestError("KerberosInterface modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class KerberosInterface(Resource):
    """Allows interaction with KerberosInterface objects on the host"""

    _schema = KerberosInterfaceSchema
    _path = "/api/protocols/nfs/kerberos/interfaces"
    _keys = ["interface.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves Kerberos interfaces.
### Related ONTAP commands
* `vserver nfs kerberos interface show`
### Learn more
* [`DOC /protocols/nfs/kerberos/interfaces`](#docs-NAS-protocols_nfs_kerberos_interfaces)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos interface show")
        def kerberos_interface_show(
            fields: List[Choices.define(["enabled", "encryption_types", "keytab_uri", "organizational_unit", "password", "spn", "user", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of KerberosInterface resources

            Args:
                enabled: Specifies if Kerberos is enabled.
                encryption_types: 
                keytab_uri: Load keytab from URI
                organizational_unit: Organizational unit
                password: Account creation password
                spn: Service principal name. Valid in PATCH.
                user: Account creation user name
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if encryption_types is not None:
                kwargs["encryption_types"] = encryption_types
            if keytab_uri is not None:
                kwargs["keytab_uri"] = keytab_uri
            if organizational_unit is not None:
                kwargs["organizational_unit"] = organizational_unit
            if password is not None:
                kwargs["password"] = password
            if spn is not None:
                kwargs["spn"] = spn
            if user is not None:
                kwargs["user"] = user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return KerberosInterface.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all KerberosInterface resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["KerberosInterface"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of a Kerberos interface.
### Related ONTAP commands
* `vserver nfs kerberos interface modify`
* `vserver nfs kerberos interface enable`
* `vserver nfs kerberos interface disable`
### Learn more
* [`DOC /protocols/nfs/kerberos/interfaces`](#docs-NAS-protocols_nfs_kerberos_interfaces)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Kerberos interfaces.
### Related ONTAP commands
* `vserver nfs kerberos interface show`
### Learn more
* [`DOC /protocols/nfs/kerberos/interfaces`](#docs-NAS-protocols_nfs_kerberos_interfaces)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a Kerberos interface.
### Related ONTAP commands
* `vserver nfs kerberos interface show`
### Learn more
* [`DOC /protocols/nfs/kerberos/interfaces`](#docs-NAS-protocols_nfs_kerberos_interfaces)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of a Kerberos interface.
### Related ONTAP commands
* `vserver nfs kerberos interface modify`
* `vserver nfs kerberos interface enable`
* `vserver nfs kerberos interface disable`
### Learn more
* [`DOC /protocols/nfs/kerberos/interfaces`](#docs-NAS-protocols_nfs_kerberos_interfaces)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos interface modify")
        async def kerberos_interface_modify(
        ) -> ResourceTable:
            """Modify an instance of a KerberosInterface resource

            Args:
                enabled: Specifies if Kerberos is enabled.
                query_enabled: Specifies if Kerberos is enabled.
                encryption_types: 
                query_encryption_types: 
                keytab_uri: Load keytab from URI
                query_keytab_uri: Load keytab from URI
                organizational_unit: Organizational unit
                query_organizational_unit: Organizational unit
                password: Account creation password
                query_password: Account creation password
                spn: Service principal name. Valid in PATCH.
                query_spn: Service principal name. Valid in PATCH.
                user: Account creation user name
                query_user: Account creation user name
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_encryption_types is not None:
                kwargs["encryption_types"] = query_encryption_types
            if query_keytab_uri is not None:
                kwargs["keytab_uri"] = query_keytab_uri
            if query_organizational_unit is not None:
                kwargs["organizational_unit"] = query_organizational_unit
            if query_password is not None:
                kwargs["password"] = query_password
            if query_spn is not None:
                kwargs["spn"] = query_spn
            if query_user is not None:
                kwargs["user"] = query_user

            if enabled is not None:
                changes["enabled"] = enabled
            if encryption_types is not None:
                changes["encryption_types"] = encryption_types
            if keytab_uri is not None:
                changes["keytab_uri"] = keytab_uri
            if organizational_unit is not None:
                changes["organizational_unit"] = organizational_unit
            if password is not None:
                changes["password"] = password
            if spn is not None:
                changes["spn"] = spn
            if user is not None:
                changes["user"] = user

            if hasattr(KerberosInterface, "find"):
                resource = KerberosInterface.find(
                    **kwargs
                )
            else:
                resource = KerberosInterface()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify KerberosInterface: %s" % err)



