r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
FlexCache is a persistent cache of an origin volume. An origin volume can only be a FlexVol while a FlexCache is always a FlexGroup.</br>
The following relationship configurations are supported:</br>

* Intra-Vserver where FlexCache and the corresponding origin volume reside in the same Vserver.
* Cross-Vserver but intra-cluster where FlexCache and the origin volume reside in the same cluster but belong to different Vservers.
* Cross-cluster where FlexCache and the origin volume reside in different clusters.</br>
FlexCache supports fan-out and more than one FlexCache can be created from one origin volume.
This API retrieves and manages FlexCache configurations in the cache cluster.
## FlexCache APIs
The following APIs can be used to perform operations related with FlexCache:

* GET       /api/storage/flexcache/flexcaches
* GET       /api/storage/flexcache/flexcaches/{uuid}
* POST      /api/storage/flexcache/flexcaches
* DELETE    /api/storage/flexcache/flexcaches/{uuid}
## Examples
### Creating a FlexCache
The POST request is used to create a FlexCache.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Flexcache()
    resource.aggregates = [{"name": "aggr_1"}]
    resource.name = "fc_333"
    resource.origins = [{"svm": {"name": "vs_3"}, "volume": {"name": "vol_o1"}}]
    resource.svm = {"name": "vs_1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Flexcache(
    {
        "origins": [{"svm": {"name": "vs_3"}, "volume": {"name": "vol_o1"}}],
        "svm": {"name": "vs_1"},
        "aggregates": [{"name": "aggr_1"}],
        "name": "fc_333",
    }
)

