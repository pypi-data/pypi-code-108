r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

# Overview
Retrieves a list of recent MetroCluster operations. To view more information about a specific operation, use the ```/cluster/metrocluster/operations/{uuid}``` API endpoint.
####
---
## Examples
### Retrieves all MetroCluster operations
```
GET https://<mgmt-ip>/api/cluster/metrocluster/operations?fields=*
{
    "records": [
        {
            "uuid": "a14ae39f-8d85-11e9-b4a7-00505682dc8b",
            "type": "check",
            "state": "successful",
            "start_time": "2019-06-14T11:15:00-07:00",
            "end_time": "2019-06-14T11:16:08-07:00",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/operations/a14ae39f-8d85-11e9-b4a7-00505682dc8b"
                }
            }
        },
        {
            "uuid": "7058df27-8d85-11e9-bbc9-005056826931",
            "type": "configure",
            "state": "successful",
            "start_time": "2019-06-12T19:46:27-07:00",
            "end_time": "2019-06-12T19:48:17-07:00",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/operations/7058df27-8d85-11e9-bbc9-005056826931"
                }
            }
        },
        {
            "uuid": "7849515d-8d84-11e9-bbc9-005056826931",
            "type": "connect",
            "state": "successful",
            "start_time": "2019-06-12T19:39:30-07:00",
            "end_time": "2019-06-12T19:42:02-07:00",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/operations/7849515d-8d84-11e9-bbc9-005056826931"
                }
            }
        },
        {
            "uuid": "331c79ad-8d84-11e9-b4a7-00505682dc8b",
            "type": "interface_create",
            "state": "successful",
            "start_time": "2019-06-12T19:37:35-07:00",
            "end_time": "2019-06-12T19:37:41-07:00",
            "_links": {
                "self": {
                    "href": "/api/cluster/metrocluster/operations/331c79ad-8d84-11e9-b4a7-00505682dc8b"
                }
            }
        }
    ],
    "num_records": 4,
    "_links": {
        "self": {
            "href": "/api/cluster/metrocluster/operations?fields=%2A"
        }
    }
}
```
### Retrieves Information about a specific MetroCluster operation
```
GET https://<mgmt-ip>/api/cluster/metrocluster/operations/0db12274-86fd-11e9-8053-00505682c342
{
    "uuid": "0db12274-86fd-11e9-8053-00505682c342",
    "name": "check",
    "state": "successful",
    "start_time": "2019-06-06T16:15:01-07:00",
    "end_time": "2019-06-06T16:16:05-07:00",
    "_links": {
        "self": {
            "href": "/api/cluster/metrocluster/operations/0db12274-86fd-11e9-8053-00505682c342"
        }
    }
}
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


__all__ = ["MetroclusterOperation", "MetroclusterOperationSchema"]
__pdoc__ = {
    "MetroclusterOperationSchema.resource": False,
    "MetroclusterOperation.metrocluster_operation_show": False,
    "MetroclusterOperation.metrocluster_operation_create": False,
    "MetroclusterOperation.metrocluster_operation_modify": False,
    "MetroclusterOperation.metrocluster_operation_delete": False,
}


class MetroclusterOperationSchema(ResourceSchema):
    """The fields of the MetroclusterOperation object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the metrocluster_operation. """

    additional_info = fields.Str(
        data_key="additional_info",
    )
    r""" Additional information for the auto heal.

Example: MetroCluster switchover with auto heal completed successfully. """

    command_line = fields.Str(
        data_key="command_line",
    )
    r""" Command line executed with the options specified.

Example: metrocluster switchover """

    end_time = ImpreciseDateTime(
        data_key="end_time",
    )
    r""" End Time

Example: 2016-03-10T22:35:16.000+0000 """

    errors = fields.List(fields.Str, data_key="errors")
    r""" List of errors in the operation.

Example: ["siteB (warning): Unable to prepare the partner cluster for a pending switchback operation. Reason: entry doesn't exist. Reboot the nodes in the partner cluster before using the \"metrocluster switchback\" command."] """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the metrocluster_operation. """

    start_time = ImpreciseDateTime(
        data_key="start_time",
    )
    r""" Start Time

Example: 2016-03-10T22:33:16.000+0000 """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['completed_with_manual_recovery_needed', 'completed_with_warnings', 'failed', 'in_progress', 'partially_successful', 'successful', 'unknown']),
    )
    r""" Indicates the state of the operation.

Valid choices:

* completed_with_manual_recovery_needed
* completed_with_warnings
* failed
* in_progress
* partially_successful
* successful
* unknown """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['check', 'configure', 'connect', 'disconnect', 'dr_group_create', 'dr_group_delete', 'heal_aggr_auto', 'heal_aggregates', 'heal_root_aggr_auto', 'heal_root_aggregates', 'interface_create', 'interface_delete', 'interface_modify', 'ip_setup', 'ip_teardown', 'modify', 'switchback', 'switchback_continuation_agent', 'switchback_simulate', 'switchover', 'switchover_simulate', 'unconfigure', 'unconfigure_continuation_agent', 'unknown']),
    )
    r""" Name of the operation.

Valid choices:

* check
* configure
* connect
* disconnect
* dr_group_create
* dr_group_delete
* heal_aggr_auto
* heal_aggregates
* heal_root_aggr_auto
* heal_root_aggregates
* interface_create
* interface_delete
* interface_modify
* ip_setup
* ip_teardown
* modify
* switchback
* switchback_continuation_agent
* switchback_simulate
* switchover
* switchover_simulate
* unconfigure
* unconfigure_continuation_agent
* unknown """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Identifier for the operation.

Example: 11111111-2222-3333-4444-abcdefabcdef """

    @property
    def resource(self):
        return MetroclusterOperation

    gettable_fields = [
        "links",
        "additional_info",
        "command_line",
        "end_time",
        "errors",
        "node.links",
        "node.name",
        "node.uuid",
        "start_time",
        "state",
        "type",
        "uuid",
    ]
    """links,additional_info,command_line,end_time,errors,node.links,node.name,node.uuid,start_time,state,type,uuid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
    ]
    """node.name,node.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in MetroclusterOperation.get_collection(fields=field)]
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
            raise NetAppRestError("MetroclusterOperation modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class MetroclusterOperation(Resource):
    r""" Data for a MetroCluster operation. REST: /api/cluster/metrocluster/operations """

    _schema = MetroclusterOperationSchema
    _path = "/api/cluster/metrocluster/operations"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the list of MetroCluster operations on the local cluster.
### Related ONTAP Commands
* `metrocluster operation history show`
### Learn more
* [`DOC /cluster/metrocluster/operations`](#docs-cluster-cluster_metrocluster_operations)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="metrocluster operation show")
        def metrocluster_operation_show(
            fields: List[Choices.define(["additional_info", "command_line", "end_time", "errors", "start_time", "state", "type", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of MetroclusterOperation resources

            Args:
                additional_info: Additional information for the auto heal.
                command_line: Command line executed with the options specified.
                end_time: End Time
                errors: List of errors in the operation.
                start_time: Start Time
                state: Indicates the state of the operation.
                type: Name of the operation.
                uuid: Identifier for the operation.
            """

            kwargs = {}
            if additional_info is not None:
                kwargs["additional_info"] = additional_info
            if command_line is not None:
                kwargs["command_line"] = command_line
            if end_time is not None:
                kwargs["end_time"] = end_time
            if errors is not None:
                kwargs["errors"] = errors
            if start_time is not None:
                kwargs["start_time"] = start_time
            if state is not None:
                kwargs["state"] = state
            if type is not None:
                kwargs["type"] = type
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return MetroclusterOperation.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all MetroclusterOperation resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the list of MetroCluster operations on the local cluster.
### Related ONTAP Commands
* `metrocluster operation history show`
### Learn more
* [`DOC /cluster/metrocluster/operations`](#docs-cluster-cluster_metrocluster_operations)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves information about a specific MetroCluster operation.
### Related ONTAP Commands
* `metrocluster operation show`

### Learn more
* [`DOC /cluster/metrocluster/operations`](#docs-cluster-cluster_metrocluster_operations)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





