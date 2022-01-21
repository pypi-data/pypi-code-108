r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API retrieves the current settings for the configuration and updates configuration backup settings. The GET operation retrieves the current settings for the configuration and the PATCH operation updates the configuration backup settings.
## Examples
These examples show how to retrieve and update the configuration backup settings.
### Retrieving the configuration backup settings
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConfigurationBackup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ConfigurationBackup()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
ConfigurationBackup({"username": "me", "url": "http://10.224.65.198/backups"})

```
</div>
</div>

---
### Updating the configuration backup settings
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConfigurationBackup

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ConfigurationBackup()
    resource.patch()

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


__all__ = ["ConfigurationBackup", "ConfigurationBackupSchema"]
__pdoc__ = {
    "ConfigurationBackupSchema.resource": False,
    "ConfigurationBackup.configuration_backup_show": False,
    "ConfigurationBackup.configuration_backup_create": False,
    "ConfigurationBackup.configuration_backup_modify": False,
    "ConfigurationBackup.configuration_backup_delete": False,
}


class ConfigurationBackupSchema(ResourceSchema):
    """The fields of the ConfigurationBackup object"""

    password = fields.Str(
        data_key="password",
    )
    r""" The password field of the configuration_backup.

Example: yourpassword """

    url = fields.Str(
        data_key="url",
    )
    r""" An external backup location for the cluster configuration. This is mostly required for single node clusters where node and cluster configuration backups cannot be copied to other nodes in the cluster.

Example: http://10.224.65.198/backups """

    username = fields.Str(
        data_key="username",
    )
    r""" The username field of the configuration_backup.

Example: me """

    validate_certificate = fields.Boolean(
        data_key="validate_certificate",
    )
    r""" Use this parameter with the value "true" to validate the digital certificate of the remote server. Digital certificate validation is available only when the HTTPS protocol is used in the URL; it is disabled by default. """

    @property
    def resource(self):
        return ConfigurationBackup

    gettable_fields = [
        "url",
        "username",
        "validate_certificate",
    ]
    """url,username,validate_certificate,"""

    patchable_fields = [
        "password",
        "url",
        "username",
        "validate_certificate",
    ]
    """password,url,username,validate_certificate,"""

    postable_fields = [
        "url",
        "username",
        "validate_certificate",
    ]
    """url,username,validate_certificate,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ConfigurationBackup.get_collection(fields=field)]
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
            raise NetAppRestError("ConfigurationBackup modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ConfigurationBackup(Resource):
    """Allows interaction with ConfigurationBackup objects on the host"""

    _schema = ConfigurationBackupSchema
    _path = "/api/support/configuration-backup"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the cluster configuration backup information.
### Learn more
* [`DOC /support/configuration-backup`](#docs-support-support_configuration-backup)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="configuration backup show")
        def configuration_backup_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single ConfigurationBackup resource

            Args:
                password: 
                url: An external backup location for the cluster configuration. This is mostly required for single node clusters where node and cluster configuration backups cannot be copied to other nodes in the cluster.
                username: 
                validate_certificate: Use this parameter with the value \"true\" to validate the digital certificate of the remote server. Digital certificate validation is available only when the HTTPS protocol is used in the URL; it is disabled by default.
            """

            kwargs = {}
            if password is not None:
                kwargs["password"] = password
            if url is not None:
                kwargs["url"] = url
            if username is not None:
                kwargs["username"] = username
            if validate_certificate is not None:
                kwargs["validate_certificate"] = validate_certificate
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = ConfigurationBackup(
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
        r"""Updates the cluster configuration backup information.

### Learn more
* [`DOC /support/configuration-backup`](#docs-support-support_configuration-backup)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="configuration backup modify")
        async def configuration_backup_modify(
        ) -> ResourceTable:
            """Modify an instance of a ConfigurationBackup resource

            Args:
                password: 
                query_password: 
                url: An external backup location for the cluster configuration. This is mostly required for single node clusters where node and cluster configuration backups cannot be copied to other nodes in the cluster.
                query_url: An external backup location for the cluster configuration. This is mostly required for single node clusters where node and cluster configuration backups cannot be copied to other nodes in the cluster.
                username: 
                query_username: 
                validate_certificate: Use this parameter with the value \"true\" to validate the digital certificate of the remote server. Digital certificate validation is available only when the HTTPS protocol is used in the URL; it is disabled by default.
                query_validate_certificate: Use this parameter with the value \"true\" to validate the digital certificate of the remote server. Digital certificate validation is available only when the HTTPS protocol is used in the URL; it is disabled by default.
            """

            kwargs = {}
            changes = {}
            if query_password is not None:
                kwargs["password"] = query_password
            if query_url is not None:
                kwargs["url"] = query_url
            if query_username is not None:
                kwargs["username"] = query_username
            if query_validate_certificate is not None:
                kwargs["validate_certificate"] = query_validate_certificate

            if password is not None:
                changes["password"] = password
            if url is not None:
                changes["url"] = url
            if username is not None:
                changes["username"] = username
            if validate_certificate is not None:
                changes["validate_certificate"] = validate_certificate

            if hasattr(ConfigurationBackup, "find"):
                resource = ConfigurationBackup.find(
                    **kwargs
                )
            else:
                resource = ConfigurationBackup()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ConfigurationBackup: %s" % err)



