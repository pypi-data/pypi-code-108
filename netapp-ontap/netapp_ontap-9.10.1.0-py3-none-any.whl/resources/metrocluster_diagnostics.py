r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to initiate a MetroCluster diagnostics operation and fetch the results of a completed diagnostics operation on a MetroCluster over IP configuration. The GET operation retrieves the results of a completed diagnostics operation for the MetroCluster over IP configuration. The POST request can be used to start a MetroCluster diagnostics operation or set up a schedule for the diagnostics to be run periodically.
## Starting a MetroCluster diagnostics operation
A new MetroCluster diagnostics operation can be started by issuing a POST to /cluster/metrocluster/diagnostics. There are no extra parameters required to initiate a diagnostics operation.
### Polling the POST job for status of diagnostics operation
After a successful POST /cluster/diagnostics operation is issued, an HTTP status code of 202 (Accepted) is returned along with a job UUID and a link in the body of the response. The POST job continues asynchronously and can be monitored by using the job UUID and the /cluster/jobs API. The "message" field in the response of the GET /cluster/jobs/{uuid} request shows the current step in the job, and the "state" field shows the overall state of the job.
<br/>
---
## Examples
### Running the diagnostics operation
This example shows the POST request for starting a diagnostic operation for a MetroCluster over IP configuration and the responses returned:
```
#API
/api/cluster/metrocluster/diagnostics
```
### POST Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.post(hydrate=True)
    print(resource)

```

### POST Response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:20:53 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Location: /api/cluster/metrocluster/diagnostics
Content-Length: 189
Content-Type: application/hal+json
{
  "job": {
    "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
      }
    }
  }
}
```
### Monitoring the job progress
Use the link provided in the response to the POST request to fetch information for the diagnostics operation job.
<br/>
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="f7d3804c-fcf7-11ea-acaf-005056bb47c1")
    resource.get()
    print(resource)

```

<br/>
#### Job status response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:21:12 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 345
Content-Type: application/hal+json
{
  "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
  "description": "POST /api/cluster/metrocluster/diagnostics",
  "state": "running",
  "message": "Checking nodes...",
  "code": 2432853,
  "start_time": "2020-09-22T13:20:53-04:00",
  "_links": {
    "self": {
      "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
    }
  }
}
```
#### Final status of the diagnostics job
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 17:29:04 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 372
Content-Type: application/hal+json
{
  "uuid": "f7d3804c-fcf7-11ea-acaf-005056bb47c1",
  "description": "POST /api/cluster/metrocluster/diagnostics",
  "state": "success",
  "message": "success",
  "code": 0,
  "start_time": "2020-09-22T13:20:53-04:00",
  "end_time": "2020-09-22T13:22:04-04:00",
  "_links": {
    "self": {
      "href": "/api/cluster/jobs/f7d3804c-fcf7-11ea-acaf-005056bb47c1"
    }
  }
}
```
### Retrieving the diagnostics operation
#### Request
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import MetroclusterDiagnostics

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = MetroclusterDiagnostics()
    resource.get()
    print(resource)

```

#### Response
```
HTTP/1.1 202 Accepted
Date: Tue, 22 Sep 2020 18:04:28 GMT
Server: libzapid-httpd
X-Content-Type-Options: nosniff
Cache-Control: no-cache,no-store,must-revalidate
Content-Length: 1005
Content-Type: application/hal+json
{
  "node": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "interface": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "aggregate": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "cluster": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "connection": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "volume": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "config_replication": {
    "timestamp": "2020-09-22T13:47:01-04:00",
    "state": "ok",
    "summary": {
      "message": ""
    }
  },
  "_links": {
    "self": {
      "href": "/api/cluster/metrocluster/diagnostics"
    }
  }
}
```
### Related ONTAP Commands

* `metrocluster check run`
* `metrocluster check show`
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


__all__ = ["MetroclusterDiagnostics", "MetroclusterDiagnosticsSchema"]
__pdoc__ = {
    "MetroclusterDiagnosticsSchema.resource": False,
    "MetroclusterDiagnostics.metrocluster_diagnostics_show": False,
    "MetroclusterDiagnostics.metrocluster_diagnostics_create": False,
    "MetroclusterDiagnostics.metrocluster_diagnostics_modify": False,
    "MetroclusterDiagnostics.metrocluster_diagnostics_delete": False,
}


class MetroclusterDiagnosticsSchema(ResourceSchema):
    """The fields of the MetroclusterDiagnostics object"""

    aggregate = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="aggregate", unknown=EXCLUDE)
    r""" The aggregate field of the metrocluster_diagnostics. """

    cluster = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="cluster", unknown=EXCLUDE)
    r""" The cluster field of the metrocluster_diagnostics. """

    config_replication = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_configreplication.MetroclusterDiagnosticsConfigreplicationSchema", data_key="config-replication", unknown=EXCLUDE)
    r""" The config_replication field of the metrocluster_diagnostics. """

    connection = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="connection", unknown=EXCLUDE)
    r""" The connection field of the metrocluster_diagnostics. """

    interface = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="interface", unknown=EXCLUDE)
    r""" The interface field of the metrocluster_diagnostics. """

    node = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="node", unknown=EXCLUDE)
    r""" The node field of the metrocluster_diagnostics. """

    volume = fields.Nested("netapp_ontap.models.metrocluster_diagnostics_aggregate.MetroclusterDiagnosticsAggregateSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the metrocluster_diagnostics. """

    @property
    def resource(self):
        return MetroclusterDiagnostics

    gettable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

    patchable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

    postable_fields = [
        "aggregate",
        "cluster",
        "config_replication",
        "connection",
        "interface",
        "node",
        "volume",
    ]
    """aggregate,cluster,config_replication,connection,interface,node,volume,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in MetroclusterDiagnostics.get_collection(fields=field)]
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
            raise NetAppRestError("MetroclusterDiagnostics modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class MetroclusterDiagnostics(Resource):
    """Allows interaction with MetroclusterDiagnostics objects on the host"""

    _schema = MetroclusterDiagnosticsSchema
    _path = "/api/cluster/metrocluster/diagnostics"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the results of a completed diagnostic operation for the MetroCluster configuration.

### Learn more
* [`DOC /cluster/metrocluster/diagnostics`](#docs-cluster-cluster_metrocluster_diagnostics)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="metrocluster diagnostics show")
        def metrocluster_diagnostics_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single MetroclusterDiagnostics resource

            Args:
            """

            kwargs = {}
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = MetroclusterDiagnostics(
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Start a MetroCluster diagnostic operation or set up a schedule for the diagnostics to be run periodically.

### Learn more
* [`DOC /cluster/metrocluster/diagnostics`](#docs-cluster-cluster_metrocluster_diagnostics)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="metrocluster diagnostics create")
        async def metrocluster_diagnostics_create(
        ) -> ResourceTable:
            """Create an instance of a MetroclusterDiagnostics resource

            Args:
                aggregate: 
                cluster: 
                config_replication: 
                connection: 
                interface: 
                node: 
                volume: 
            """

            kwargs = {}
            if aggregate is not None:
                kwargs["aggregate"] = aggregate
            if cluster is not None:
                kwargs["cluster"] = cluster
            if config_replication is not None:
                kwargs["config_replication"] = config_replication
            if connection is not None:
                kwargs["connection"] = connection
            if interface is not None:
                kwargs["interface"] = interface
            if node is not None:
                kwargs["node"] = node
            if volume is not None:
                kwargs["volume"] = volume

            resource = MetroclusterDiagnostics(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create MetroclusterDiagnostics: %s" % err)
            return [resource]




