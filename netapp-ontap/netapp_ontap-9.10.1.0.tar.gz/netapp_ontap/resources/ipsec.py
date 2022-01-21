r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The following operations are supported:

* GET to retrieve the IPsec status: GET security/ipsec
* Patch to update IPsec status: PATCH security/ipsec
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


__all__ = ["Ipsec", "IpsecSchema"]
__pdoc__ = {
    "IpsecSchema.resource": False,
    "Ipsec.ipsec_show": False,
    "Ipsec.ipsec_create": False,
    "Ipsec.ipsec_modify": False,
    "Ipsec.ipsec_delete": False,
}


class IpsecSchema(ResourceSchema):
    """The fields of the Ipsec object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ipsec. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Indicates whether or not IPsec is enabled. """

    replay_window = Size(
        data_key="replay_window",
    )
    r""" Replay window size in packets, where 0 indicates that the relay window is disabled. """

    @property
    def resource(self):
        return Ipsec

    gettable_fields = [
        "links",
        "enabled",
        "replay_window",
    ]
    """links,enabled,replay_window,"""

    patchable_fields = [
        "enabled",
        "replay_window",
    ]
    """enabled,replay_window,"""

    postable_fields = [
        "enabled",
        "replay_window",
    ]
    """enabled,replay_window,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Ipsec.get_collection(fields=field)]
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
            raise NetAppRestError("Ipsec modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Ipsec(Resource):
    r""" Manages IPsec configuration via REST APIs. """

    _schema = IpsecSchema
    _path = "/api/security/ipsec"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves IPsec configuration via REST APIs.
### Related ONTAP commands
* 'security ipsec config show'

### Learn more
* [`DOC /security/ipsec`](#docs-security-security_ipsec)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec show")
        def ipsec_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single Ipsec resource

            Args:
                enabled: Indicates whether or not IPsec is enabled.
                replay_window: Replay window size in packets, where 0 indicates that the relay window is disabled.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if replay_window is not None:
                kwargs["replay_window"] = replay_window
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = Ipsec(
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
        r"""Updates IPsec configuration via REST APIs.
### Related ONTAP commands
* 'security ipsec config modify'

### Learn more
* [`DOC /security/ipsec`](#docs-security-security_ipsec)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ipsec modify")
        async def ipsec_modify(
        ) -> ResourceTable:
            """Modify an instance of a Ipsec resource

            Args:
                enabled: Indicates whether or not IPsec is enabled.
                query_enabled: Indicates whether or not IPsec is enabled.
                replay_window: Replay window size in packets, where 0 indicates that the relay window is disabled.
                query_replay_window: Replay window size in packets, where 0 indicates that the relay window is disabled.
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_replay_window is not None:
                kwargs["replay_window"] = query_replay_window

            if enabled is not None:
                changes["enabled"] = enabled
            if replay_window is not None:
                changes["replay_window"] = replay_window

            if hasattr(Ipsec, "find"):
                resource = Ipsec.find(
                    **kwargs
                )
            else:
                resource = Ipsec()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Ipsec: %s" % err)



