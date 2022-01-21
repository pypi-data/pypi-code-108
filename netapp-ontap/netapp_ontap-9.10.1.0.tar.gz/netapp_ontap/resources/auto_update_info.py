r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The Automatic Update feature helps keep the ONTAP cluster current with the latest software component updates by automatically downloading and applying them to the cluster.
By enabling this feature, you agree to the following terms:
---
### AUTOMATIC UPDATE TERMS
*These Automatic Update Terms ("Terms") set forth the terms and conditions between NetApp, Inc., NetApp B.V., or any of  their affiliates ("NetApp") and End User Customer ("Customer") in connection with the feature enabling Customer to receive software patches, upgrades, and updates to NetApp Software automatically ("Automatic Update"). By agreeing to and accepting Automatic Updates, Customer agrees to be bound by these Terms, as well as NetApp's End User License Agreement and Support Terms available at https://www.netapp.com/how-to-buy/sales-terms-and-conditions/.*
<br/>
*By enabling the Automatic Update feature, Customer agrees to receive Automatic Updates that NetApp may provide from time to time, without any additional notice, and NetApp will not be liable for any damages, loss of data or loss of functionalities arising from provision of Automatic Updates. Customer may revoke acceptance of these Terms and disable the receipt of Automatic Updates by setting the feature configuration to "Disabled" in ONTAP.*
<br/>
---
Important note:
When the automatic update feature is disabled

  * No new updates are shown to the user
  * All automatic updates currently scheduled will have their schedules cancelled.
  * All automatic updates currently waiting for user confirmation cannnot be started until the feature is re-enabled.
---
## Examples
### Retrieving the current status of the automatic update feature
The following example shows how to retrieve the current status of the automatic update feature:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutoUpdateInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutoUpdateInfo()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
AutoUpdateInfo(
    {
        "eula": {
            "accepted_timestamp": "2020-12-01T21:24:44-04:00",
            "user_id_accepted": "admin",
            "accepted": True,
            "accepted_ip_address": "192.168.1.125",
        },
        "enabled": True,
        "_links": {"self": {}},
    }
)

```
</div>
</div>

---
### Updating the status of the automatic update feature
The following example shows how to update the status of the automatic update feature:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AutoUpdateInfo

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AutoUpdateInfo()
    resource.enabled = True
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


__all__ = ["AutoUpdateInfo", "AutoUpdateInfoSchema"]
__pdoc__ = {
    "AutoUpdateInfoSchema.resource": False,
    "AutoUpdateInfo.auto_update_info_show": False,
    "AutoUpdateInfo.auto_update_info_create": False,
    "AutoUpdateInfo.auto_update_info_modify": False,
    "AutoUpdateInfo.auto_update_info_delete": False,
}


class AutoUpdateInfoSchema(ResourceSchema):
    """The fields of the AutoUpdateInfo object"""

    links = fields.Nested("netapp_ontap.models.application_subsystem_map_object_subsystem_links.ApplicationSubsystemMapObjectSubsystemLinksSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the auto_update_info. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Flag indicating feature state.

Example: true """

    eula = fields.Nested("netapp_ontap.models.auto_update_info_eula.AutoUpdateInfoEulaSchema", data_key="eula", unknown=EXCLUDE)
    r""" The eula field of the auto_update_info. """

    @property
    def resource(self):
        return AutoUpdateInfo

    gettable_fields = [
        "links",
        "enabled",
        "eula",
    ]
    """links,enabled,eula,"""

    patchable_fields = [
        "links",
        "enabled",
        "eula",
    ]
    """links,enabled,eula,"""

    postable_fields = [
        "links",
        "eula",
    ]
    """links,eula,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in AutoUpdateInfo.get_collection(fields=field)]
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
            raise NetAppRestError("AutoUpdateInfo modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class AutoUpdateInfo(Resource):
    """Allows interaction with AutoUpdateInfo objects on the host"""

    _schema = AutoUpdateInfoSchema
    _path = "/api/support/auto-update"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the current status of the automatic update feature and the End User License Agreement (EULA).

### Learn more
* [`DOC /support/auto-update`](#docs-support-support_auto-update)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="auto update info show")
        def auto_update_info_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single AutoUpdateInfo resource

            Args:
                enabled: Flag indicating feature state.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = AutoUpdateInfo(
                **kwargs
            )
            resource.get()
            return [resource]


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the current enabled status of the automatic update feature and accepts the EULA.

### Learn more
* [`DOC /support/auto-update`](#docs-support-support_auto-update)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="auto update info modify")
        async def auto_update_info_modify(
        ) -> ResourceTable:
            """Modify an instance of a AutoUpdateInfo resource

            Args:
                enabled: Flag indicating feature state.
                query_enabled: Flag indicating feature state.
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled

            if enabled is not None:
                changes["enabled"] = enabled

            if hasattr(AutoUpdateInfo, "find"):
                resource = AutoUpdateInfo.find(
                    **kwargs
                )
            else:
                resource = AutoUpdateInfo()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify AutoUpdateInfo: %s" % err)



