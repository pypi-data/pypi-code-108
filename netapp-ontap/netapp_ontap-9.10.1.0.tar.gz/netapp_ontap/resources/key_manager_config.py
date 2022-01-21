r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Retrieves or modifies the key management configuration options. The following operations are supported:

* GET
* PATCH
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


__all__ = ["KeyManagerConfig", "KeyManagerConfigSchema"]
__pdoc__ = {
    "KeyManagerConfigSchema.resource": False,
    "KeyManagerConfig.key_manager_config_show": False,
    "KeyManagerConfig.key_manager_config_create": False,
    "KeyManagerConfig.key_manager_config_modify": False,
    "KeyManagerConfig.key_manager_config_delete": False,
}


class KeyManagerConfigSchema(ResourceSchema):
    """The fields of the KeyManagerConfig object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the key_manager_config. """

    cc_mode_enabled = fields.Boolean(
        data_key="cc_mode_enabled",
    )
    r""" Indicates whether the Common Criteria Mode configuration is enabled. """

    health_monitor_polling_interval = Size(
        data_key="health_monitor_polling_interval",
    )
    r""" Health Monitor Polling Period, in minutes. Supported value range of 15-30 minutes.

Example: 20 """

    passphrase = fields.Str(
        data_key="passphrase",
    )
    r""" Current cluster-wide passphrase. This is a required field when setting the cc_mode_enabled field value to true. This is not audited.

Example: The cluster passphrase of length 64-256 ASCII characters. """

    @property
    def resource(self):
        return KeyManagerConfig

    gettable_fields = [
        "links",
        "cc_mode_enabled",
        "health_monitor_polling_interval",
    ]
    """links,cc_mode_enabled,health_monitor_polling_interval,"""

    patchable_fields = [
        "cc_mode_enabled",
        "health_monitor_polling_interval",
        "passphrase",
    ]
    """cc_mode_enabled,health_monitor_polling_interval,passphrase,"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in KeyManagerConfig.get_collection(fields=field)]
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
            raise NetAppRestError("KeyManagerConfig modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class KeyManagerConfig(Resource):
    r""" Manages the various keymanager configuration options. """

    _schema = KeyManagerConfigSchema
    _path = "/api/security/key-manager-configs"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves key manager configurations.
### Related ONTAP commands
* `security key-manager config show`

### Learn more
* [`DOC /security/key-manager-configs`](#docs-security-security_key-manager-configs)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="key manager config show")
        def key_manager_config_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single KeyManagerConfig resource

            Args:
                cc_mode_enabled: Indicates whether the Common Criteria Mode configuration is enabled.
                health_monitor_polling_interval: Health Monitor Polling Period, in minutes. Supported value range of 15-30 minutes.
                passphrase: Current cluster-wide passphrase. This is a required field when setting the cc_mode_enabled field value to true. This is not audited.
            """

            kwargs = {}
            if cc_mode_enabled is not None:
                kwargs["cc_mode_enabled"] = cc_mode_enabled
            if health_monitor_polling_interval is not None:
                kwargs["health_monitor_polling_interval"] = health_monitor_polling_interval
            if passphrase is not None:
                kwargs["passphrase"] = passphrase
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = KeyManagerConfig(
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
        r"""Updates key manager configurations.
### Related ONTAP commands
* `security key-manager config modify`

### Learn more
* [`DOC /security/key-manager-configs`](#docs-security-security_key-manager-configs)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="key manager config modify")
        async def key_manager_config_modify(
        ) -> ResourceTable:
            """Modify an instance of a KeyManagerConfig resource

            Args:
                cc_mode_enabled: Indicates whether the Common Criteria Mode configuration is enabled.
                query_cc_mode_enabled: Indicates whether the Common Criteria Mode configuration is enabled.
                health_monitor_polling_interval: Health Monitor Polling Period, in minutes. Supported value range of 15-30 minutes.
                query_health_monitor_polling_interval: Health Monitor Polling Period, in minutes. Supported value range of 15-30 minutes.
                passphrase: Current cluster-wide passphrase. This is a required field when setting the cc_mode_enabled field value to true. This is not audited.
                query_passphrase: Current cluster-wide passphrase. This is a required field when setting the cc_mode_enabled field value to true. This is not audited.
            """

            kwargs = {}
            changes = {}
            if query_cc_mode_enabled is not None:
                kwargs["cc_mode_enabled"] = query_cc_mode_enabled
            if query_health_monitor_polling_interval is not None:
                kwargs["health_monitor_polling_interval"] = query_health_monitor_polling_interval
            if query_passphrase is not None:
                kwargs["passphrase"] = query_passphrase

            if cc_mode_enabled is not None:
                changes["cc_mode_enabled"] = cc_mode_enabled
            if health_monitor_polling_interval is not None:
                changes["health_monitor_polling_interval"] = health_monitor_polling_interval
            if passphrase is not None:
                changes["passphrase"] = passphrase

            if hasattr(KeyManagerConfig, "find"):
                resource = KeyManagerConfig.find(
                    **kwargs
                )
            else:
                resource = KeyManagerConfig()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify KeyManagerConfig: %s" % err)



