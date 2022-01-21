r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
ONTAP allows both CIFS and NFS to access the same datastore. This datastore can contain symbolic links which are files, created by UNIX clients. It contains a reference to another file or directory. If an SMB client accesses a symbolic link, it is redirected to the target file or directory that the symbolic link refers to. The symbolic links can point to files within the volume that contain the share, or to files that are contained in other volumes on the Storage Virtual Machine (SVM), or even to volumes contained on other SVMs.<p/>
There are two types of symbolic links:

  * <b>Relative</b>  A relative symbolic link contains a reference to the file or directory relative to its parent directory. Therefore, the path of the file it is referring to should not begin with a backslash (/). If you enable symbolic links on a share, relative symbolic links work without UNIX symlink mapping.
  * <b>Absolute</b> An absolute symbolic link contains a reference to a file or directory in the form of an absolute path. Therefore, the path of the file it is referring to should begin with a backslash (/). An absolute symbolic link can refer to a file or directory within or outside of the file system of the symbolic link. If the target is not in the same local file system, the symbolic link is called a "widelink". If the symbolic link is enabled on a share and absolute symbolic links do not work right away, the mapping between the UNIX path of the symbolic link to the destination CIFS path must be created. When creating absolute symbolic link mappings, locality could be either "local" or "widelink" and it must be specified. If UNIX symlink mapping is created for a file or directory which is outside of the local share but the locality is set to "local", ONTAP does not allow access to the target.
</br>A UNIX symbolic link support could be added to SMB shares by specifying the <i>unix_symlink</i> property during the creation of SMB shares or at any time by modifying the existing SMB <i>unix_symlink</i> property. UNIX symbolic link support is enabled by default.<p/>
## Examples
### Creating a UNIX symlink mapping for CIFS shares
To create UNIX symlink mappings for SMB shares, use the following API. Note the <i>return_records=true</i> query parameter used to obtain the newly created entry in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSymlinkMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSymlinkMapping()
    resource.svm = {"name": "vs1", "uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb"}
    resource.target = {
        "home_directory": False,
        "locality": "local",
        "path": "/dir1/dir2/",
        "server": "cifs123",
        "share": "sh1",
    }
    resource.unix_path = "/mnt/eng_volume/"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
CifsSymlinkMapping(
    {
        "unix_path": "/mnt/eng_volume/",
        "target": {
            "share": "sh1",
            "server": "cifs123",
            "locality": "local",
            "home_directory": False,
            "path": "/dir1/dir2/",
        },
        "svm": {"uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb", "name": "vs1"},
    }
)

```
</div>
</div>

---
### Retrieving UNIX symlink mappings for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSymlinkMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(CifsSymlinkMapping.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    CifsSymlinkMapping(
        {
            "unix_path": "/mnt/eng_volume/",
            "target": {
                "share": "sh1",
                "server": "CIFS123",
                "locality": "local",
                "home_directory": False,
                "path": "/dir1/dir2/",
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/000c5cd2-ebdf-11e8-a96e-0050568ea3cb"
                    }
                },
                "uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb",
                "name": "vs1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/cifs/unix-symlink-mapping/000c5cd2-ebdf-11e8-a96e-0050568ea3cb/%2Fmnt%2Feng_volume%2F"
                }
            },
        }
    ),
    CifsSymlinkMapping(
        {
            "unix_path": "/mnt/eng_volume/",
            "target": {
                "share": "ENG_SHARE",
                "server": "ENGCIFS",
                "locality": "widelink",
                "home_directory": False,
                "path": "/dir1/dir2/",
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/1d30d1b1-ebdf-11e8-a96e-0050568ea3cb"
                    }
                },
                "uuid": "1d30d1b1-ebdf-11e8-a96e-0050568ea3cb",
                "name": "vs2",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/cifs/unix-symlink-mapping/1d30d1b1-ebdf-11e8-a96e-0050568ea3cb/%2Fmnt%2Feng_volume%2F"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving a specific UNIX symlink mapping for an SVM
The mapping being returned is identified by the UUID of its SVM and the unix-path.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSymlinkMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSymlinkMapping(
        unix_path="/mnt/eng_volume/",
        **{"svm.uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
CifsSymlinkMapping(
    {
        "unix_path": "/mnt/eng_volume/",
        "target": {
            "share": "sh1",
            "server": "CIFS123",
            "locality": "local",
            "home_directory": False,
            "path": "/dir1/dir2/",
        },
        "svm": {"uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb", "name": "vs1"},
    }
)

```
</div>
</div>

