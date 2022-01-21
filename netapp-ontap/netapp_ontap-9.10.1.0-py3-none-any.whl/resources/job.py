r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
You can use this API to view and manipulate jobs. Jobs provide information about asynchronous operations. Some long-running jobs are paused or cancelled by calling a PATCH request. Individual operations indicate if they support PATCH requests on the job. After a job transitions to a terminal state, it is deleted after a default time of 300 seconds. Attempts to call a GET or PATCH request on the job returns a 404 error code After the job has been deleted.
## Example
The following examples show how to retrieve and update a job state:
### Retrieving job information
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="b5145e1d-b53b-11e8-8252-005056bbd8f5")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Job(
    {
        "message": "creating_node_backups",
        "code": 0,
        "uuid": "b5145e1d-b53b-11e8-8252-005056bbd8f5",
        "state": "running",
        "description": "Cluster Backup Job",
        "_links": {
            "self": {"href": "/api/cluster/jobs/b5145e1d-b53b-11e8-8252-005056bbd8f5"}
        },
    }
)

```
</div>
</div>

---
### Updating a job that supports the new state
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Job

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Job(uuid="b5145e1d-b53b-11e8-8252-005056bbd8f5")
    resource.patch(hydrate=True, action="cancel")

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


__all__ = ["Job", "JobSchema"]
__pdoc__ = {
    "JobSchema.resource": False,
    "Job.job_show": False,
    "Job.job_create": False,
    "Job.job_modify": False,
    "Job.job_delete": False,
}


class JobSchema(ResourceSchema):
    """The fields of the Job object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the job. """

    code = Size(
        data_key="code",
    )
    r""" If the state indicates "failure", this is the final error code.

Example: 0 """

    description = fields.Str(
        data_key="description",
    )
    r""" The description of the job to help identify it independent of the UUID.

Example: App Snapshot Job """

    end_time = ImpreciseDateTime(
        data_key="end_time",
    )
    r""" The time the job ended. """

    error = fields.Nested("netapp_ontap.models.error.ErrorSchema", data_key="error", unknown=EXCLUDE)
    r""" The error field of the job. """

    message = fields.Str(
        data_key="message",
    )
    r""" A message corresponding to the state of the job providing additional details about the current state.

Example: Complete: Successful """

    start_time = ImpreciseDateTime(
        data_key="start_time",
    )
    r""" The time the job started. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['queued', 'running', 'paused', 'success', 'failure']),
    )
    r""" The state of the job.

Valid choices:

* queued
* running
* paused
* success
* failure """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the job. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The uuid field of the job.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return Job

    gettable_fields = [
        "links",
        "code",
        "description",
        "end_time",
        "error",
        "message",
        "start_time",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,code,description,end_time,error,message,start_time,state,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Job.get_collection(fields=field)]
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
            raise NetAppRestError("Job modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Job(Resource):
    """Allows interaction with Job objects on the host"""

    _schema = JobSchema
    _path = "/api/cluster/jobs"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of recently running asynchronous jobs. After a job transitions to a failure or success state, it is deleted after a default time of 300 seconds.
### Learn more
* [`DOC /cluster/jobs`](#docs-cluster-cluster_jobs)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="job show")
        def job_show(
            fields: List[Choices.define(["code", "description", "end_time", "message", "start_time", "state", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Job resources

            Args:
                code: If the state indicates \"failure\", this is the final error code.
                description: The description of the job to help identify it independent of the UUID.
                end_time: The time the job ended.
                message: A message corresponding to the state of the job providing additional details about the current state.
                start_time: The time the job started.
                state: The state of the job.
                uuid: 
            """

            kwargs = {}
            if code is not None:
                kwargs["code"] = code
            if description is not None:
                kwargs["description"] = description
            if end_time is not None:
                kwargs["end_time"] = end_time
            if message is not None:
                kwargs["message"] = message
            if start_time is not None:
                kwargs["start_time"] = start_time
            if state is not None:
                kwargs["state"] = state
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Job.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Job resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Job"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the state of a specific asynchronous job.
### Learn more
* [`DOC /cluster/jobs`](#docs-cluster-cluster_jobs)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of recently running asynchronous jobs. After a job transitions to a failure or success state, it is deleted after a default time of 300 seconds.
### Learn more
* [`DOC /cluster/jobs`](#docs-cluster-cluster_jobs)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the details of a specific asynchronous job. After a job transitions to a failure or success state, it is deleted after a default time of 300 seconds.
### Learn more
* [`DOC /cluster/jobs`](#docs-cluster-cluster_jobs)"""
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
        r"""Updates the state of a specific asynchronous job.
### Learn more
* [`DOC /cluster/jobs`](#docs-cluster-cluster_jobs)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="job modify")
        async def job_modify(
        ) -> ResourceTable:
            """Modify an instance of a Job resource

            Args:
                code: If the state indicates \"failure\", this is the final error code.
                query_code: If the state indicates \"failure\", this is the final error code.
                description: The description of the job to help identify it independent of the UUID.
                query_description: The description of the job to help identify it independent of the UUID.
                end_time: The time the job ended.
                query_end_time: The time the job ended.
                message: A message corresponding to the state of the job providing additional details about the current state.
                query_message: A message corresponding to the state of the job providing additional details about the current state.
                start_time: The time the job started.
                query_start_time: The time the job started.
                state: The state of the job.
                query_state: The state of the job.
                uuid: 
                query_uuid: 
            """

            kwargs = {}
            changes = {}
            if query_code is not None:
                kwargs["code"] = query_code
            if query_description is not None:
                kwargs["description"] = query_description
            if query_end_time is not None:
                kwargs["end_time"] = query_end_time
            if query_message is not None:
                kwargs["message"] = query_message
            if query_start_time is not None:
                kwargs["start_time"] = query_start_time
            if query_state is not None:
                kwargs["state"] = query_state
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if code is not None:
                changes["code"] = code
            if description is not None:
                changes["description"] = description
            if end_time is not None:
                changes["end_time"] = end_time
            if message is not None:
                changes["message"] = message
            if start_time is not None:
                changes["start_time"] = start_time
            if state is not None:
                changes["state"] = state
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Job, "find"):
                resource = Job.find(
                    **kwargs
                )
            else:
                resource = Job()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Job: %s" % err)



