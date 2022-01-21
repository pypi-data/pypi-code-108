r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

##  Examples
### Retrieving the Kerberos realm details
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosRealm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(KerberosRealm.get_collection()))

```

### Creating the Kerberos realm for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosRealm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = KerberosRealm()
    resource.svm.uuid = "05c90dc2-7343-11e8-9eb4-0050568be2b7"
    resource.name = "NFS-NSR-W02.RTP.NETAPP.COM"
    resource.kdc = {"vendor": "microsoft", "ip": "10.225.185.112", "port": 88}
    resource.comment = "realm"
    resource.ad_server = {
        "name": "nfs-nsr-w02.rtp.netapp.com",
        "address": "10.225.185.112",
    }
    resource.post(hydrate=True)
    print(resource)

```

### Updating the Kerberos realm for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosRealm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = KerberosRealm(
        name="NFS-NSR-W02.RTP.NETAPP.COM",
        **{"svm.uuid": "05c90dc2-7343-11e8-9eb4-0050568be2b7"}
    )
    resource.kdc = {"vendor": "Microsoft", "ip": "100.225.185.112", "port": 88}
    resource.comment = "realm modify"
    resource.ad_server = {"name": "nfs.netapp.com", "address": "192.2.18.112"}
    resource.patch()

```

### Deleting the Kerberos realm for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import KerberosRealm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = KerberosRealm(
        name="NFS-NSR-W02.RTP.NETAPP.COM",
        **{"svm.uuid": "05c90dc2-7343-11e8-9eb4-0050568be2b7"}
    )
    resource.delete()

```

---
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


__all__ = ["KerberosRealm", "KerberosRealmSchema"]
__pdoc__ = {
    "KerberosRealmSchema.resource": False,
    "KerberosRealm.kerberos_realm_show": False,
    "KerberosRealm.kerberos_realm_create": False,
    "KerberosRealm.kerberos_realm_modify": False,
    "KerberosRealm.kerberos_realm_delete": False,
}


