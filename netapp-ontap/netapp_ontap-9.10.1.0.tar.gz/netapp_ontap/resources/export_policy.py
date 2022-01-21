r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

##  Export Policies
### 1) Retrieve the export policy details
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ExportPolicy.get_collection()))

```

---
### 2) Create an export policy for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportPolicy()
    resource.name = "P1"
    resource.rules = [
        {
            "clients": [{"match": "host1"}],
            "ro_rule": ["krb5"],
            "rw_rule": ["ntlm"],
            "anonymous_user": "anon1",
            "chown_mode": "restricted",
            "allow_suid": True,
        },
        {
            "clients": [{"match": "host2"}],
            "ro_rule": ["sys"],
            "rw_rule": ["ntlm"],
            "superuser": ["any"],
            "allow_device_creation": True,
            "ntfs_unix_security": "fail",
        },
    ]
    resource.post(hydrate=True)
    print(resource)

```

---
### 3) Update an export policy for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportPolicy(id=8589934594)
    resource.name = "S1"
    resource.rules = [
        {"clients": [{"match": "host4"}], "ro_rule": ["krb5"], "rw_rule": ["ntlm"]}
    ]
    resource.patch()

```

---
### 4) Delete an export policy for an SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportPolicy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportPolicy(id=8589934594)
    resource.delete()

```

---
##  Export Rules
### 1) Retrieve the export policy rule details for an export policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ExportRule.get_collection(8589934595)))

```

---
### 2) Create an export policy rule for an export policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportRule(8589934595)
    resource.clients = [{"match": "host2"}]
    resource.ro_rule = ["sys"]
    resource.rw_rule = ["ntlm"]
    resource.post(hydrate=True)
    print(resource)

```

---
### 3) Update an export policy rule for an export policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportRule(8589934595, index=5)
    resource.clients = [{"match": "host4"}]
    resource.ro_rule = ["sys"]
    resource.rw_rule = ["krb5"]
    resource.patch(hydrate=True, new_index=10)

```

---
### 4) Delete an export policy rule for an export policy
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportRule(8589934595, index=15)
    resource.delete()

```

---
##  Export Clients
### 1) Retrieve the export client matches of an export policy rule
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportClient

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(ExportClient.get_collection(8589934593, 2)))

```

---
### 2) Add an export client match to an export policy rule
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportClient

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportClient(8589934593, 1)
    resource.match = "host4"
    resource.post(hydrate=True)
    print(resource)

```

---
### 3) Delete an export client match from an export policy rule
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ExportClient

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ExportClient(8589934593, 1, match="host1,host2")
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


__all__ = ["ExportPolicy", "ExportPolicySchema"]
__pdoc__ = {
    "ExportPolicySchema.resource": False,
    "ExportPolicy.export_policy_show": False,
    "ExportPolicy.export_policy_create": False,
    "ExportPolicy.export_policy_modify": False,
    "ExportPolicy.export_policy_delete": False,
}