```
</div>
</div>

curl -X POST "https://<mgmt-ip>/api/storage/flexcache/flexcaches" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"aggregates\": [ { \"name\": \"aggr_1\" } ], \"name\": \"fc_333\", \"origins\": [ {  \"svm\": { \"name\": \"vs_3\"  }, \"volume\": { \"name\": \"vol_o1\" } } ], \"svm\": { \"name\": \"vs_1\" },  \"path\": \"/fc_333\", \"prepopulate\": { \"dir_paths\": [ \"/dir1\" ] } }"
# The response:
{
  "job": {
    "uuid": "e751dd5d-0f3c-11e9-8b2b-0050568e0b79",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/e751dd5d-0f3c-11e9-8b2b-0050568e0b79"
      }
    }
  }
}
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Flexcache()
    resource.aggregates = [{"name": "aggr_1"}]
    resource.name = "fc_333"
    resource.origins = [{"svm": {"name": "vs_3"}, "volume": {"name": "vol_o1"}}]
    resource.svm = {"name": "vs_1"}
    resource.path = "/       fc_333"
    resource.prepopulate = {
        "dir_paths": ["/dir1"],
        "exclude_dir_paths": ["/dir1/dir11"],
    }
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Flexcache(
    {
        "origins": [{"svm": {"name": "vs_3"}, "volume": {"name": "vol_o1"}}],
        "svm": {"name": "vs_1"},
        "path": "/       fc_333",
        "prepopulate": {"dir_paths": ["/dir1"], "exclude_dir_paths": ["/dir1/dir11"]},
        "aggregates": [{"name": "aggr_1"}],
        "name": "fc_333",
    }
)

```
</div>
</div>
`
curl -X POST "https://<mgmt-ip>/api/storage/flexcache/flexcaches" -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"aggregates\": [ { \"name\": \"aggr_1\" } ], \"name\": \"fc_333\", \"origins\": [ {  \"svm\": { \"name\": \"vs_3\"  }, \"volume\": { \"name\": \"vol_o1\" } } ], \"svm\":{ \"name\": \"vs_1\" }, \"dr_cache\": true,  \"path\": \"/fc_333\", \"prepopulate\": { \"dir_paths\": [ \"/dir1\" ] } }"
# The response:
{
  "job": {
    "uuid": "e751dd5d-0f3c-11e9-8b2b-0050568e0b79",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/e751dd5d-0f3c-11e9-8b2b-0050568e0b79"
      }
    }
  }
}
```
### Retrieving FlexCache attributes
The GET request is used to retrieve FlexCache attributes. The object includes a large set of fields which can be expensive to retrieve. Most notably, the fields size, guarantee.type, aggregates, path, origins.ip_address, origins.size, and origins.state are expensive to retrieve. The recommended method to use this API is to filter and retrieve only the required fields.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Flexcache.get_collection()))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    Flexcache(
        {
            "uuid": "04d5e07b-0ebe-11e9-8180-0050568e0b79",
            "name": "fc_322",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/flexcaches/04d5e07b-0ebe-11e9-8180-0050568e0b79"
                }
            },
        }
    ),
    Flexcache(
        {
            "uuid": "47902654-0ea4-11e9-8180-0050568e0b79",
            "name": "fc_321",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/flexcaches/47902654-0ea4-11e9-8180-0050568e0b79"
                }
            },
        }
    ),
    Flexcache(
        {
            "uuid": "77e911ff-0ebe-11e9-8180-0050568e0b79",
            "name": "fc_323",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/flexcaches/77e911ff-0ebe-11e9-8180-0050568e0b79"
                }
            },
        }
    ),
    Flexcache(
        {
            "uuid": "ddb42bbc-0e95-11e9-8180-0050568e0b79",
            "name": "fc_32",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/flexcaches/ddb42bbc-0e95-11e9-8180-0050568e0b79"
                }
            },
        }
    ),
    Flexcache(
        {
            "uuid": "ec774932-0f3c-11e9-8b2b-0050568e0b79",
            "name": "fc_333",
            "_links": {
                "self": {
                    "href": "/api/storage/flexcache/flexcaches/ec774932-0f3c-11e9-8b2b-0050568e0b79"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving the attributes of a FlexCache
The GET request is used to retrieve the attributes of a FlexCache. The object includes a large set of fields which can be expensive to retrieve. Most notably, the fields size, guarantee.type, aggregates, path, origins.ip_address, origins.size, and origins.state are expensive to retrieve. The recommended method to use this API is to filter and retrieve only the required fields.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Flexcache(uuid="ec774932-0f3c-11e9-8b2b-0050568e0b79")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Flexcache(
    {
        "origins": [
            {
                "cluster": {
                    "uuid": "50733f81-0e90-11e9-b391-0050568e4115",
                    "name": "node2",
                },
                "svm": {"uuid": "8aa2cd28-0e92-11e9-b391-0050568e4115", "name": "vs_3"},
                "volume": {
                    "uuid": "2bc957dd-2617-4afb-8d2f-66ac6070d313",
                    "name": "vol_o1",
                },
                "create_time": "2019-01-03T15:19:55+05:30",
                "ip_address": "10.140.103.175",
                "state": "online",
                "size": 20971520,
            }
        ],
        "svm": {"uuid": "e708fbe2-0e92-11e9-8180-0050568e0b79", "name": "vs_1"},
        "uuid": "ec774932-0f3c-11e9-8b2b-0050568e0b79",
        "guarantee": {"type": "volume"},
        "dr_cache": True,
        "size": 4294967296,
        "aggregates": [
            {"name": "aggr_1", "uuid": "26f34b76-88f8-4a47-b5e0-d8e901fb1114"}
        ],
        "name": "fc_333",
        "_links": {
            "self": {
                "href": "/api/storage/flexcache/flexcaches/ec774932-0f3c-11e9-8b2b-0050568e0b79"
            }
        },
    }
)

```
</div>
</div>

### Deleting a FlexCache
The DELETE request is used to delete a FlexCache.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Flexcache(uuid="ec774932-0f3c-11e9-8b2b-0050568e0b79")
    resource.delete()

```

### Modifying a FlexCache volume
Use the PATCH request to update a FlexCache volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Flexcache

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Flexcache(uuid="ec774932-0f3c-11e9-8b2b-0050568e0b79")
    resource.prepopulate = {"dir_paths": ["/dir1"]}
    resource.patch()

```

# The call
curl -X PATCH "https://<mgmt-ip>/api/storage/flexcache/flexcaches/ec774932-0f3c-11e9-8b2b-0050568e0b79"  -H  "accept: application/json" -H  "Content-Type: application/json" -d "{ \"prepopulate\": { \"dir_paths\": [ \"/dir1\" ], \"exclude_dir_paths\": [ \"/dir1/dir11\" ] } }"
# The response:
{
  "job": {
    "uuid": "b574c48c-1da7-11eb-b006-005056ac6a93",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/b574c48c-1da7-11eb-b006-005056ac6a93"
      }
    }
  }
}
````
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


__all__ = ["Flexcache", "FlexcacheSchema"]
__pdoc__ = {
    "FlexcacheSchema.resource": False,
    "Flexcache.flexcache_show": False,
    "Flexcache.flexcache_create": False,
    "Flexcache.flexcache_modify": False,
    "Flexcache.flexcache_delete": False,
}


class FlexcacheSchema(ResourceSchema):
    """The fields of the Flexcache object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the flexcache. """

    aggregates = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="aggregates")
    r""" The aggregates field of the flexcache. """

    constituents_per_aggregate = Size(
        data_key="constituents_per_aggregate",
    )
    r""" Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned. """

    dr_cache = fields.Boolean(
        data_key="dr_cache",
    )
    r""" If set to true, a DR cache is created. """

    global_file_locking_enabled = fields.Boolean(
        data_key="global_file_locking_enabled",
    )
    r""" Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the "is_disconnected_mode_off_for_locks" flag is always set to "true". """

    guarantee = fields.Nested("netapp_ontap.models.flexcache_guarantee.FlexcacheGuaranteeSchema", data_key="guarantee", unknown=EXCLUDE)
    r""" The guarantee field of the flexcache. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=203),
    )
    r""" FlexCache name

Example: vol1 """

    origins = fields.List(fields.Nested("netapp_ontap.models.flexcache_relationship.FlexcacheRelationshipSchema", unknown=EXCLUDE), data_key="origins")
    r""" The origins field of the flexcache. """

    path = fields.Str(
        data_key="path",
    )
    r""" The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.

Example: /user/my_fc """

    prepopulate = fields.Nested("netapp_ontap.models.flexcache_prepopulate.FlexcachePrepopulateSchema", data_key="prepopulate", unknown=EXCLUDE)
    r""" The prepopulate field of the flexcache. """

    size = Size(
        data_key="size",
    )
    r""" Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the flexcache. """

    use_tiered_aggregate = fields.Boolean(
        data_key="use_tiered_aggregate",
    )
    r""" Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" FlexCache UUID. Unique identifier for the FlexCache.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return Flexcache

    gettable_fields = [
        "links",
        "aggregates.links",
        "aggregates.name",
        "aggregates.uuid",
        "constituents_per_aggregate",
        "dr_cache",
        "global_file_locking_enabled",
        "guarantee",
        "name",
        "origins",
        "path",
        "size",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "use_tiered_aggregate",
        "uuid",
    ]
    """links,aggregates.links,aggregates.name,aggregates.uuid,constituents_per_aggregate,dr_cache,global_file_locking_enabled,guarantee,name,origins,path,size,svm.links,svm.name,svm.uuid,use_tiered_aggregate,uuid,"""

    patchable_fields = [
        "prepopulate",
    ]
    """prepopulate,"""

    postable_fields = [
        "aggregates.name",
        "aggregates.uuid",
        "constituents_per_aggregate",
        "dr_cache",
        "global_file_locking_enabled",
        "guarantee",
        "name",
        "origins",
        "path",
        "prepopulate",
        "size",
        "svm.name",
        "svm.uuid",
        "use_tiered_aggregate",
    ]
    """aggregates.name,aggregates.uuid,constituents_per_aggregate,dr_cache,global_file_locking_enabled,guarantee,name,origins,path,prepopulate,size,svm.name,svm.uuid,use_tiered_aggregate,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Flexcache.get_collection(fields=field)]
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
            raise NetAppRestError("Flexcache modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Flexcache(Resource):
    r""" Defines the cache endpoint of FlexCache. """

    _schema = FlexcacheSchema
    _path = "/api/storage/flexcache/flexcaches"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `origins.ip_address` - IP address of origin.
* `origins.size` - Physical size of origin.
* `origins.state` - State of origin.
* `size` - Physical size of FlexCache.
* `guarantee.type` - Space guarantee style of FlexCache.
* `aggregates.name` or `aggregates.uuid` - Name or UUID of aggregrate of FlexCache volume.
* `path` - Fully-qualified path of the owning SVM's namespace where the FlexCache is mounted.
### Related ONTAP commands
* `volume flexcache show`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache show")
        def flexcache_show(
            fields: List[Choices.define(["constituents_per_aggregate", "dr_cache", "global_file_locking_enabled", "name", "path", "size", "use_tiered_aggregate", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Flexcache resources

            Args:
                constituents_per_aggregate: Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned.
                dr_cache: If set to true, a DR cache is created.
                global_file_locking_enabled: Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the \"is_disconnected_mode_off_for_locks\" flag is always set to \"true\".
                name: FlexCache name
                path: The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.
                size: Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB.
                use_tiered_aggregate: Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume.
                uuid: FlexCache UUID. Unique identifier for the FlexCache.
            """

            kwargs = {}
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if dr_cache is not None:
                kwargs["dr_cache"] = dr_cache
            if global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = global_file_locking_enabled
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path
            if size is not None:
                kwargs["size"] = size
            if use_tiered_aggregate is not None:
                kwargs["use_tiered_aggregate"] = use_tiered_aggregate
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Flexcache.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Flexcache resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Flexcache"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Prepopulates a FlexCache volume in the cluster.
### Required properties
* `uuid` - FlexCache volume UUID.
* `prepopulate.dir_paths` - List of directory-paths to be prepopulated for the FlexCache volume.
### Recommended optional properties
* `prepopulate.exclude_dir_paths` - List of directory-paths to be excluded from prepopulation for the FlexCache volume.
### Default property values
If not specified in PATCH, the following default property value is assigned:
* `prepopulate.recurse` - Default value is "true".
### Related ONTAP commands
* `volume flexcache prepopulate start`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Flexcache"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Flexcache"], NetAppResponse]:
        r"""Creates a FlexCache in the cluster.
### Required properties
* `name` - Name of FlexCache volume.
* `origins.volume.name` or `origins.volume.uuid` - Name or UUID of origin volume.
* `origins.svm.name` - Name of origin Vserver.
* `svm.name` or `svm.uuid` - Name or UUID of Vserver where FlexCache will be created.
### Recommended optional properties
* `path` - Path to mount the FlexCache volume
* `prepopulate.dir_paths` - List of directory-paths to be prepopulated for the FlexCache volume.
* `prepopulate.exclude_dir_paths` - List of directory-paths to be excluded from prepopulation for he FlexCache volume.
### Default property values
If not specified in POST, the following default property values are assigned:
* `size` - 10% of origin volume size or 1GB per constituent, whichever is greater.
* `guarantee.type` - none. FlexCache is thin provisioned by default.
* `constituents_per_aggregate` - 4 if aggregates.name or aggregates.uuid is used.
* `use_tiered_aggregate` - false if aggr-list is not used. This property is only used when auto-provisioning a FlexCache volume.
* `is_disconnected_mode_off_for_locks` - false. This property specifies if the origin will honor the cache side locks when doing the lock checks in the disconnected mode.
* `dr_cache` - false if FlexCache is not a DR cache. This property is used to create a DR FlexCache.
* `global_file_locking_enabled` - false. This property specifies whether global file locking is enabled on the FlexCache volume.
### Related ONTAP commands
* `volume flexcache create`
* `volume flexcache prepopulate start`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Flexcache"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a FlexCache. If a FlexCache volume is online, it is offlined before deletion.
### Related ONTAP commands
* `volume flexcache delete`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `origins.ip_address` - IP address of origin.
* `origins.size` - Physical size of origin.
* `origins.state` - State of origin.
* `size` - Physical size of FlexCache.
* `guarantee.type` - Space guarantee style of FlexCache.
* `aggregates.name` or `aggregates.uuid` - Name or UUID of aggregrate of FlexCache volume.
* `path` - Fully-qualified path of the owning SVM's namespace where the FlexCache is mounted.
### Related ONTAP commands
* `volume flexcache show`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves attributes of the FlexCache in the cluster.
### Expensive properties
There is an added cost to retrieving values for these properties. They are included by default in GET. The recommended method to use this API is to filter and retrieve only the required fields. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `origins.ip_address` - IP address of origin.
* `origins.size` - Physical size of origin.
* `origins.state` - State of origin.
* `size` - Physical size of FlexCache.
* `guarantee.type` - Space guarantee style of FlexCache.
* `aggregates.name` or `aggregates.uuid` - Name or UUID of aggregrate of FlexCache volume.
* `path` - Fully-qualified path of the owning SVM's namespace where the FlexCache is mounted.
### Related ONTAP commands
* `volume flexcache show`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a FlexCache in the cluster.
### Required properties
* `name` - Name of FlexCache volume.
* `origins.volume.name` or `origins.volume.uuid` - Name or UUID of origin volume.
* `origins.svm.name` - Name of origin Vserver.
* `svm.name` or `svm.uuid` - Name or UUID of Vserver where FlexCache will be created.
### Recommended optional properties
* `path` - Path to mount the FlexCache volume
* `prepopulate.dir_paths` - List of directory-paths to be prepopulated for the FlexCache volume.
* `prepopulate.exclude_dir_paths` - List of directory-paths to be excluded from prepopulation for he FlexCache volume.
### Default property values
If not specified in POST, the following default property values are assigned:
* `size` - 10% of origin volume size or 1GB per constituent, whichever is greater.
* `guarantee.type` - none. FlexCache is thin provisioned by default.
* `constituents_per_aggregate` - 4 if aggregates.name or aggregates.uuid is used.
* `use_tiered_aggregate` - false if aggr-list is not used. This property is only used when auto-provisioning a FlexCache volume.
* `is_disconnected_mode_off_for_locks` - false. This property specifies if the origin will honor the cache side locks when doing the lock checks in the disconnected mode.
* `dr_cache` - false if FlexCache is not a DR cache. This property is used to create a DR FlexCache.
* `global_file_locking_enabled` - false. This property specifies whether global file locking is enabled on the FlexCache volume.
### Related ONTAP commands
* `volume flexcache create`
* `volume flexcache prepopulate start`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache create")
        async def flexcache_create(
        ) -> ResourceTable:
            """Create an instance of a Flexcache resource

            Args:
                links: 
                aggregates: 
                constituents_per_aggregate: Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned.
                dr_cache: If set to true, a DR cache is created.
                global_file_locking_enabled: Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the \"is_disconnected_mode_off_for_locks\" flag is always set to \"true\".
                guarantee: 
                name: FlexCache name
                origins: 
                path: The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.
                prepopulate: 
                size: Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB.
                svm: 
                use_tiered_aggregate: Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume.
                uuid: FlexCache UUID. Unique identifier for the FlexCache.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if aggregates is not None:
                kwargs["aggregates"] = aggregates
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if dr_cache is not None:
                kwargs["dr_cache"] = dr_cache
            if global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = global_file_locking_enabled
            if guarantee is not None:
                kwargs["guarantee"] = guarantee
            if name is not None:
                kwargs["name"] = name
            if origins is not None:
                kwargs["origins"] = origins
            if path is not None:
                kwargs["path"] = path
            if prepopulate is not None:
                kwargs["prepopulate"] = prepopulate
            if size is not None:
                kwargs["size"] = size
            if svm is not None:
                kwargs["svm"] = svm
            if use_tiered_aggregate is not None:
                kwargs["use_tiered_aggregate"] = use_tiered_aggregate
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = Flexcache(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Flexcache: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Prepopulates a FlexCache volume in the cluster.
### Required properties
* `uuid` - FlexCache volume UUID.
* `prepopulate.dir_paths` - List of directory-paths to be prepopulated for the FlexCache volume.
### Recommended optional properties
* `prepopulate.exclude_dir_paths` - List of directory-paths to be excluded from prepopulation for the FlexCache volume.
### Default property values
If not specified in PATCH, the following default property value is assigned:
* `prepopulate.recurse` - Default value is "true".
### Related ONTAP commands
* `volume flexcache prepopulate start`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache modify")
        async def flexcache_modify(
        ) -> ResourceTable:
            """Modify an instance of a Flexcache resource

            Args:
                constituents_per_aggregate: Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned.
                query_constituents_per_aggregate: Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned.
                dr_cache: If set to true, a DR cache is created.
                query_dr_cache: If set to true, a DR cache is created.
                global_file_locking_enabled: Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the \"is_disconnected_mode_off_for_locks\" flag is always set to \"true\".
                query_global_file_locking_enabled: Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the \"is_disconnected_mode_off_for_locks\" flag is always set to \"true\".
                name: FlexCache name
                query_name: FlexCache name
                path: The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.
                query_path: The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.
                size: Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB.
                query_size: Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB.
                use_tiered_aggregate: Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume.
                query_use_tiered_aggregate: Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume.
                uuid: FlexCache UUID. Unique identifier for the FlexCache.
                query_uuid: FlexCache UUID. Unique identifier for the FlexCache.
            """

            kwargs = {}
            changes = {}
            if query_constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = query_constituents_per_aggregate
            if query_dr_cache is not None:
                kwargs["dr_cache"] = query_dr_cache
            if query_global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = query_global_file_locking_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_path is not None:
                kwargs["path"] = query_path
            if query_size is not None:
                kwargs["size"] = query_size
            if query_use_tiered_aggregate is not None:
                kwargs["use_tiered_aggregate"] = query_use_tiered_aggregate
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if constituents_per_aggregate is not None:
                changes["constituents_per_aggregate"] = constituents_per_aggregate
            if dr_cache is not None:
                changes["dr_cache"] = dr_cache
            if global_file_locking_enabled is not None:
                changes["global_file_locking_enabled"] = global_file_locking_enabled
            if name is not None:
                changes["name"] = name
            if path is not None:
                changes["path"] = path
            if size is not None:
                changes["size"] = size
            if use_tiered_aggregate is not None:
                changes["use_tiered_aggregate"] = use_tiered_aggregate
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Flexcache, "find"):
                resource = Flexcache.find(
                    **kwargs
                )
            else:
                resource = Flexcache()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Flexcache: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a FlexCache. If a FlexCache volume is online, it is offlined before deletion.
### Related ONTAP commands
* `volume flexcache delete`
### Learn more
* [`DOC /storage/flexcache/flexcaches`](#docs-storage-storage_flexcache_flexcaches)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="flexcache delete")
        async def flexcache_delete(
        ) -> None:
            """Delete an instance of a Flexcache resource

            Args:
                constituents_per_aggregate: Number of FlexCache constituents per aggregate when the 'aggregates' field is mentioned.
                dr_cache: If set to true, a DR cache is created.
                global_file_locking_enabled: Specifies whether or not a FlexCache volume has global file locking mode enabled. Global file locking mode is a mode where protocol read locking semantics are enforced across all FlexCaches and origins of a FlexCache volume. When global file locking mode is enabled, the \"is_disconnected_mode_off_for_locks\" flag is always set to \"true\".
                name: FlexCache name
                path: The fully-qualified path in the owning SVM's namespace at which the FlexCache is mounted. The path is case insensitive and must be unique within a SVM's namespace. Path must begin with '/' and must not end with '/'. Only one FlexCache be mounted at any given junction path.
                size: Physical size of the FlexCache. The recommended size for a FlexCache is 10% of the origin volume. The minimum FlexCache constituent size is 1GB.
                use_tiered_aggregate: Specifies whether or not a Fabricpool-enabled aggregate can be used in FlexCache creation. The use_tiered_aggregate is only used when auto-provisioning a FlexCache volume.
                uuid: FlexCache UUID. Unique identifier for the FlexCache.
            """

            kwargs = {}
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if dr_cache is not None:
                kwargs["dr_cache"] = dr_cache
            if global_file_locking_enabled is not None:
                kwargs["global_file_locking_enabled"] = global_file_locking_enabled
            if name is not None:
                kwargs["name"] = name
            if path is not None:
                kwargs["path"] = path
            if size is not None:
                kwargs["size"] = size
            if use_tiered_aggregate is not None:
                kwargs["use_tiered_aggregate"] = use_tiered_aggregate
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(Flexcache, "find"):
                resource = Flexcache.find(
                    **kwargs
                )
            else:
                resource = Flexcache()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Flexcache: %s" % err)


