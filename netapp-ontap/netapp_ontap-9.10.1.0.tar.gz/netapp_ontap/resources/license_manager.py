r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API is used to manage information about the license manager instance associated with the cluster.</br>
When an ONTAP cluster is initially created to use the capacity pools licensing model, information about the license manager instance that the cluster should use is pre-configured. Generally, this configuration does not need to be updated unless the license manager instance changes its IP address.</br>
The license manager is currently bundled with the ONTAP Select Deploy utility and runs on the same VM as ONTAP Select Deploy. Use this API to update the license manager IP address when the Deploy VM changes its IP address.</br>
---
## Examples
### Retrieving information about the license manager instance associated with the cluster
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicenseManager

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LicenseManager.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LicenseManager(
        {
            "default": True,
            "uuid": "4ea7a442-86d1-11e0-ae1c-112233445566",
            "uri": {"host": "10.1.1.1"},
        }
    )
]

```
</div>
</div>

### Updating an existing license manager instance
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicenseManager

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicenseManager(uuid="4ea7a442-86d1-11e0-ae1c-112233445566")
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


__all__ = ["LicenseManager", "LicenseManagerSchema"]
__pdoc__ = {
    "LicenseManagerSchema.resource": False,
    "LicenseManager.license_manager_show": False,
    "LicenseManager.license_manager_create": False,
    "LicenseManager.license_manager_modify": False,
    "LicenseManager.license_manager_delete": False,
}


class LicenseManagerSchema(ResourceSchema):
    """The fields of the LicenseManager object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the license_manager. """

    default = fields.Boolean(
        data_key="default",
    )
    r""" Flag that indicates whether it's the default license manager instance used by the cluster.'
When a capacity pool is created and if the license manager field is omitted, it is assumed that the license of the capacity pool is installed on the default license manager instance. """

    uri = fields.Nested("netapp_ontap.models.license_manager_uri.LicenseManagerUriSchema", data_key="uri", unknown=EXCLUDE)
    r""" The uri field of the license_manager. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the license_manager.

Example: 4ea7a442-86d1-11e0-ae1c-112233445566 """

    @property
    def resource(self):
        return LicenseManager

    gettable_fields = [
        "links",
        "default",
        "uri",
        "uuid",
    ]
    """links,default,uri,uuid,"""

    patchable_fields = [
        "uri",
    ]
    """uri,"""

    postable_fields = [
        "uri",
    ]
    """uri,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LicenseManager.get_collection(fields=field)]
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
            raise NetAppRestError("LicenseManager modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LicenseManager(Resource):
    r""" Information on a license manager instance associated with the cluster. """

    _schema = LicenseManagerSchema
    _path = "/api/cluster/licensing/license-managers"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of license managers.
### Learn more
* [`DOC /cluster/licensing/license-managers`](#docs-cluster-cluster_licensing_license-managers)
### Related ONTAP commands
* `system license license-manager show`
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="license manager show")
        def license_manager_show(
            fields: List[Choices.define(["default", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LicenseManager resources

            Args:
                default: Flag that indicates whether it's the default license manager instance used by the cluster.' When a capacity pool is created and if the license manager field is omitted, it is assumed that the license of the capacity pool is installed on the default license manager instance. 
                uuid: 
            """

            kwargs = {}
            if default is not None:
                kwargs["default"] = default
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LicenseManager.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LicenseManager resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LicenseManager"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the license manager configuration.
### Learn more
* [`DOC /cluster/licensing/license-managers`](#docs-cluster-cluster_licensing_license-managers)
### Related ONTAP commands
* `system license license-manager modify`
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of license managers.
### Learn more
* [`DOC /cluster/licensing/license-managers`](#docs-cluster-cluster_licensing_license-managers)
### Related ONTAP commands
* `system license license-manager show`
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about the license manager.
### Learn more
* [`DOC /cluster/licensing/license-managers`](#docs-cluster-cluster_licensing_license-managers)
### Related ONTAP commands
* `system license license-manager show`
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
        r"""Updates the license manager configuration.
### Learn more
* [`DOC /cluster/licensing/license-managers`](#docs-cluster-cluster_licensing_license-managers)
### Related ONTAP commands
* `system license license-manager modify`
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="license manager modify")
        async def license_manager_modify(
        ) -> ResourceTable:
            """Modify an instance of a LicenseManager resource

            Args:
                default: Flag that indicates whether it's the default license manager instance used by the cluster.' When a capacity pool is created and if the license manager field is omitted, it is assumed that the license of the capacity pool is installed on the default license manager instance. 
                query_default: Flag that indicates whether it's the default license manager instance used by the cluster.' When a capacity pool is created and if the license manager field is omitted, it is assumed that the license of the capacity pool is installed on the default license manager instance. 
                uuid: 
                query_uuid: 
            """

            kwargs = {}
            changes = {}
            if query_default is not None:
                kwargs["default"] = query_default
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if default is not None:
                changes["default"] = default
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(LicenseManager, "find"):
                resource = LicenseManager.find(
                    **kwargs
                )
            else:
                resource = LicenseManager()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LicenseManager: %s" % err)