class ExportPolicySchema(ResourceSchema):
    """The fields of the ExportPolicy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the export_policy. """

    id = Size(
        data_key="id",
    )
    r""" Export Policy ID """

    name = fields.Str(
        data_key="name",
    )
    r""" Export Policy Name """

    rules = fields.List(fields.Nested("netapp_ontap.models.export_rules.ExportRulesSchema", unknown=EXCLUDE), data_key="rules")
    r""" Rules of the Export Policy. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the export_policy. """

    @property
    def resource(self):
        return ExportPolicy

    gettable_fields = [
        "links",
        "id",
        "name",
        "rules",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,id,name,rules,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "name",
        "rules",
        "svm.name",
        "svm.uuid",
    ]
    """name,rules,svm.name,svm.uuid,"""

    postable_fields = [
        "name",
        "rules",
        "svm.name",
        "svm.uuid",
    ]
    """name,rules,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ExportPolicy.get_collection(fields=field)]
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
            raise NetAppRestError("ExportPolicy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ExportPolicy(Resource):
    """Allows interaction with ExportPolicy objects on the host"""

    _schema = ExportPolicySchema
    _path = "/api/protocols/nfs/export-policies"
    _keys = ["id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves export policies.
### Related ONTAP commands
* `vserver export-policy show`
* `vserver export-policy rule show`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export policy show")
        def export_policy_show(
            fields: List[Choices.define(["id", "name", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ExportPolicy resources

            Args:
                id: Export Policy ID
                name: Export Policy Name
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ExportPolicy.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ExportPolicy resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["ExportPolicy"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of an export policy to change an export policy name or replace all export policy rules.
### Related ONTAP commands
* `vserver export-policy rename`
* `vserver export-policy rule delete`
* `vserver export-policy rule create`
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
        records: Iterable["ExportPolicy"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ExportPolicy"], NetAppResponse]:
        r"""Creates an export policy. An SVM can have any number of export policies to define rules for which clients can access data exported by the SVM. A policy with no rules prohibits access.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create an export policy.
* `name`  - Name of the export policy.
### Recommended optional properties
* `rules`  - Rule(s) of an export policy. Used to create the export rule and populate the export policy with export rules in a single request.
### Related ONTAP commands
* `vserver export-policy create`
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
        records: Iterable["ExportPolicy"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy.
### Related ONTAP commands
* `vserver export-policy delete`
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
        r"""Retrieves export policies.
### Related ONTAP commands
* `vserver export-policy show`
* `vserver export-policy rule show`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an export policy.
### Related ONTAP commands
* `vserver export-policy show`
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
        r"""Creates an export policy. An SVM can have any number of export policies to define rules for which clients can access data exported by the SVM. A policy with no rules prohibits access.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create an export policy.
* `name`  - Name of the export policy.
### Recommended optional properties
* `rules`  - Rule(s) of an export policy. Used to create the export rule and populate the export policy with export rules in a single request.
### Related ONTAP commands
* `vserver export-policy create`
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
        @recline.command(name="export policy create")
        async def export_policy_create(
        ) -> ResourceTable:
            """Create an instance of a ExportPolicy resource

            Args:
                links: 
                id: Export Policy ID
                name: Export Policy Name
                rules: Rules of the Export Policy.
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if rules is not None:
                kwargs["rules"] = rules
            if svm is not None:
                kwargs["svm"] = svm

            resource = ExportPolicy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ExportPolicy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the properties of an export policy to change an export policy name or replace all export policy rules.
### Related ONTAP commands
* `vserver export-policy rename`
* `vserver export-policy rule delete`
* `vserver export-policy rule create`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export policy modify")
        async def export_policy_modify(
        ) -> ResourceTable:
            """Modify an instance of a ExportPolicy resource

            Args:
                id: Export Policy ID
                query_id: Export Policy ID
                name: Export Policy Name
                query_name: Export Policy Name
            """

            kwargs = {}
            changes = {}
            if query_id is not None:
                kwargs["id"] = query_id
            if query_name is not None:
                kwargs["name"] = query_name

            if id is not None:
                changes["id"] = id
            if name is not None:
                changes["name"] = name

            if hasattr(ExportPolicy, "find"):
                resource = ExportPolicy.find(
                    **kwargs
                )
            else:
                resource = ExportPolicy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ExportPolicy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an export policy.
### Related ONTAP commands
* `vserver export-policy delete`
### Learn more
* [`DOC /protocols/nfs/export-policies`](#docs-NAS-protocols_nfs_export-policies)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="export policy delete")
        async def export_policy_delete(
        ) -> None:
            """Delete an instance of a ExportPolicy resource

            Args:
                id: Export Policy ID
                name: Export Policy Name
            """

            kwargs = {}
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name

            if hasattr(ExportPolicy, "find"):
                resource = ExportPolicy.find(
                    **kwargs
                )
            else:
                resource = ExportPolicy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ExportPolicy: %s" % err)


