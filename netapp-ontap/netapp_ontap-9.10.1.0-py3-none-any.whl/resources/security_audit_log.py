r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
These APIs return audit log records. The GET requests retrieves all audit log records. An audit log record contains information such as timestamp, node name, index and so on.
<br />
---
## Example
### Retrieving audit log records
The following example shows the audit log records.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecurityAuditLog

with HostConnection(
    "<cluster-ip>", username="admin", password="password", verify=False
):
    print(list(SecurityAuditLog.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    SecurityAuditLog(
        {
            "timestamp": "2019-03-08T11:03:32-05:00",
            "scope": "cluster",
            "input": "GET /api/security/audit/destinations/",
            "application": "http",
            "state": "pending",
            "index": 4294967299,
            "location": "172.21.16.89",
            "node": {
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/bc9af9da-41bb-11e9-a3db-005056bb27cf"
                    }
                },
                "uuid": "bc9af9da-41bb-11e9-a3db-005056bb27cf",
                "name": "node1",
            },
            "user": "admin",
        }
    )
]

```
</div>
</div>

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


__all__ = ["SecurityAuditLog", "SecurityAuditLogSchema"]
__pdoc__ = {
    "SecurityAuditLogSchema.resource": False,
    "SecurityAuditLog.security_audit_log_show": False,
    "SecurityAuditLog.security_audit_log_create": False,
    "SecurityAuditLog.security_audit_log_modify": False,
    "SecurityAuditLog.security_audit_log_delete": False,
}


class SecurityAuditLogSchema(ResourceSchema):
    """The fields of the SecurityAuditLog object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the security_audit_log. """

    application = fields.Str(
        data_key="application",
        validate=enum_validation(['internal', 'console', 'rsh', 'telnet', 'ssh', 'ontapi', 'http', 'system']),
    )
    r""" This identifies the "application" by which the request was processed.


Valid choices:

* internal
* console
* rsh
* telnet
* ssh
* ontapi
* http
* system """

    command_id = fields.Str(
        data_key="command_id",
    )
    r""" This is the command ID for this request.
Each command received on a CLI session is assigned a command ID. This enables you to correlate a request and response. """

    index = Size(
        data_key="index",
    )
    r""" Internal index for accessing records with same time/node. This is a 64 bit unsigned value. """

    input = fields.Str(
        data_key="input",
    )
    r""" The request. """

    location = fields.Str(
        data_key="location",
    )
    r""" This identifies the location of the remote user. This is an IP address or "console". """

    message = fields.Str(
        data_key="message",
    )
    r""" This is an optional field that might contain "error" or "additional information" about the status of a command. """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the security_audit_log. """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['svm', 'cluster']),
    )
    r""" Set to "svm" when the request is on a data SVM; otherwise set to "cluster".

Valid choices:

* svm
* cluster """

    session_id = fields.Str(
        data_key="session_id",
    )
    r""" This is the session ID on which the request is received. Each SSH session is assigned a session ID.
Each http/ontapi/snmp request is assigned a unique session ID. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['pending', 'success', 'error']),
    )
    r""" State of of this request.

Valid choices:

* pending
* success
* error """

    svm = fields.Nested("netapp_ontap.models.security_audit_log_svm.SecurityAuditLogSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the security_audit_log. """

    timestamp = ImpreciseDateTime(
        data_key="timestamp",
    )
    r""" Log entry timestamp. Valid in URL """

    user = fields.Str(
        data_key="user",
    )
    r""" Username of the remote user. """

    @property
    def resource(self):
        return SecurityAuditLog

    gettable_fields = [
        "links",
        "application",
        "command_id",
        "index",
        "input",
        "location",
        "message",
        "node.links",
        "node.name",
        "node.uuid",
        "scope",
        "session_id",
        "state",
        "svm",
        "timestamp",
        "user",
    ]
    """links,application,command_id,index,input,location,message,node.links,node.name,node.uuid,scope,session_id,state,svm,timestamp,user,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
        "scope",
        "svm",
    ]
    """node.name,node.uuid,scope,svm,"""

    postable_fields = [
        "node.name",
        "node.uuid",
        "scope",
        "svm",
    ]
    """node.name,node.uuid,scope,svm,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecurityAuditLog.get_collection(fields=field)]
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
            raise NetAppRestError("SecurityAuditLog modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecurityAuditLog(Resource):
    """Allows interaction with SecurityAuditLog objects on the host"""

    _schema = SecurityAuditLogSchema
    _path = "/api/security/audit/messages"

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the administrative audit log viewer.
### Learn more
* [`DOC /security/audit/messages`](#docs-security-security_audit_messages)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security audit log show")
        def security_audit_log_show(
            fields: List[Choices.define(["application", "command_id", "index", "input", "location", "message", "scope", "session_id", "state", "timestamp", "user", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SecurityAuditLog resources

            Args:
                application: This identifies the \"application\" by which the request was processed. 
                command_id: This is the command ID for this request. Each command received on a CLI session is assigned a command ID. This enables you to correlate a request and response. 
                index: Internal index for accessing records with same time/node. This is a 64 bit unsigned value.
                input: The request.
                location: This identifies the location of the remote user. This is an IP address or \"console\".
                message: This is an optional field that might contain \"error\" or \"additional information\" about the status of a command.
                scope: Set to \"svm\" when the request is on a data SVM; otherwise set to \"cluster\".
                session_id: This is the session ID on which the request is received. Each SSH session is assigned a session ID. Each http/ontapi/snmp request is assigned a unique session ID. 
                state: State of of this request.
                timestamp: Log entry timestamp. Valid in URL
                user: Username of the remote user.
            """

            kwargs = {}
            if application is not None:
                kwargs["application"] = application
            if command_id is not None:
                kwargs["command_id"] = command_id
            if index is not None:
                kwargs["index"] = index
            if input is not None:
                kwargs["input"] = input
            if location is not None:
                kwargs["location"] = location
            if message is not None:
                kwargs["message"] = message
            if scope is not None:
                kwargs["scope"] = scope
            if session_id is not None:
                kwargs["session_id"] = session_id
            if state is not None:
                kwargs["state"] = state
            if timestamp is not None:
                kwargs["timestamp"] = timestamp
            if user is not None:
                kwargs["user"] = user
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SecurityAuditLog.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SecurityAuditLog resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the administrative audit log viewer.
### Learn more
* [`DOC /security/audit/messages`](#docs-security-security_audit_messages)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)






