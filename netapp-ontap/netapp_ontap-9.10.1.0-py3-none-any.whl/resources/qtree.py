r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A qtree is a logically defined file system that can exist as a special subdirectory of the root directory within a FlexVol volume or a FlexGroup volume.<br/>
## Qtree QoS policy
Qtree QoS policy and settings enforce Service Level Objectives (SLOs) on a qtree. SLOs can be set by specifying "qos_policy.max_throughput_iops" and/or "qos_policy.max_throughput_mbps" or "qos_policy.min_throughput_iops" and/or "qos_policy.min_throughput_mbps".
Specifying "min_throughput_iops" or "min_throughput_mbps" is only supported on volumes hosted on a node that is flash optimized. A pre-created QoS policy can also be used by specifying "qos_policy.name" or "qos_policy.uuid" properties.
Setting or assigning a QoS policy to a qtree is not supported if its containing volume or SVM has a QoS policy attached, or a file or LUN in its containing volume already has a QoS policy attached.
<br/>
## Qtree APIs
The following APIs are used to create, retrieve, modify, and delete qtrees.

* POST      /api/storage/qtrees
* GET       /api/storage/qtrees
* GET       /api/storage/qtrees/{volume-uuid}/{qtree-id}
* PATCH     /api/storage/qtrees/{volume-uuid}/{qtree-id}
* DELETE    /api/storage/qtrees/{volume-uuid}/{qtree-id}
## Examples
### Creating a qtree inside a volume for an SVM
This API is used to create a qtree inside a volume for an SVM.<br/>
The following example shows how to create a qtree in a FlexVol volume with a given security style, user, group, UNIX permissions, an export policy, and a QoS policy.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Qtree()
    resource.svm = {"name": "svm1"}
    resource.volume = {"name": "fv"}
    resource.name = "qt1"
    resource.security_style = "unix"
    resource.user = {"name": "unix_user1"}
    resource.group = {"name": "unix_group1"}
    resource.unix_permissions = 744
    resource.export_policy = {"name": "default"}
    resource.qos_policy = {"max_throughput_iops": 1000}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Qtree(
    {
        "unix_permissions": 744,
        "group": {"name": "unix_group1"},
        "name": "qt1",
        "export_policy": {"name": "default"},
        "qos_policy": {
            "uuid": "39ac471f-ff35-11e9-b0f9-005056a7ab52",
            "name": "vs0_auto_gen_policy_39a9522f_ff35_11e9_b0f9_005056a7ab52",
        },
        "svm": {"name": "svm1"},
        "security_style": "unix",
        "volume": {"name": "fv"},
        "user": {"name": "unix_user1"},
        "_links": {"self": {"href": "/api/storage/qtrees/?volume.name=fv&name=qt1"}},
    }
)

```
</div>
</div>

---
### Retrieving qtrees
This API is used to retrieve qtrees. <br/>
The following example shows how to retrieve qtrees belonging to SVM _svm1_ and volume _fv_. The `svm.name` and `volume.name` query parameters are used to find the required qtrees.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Qtree.get_collection(**{"svm.name": "svm1", "volume.name": "fv"})))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    Qtree(
        {
            "name": "",
            "id": 0,
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b68f961b-4cee-11e9-930a-005056a7f717"
                    }
                },
                "uuid": "b68f961b-4cee-11e9-930a-005056a7f717",
                "name": "svm1",
            },
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/cb20da45-4f6b-11e9-9a71-005056a7f717"
                    }
                },
                "uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717",
                "name": "fv",
            },
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/cb20da45-4f6b-11e9-9a71-005056a7f717/0"
                }
            },
        }
    ),
    Qtree(
        {
            "name": "qt1",
            "id": 1,
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b68f961b-4cee-11e9-930a-005056a7f717"
                    }
                },
                "uuid": "b68f961b-4cee-11e9-930a-005056a7f717",
                "name": "svm1",
            },
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/cb20da45-4f6b-11e9-9a71-005056a7f717"
                    }
                },
                "uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717",
                "name": "fv",
            },
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/cb20da45-4f6b-11e9-9a71-005056a7f717/1"
                }
            },
        }
    ),
    Qtree(
        {
            "name": "qt2",
            "id": 2,
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/b68f961b-4cee-11e9-930a-005056a7f717"
                    }
                },
                "uuid": "b68f961b-4cee-11e9-930a-005056a7f717",
                "name": "svm1",
            },
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/cb20da45-4f6b-11e9-9a71-005056a7f717"
                    }
                },
                "uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717",
                "name": "fv",
            },
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/cb20da45-4f6b-11e9-9a71-005056a7f717/2"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving properties of a specific qtree using a qtree identifier
This API is used to retrieve properties of a specific qtree using qtree.id.<br/>
The following example shows how to use the qtree identifier to retrieve all properties of the qtree using the `fields` query parameter.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Qtree(id=2, **{"volume.uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717"})
    resource.get(fields="*")
    print(resource)

```

