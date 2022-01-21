r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
FlexCache is a persistent cache of an origin volume. An origin volume can only be a FlexVol while a FlexCache is always a FlexGroup.</br>
The following relationship configurations are supported:

* Intra-Vserver where FlexCache and the corresponding origin volume reside in the same Vserver.
* Cross-Vserver but intra-cluster where FlexCache and the origin volume reside in the same cluster but belong to different Vservers.
* Cross-cluster where FlexCache and the origin volume reside in different clusters.</br>
FlexCache supports fan-out and more than one FlexCache can be created from one origin volume.
This API retrieves the origin of FlexCache onfigurations in the origin cluster.
## FlexCache APIs
The following APIs can be used to perform operations related to the origin of a FlexCache:

* GET       /api/storage/flexcache/origins
* GET       /api/storage/flexcache/origins/{uuid}
* PATCH     /api/storage/flexcache/origins/{uuid}
## Examples
### Retrieving origins of FlexCache attributes
The GET request is used to retrieve the origins of FlexCache attributes.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FlexcacheOrigin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(FlexcacheOrigin.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    FlexcacheOrigin(
        {
            "uuid": "2bc957dd-2617-4afb-8d2f-66ac6070d313",
            "name": "vol_o1",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/origins/2bc957dd-2617-4afb-8d2f-66ac6070d313"
                }
            },
        }
    ),
    FlexcacheOrigin(
        {
            "uuid": "80fcaee4-0dc2-488b-afb8-86d28a34cda8",
            "name": "vol_1",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/origins/80fcaee4-0dc2-488b-afb8-86d28a34cda8"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving the attributes of an origin volume
The GET request is used to retrieve the attributes of an origin volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FlexcacheOrigin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FlexcacheOrigin(uuid="80fcaee4-0dc2-488b-afb8-86d28a34cda8")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
FlexcacheOrigin(
    {
        "block_level_invalidation": False,
        "svm": {"uuid": "8aa2cd28-0e92-11e9-b391-0050568e4115", "name": "vs_3"},
        "uuid": "80fcaee4-0dc2-488b-afb8-86d28a34cda8",
        "flexcaches": [
            {
                "cluster": {
                    "uuid": "c32f16b8-0e90-11e9-aed0-0050568eddbe",
                    "name": "node4",
                },
                "svm": {
                    "uuid": "36f68322-0e93-11e9-aed0-0050568eddbe",
                    "name": "vs_1_4",
                },
                "volume": {
                    "uuid": "4e7f9d49-0e96-11e9-aed0-0050568eddbe",
                    "name": "fc_42",
                },
                "create_time": "2019-01-02T19:27:22+05:30",
                "ip_address": "10.140.103.183",
            },
            {
                "cluster": {
                    "uuid": "c32f16b8-0e90-11e9-aed0-0050568eddbe",
                    "name": "node4",
                },
                "svm": {
                    "uuid": "36f68322-0e93-11e9-aed0-0050568eddbe",
                    "name": "vs_1_4",
                },
                "volume": {
                    "uuid": "71ee8f36-0ea4-11e9-aed0-0050568eddbe",
                    "name": "fc_421",
                },
                "create_time": "2019-01-02T21:08:34+05:30",
                "ip_address": "10.140.103.183",
            },
            {
                "cluster": {
                    "uuid": "c32f16b8-0e90-11e9-aed0-0050568eddbe",
                    "name": "node4",
                },
                "svm": {
                    "uuid": "36f68322-0e93-11e9-aed0-0050568eddbe",
                    "name": "vs_1_4",
                },
                "volume": {"name": "fc_422"},
                "create_time": "2019-01-03T11:14:38+05:30",
                "ip_address": "10.140.103.183",
            },
            {
                "cluster": {
                    "uuid": "8eb21b3b-0e90-11e9-8180-0050568e0b79",
                    "name": "node3",
                },
                "svm": {"uuid": "e708fbe2-0e92-11e9-8180-0050568e0b79", "name": "vs_1"},
                "volume": {
                    "uuid": "ddb42bbc-0e95-11e9-8180-0050568e0b79",
                    "name": "fc_32",
                },
                "create_time": "2019-01-02T19:24:14+05:30",
                "ip_address": "10.140.103.179",
                "state": "online",
                "size": 4294967296,
            },
            {
                "cluster": {
                    "uuid": "8eb21b3b-0e90-11e9-8180-0050568e0b79",
                    "name": "node3",
                },
                "svm": {"uuid": "e708fbe2-0e92-11e9-8180-0050568e0b79", "name": "vs_1"},
                "volume": {
                    "uuid": "47902654-0ea4-11e9-8180-0050568e0b79",
                    "name": "fc_321",
                },
                "create_time": "2019-01-02T21:07:23+05:30",
                "ip_address": "10.140.103.179",
                "state": "online",
                "size": 4294967296,
            },
            {
                "cluster": {
                    "uuid": "8eb21b3b-0e90-11e9-8180-0050568e0b79",
                    "name": "node3",
                },
                "svm": {"uuid": "e708fbe2-0e92-11e9-8180-0050568e0b79", "name": "vs_1"},
                "volume": {
                    "uuid": "04d5e07b-0ebe-11e9-8180-0050568e0b79",
                    "name": "fc_322",
                },
                "create_time": "2019-01-03T00:11:38+05:30",
                "ip_address": "10.140.103.179",
                "state": "online",
                "size": 4294967296,
            },
            {
                "cluster": {
                    "uuid": "8eb21b3b-0e90-11e9-8180-0050568e0b79",
                    "name": "node3",
                },
                "svm": {"uuid": "e708fbe2-0e92-11e9-8180-0050568e0b79", "name": "vs_1"},
                "volume": {
                    "uuid": "77e911ff-0ebe-11e9-8180-0050568e0b79",
                    "name": "fc_323",
                },
                "create_time": "2019-01-03T00:14:52+05:30",
                "ip_address": "10.140.103.179",
                "state": "online",
                "size": 4294967296,
            },
        ],
        "global_file_locking_enabled": True,
        "name": "vol_1",
        "_links": {
            "self": {
                "href": "/api/storage/flexcache/origins/80fcaee4-0dc2-488b-afb8-86d28a34cda8"
            }
        },
    }
)

```
</div>
</div>

### Modifying origin options of an origin volume
Use the PATCH request to update options of an origin volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import FlexcacheOrigin

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = FlexcacheOrigin(uuid="1fbc0ebb-2440-11eb-a86c-005056ac8ca0")
    resource.block_level_invalidation = True
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


__all__ = ["FlexcacheOrigin", "FlexcacheOriginSchema"]
__pdoc__ = {
    "FlexcacheOriginSchema.resource": False,
    "FlexcacheOrigin.flexcache_origin_show": False,
    "FlexcacheOrigin.flexcache_origin_create": False,
    "FlexcacheOrigin.flexcache_origin_modify": False,
    "FlexcacheOrigin.flexcache_origin_delete": False,
}


class FlexcacheOriginSchema(ResourceSchema):
    """The fields of the FlexcacheOrigin object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the flexcache_origin. """

    block_level_invalidation = fields.Boolean(
        data_key="block_level_invalidation",
    )
    r""" Block level invalidation enables the FlexCache volume to retain blocks that are not changed at the FlexCache volume without having to evict them. This means that the FlexCache volume does not have to again incur the cost of fetching blocks over the WAN from the FlexCache volume origin on the next client access. Block level invalidation is a property of the origin volume. Without block level invalidation, any write at the origin volume would evict the whole file at the FlexCache volume, since by default, origin volume does a file level invalidation. """

    flexcaches = fields.List(fields.Nested("netapp_ontap.models.flexcache_relationship.FlexcacheRelationshipSchema", unknown=EXCLUDE), data_key="flexcaches")
    r""" The flexcaches field of the flexcache_origin. """

    global_file_locking_enabled = fields.Boolean(
        data_key="global_file_locking_enabled",
    )
    r""" Specifies whether a global file locking option is enabled for an origin volume of a FlexCache volume. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=203),
    )
    r""" Origin volume name

Example: vol1, vol_2 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the flexcache_origin. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Origin volume UUID. Unique identifier for origin of FlexCache.

Example: 1cd8a442-86d1-11e0-ae1c-123478563512 """

    @property
    def resource(self):
        return FlexcacheOrigin

    gettable_fields = [
        "links",
        "block_level_invalidation",
        "flexcaches",
        "global_file_locking_enabled",
        "name",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,block_level_invalidation,flexcaches,global_file_locking_enabled,name,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "block_level_invalidation",
        "name",
    ]
    """block_level_invalidation,name,"""

    postable_fields = [
        "flexcaches",
        "name",
        "svm.name",
        "svm.uuid",
    ]
    """flexcaches,name,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in FlexcacheOrigin.get_collection(fields=field)]
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
            raise NetAppRestError("FlexcacheOrigin modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class FlexcacheOrigin(Resource):
    r""" Defines the origin endpoint of FlexCache. """

    _schema = FlexcacheOriginSchema
    _path = "/api/storage/flexcache/origins"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves origin of FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `flexcaches.ip_address` - IP address of FlexCache.
* `flexcaches.size` - Physical size of FlexCache.
* `flexcaches.guarantee.type` - Space guarantee style of FlexCache.
* `flexcaches.state` - State of FlexCache.
### Related ONTAP commands
* `volume flexcache origin show-caches`
### Learn more
* [`DOC /storage/flexcache/origins`](#docs-storage-storage_flexcache_origins)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache origin show")
        def flexcache_origin_show(
            fields: List[Choices.define(["block_level_invalidation", "global_file_locking_enabled", "name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of FlexcacheOrigin resources

            Args:
                block_level_invalidation: Block level invalidation enables the FlexCache volume to retain blocks that are not changed at the FlexCache volume without having to evict them. This means that the FlexCache volume does not have to again incur the cost of fetching blocks over the WAN from the FlexCache volume origin on the next client access. Block level invalidation is a property of the origin volume. Without block level invalidation, any write at the origin volume would evict the whole file at the FlexCache volume, since by default, origin volume does a file level invalidation.
                global_file_locking_enabled: Specifies whether a global file locking option is enabled for an origin volume of a FlexCache volume.
                name: Origin volume name
                uuid: Origin volume UUID. Unique identifier for origin of FlexCache.
            """

            kwargs = {}
            if block_level_invalidation is not None:
                kwargs["block_level_invalidation"] = block_level_invalidation
            if global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = global_file_locking_enabled
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return FlexcacheOrigin.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all FlexcacheOrigin resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["FlexcacheOrigin"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Modifies origin options for a origin volume in the cluster.
### Required properties
* `uuid` - Origin volume UUID.
* `block_level_invalidation` - Value for the Block Level Invalidation flag - options {true|false}.
### Related ONTAP commands
* `volume flexcache origin config modify`
### Learn more
* [`DOC /storage/flexcache/origins`](#docs-storage-storage_flexcache_origins)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves origin of FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `flexcaches.ip_address` - IP address of FlexCache.
* `flexcaches.size` - Physical size of FlexCache.
* `flexcaches.guarantee.type` - Space guarantee style of FlexCache.
* `flexcaches.state` - State of FlexCache.
### Related ONTAP commands
* `volume flexcache origin show-caches`
### Learn more
* [`DOC /storage/flexcache/origins`](#docs-storage-storage_flexcache_origins)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves attributes of the origin of a FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are included by default in GET results. The recommended method to use this API is to filter and retrieve only the required fields. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `flexcaches.ip_address` - IP address of FlexCache.
* `flexcaches.size` - Physical size of FlexCache.
* `flexcaches.guarantee.type` - Space guarantee style of FlexCache.
* `flexcaches.state` - State of FlexCache.
* `flexcaches.dr_cache` - True if the cache is a DR cache.
### Related ONTAP commands
* `volume flexcache origin show-caches`
### Learn more
* [`DOC /storage/flexcache/origins`](#docs-storage-storage_flexcache_origins)
"""
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
        r"""Modifies origin options for a origin volume in the cluster.
### Required properties
* `uuid` - Origin volume UUID.
* `block_level_invalidation` - Value for the Block Level Invalidation flag - options {true|false}.
### Related ONTAP commands
* `volume flexcache origin config modify`
### Learn more
* [`DOC /storage/flexcache/origins`](#docs-storage-storage_flexcache_origins)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache origin modify")
        async def flexcache_origin_modify(
        ) -> ResourceTable:
            """Modify an instance of a FlexcacheOrigin resource

            Args:
                block_level_invalidation: Block level invalidation enables the FlexCache volume to retain blocks that are not changed at the FlexCache volume without having to evict them. This means that the FlexCache volume does not have to again incur the cost of fetching blocks over the WAN from the FlexCache volume origin on the next client access. Block level invalidation is a property of the origin volume. Without block level invalidation, any write at the origin volume would evict the whole file at the FlexCache volume, since by default, origin volume does a file level invalidation.
                query_block_level_invalidation: Block level invalidation enables the FlexCache volume to retain blocks that are not changed at the FlexCache volume without having to evict them. This means that the FlexCache volume does not have to again incur the cost of fetching blocks over the WAN from the FlexCache volume origin on the next client access. Block level invalidation is a property of the origin volume. Without block level invalidation, any write at the origin volume would evict the whole file at the FlexCache volume, since by default, origin volume does a file level invalidation.
                global_file_locking_enabled: Specifies whether a global file locking option is enabled for an origin volume of a FlexCache volume.
                query_global_file_locking_enabled: Specifies whether a global file locking option is enabled for an origin volume of a FlexCache volume.
                name: Origin volume name
                query_name: Origin volume name
                uuid: Origin volume UUID. Unique identifier for origin of FlexCache.
                query_uuid: Origin volume UUID. Unique identifier for origin of FlexCache.
            """

            kwargs = {}
            changes = {}
            if query_block_level_invalidation is not None:
                kwargs["block_level_invalidation"] = query_block_level_invalidation
            if query_global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = query_global_file_locking_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if block_level_invalidation is not None:
                changes["block_level_invalidation"] = block_level_invalidation
            if global_file_locking_enabled is not None:
                changes["global_file_locking_enabled"] = global_file_locking_enabled
            if name is not None:
                changes["name"] = name
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(FlexcacheOrigin, "find"):
                resource = FlexcacheOrigin.find(
                    **kwargs
                )
            else:
                resource = FlexcacheOrigin()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify FlexcacheOrigin: %s" % err)



