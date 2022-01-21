r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Allows access to the EMS event catalog. The catalog contains a list of all events supported by the system and their corresponding descriptions, the reason for an event occurrence, and how to correct issues related to the event.
## Example
### Querying for the first event that has a message name beginning with 'C'
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import EmsMessage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(EmsMessage.get_collection(fields="name", max_records=1, name="C*")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    EmsMessage(
        {
            "name": "CR.Data.File.Inaccessible",
            "_links": {
                "self": {"href": "/api/support/ems/messages/CR.Data.File.Inaccessible"}
            },
        }
    )
]

```
</div>
</div>

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


__all__ = ["EmsMessage", "EmsMessageSchema"]
__pdoc__ = {
    "EmsMessageSchema.resource": False,
    "EmsMessage.ems_message_show": False,
    "EmsMessage.ems_message_create": False,
    "EmsMessage.ems_message_modify": False,
    "EmsMessage.ems_message_delete": False,
}


class EmsMessageSchema(ResourceSchema):
    """The fields of the EmsMessage object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ems_message. """

    corrective_action = fields.Str(
        data_key="corrective_action",
    )
    r""" Corrective action """

    deprecated = fields.Boolean(
        data_key="deprecated",
    )
    r""" Is deprecated?

Example: true """

    description = fields.Str(
        data_key="description",
    )
    r""" Description """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the event.

Example: callhome.spares.low """

    severity = fields.Str(
        data_key="severity",
        validate=enum_validation(['emergency', 'alert', 'error', 'notice', 'informational', 'debug']),
    )
    r""" Severity

Valid choices:

* emergency
* alert
* error
* notice
* informational
* debug """

    snmp_trap_type = fields.Str(
        data_key="snmp_trap_type",
        validate=enum_validation(['standard', 'built_in', 'severity_based']),
    )
    r""" SNMP trap type

Valid choices:

* standard
* built_in
* severity_based """

    @property
    def resource(self):
        return EmsMessage

    gettable_fields = [
        "links",
        "corrective_action",
        "deprecated",
        "description",
        "name",
        "severity",
        "snmp_trap_type",
    ]
    """links,corrective_action,deprecated,description,name,severity,snmp_trap_type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in EmsMessage.get_collection(fields=field)]
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
            raise NetAppRestError("EmsMessage modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class EmsMessage(Resource):
    """Allows interaction with EmsMessage objects on the host"""

    _schema = EmsMessageSchema
    _path = "/api/support/ems/messages"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the event catalog definitions.
### Related ONTAP commands
* `event catalog show`

### Learn more
* [`DOC /support/ems/messages`](#docs-support-support_ems_messages)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ems message show")
        def ems_message_show(
            fields: List[Choices.define(["corrective_action", "deprecated", "description", "name", "severity", "snmp_trap_type", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of EmsMessage resources

            Args:
                corrective_action: Corrective action
                deprecated: Is deprecated?
                description: Description
                name: Name of the event.
                severity: Severity
                snmp_trap_type: SNMP trap type
            """

            kwargs = {}
            if corrective_action is not None:
                kwargs["corrective_action"] = corrective_action
            if deprecated is not None:
                kwargs["deprecated"] = deprecated
            if description is not None:
                kwargs["description"] = description
            if name is not None:
                kwargs["name"] = name
            if severity is not None:
                kwargs["severity"] = severity
            if snmp_trap_type is not None:
                kwargs["snmp_trap_type"] = snmp_trap_type
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return EmsMessage.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all EmsMessage resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the event catalog definitions.
### Related ONTAP commands
* `event catalog show`

### Learn more
* [`DOC /support/ems/messages`](#docs-support-support_ems_messages)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