class KerberosRealmSchema(ResourceSchema):
    """The fields of the KerberosRealm object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the kerberos_realm. """

    ad_server = fields.Nested("netapp_ontap.models.kerberos_realm_ad_server.KerberosRealmAdServerSchema", data_key="ad_server", unknown=EXCLUDE)
    r""" The ad_server field of the kerberos_realm. """

    comment = fields.Str(
        data_key="comment",
    )
    r""" Comment """

    encryption_types = fields.List(fields.Str, data_key="encryption_types")
    r""" The encryption_types field of the kerberos_realm. """

    kdc = fields.Nested("netapp_ontap.models.kerberos_realm_kdc.KerberosRealmKdcSchema", data_key="kdc", unknown=EXCLUDE)
    r""" The kdc field of the kerberos_realm. """

    name = fields.Str(
        data_key="name",
    )
    r""" Kerberos realm """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the kerberos_realm. """

    @property
    def resource(self):
        return KerberosRealm

    gettable_fields = [
        "links",
        "ad_server",
        "comment",
        "encryption_types",
        "kdc",
        "name",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,ad_server,comment,encryption_types,kdc,name,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "ad_server",
        "comment",
        "kdc",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """ad_server,comment,kdc,name,svm.name,svm.uuid,"""

    postable_fields = [
        "ad_server",
        "comment",
        "kdc",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """ad_server,comment,kdc,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in KerberosRealm.get_collection(fields=field)]
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
            raise NetAppRestError("KerberosRealm modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class KerberosRealm(Resource):
    """Allows interaction with KerberosRealm objects on the host"""

    _schema = KerberosRealmSchema
    _path = "/api/protocols/nfs/kerberos/realms"
    _keys = ["svm.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves Kerberos realms.
### Related ONTAP commands
* `vserver nfs kerberos realm show`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos realm show")
        def kerberos_realm_show(
            fields: List[Choices.define(["comment", "encryption_types", "name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of KerberosRealm resources

            Args:
                comment: Comment
                encryption_types: 
                name: Kerberos realm
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if encryption_types is not None:
                kwargs["encryption_types"] = encryption_types
            if name is not None:
                kwargs["name"] = name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return KerberosRealm.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all KerberosRealm resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["KerberosRealm"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of a Kerberos realm.
* `vserver nfs kerberos realm modify`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["KerberosRealm"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["KerberosRealm"], NetAppResponse]:
        r"""Creates a Kerberos realm.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM on which to create the Kerberos realm.
* `name` - Base name for the Kerberos realm.
* `kdc.vendor` - Vendor of the Key Distribution Center (KDC) server for this Kerberos realm. If the configuration uses a Microsoft Active Directory domain for authentication, this field nust be `microsoft`.
* `kdc.ip` - IP address of the KDC server for this Kerberos realm.
### Recommended optional properties
* `ad_server.name` - Host name of the Active Directory Domain Controller (DC). This is a mandatory parameter if the kdc-vendor is `microsoft`.
* `ad_server.address` - IP address of the Active Directory Domain Controller (DC). This is a mandatory parameter if the kdc-vendor is `microsoft`.
### Default property values
If not specified in POST, the following default property value is assigned:
* `kdc.port` - _88_
### Related ONTAP commands
* `vserver nfs kerberos realm create`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
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
        records: Iterable["KerberosRealm"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Kerberos realm.
* `vserver nfs kerberos realm delete`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Kerberos realms.
### Related ONTAP commands
* `vserver nfs kerberos realm show`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a Kerberos realm.
* `vserver nfs kerberos realm show`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
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
        r"""Creates a Kerberos realm.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM on which to create the Kerberos realm.
* `name` - Base name for the Kerberos realm.
* `kdc.vendor` - Vendor of the Key Distribution Center (KDC) server for this Kerberos realm. If the configuration uses a Microsoft Active Directory domain for authentication, this field nust be `microsoft`.
* `kdc.ip` - IP address of the KDC server for this Kerberos realm.
### Recommended optional properties
* `ad_server.name` - Host name of the Active Directory Domain Controller (DC). This is a mandatory parameter if the kdc-vendor is `microsoft`.
* `ad_server.address` - IP address of the Active Directory Domain Controller (DC). This is a mandatory parameter if the kdc-vendor is `microsoft`.
### Default property values
If not specified in POST, the following default property value is assigned:
* `kdc.port` - _88_
### Related ONTAP commands
* `vserver nfs kerberos realm create`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos realm create")
        async def kerberos_realm_create(
        ) -> ResourceTable:
            """Create an instance of a KerberosRealm resource

            Args:
                links: 
                ad_server: 
                comment: Comment
                encryption_types: 
                kdc: 
                name: Kerberos realm
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if ad_server is not None:
                kwargs["ad_server"] = ad_server
            if comment is not None:
                kwargs["comment"] = comment
            if encryption_types is not None:
                kwargs["encryption_types"] = encryption_types
            if kdc is not None:
                kwargs["kdc"] = kdc
            if name is not None:
                kwargs["name"] = name
            if svm is not None:
                kwargs["svm"] = svm

            resource = KerberosRealm(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create KerberosRealm: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of a Kerberos realm.
* `vserver nfs kerberos realm modify`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos realm modify")
        async def kerberos_realm_modify(
        ) -> ResourceTable:
            """Modify an instance of a KerberosRealm resource

            Args:
                comment: Comment
                query_comment: Comment
                encryption_types: 
                query_encryption_types: 
                name: Kerberos realm
                query_name: Kerberos realm
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_encryption_types is not None:
                kwargs["encryption_types"] = query_encryption_types
            if query_name is not None:
                kwargs["name"] = query_name

            if comment is not None:
                changes["comment"] = comment
            if encryption_types is not None:
                changes["encryption_types"] = encryption_types
            if name is not None:
                changes["name"] = name

            if hasattr(KerberosRealm, "find"):
                resource = KerberosRealm.find(
                    **kwargs
                )
            else:
                resource = KerberosRealm()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify KerberosRealm: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Kerberos realm.
* `vserver nfs kerberos realm delete`
### Learn more
* [`DOC /protocols/nfs/kerberos/realms`](#docs-NAS-protocols_nfs_kerberos_realms)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="kerberos realm delete")
        async def kerberos_realm_delete(
        ) -> None:
            """Delete an instance of a KerberosRealm resource

            Args:
                comment: Comment
                encryption_types: 
                name: Kerberos realm
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if encryption_types is not None:
                kwargs["encryption_types"] = encryption_types
            if name is not None:
                kwargs["name"] = name

            if hasattr(KerberosRealm, "find"):
                resource = KerberosRealm.find(
                    **kwargs
                )
            else:
                resource = KerberosRealm()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete KerberosRealm: %s" % err)