### Updating a specific UNIX symlink mapping for an SVM
The mapping being modified is identified by the UUID of its SVM and the unix-path.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSymlinkMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSymlinkMapping(
        unix_path="/mnt/eng_volume/",
        **{"svm.uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb"}
    )
    resource.target = {
        "home_directory": True,
        "locality": "widelink",
        "path": "/new_path/",
        "server": "HR_SERVER",
        "share": "sh2",
    }
    resource.patch()

```

### Removing a specific UNIX symlink mapping for an SVM
The mapping being removed is identified by the UUID of its SVM and the unix-path.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSymlinkMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSymlinkMapping(
        unix_path="/mnt/eng_volume/",
        **{"svm.uuid": "000c5cd2-ebdf-11e8-a96e-0050568ea3cb"}
    )
    resource.delete()

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


__all__ = ["CifsSymlinkMapping", "CifsSymlinkMappingSchema"]
__pdoc__ = {
    "CifsSymlinkMappingSchema.resource": False,
    "CifsSymlinkMapping.cifs_symlink_mapping_show": False,
    "CifsSymlinkMapping.cifs_symlink_mapping_create": False,
    "CifsSymlinkMapping.cifs_symlink_mapping_modify": False,
    "CifsSymlinkMapping.cifs_symlink_mapping_delete": False,
}


class CifsSymlinkMappingSchema(ResourceSchema):
    """The fields of the CifsSymlinkMapping object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cifs_symlink_mapping. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the cifs_symlink_mapping. """

    target = fields.Nested("netapp_ontap.models.cifs_target.CifsTargetSchema", data_key="target", unknown=EXCLUDE)
    r""" The target field of the cifs_symlink_mapping. """

    unix_path = fields.Str(
        data_key="unix_path",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Specifies the UNIX path prefix to be matched for the mapping.

Example: /mnt/eng_volume/ """

    @property
    def resource(self):
        return CifsSymlinkMapping

    gettable_fields = [
        "links",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "target",
        "unix_path",
    ]
    """links,svm.links,svm.name,svm.uuid,target,unix_path,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
        "target",
    ]
    """svm.name,svm.uuid,target,"""

    postable_fields = [
        "svm.name",
        "svm.uuid",
        "target",
        "unix_path",
    ]
    """svm.name,svm.uuid,target,unix_path,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in CifsSymlinkMapping.get_collection(fields=field)]
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
            raise NetAppRestError("CifsSymlinkMapping modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class CifsSymlinkMapping(Resource):
    r""" ONTAP allows for both CIFS and NFS access to the same datastore. This datastore can contain symbolic links created by UNIX clients which can point anywhere from the perspective of the UNIX client. To Access such UNIX symlink from CIFS share, we need to create a CIFS symbolic link path mapping from a UNIX symlink and target it as a CIFS path. """

    _schema = CifsSymlinkMappingSchema
    _path = "/api/protocols/cifs/unix-symlink-mapping"
    _keys = ["svm.uuid", "unix_path"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves UNIX symbolic link mappings for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink show`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs symlink mapping show")
        def cifs_symlink_mapping_show(
            fields: List[Choices.define(["unix_path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of CifsSymlinkMapping resources

            Args:
                unix_path: Specifies the UNIX path prefix to be matched for the mapping.
            """

            kwargs = {}
            if unix_path is not None:
                kwargs["unix_path"] = unix_path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return CifsSymlinkMapping.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all CifsSymlinkMapping resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["CifsSymlinkMapping"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the UNIX symbolic link mapping for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink modify`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["CifsSymlinkMapping"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["CifsSymlinkMapping"], NetAppResponse]:
        r"""Creates a UNIX symbolic link mapping for a CIFS client.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the CIFS unix-symlink-mapping.
* `unix_path` - UNIX path to which the CIFS symlink mapping to be created.
* `target.share` - CIFS share name on the destination CIFS server to which the UNIX symbolic link is pointing.
* `target.path` - CIFS path on the destination to which the symbolic link maps.
### Default property values
* `target.server` - _Local_NetBIOS_Server_Name_
* `locality` - _local_
* `home_directory` - _false_
### Related ONTAP commands
* `vserver cifs symlink create`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
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
        records: Iterable["CifsSymlinkMapping"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the UNIX symbolic link mapping for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink delete`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves UNIX symbolic link mappings for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink show`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a UNIX symbolic link mapping for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink show`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
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
        r"""Creates a UNIX symbolic link mapping for a CIFS client.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the CIFS unix-symlink-mapping.
* `unix_path` - UNIX path to which the CIFS symlink mapping to be created.
* `target.share` - CIFS share name on the destination CIFS server to which the UNIX symbolic link is pointing.
* `target.path` - CIFS path on the destination to which the symbolic link maps.
### Default property values
* `target.server` - _Local_NetBIOS_Server_Name_
* `locality` - _local_
* `home_directory` - _false_
### Related ONTAP commands
* `vserver cifs symlink create`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs symlink mapping create")
        async def cifs_symlink_mapping_create(
        ) -> ResourceTable:
            """Create an instance of a CifsSymlinkMapping resource

            Args:
                links: 
                svm: 
                target: 
                unix_path: Specifies the UNIX path prefix to be matched for the mapping.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if svm is not None:
                kwargs["svm"] = svm
            if target is not None:
                kwargs["target"] = target
            if unix_path is not None:
                kwargs["unix_path"] = unix_path

            resource = CifsSymlinkMapping(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create CifsSymlinkMapping: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the UNIX symbolic link mapping for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink modify`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs symlink mapping modify")
        async def cifs_symlink_mapping_modify(
        ) -> ResourceTable:
            """Modify an instance of a CifsSymlinkMapping resource

            Args:
                unix_path: Specifies the UNIX path prefix to be matched for the mapping.
                query_unix_path: Specifies the UNIX path prefix to be matched for the mapping.
            """

            kwargs = {}
            changes = {}
            if query_unix_path is not None:
                kwargs["unix_path"] = query_unix_path

            if unix_path is not None:
                changes["unix_path"] = unix_path

            if hasattr(CifsSymlinkMapping, "find"):
                resource = CifsSymlinkMapping.find(
                    **kwargs
                )
            else:
                resource = CifsSymlinkMapping()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify CifsSymlinkMapping: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the UNIX symbolic link mapping for CIFS clients.
### Related ONTAP commands
* `vserver cifs symlink delete`
### Learn more
* [`DOC /protocols/cifs/unix-symlink-mapping`](#docs-NAS-protocols_cifs_unix-symlink-mapping)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs symlink mapping delete")
        async def cifs_symlink_mapping_delete(
        ) -> None:
            """Delete an instance of a CifsSymlinkMapping resource

            Args:
                unix_path: Specifies the UNIX path prefix to be matched for the mapping.
            """

            kwargs = {}
            if unix_path is not None:
                kwargs["unix_path"] = unix_path

            if hasattr(CifsSymlinkMapping, "find"):
                resource = CifsSymlinkMapping.find(
                    **kwargs
                )
            else:
                resource = CifsSymlinkMapping()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete CifsSymlinkMapping: %s" % err)


