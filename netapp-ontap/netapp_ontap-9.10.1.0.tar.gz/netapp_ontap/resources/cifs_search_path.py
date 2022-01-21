r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
ONTAP home directory functionality can be used to create home directories for SMB users on the CIFS server and automatically offer each user a dynamic share to their home directory without creating an individual SMB share for each user.<p/>
The home directory search path is a set of absolute paths from the root of an SVM that directs ONTAP to search for home directories. If there are multiple search paths, ONTAP tries them in the order specified until it finds a valid path. To use the CIFS home directories feature, at least one home directory search path must be added for an SVM. <p/>
## Examples
### Creating a home directory search path
To create a home directory search path, use the following API. Note the <i>return_records=true</i> query parameter used to obtain the newly created entry in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSearchPath

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSearchPath()
    resource.path = "/"
    resource.svm = {"name": "vs1", "uuid": "a41fd873-ecf8-11e8-899d-0050568e9333"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
CifsSearchPath(
    {
        "path": "/",
        "svm": {"uuid": "a41fd873-ecf8-11e8-899d-0050568e9333", "name": "vs1"},
    }
)

```
</div>
</div>

---
### Retrieving the CIFS home directory search paths configuration for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSearchPath

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(CifsSearchPath.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    CifsSearchPath(
        {
            "path": "/",
            "svm": {"uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e", "name": "vs1"},
            "index": 1,
        }
    ),
    CifsSearchPath(
        {
            "path": "/a",
            "svm": {"uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e", "name": "vs1"},
            "index": 2,
        }
    ),
    CifsSearchPath(
        {
            "path": "/",
            "svm": {"uuid": "4f23449b-f4ce-11e8-b075-0050568e278e", "name": "vs2"},
            "index": 1,
        }
    ),
    CifsSearchPath(
        {
            "path": "/1",
            "svm": {"uuid": "4f23449b-f4ce-11e8-b075-0050568e278e", "name": "vs2"},
            "index": 2,
        }
    ),
]

```
</div>
</div>

### Retrieving a specific home directory searchpath configuration for an SVM
The configuration returned is identified by the UUID of its SVM and the index (position) in the list of search paths that is searched to  find a home directory of a user. <br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSearchPath

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSearchPath(
        index=2, **{"svm.uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
CifsSearchPath(
    {
        "path": "/a",
        "svm": {"uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e", "name": "vs1"},
        "index": 2,
    }
)

```
</div>
</div>

### Reordering a specific home drectory search path in the list
An entry in the home directory search path list can be reordered to a new positin by specifying the 'new_index' field. The reordered configuration is identified by the UUID of its SVM and the index. <br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSearchPath

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSearchPath(
        index=2, **{"svm.uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e"}
    )
    resource.patch(hydrate=True, new_index=1)

```

### Removing a specific home directory search path for an SVM
The entry being removed is identified by the UUID of its SVM and the index. <br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import CifsSearchPath

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = CifsSearchPath(
        index=2, **{"svm.uuid": "2d96f9aa-f4ce-11e8-b075-0050568e278e"}
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


__all__ = ["CifsSearchPath", "CifsSearchPathSchema"]
__pdoc__ = {
    "CifsSearchPathSchema.resource": False,
    "CifsSearchPath.cifs_search_path_show": False,
    "CifsSearchPath.cifs_search_path_create": False,
    "CifsSearchPath.cifs_search_path_modify": False,
    "CifsSearchPath.cifs_search_path_delete": False,
}


class CifsSearchPathSchema(ResourceSchema):
    """The fields of the CifsSearchPath object"""

    index = Size(
        data_key="index",
    )
    r""" The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST. """

    path = fields.Str(
        data_key="path",
    )
    r""" The file system path that is searched to find the home directory of the CIFS client.

Example: /HomeDirectory/EngDomain """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the cifs_search_path. """

    @property
    def resource(self):
        return CifsSearchPath

    gettable_fields = [
        "index",
        "path",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """index,path,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "path",
        "svm.name",
        "svm.uuid",
    ]
    """path,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in CifsSearchPath.get_collection(fields=field)]
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
            raise NetAppRestError("CifsSearchPath modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class CifsSearchPath(Resource):
    r""" This is a list of CIFS home directory search paths. When a CIFS client connects to a home directory share, these paths are searched in the order indicated by the position field to find the home directory of the connected CIFS client. """

    _schema = CifsSearchPathSchema
    _path = "/api/protocols/cifs/home-directory/search-paths"
    _keys = ["svm.uuid", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves CIFS home directory search paths.
### Related ONTAP commands
* `cifs server home-directory search-path show`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs search path show")
        def cifs_search_path_show(
            fields: List[Choices.define(["index", "path", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of CifsSearchPath resources

            Args:
                index: The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST.
                path: The file system path that is searched to find the home directory of the CIFS client.
            """

            kwargs = {}
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return CifsSearchPath.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all CifsSearchPath resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["CifsSearchPath"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Reorders a CIFS home directory search path.
### Related ONTAP commands
* `cifs server home-directory search-path reorder`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["CifsSearchPath"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["CifsSearchPath"], NetAppResponse]:
        r"""Creates a home directory search path.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the home directory search path.
* `path` - Path in the owning SVM namespace that is used to search for home directories.
### Related ONTAP commands
* `cifs server home-directory search-path add`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
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
        records: Iterable["CifsSearchPath"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a CIFS home directory search path.
### Related ONTAP commands
* `cifs server home-directory search-path remove`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves CIFS home directory search paths.
### Related ONTAP commands
* `cifs server home-directory search-path show`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a CIFS home directory search path of an SVM.
### Related ONTAP commands
* `cifs server home-directory search-path show`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
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
        r"""Creates a home directory search path.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the home directory search path.
* `path` - Path in the owning SVM namespace that is used to search for home directories.
### Related ONTAP commands
* `cifs server home-directory search-path add`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs search path create")
        async def cifs_search_path_create(
        ) -> ResourceTable:
            """Create an instance of a CifsSearchPath resource

            Args:
                index: The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST.
                path: The file system path that is searched to find the home directory of the CIFS client.
                svm: 
            """

            kwargs = {}
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path
            if svm is not None:
                kwargs["svm"] = svm

            resource = CifsSearchPath(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create CifsSearchPath: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Reorders a CIFS home directory search path.
### Related ONTAP commands
* `cifs server home-directory search-path reorder`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs search path modify")
        async def cifs_search_path_modify(
        ) -> ResourceTable:
            """Modify an instance of a CifsSearchPath resource

            Args:
                index: The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST.
                query_index: The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST.
                path: The file system path that is searched to find the home directory of the CIFS client.
                query_path: The file system path that is searched to find the home directory of the CIFS client.
            """

            kwargs = {}
            changes = {}
            if query_index is not None:
                kwargs["index"] = query_index
            if query_path is not None:
                kwargs["path"] = query_path

            if index is not None:
                changes["index"] = index
            if path is not None:
                changes["path"] = path

            if hasattr(CifsSearchPath, "find"):
                resource = CifsSearchPath.find(
                    **kwargs
                )
            else:
                resource = CifsSearchPath()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify CifsSearchPath: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a CIFS home directory search path.
### Related ONTAP commands
* `cifs server home-directory search-path remove`
### Learn more
* [`DOC /protocols/cifs/home-directory/search-paths`](#docs-NAS-protocols_cifs_home-directory_search-paths)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cifs search path delete")
        async def cifs_search_path_delete(
        ) -> None:
            """Delete an instance of a CifsSearchPath resource

            Args:
                index: The position in the list of paths that is searched to find the home directory of the CIFS client. Not available in POST.
                path: The file system path that is searched to find the home directory of the CIFS client.
            """

            kwargs = {}
            if index is not None:
                kwargs["index"] = index
            if path is not None:
                kwargs["path"] = path

            if hasattr(CifsSearchPath, "find"):
                resource = CifsSearchPath.find(
                    **kwargs
                )
            else:
                resource = CifsSearchPath()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete CifsSearchPath: %s" % err)


