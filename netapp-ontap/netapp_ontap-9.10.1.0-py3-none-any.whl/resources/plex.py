r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
The Storage Aggregate Plex API provides relevant state information for each plex in the aggregate.
For each plex, details are provided for the RAID groups in the plex and the disks that make up each RAID group.<br>
## Examples
### Retrieving the list of plexes in an aggregate
The following example shows the response with the list of plexes in an aggregate:<br>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Plex

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Plex.get_collection("19425837-f2fa-4a9f-8f01-712f626c983c")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[Plex({"name": "plex0"}), Plex({"name": "plex4"})]

```
</div>
</div>

### Retrieving a specific plex in an aggregate
The following example shows the response when requesting a specific plex of an aggregate:<br>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Plex

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Plex("19425837-f2fa-4a9f-8f01-712f626c983c", name="plex0")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Plex(
    {
        "pool": "pool0",
        "aggregate": {"name": "test1", "uuid": "19425837-f2fa-4a9f-8f01-712f626c983c"},
        "resync": {"active": False},
        "raid_groups": [
            {
                "reconstruct": {"active": False},
                "disks": [
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "dparity",
                        "state": "normal",
                        "disk": {"name": "1.1.29"},
                    },
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "parity",
                        "state": "normal",
                        "disk": {"name": "1.1.4"},
                    },
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "data",
                        "state": "normal",
                        "disk": {"name": "1.1.30"},
                    },
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "data",
                        "state": "normal",
                        "disk": {"name": "1.1.5"},
                    },
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "data",
                        "state": "normal",
                        "disk": {"name": "1.1.31"},
                    },
                    {
                        "usable_size": 86769664,
                        "type": "ssd",
                        "position": "data",
                        "state": "normal",
                        "disk": {"name": "1.1.6"},
                    },
                ],
                "cache_tier": False,
                "degraded": False,
                "recomputing_parity": {"active": False},
                "name": "rg0",
                "raid_type": "raid_dp",
            }
        ],
        "state": "normal",
        "name": "plex0",
        "online": True,
    }
)

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


__all__ = ["Plex", "PlexSchema"]
__pdoc__ = {
    "PlexSchema.resource": False,
    "Plex.plex_show": False,
    "Plex.plex_create": False,
    "Plex.plex_modify": False,
    "Plex.plex_delete": False,
}


class PlexSchema(ResourceSchema):
    """The fields of the Plex object"""

    aggregate = fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", data_key="aggregate", unknown=EXCLUDE)
    r""" The aggregate field of the plex. """

    name = fields.Str(
        data_key="name",
    )
    r""" Plex name

Example: plex0 """

    online = fields.Boolean(
        data_key="online",
    )
    r""" Plex is online """

    pool = fields.Str(
        data_key="pool",
        validate=enum_validation(['pool0', 'pool1']),
    )
    r""" SyncMirror pool assignment

Valid choices:

* pool0
* pool1 """

    raid_groups = fields.List(fields.Nested("netapp_ontap.models.raid_group.RaidGroupSchema", unknown=EXCLUDE), data_key="raid_groups")
    r""" The raid_groups field of the plex. """

    resync = fields.Nested("netapp_ontap.models.plex_resync.PlexResyncSchema", data_key="resync", unknown=EXCLUDE)
    r""" The resync field of the plex. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['normal', 'failed', 'out_of_date']),
    )
    r""" Plex state

Valid choices:

* normal
* failed
* out_of_date """

    @property
    def resource(self):
        return Plex

    gettable_fields = [
        "aggregate.links",
        "aggregate.name",
        "aggregate.uuid",
        "name",
        "online",
        "pool",
        "raid_groups",
        "resync",
        "state",
    ]
    """aggregate.links,aggregate.name,aggregate.uuid,name,online,pool,raid_groups,resync,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Plex.get_collection(fields=field)]
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
            raise NetAppRestError("Plex modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Plex(Resource):
    """Allows interaction with Plex objects on the host"""

    _schema = PlexSchema
    _path = "/api/storage/aggregates/{aggregate[uuid]}/plexes"
    _keys = ["aggregate.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of plexes for the specified aggregate.
### Related ONTAP commands
* `storage aggregate plex show`

### Learn more
* [`DOC /storage/aggregates/{aggregate.uuid}/plexes`](#docs-storage-storage_aggregates_{aggregate.uuid}_plexes)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="plex show")
        def plex_show(
            aggregate_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            online: Choices.define(_get_field_list("online"), cache_choices=True, inexact=True)=None,
            pool: Choices.define(_get_field_list("pool"), cache_choices=True, inexact=True)=None,
            state: Choices.define(_get_field_list("state"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "online", "pool", "state", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Plex resources

            Args:
                name: Plex name
                online: Plex is online
                pool: SyncMirror pool assignment
                state: Plex state
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if online is not None:
                kwargs["online"] = online
            if pool is not None:
                kwargs["pool"] = pool
            if state is not None:
                kwargs["state"] = state
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Plex.get_collection(
                aggregate_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Plex resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of plexes for the specified aggregate.
### Related ONTAP commands
* `storage aggregate plex show`

### Learn more
* [`DOC /storage/aggregates/{aggregate.uuid}/plexes`](#docs-storage-storage_aggregates_{aggregate.uuid}_plexes)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the plex specified by the aggregate UUID and plex name.
### Related ONTAP commands
* `storage aggregate plex show`

### Learn more
* [`DOC /storage/aggregates/{aggregate.uuid}/plexes`](#docs-storage-storage_aggregates_{aggregate.uuid}_plexes)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