---
### Retrieving properties of a specific qtree using the qtree name
This API is used to retrieve properties of a specific qtree using "qtree.name".
The following example shows how to retrieve all of the properties belonging to qtree "qt2". The `svm.name` and `volume.name` query parameters are used here along with the qtree name.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            Qtree.get_collection(
                name="qt2", fields="*", **{"svm.name": "svm1", "volume.name": "fv"}
            )
        )
    )

```

---
### Updating a qtree
This API is used to update a qtree. <br/>
The following example shows how to update properties in a qtree.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Qtree(id=2, **{"volume.uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717"})
    resource.security_style = "mixed"
    resource.user = {"name": "unix_user1"}
    resource.group = {"name": "unix_group1"}
    resource.unix_permissions = 777
    resource.export_policy = {"id": "9", "name": "exp1"}
    resource.qos_policy = {"uuid": "39ac471f-ff35-11e9-b0f9-005056a7ab53"}
    resource.patch()

```

---
### Renaming a qtree
This API is used to rename a qtree. <br/>
The following example below shows how to rename a qtree with a new name.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Qtree(id=1, **{"volume.uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717"})
    resource.name = "new_qt1"
    resource.patch()

```

---
### Deleting a qtree inside a volume of an SVM
This API is used to delete a qtree inside a volume of an SVM.</br>
The following example shows how to delete a qtree.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Qtree

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Qtree(id=2, **{"volume.uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717"})
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


__all__ = ["Qtree", "QtreeSchema"]
__pdoc__ = {
    "QtreeSchema.resource": False,
    "Qtree.qtree_show": False,
    "Qtree.qtree_create": False,
    "Qtree.qtree_modify": False,
    "Qtree.qtree_delete": False,
}


class QtreeSchema(ResourceSchema):
    """The fields of the Qtree object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the qtree. """

    export_policy = fields.Nested("netapp_ontap.resources.export_policy.ExportPolicySchema", data_key="export_policy", unknown=EXCLUDE)
    r""" The export_policy field of the qtree. """

    filesystem_path = fields.Str(
        data_key="filesystem_path",
    )
    r""" Path of the qtree directory. This path is relative to the volume root directory.

Example: /dir1/qtree1 """

    group = fields.Nested("netapp_ontap.models.qtree_group.QtreeGroupSchema", data_key="group", unknown=EXCLUDE)
    r""" The group field of the qtree. """

    id = Size(
        data_key="id",
        validate=integer_validation(minimum=0, maximum=4994),
    )
    r""" The identifier for the qtree, unique within the qtree's volume.


Example: 1 """

    name = fields.Str(
        data_key="name",
    )
    r""" The name of the qtree. Required in POST; optional in PATCH. """

    nas = fields.Nested("netapp_ontap.models.qtree_nas.QtreeNasSchema", data_key="nas", unknown=EXCLUDE)
    r""" The nas field of the qtree. """

    path = fields.Str(
        data_key="path",
    )
    r""" Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.

Example: /volume3/qtree1 """

    qos_policy = fields.Nested("netapp_ontap.resources.qos_policy.QosPolicySchema", data_key="qos_policy", unknown=EXCLUDE)
    r""" The qos_policy field of the qtree. """

    security_style = fields.Str(
        data_key="security_style",
    )
    r""" The security_style field of the qtree. """

    statistics = fields.Nested("netapp_ontap.models.qtree_statistics_raw.QtreeStatisticsRawSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the qtree. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the qtree. """

    unix_permissions = Size(
        data_key="unix_permissions",
    )
    r""" The UNIX permissions for the qtree. Valid in POST or PATCH.

Example: 493 """

    user = fields.Nested("netapp_ontap.models.qtree_user.QtreeUserSchema", data_key="user", unknown=EXCLUDE)
    r""" The user field of the qtree. """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the qtree. """

    @property
    def resource(self):
        return Qtree

    gettable_fields = [
        "links",
        "export_policy.links",
        "export_policy.id",
        "export_policy.name",
        "filesystem_path",
        "group",
        "id",
        "name",
        "nas",
        "path",
        "qos_policy.links",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "security_style",
        "statistics.iops_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "unix_permissions",
        "user",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,export_policy.links,export_policy.id,export_policy.name,filesystem_path,group,id,name,nas,path,qos_policy.links,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,security_style,statistics.iops_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,svm.links,svm.name,svm.uuid,unix_permissions,user,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "export_policy.id",
        "export_policy.name",
        "filesystem_path",
        "group",
        "name",
        "nas",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "security_style",
        "unix_permissions",
        "user",
    ]
    """export_policy.id,export_policy.name,filesystem_path,group,name,nas,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,security_style,unix_permissions,user,"""

    postable_fields = [
        "export_policy.id",
        "export_policy.name",
        "filesystem_path",
        "group",
        "name",
        "nas",
        "qos_policy.max_throughput_iops",
        "qos_policy.max_throughput_mbps",
        "qos_policy.min_throughput_iops",
        "qos_policy.min_throughput_mbps",
        "qos_policy.name",
        "qos_policy.uuid",
        "security_style",
        "svm.name",
        "svm.uuid",
        "unix_permissions",
        "user",
        "volume.name",
        "volume.uuid",
    ]
    """export_policy.id,export_policy.name,filesystem_path,group,name,nas,qos_policy.max_throughput_iops,qos_policy.max_throughput_mbps,qos_policy.min_throughput_iops,qos_policy.min_throughput_mbps,qos_policy.name,qos_policy.uuid,security_style,svm.name,svm.uuid,unix_permissions,user,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Qtree.get_collection(fields=field)]
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
            raise NetAppRestError("Qtree modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Qtree(Resource):
    r""" A qtree is a directory at the top level of a volume to which a custom export policy (for fine-grained access control) and a quota rule can be applied, if required. """

    _schema = QtreeSchema
    _path = "/api/storage/qtrees"
    _keys = ["volume.uuid", "id"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves qtrees configured for all FlexVol volumes or FlexGroup volumes. <br/>
Use the `fields` query parameter to retrieve all properties of the qtree. If the `fields` query parameter is not used, then GET returns the qtree `name` and qtree `id` only.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
### Related ONTAP commands
* `qtree show`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qtree show")
        def qtree_show(
            fields: List[Choices.define(["filesystem_path", "id", "name", "path", "security_style", "unix_permissions", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Qtree resources

            Args:
                filesystem_path: Path of the qtree directory. This path is relative to the volume root directory.
                id: The identifier for the qtree, unique within the qtree's volume. 
                name: The name of the qtree. Required in POST; optional in PATCH.
                path: Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.
                security_style: 
                unix_permissions: The UNIX permissions for the qtree. Valid in POST or PATCH.
            """

            kwargs = {}
            if filesystem_path is not None:
                kwargs["filesystem_path"] = filesystem_path
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path
            if security_style is not None:
                kwargs["security_style"] = security_style
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Qtree.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Qtree resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Qtree"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates properties for a specific qtree.
### Related ONTAP commands
* `qtree modify`
* `qtree rename`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Qtree"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Qtree"], NetAppResponse]:
        r"""Creates a qtree in a FlexVol volume or a FlexGroup volume. <br/>
After a qtree is created, the new qtree is assigned an identifier. This identifier is obtained using a qtree GET request. This identifier is used in the API path for the qtree PATCH and DELETE operations.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the qtree.
* `volume.uuid` or `volume.name` - Existing volume in which to create the qtree.
* `name` - Name for the qtree.
### Recommended optional properties
If not specified in POST, the values are inherited from the volume.
* `security_style` - Security style for the qtree.
* `unix_permissions` - UNIX permissions for the qtree.
* `export_policy.name or export_policy.id` - Export policy of the SVM for the qtree.
### Related ONTAP commands
* `qtree create`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Qtree"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a qtree.
### Related ONTAP commands
* `qtree delete`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves qtrees configured for all FlexVol volumes or FlexGroup volumes. <br/>
Use the `fields` query parameter to retrieve all properties of the qtree. If the `fields` query parameter is not used, then GET returns the qtree `name` and qtree `id` only.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
### Related ONTAP commands
* `qtree show`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves properties for a specific qtree identified by the `volume.uuid` and the `id` in the API path.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
### Related ONTAP commands
* `qtree show`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
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
        r"""Creates a qtree in a FlexVol volume or a FlexGroup volume. <br/>
After a qtree is created, the new qtree is assigned an identifier. This identifier is obtained using a qtree GET request. This identifier is used in the API path for the qtree PATCH and DELETE operations.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the qtree.
* `volume.uuid` or `volume.name` - Existing volume in which to create the qtree.
* `name` - Name for the qtree.
### Recommended optional properties
If not specified in POST, the values are inherited from the volume.
* `security_style` - Security style for the qtree.
* `unix_permissions` - UNIX permissions for the qtree.
* `export_policy.name or export_policy.id` - Export policy of the SVM for the qtree.
### Related ONTAP commands
* `qtree create`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qtree create")
        async def qtree_create(
        ) -> ResourceTable:
            """Create an instance of a Qtree resource

            Args:
                links: 
                export_policy: 
                filesystem_path: Path of the qtree directory. This path is relative to the volume root directory.
                group: 
                id: The identifier for the qtree, unique within the qtree's volume. 
                name: The name of the qtree. Required in POST; optional in PATCH.
                nas: 
                path: Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.
                qos_policy: 
                security_style: 
                statistics: 
                svm: 
                unix_permissions: The UNIX permissions for the qtree. Valid in POST or PATCH.
                user: 
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if export_policy is not None:
                kwargs["export_policy"] = export_policy
            if filesystem_path is not None:
                kwargs["filesystem_path"] = filesystem_path
            if group is not None:
                kwargs["group"] = group
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if nas is not None:
                kwargs["nas"] = nas
            if path is not None:
                kwargs["path"] = path
            if qos_policy is not None:
                kwargs["qos_policy"] = qos_policy
            if security_style is not None:
                kwargs["security_style"] = security_style
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions
            if user is not None:
                kwargs["user"] = user
            if volume is not None:
                kwargs["volume"] = volume

            resource = Qtree(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Qtree: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates properties for a specific qtree.
### Related ONTAP commands
* `qtree modify`
* `qtree rename`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qtree modify")
        async def qtree_modify(
        ) -> ResourceTable:
            """Modify an instance of a Qtree resource

            Args:
                filesystem_path: Path of the qtree directory. This path is relative to the volume root directory.
                query_filesystem_path: Path of the qtree directory. This path is relative to the volume root directory.
                id: The identifier for the qtree, unique within the qtree's volume. 
                query_id: The identifier for the qtree, unique within the qtree's volume. 
                name: The name of the qtree. Required in POST; optional in PATCH.
                query_name: The name of the qtree. Required in POST; optional in PATCH.
                path: Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.
                query_path: Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.
                security_style: 
                query_security_style: 
                unix_permissions: The UNIX permissions for the qtree. Valid in POST or PATCH.
                query_unix_permissions: The UNIX permissions for the qtree. Valid in POST or PATCH.
            """

            kwargs = {}
            changes = {}
            if query_filesystem_path is not None:
                kwargs["filesystem_path"] = query_filesystem_path
            if query_id is not None:
                kwargs["id"] = query_id
            if query_name is not None:
                kwargs["name"] = query_name
            if query_path is not None:
                kwargs["path"] = query_path
            if query_security_style is not None:
                kwargs["security_style"] = query_security_style
            if query_unix_permissions is not None:
                kwargs["unix_permissions"] = query_unix_permissions

            if filesystem_path is not None:
                changes["filesystem_path"] = filesystem_path
            if id is not None:
                changes["id"] = id
            if name is not None:
                changes["name"] = name
            if path is not None:
                changes["path"] = path
            if security_style is not None:
                changes["security_style"] = security_style
            if unix_permissions is not None:
                changes["unix_permissions"] = unix_permissions

            if hasattr(Qtree, "find"):
                resource = Qtree.find(
                    **kwargs
                )
            else:
                resource = Qtree()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Qtree: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a qtree.
### Related ONTAP commands
* `qtree delete`

### Learn more
* [`DOC /storage/qtrees`](#docs-storage-storage_qtrees)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="qtree delete")
        async def qtree_delete(
        ) -> None:
            """Delete an instance of a Qtree resource

            Args:
                filesystem_path: Path of the qtree directory. This path is relative to the volume root directory.
                id: The identifier for the qtree, unique within the qtree's volume. 
                name: The name of the qtree. Required in POST; optional in PATCH.
                path: Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH. This field is to be deprecated and replaced with nas.path.
                security_style: 
                unix_permissions: The UNIX permissions for the qtree. Valid in POST or PATCH.
            """

            kwargs = {}
            if filesystem_path is not None:
                kwargs["filesystem_path"] = filesystem_path
            if id is not None:
                kwargs["id"] = id
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path
            if security_style is not None:
                kwargs["security_style"] = security_style
            if unix_permissions is not None:
                kwargs["unix_permissions"] = unix_permissions

            if hasattr(Qtree, "find"):
                resource = Qtree.find(
                    **kwargs
                )
            else:
                resource = Qtree()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Qtree: %s" % err)


