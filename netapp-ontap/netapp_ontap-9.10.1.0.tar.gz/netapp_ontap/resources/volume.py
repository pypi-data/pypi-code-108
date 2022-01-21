r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
FlexVol volumes are logical containers used by ONTAP to serve data to clients.  They contain file systems in a NAS environment and LUNs in a SAN environment.<br/>
A FlexGroup volume is a scale-out NAS container that provides high performance along with automatic load distribution and scalability. A FlexGroup volume contains several constituents that automatically and transparently share the traffic.</br>
FlexClone volumes are writable, point-in-time copies of a FlexVol volume. At this time, FlexClones of FlexGroups are not supported.<br/>
Volumes with SnapLock type Compliance or Enterprise, are referred to as SnapLock volumes. Volumes with SnapLock type cannot be of FlexGroup style. Once a SnapLock aggregate is created, by default, volumes created inside the aggregate inherit the "snaplock" property from the aggregate. It is possible to create a SnapLock volume by specifying SnapLock parameters. SnapLock parameters are only available at the "advanced" privilege level.<br/>
ONTAP storage APIs allow you to create, modify, and monitor volumes and aggregates.<br/>
## Storage efficiency
Storage efficiency is used to remove duplicate blocks in the data and to compress the data. Efficiency has deduplication, compression, cross volume deduplication, and compaction options. On All Flash systems, all efficiencies are enabled by default on volume creation. Options such as "background/inline/both" are treated as both, which means both background and inline are enabled for any efficiency option. The option "none"  disables both background and inline efficiency.<br/>
To enable any efficiency option on all-flash or FAS systems, background deduplication is always enabled.<br/>
## Quotas
Quotas provide a way to restrict or track the files and space usage by a user, group, or qtree. Quotas are enabled for a specific FlexVol or a FlexGroup volume.<br/>
The following APIs can be used to enable or disable and obtain quota state for a FlexVol or a FlexGroup volume:

* PATCH  /api/storage/volumes/{uuid} -d '{"quota.enabled":"true"}'
* PATCH  /api/storage/volumes/{uuid} -d '{"quota.enabled":"false"}'
* GET    /api/storage/volumes/{uuid}/?fields=quota.state
## File System Analytics
File system analytics provide a quick method for obtaining information summarizing properties of all files within any directory tree of a volume. For more information on file system analytics, see [`DOC /storage/volumes{volume.uuid}/files/{path}`](#docs-storage-storage_volumes_{volume.uuid}_files_{path}). Analytics can be enabled or disabled on individual volumes.<br/>
The following APIs can be used to enable or disable and obtain analytics state for a FlexVol volume or a FlexGroup volume:

* PATCH  /api/storage/volumes/{uuid} -d '{"analytics.state":"on"}'
* PATCH  /api/storage/volumes/{uuid} -d '{"analytics.state":"off"}'
* GET    /api/storage/volumes/{uuid}/?fields=analytics
## QoS
QoS policy and settings enforce Service Level Objectives (SLO) on a volume. SLO can be set by specifying qos.max_throughput_iops and/or qos.max_throughput_mbps or qos.min_throughput_iops and/or qos.min_throughput_mbps. Specifying min_throughput_iops or min_throughput_mbps is only supported on volumes hosted on a node that is flash optimized. A pre-created QoS policy can also be used by specifying qos.name or qos.uuid property. <br/>
## Performance monitoring
Performance of a volume can be monitored by the `metric.*` and `statistics.*` fields. These show the performance of the volume in terms of IOPS, latency and throughput. The `metric.*` fields denote an average whereas `statistics.*` fields denote a real-time monotonically increasing value aggregated across all nodes. <br/>
## Volume APIs
The following APIs are used to perform operations related with FlexVol volumes and FlexGroup volumes:

* POST      /api/storage/volumes
* GET       /api/storage/volumes
* GET       /api/storage/volumes/{uuid}
* PATCH     /api/storage/volumes/{uuid}
* DELETE    /api/storage/volumes/{uuid}
## Examples
### Creating a volume
The POST request is used to create a new volume and to specify its properties.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume()
    resource.name = "vol1"
    resource.aggregates = [{"name": "aggr1"}]
    resource.svm = {"name": "vs1"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
Volume({"aggregates": [{"name": "aggr1"}], "svm": {"name": "vs1"}, "name": "vol1"})

```
</div>
</div>

### Creating a SnapLock volume and specifying its properties using POST
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume()
    resource.name = "vol1"
    resource.aggregates = [{"name": "aggr1"}]
    resource.svm = {"name": "vs1"}
    resource.snaplock = {"retention": {"default": "P20Y"}, "type": "compliance"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Volume(
    {
        "aggregates": [{"name": "aggr1"}],
        "svm": {"name": "vs1"},
        "snaplock": {"type": "compliance", "retention": {"default": "P20Y"}},
        "name": "vol1",
    }
)

```
</div>
</div>

### Creating a FlexGroup volume and specifying its properties using POST
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume()
    resource.name = "vol1"
    resource.state = "online"
    resource.type = "RW"
    resource.aggregates = [{"name": "aggr1"}, {"name": "aggr2"}, {"name": "aggr3"}]
    resource.constituents_per_aggregate = "1"
    resource.svm = {"name": "vs1"}
    resource.size = "240MB"
    resource.encryption = {"enabled": "False"}
    resource.efficiency = {"compression": "both"}
    resource.autosize = {"maximum": "500MB", "minimum": "240MB"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
Volume(
    {
        "autosize": {"minimum": 251658240, "maximum": 524288000},
        "state": "online",
        "size": 251658240,
        "encryption": {"enabled": False},
        "type": "RW",
        "efficiency": {"compression": "both"},
        "aggregates": [{"name": "aggr1"}, {"name": "aggr2"}, {"name": "aggr3"}],
        "svm": {"name": "vs1"},
        "constituents_per_aggregate": 1,
        "name": "vol1",
    }
)

```
</div>
</div>

### Creating a FlexClone and specifying its properties using POST
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume()
    resource.name = "vol1_clone"
    resource.clone = {"parent_volume": {"name": "vol1"}, "is_flexclone": "true"}
    resource.svm = {"name": "vs0"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
Volume(
    {
        "clone": {"parent_volume": {"name": "vol1"}, "is_flexclone": True},
        "svm": {"name": "vs0"},
        "name": "vol1_clone",
    }
)

```
</div>
</div>

## Volumes reported in the GET REST API
### The following types of volumes are reported:

*  RW, DP and LS volumes
*  FlexGroup volume
*  FlexCache volume
*  FlexClone volume
*  FlexGroup constituent
<br/>
### The following volumes are not reported:

*  DEL and TMP type volume
*  Node Root volume
*  System Vserver volume
*  FlexCache constituent
## Examples
### Retrieving the list of volumes
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(Volume.get_collection()))

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
[
    Volume(
        {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/2d1167cc-c3f2-495a-a23f-8f50b071b9b8"
                }
            },
            "uuid": "2d1167cc-c3f2-495a-a23f-8f50b071b9b8",
            "name": "vsdata_root",
        }
    ),
    Volume(
        {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/3969be7e-78b4-4b4c-82a4-fa86331f03df"
                }
            },
            "uuid": "3969be7e-78b4-4b4c-82a4-fa86331f03df",
            "name": "vsfg_root",
        }
    ),
    Volume(
        {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/59c03ac5-e708-4ce8-a676-278dc249fda2"
                }
            },
            "uuid": "59c03ac5-e708-4ce8-a676-278dc249fda2",
            "name": "svm_root",
        }
    ),
    Volume(
        {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/6802635b-8036-11e8-aae5-0050569503ac"
                }
            },
            "uuid": "6802635b-8036-11e8-aae5-0050569503ac",
            "name": "fgvol",
        }
    ),
    Volume(
        {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/d0c3359c-5448-4a9b-a077-e3295a7e9057"
                }
            },
            "uuid": "d0c3359c-5448-4a9b-a077-e3295a7e9057",
            "name": "datavol",
        }
    ),
]

```
</div>
</div>

### Retrieving the attributes of a volume
The GET request is used to retrieve the attributes of a volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
Volume(
    {
        "files": {"maximum": 566, "used": 96},
        "language": "en_us",
        "_links": {
            "self": {
                "href": "/api/storage/volumes/d0c3359c-5448-4a9b-a077-e3295a7e9057"
            }
        },
        "snapshot_policy": {"name": "default"},
        "statistics": {
            "cloud": {
                "latency_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
                "iops_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
                "status": "ok",
                "timestamp": "2019-04-09T05:50:42+00:00",
            },
            "iops_raw": {"total": 3, "write": 0, "read": 0, "other": 3},
            "status": "ok",
            "timestamp": "2019-04-09T05:50:42+00:00",
            "flexcache_raw": {
                "cache_miss_blocks": 0,
                "status": "ok",
                "client_requested_blocks": 0,
                "timestamp": "2019-04-09T05:50:15+00:00",
            },
            "latency_raw": {"total": 38298, "write": 0, "read": 0, "other": 38298},
            "throughput_raw": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "state": "online",
        "metric": {
            "cloud": {
                "status": "ok",
                "timestamp": "2019-04-09T05:50:15+00:00",
                "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
                "duration": "PT15S",
                "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
            },
            "flexcache": {
                "status": "ok",
                "bandwidth_savings": 0,
                "timestamp": "2019-04-09T05:50:15+00:00",
                "cache_miss_percent": 0,
                "duration": "PT1D",
            },
            "status": "ok",
            "timestamp": "2019-04-09T05:50:15+00:00",
            "latency": {"total": 0, "write": 0, "read": 0, "other": 0},
            "throughput": {"total": 0, "write": 0, "read": 0, "other": 0},
            "duration": "PT15S",
            "iops": {"total": 0, "write": 0, "read": 0, "other": 0},
        },
        "qos": {
            "policy": {"uuid": "228454af-5a8b-11e9-bd5b-005056ac6f1f", "name": "pg1"}
        },
        "size": 20971520,
        "encryption": {"type": "none", "enabled": False, "state": "none", "key_id": ""},
        "error_state": {"is_inconsistent": False, "has_bad_blocks": False},
        "uuid": "d0c3359c-5448-4a9b-a077-e3295a7e9057",
        "anti_ransomware_state": "disabled",
        "create_time": "2018-07-05T14:56:44+05:30",
        "style": "flexvol",
        "comment": "This is a data volume",
        "type": "rw",
        "aggregates": [
            {
                "name": "data",
                "uuid": "aa742322-36bc-4d98-bbc4-0a827534c035",
                "_links": {"self": {"href": "/api/cluster/aggregates/data"}},
            }
        ],
        "svm": {"uuid": "d61b69f5-7458-11e8-ad3f-0050569503ac", "name": "vsdata"},
        "snaplock": {
            "type": "enterprise",
            "expiry_time": "2038-01-19T08:44:28+05:30",
            "append_mode_enabled": False,
            "autocommit_period": "none",
            "is_audit_log": False,
            "retention": {"default": "P0Y", "maximum": "P30Y", "minimum": "P0Y"},
            "privileged_delete": "disabled",
            "litigation_count": 0,
            "compliance_clock_time": "2019-05-24T10:59:00+05:30",
        },
        "nas": {
            "unix_permissions": 4755,
            "gid": 2468,
            "junction_parent": {
                "name": "vol1",
                "uuid": "a2564f80-25fb-41e8-9b49-44de2600991f",
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/a2564f80-25fb-41e8-9b49-44de2600991f"
                    }
                },
            },
            "export_policy": {"id": 8589934593, "name": "default"},
            "security_style": "unix",
            "uid": 1357,
        },
        "name": "datavol",
    }
)

```
</div>
</div>

### Retrieving the quota state of a FlexVol or a FlexGroup volume
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="cb20da45-4f6b-11e9-9a71-005056a7f717")
    resource.get(fields="quota.state")
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
Volume(
    {
        "_links": {
            "self": {
                "href": "/api/storage/volumes/cb20da45-4f6b-11e9-9a71-005056a7f717/"
            }
        },
        "quota": {"state": "on"},
        "uuid": "cb20da45-4f6b-11e9-9a71-005056a7f717",
        "name": "fv",
    }
)

```
</div>
</div>

### Retrieving the constituents of a FlexGroup volume
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.get(fields="constituents")
    print(resource)

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
Volume(
    {
        "_links": {
            "self": {
                "href": "/api/storage/volumes/d0c3359c-5448-4a9b-a077-e3295a7e9057"
            }
        },
        "uuid": "d0c3359c-5448-4a9b-a077-e3295a7e9057",
        "constituents": [
            {
                "space": {
                    "over_provisioned": 0,
                    "logical_space": {
                        "enforcement": False,
                        "used_by_afs": 30273536,
                        "reporting": False,
                    },
                    "metadata": 4087808,
                    "local_tier_footprint": 540958720,
                    "total_footprint": 540958720,
                    "available": 479756288,
                    "snapshot": {"reserve_percent": 5, "autodelete_enabled": False},
                    "used": 30273536,
                    "size": 536870912,
                    "footprint": 389120,
                },
                "aggregates": {
                    "name": "vs_aggr",
                    "uuid": "2e00716c-eb54-45a9-8ca5-be50ccd40708",
                },
                "name": "fg__0001",
            },
            {
                "space": {
                    "over_provisioned": 0,
                    "logical_space": {
                        "enforcement": False,
                        "used_by_afs": 30273536,
                        "reporting": False,
                    },
                    "metadata": 4087808,
                    "local_tier_footprint": 540958720,
                    "total_footprint": 540958720,
                    "available": 479756288,
                    "snapshot": {"reserve_percent": 5, "autodelete_enabled": False},
                    "used": 30273536,
                    "size": 536870912,
                    "footprint": 389120,
                },
                "aggregates": {
                    "name": "aggr1",
                    "uuid": "f655cf4f-8208-4fc8-bfc8-4f238d434402",
                },
                "name": "fg__0002",
            },
            {
                "space": {
                    "over_provisioned": 0,
                    "logical_space": {
                        "enforcement": False,
                        "used_by_afs": 30273536,
                        "reporting": False,
                    },
                    "metadata": 4087808,
                    "local_tier_footprint": 540958720,
                    "total_footprint": 540958720,
                    "available": 479756288,
                    "snapshot": {"reserve_percent": 5, "autodelete_enabled": False},
                    "used": 30273536,
                    "size": 536870912,
                    "footprint": 389120,
                },
                "aggregates": {
                    "name": "aggr2",
                    "uuid": "c7239f14-b861-46fc-b406-70fe13c1a4fb",
                },
                "name": "fg__0003",
            },
            {
                "space": {
                    "over_provisioned": 0,
                    "logical_space": {
                        "enforcement": False,
                        "used_by_afs": 30273536,
                        "reporting": False,
                    },
                    "metadata": 4087808,
                    "local_tier_footprint": 540958720,
                    "total_footprint": 540958720,
                    "available": 479756288,
                    "snapshot": {"reserve_percent": 5, "autodelete_enabled": False},
                    "used": 30273536,
                    "size": 536870912,
                    "footprint": 389120,
                },
                "aggregates": {
                    "name": "aggr3",
                    "uuid": "4c86137a-06af-482d-a41c-d64acc5dcea4",
                },
                "name": "fg__0004",
            },
        ],
        "name": "fg",
    }
)

```
</div>
</div>

## Updating the attributes of a volume
## Examples
### Updating the attributes of a volume
The PATCH request is used to update the attributes of a volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.size = 26214400
    resource.nas = {"security_style": "mixed"}
    resource.comment = "This is a data volume"
    resource.patch()

```

### Updating the attributes of a FlexClone using PATCH
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.clone = {"split_initiated": "true"}
    resource.patch()

```

### Enabling quotas for a FlexVol or a FlexGroup volume using PATCH
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.quota = {"enabled": "true"}
    resource.patch()

```

### Disabling quotas for a FlexVol or a FlexGroup volume using PATCH
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.quota = {"enabled": "false"}
    resource.patch()

```

## Add tiering object tags for a FlexVol using PATCH
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.tiering.object_tags = ["key1=val1", "key2=val2"]
    resource.patch()

```

### Remove tiering object tags for a FlexVol using PATCH
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="d0c3359c-5448-4a9b-a077-e3295a7e9057")
    resource.tiering.object_tags = []
    resource.patch()

```

## Deleting a volume
## Example
### Deleting a volume
The DELETE request is used to delete a volume.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Volume

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Volume(uuid="{uuid}")
    resource.delete()

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


__all__ = ["Volume", "VolumeSchema"]
__pdoc__ = {
    "VolumeSchema.resource": False,
    "Volume.volume_show": False,
    "Volume.volume_create": False,
    "Volume.volume_modify": False,
    "Volume.volume_delete": False,
}


class VolumeSchema(ResourceSchema):
    """The fields of the Volume object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the volume. """

    access_time_enabled = fields.Boolean(
        data_key="access_time_enabled",
    )
    r""" Indicates whether or not access time updates are enabled on the volume. """

    activity_tracking = fields.Nested("netapp_ontap.models.volume_activity_tracking.VolumeActivityTrackingSchema", data_key="activity_tracking", unknown=EXCLUDE)
    r""" The activity_tracking field of the volume. """

    aggregates = fields.List(fields.Nested("netapp_ontap.resources.aggregate.AggregateSchema", unknown=EXCLUDE), data_key="aggregates")
    r""" Aggregate hosting the volume. Required on POST. """

    analytics = fields.Nested("netapp_ontap.models.volume_analytics.VolumeAnalyticsSchema", data_key="analytics", unknown=EXCLUDE)
    r""" The analytics field of the volume. """

    anti_ransomware = fields.Nested("netapp_ontap.models.anti_ransomware_volume.AntiRansomwareVolumeSchema", data_key="anti_ransomware", unknown=EXCLUDE)
    r""" The anti_ransomware field of the volume. """

    anti_ransomware_state = fields.Str(
        data_key="anti_ransomware_state",
        validate=enum_validation(['disabled', 'enabled', 'dry_run', 'paused', 'disable_in_progress', 'enable_paused', 'dry_run_paused']),
    )
    r""" The Anti-ransomware state of the volume. If no "anti_ransomware_state" property is specified, the volume inherits the value from its parent SVM's "anti_ransomware_default_volume_state" property. If this value is "disabled", Anti-ransomware is disabled on the volume. If this value is "enabled", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is "dry_run", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The "dry_run" state is same as the "enabled" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is "paused", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is "disable_in_progress", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is "enable_paused", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is "dry_run_paused", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only "disabled", "enabled" and "dry_run", whereas for PATCH, "paused" is also valid along with the three valid states for POST.

Valid choices:

* disabled
* enabled
* dry_run
* paused
* disable_in_progress
* enable_paused
* dry_run_paused """

    application = fields.Nested("netapp_ontap.models.volume_application.VolumeApplicationSchema", data_key="application", unknown=EXCLUDE)
    r""" The application field of the volume. """

    autosize = fields.Nested("netapp_ontap.models.volume_autosize.VolumeAutosizeSchema", data_key="autosize", unknown=EXCLUDE)
    r""" The autosize field of the volume. """

    clone = fields.Nested("netapp_ontap.models.volume_clone.VolumeCloneSchema", data_key="clone", unknown=EXCLUDE)
    r""" The clone field of the volume. """

    cloud_retrieval_policy = fields.Str(
        data_key="cloud_retrieval_policy",
        validate=enum_validation(['default', 'on_read', 'never', 'promote']),
    )
    r""" This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are
"default" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved.
"on_read" policy retrieves tiered data for all client driven data reads.
"never" policy never retrieves tiered data.
"promote" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved.


Valid choices:

* default
* on_read
* never
* promote """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=1023),
    )
    r""" A comment for the volume. Valid in POST or PATCH. """

    consistency_group = fields.Nested("netapp_ontap.models.volume_consistency_group.VolumeConsistencyGroupSchema", data_key="consistency_group", unknown=EXCLUDE)
    r""" The consistency_group field of the volume. """

    constituents = fields.List(fields.Nested("netapp_ontap.models.volume_constituents.VolumeConstituentsSchema", unknown=EXCLUDE), data_key="constituents")
    r""" The constituents field of the volume. """

    constituents_per_aggregate = Size(
        data_key="constituents_per_aggregate",
        validate=integer_validation(minimum=1, maximum=1000),
    )
    r""" Specifies the number of times to iterate over the aggregates listed with the "aggregates.name" or "aggregates.uuid" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the "constituents_per_aggregate" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list. """

    convert_unicode = fields.Boolean(
        data_key="convert_unicode",
    )
    r""" Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients. """

    create_time = ImpreciseDateTime(
        data_key="create_time",
    )
    r""" Creation time of the volume. This field is generated when the volume is created.

Example: 2018-06-04T19:00:00.000+0000 """

    efficiency = fields.Nested("netapp_ontap.models.volume_efficiency.VolumeEfficiencySchema", data_key="efficiency", unknown=EXCLUDE)
    r""" The efficiency field of the volume. """

    encryption = fields.Nested("netapp_ontap.models.volume_encryption.VolumeEncryptionSchema", data_key="encryption", unknown=EXCLUDE)
    r""" The encryption field of the volume. """

    error_state = fields.Nested("netapp_ontap.models.volume_error_state.VolumeErrorStateSchema", data_key="error_state", unknown=EXCLUDE)
    r""" The error_state field of the volume. """

    files = fields.Nested("netapp_ontap.models.volume_files.VolumeFilesSchema", data_key="files", unknown=EXCLUDE)
    r""" The files field of the volume. """

    flash_pool = fields.Nested("netapp_ontap.models.volume_flash_pool.VolumeFlashPoolSchema", data_key="flash_pool", unknown=EXCLUDE)
    r""" The flash_pool field of the volume. """

    flexcache_endpoint_type = fields.Str(
        data_key="flexcache_endpoint_type",
        validate=enum_validation(['none', 'cache', 'origin']),
    )
    r""" FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.

Valid choices:

* none
* cache
* origin """

    flexgroup = fields.Nested("netapp_ontap.models.volume_flexgroup.VolumeFlexgroupSchema", data_key="flexgroup", unknown=EXCLUDE)
    r""" The flexgroup field of the volume. """

    guarantee = fields.Nested("netapp_ontap.models.volume_guarantee.VolumeGuaranteeSchema", data_key="guarantee", unknown=EXCLUDE)
    r""" The guarantee field of the volume. """

    is_object_store = fields.Boolean(
        data_key="is_object_store",
    )
    r""" Specifies whether the volume is provisioned for an object store server. """

    is_svm_root = fields.Boolean(
        data_key="is_svm_root",
    )
    r""" Specifies whether the volume is a root volume of the SVM it belongs to. """

    language = fields.Str(
        data_key="language",
        validate=enum_validation(['ar', 'ar.utf_8', 'c', 'c.utf_8', 'cs', 'cs.utf_8', 'da', 'da.utf_8', 'de', 'de.utf_8', 'en', 'en.utf_8', 'en_us', 'en_us.utf_8', 'es', 'es.utf_8', 'fi', 'fi.utf_8', 'fr', 'fr.utf_8', 'he', 'he.utf_8', 'hr', 'hr.utf_8', 'hu', 'hu.utf_8', 'it', 'it.utf_8', 'ja', 'ja.utf_8', 'ja_jp.932', 'ja_jp.932.utf_8', 'ja_jp.pck', 'ja_jp.pck.utf_8', 'ja_jp.pck_v2', 'ja_jp.pck_v2.utf_8', 'ja_v1', 'ja_v1.utf_8', 'ko', 'ko.utf_8', 'nl', 'nl.utf_8', 'no', 'no.utf_8', 'pl', 'pl.utf_8', 'pt', 'pt.utf_8', 'ro', 'ro.utf_8', 'ru', 'ru.utf_8', 'sk', 'sk.utf_8', 'sl', 'sl.utf_8', 'sv', 'sv.utf_8', 'tr', 'tr.utf_8', 'utf8mb4', 'zh', 'zh.gbk', 'zh.gbk.utf_8', 'zh.utf_8', 'zh_tw', 'zh_tw.big5', 'zh_tw.big5.utf_8', 'zh_tw.utf_8']),
    )
    r""" Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.

Valid choices:

* ar
* ar.utf_8
* c
* c.utf_8
* cs
* cs.utf_8
* da
* da.utf_8
* de
* de.utf_8
* en
* en.utf_8
* en_us
* en_us.utf_8
* es
* es.utf_8
* fi
* fi.utf_8
* fr
* fr.utf_8
* he
* he.utf_8
* hr
* hr.utf_8
* hu
* hu.utf_8
* it
* it.utf_8
* ja
* ja.utf_8
* ja_jp.932
* ja_jp.932.utf_8
* ja_jp.pck
* ja_jp.pck.utf_8
* ja_jp.pck_v2
* ja_jp.pck_v2.utf_8
* ja_v1
* ja_v1.utf_8
* ko
* ko.utf_8
* nl
* nl.utf_8
* no
* no.utf_8
* pl
* pl.utf_8
* pt
* pt.utf_8
* ro
* ro.utf_8
* ru
* ru.utf_8
* sk
* sk.utf_8
* sl
* sl.utf_8
* sv
* sv.utf_8
* tr
* tr.utf_8
* utf8mb4
* zh
* zh.gbk
* zh.gbk.utf_8
* zh.utf_8
* zh_tw
* zh_tw.big5
* zh_tw.big5.utf_8
* zh_tw.utf_8 """

    max_dir_size = Size(
        data_key="max_dir_size",
    )
    r""" Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support. """

    metric = fields.Nested("netapp_ontap.resources.volume_metrics.VolumeMetricsSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the volume. """

    movement = fields.Nested("netapp_ontap.models.volume_movement1.VolumeMovement1Schema", data_key="movement", unknown=EXCLUDE)
    r""" The movement field of the volume. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=203),
    )
    r""" Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.

Example: vol_cs_dept """

    nas = fields.Nested("netapp_ontap.models.volume_nas.VolumeNasSchema", data_key="nas", unknown=EXCLUDE)
    r""" The nas field of the volume. """

    qos = fields.Nested("netapp_ontap.models.volume_qos.VolumeQosSchema", data_key="qos", unknown=EXCLUDE)
    r""" The qos field of the volume. """

    queue_for_encryption = fields.Boolean(
        data_key="queue_for_encryption",
    )
    r""" Specifies whether the volume is queued for encryption. """

    quota = fields.Nested("netapp_ontap.models.volume_quota.VolumeQuotaSchema", data_key="quota", unknown=EXCLUDE)
    r""" The quota field of the volume. """

    scheduled_snapshot_naming_scheme = fields.Str(
        data_key="scheduled_snapshot_naming_scheme",
        validate=enum_validation(['create_time', 'ordinal']),
    )
    r""" Naming Scheme for automatic Snapshot copies:

* create_time - Automatic Snapshot copies are saved as per the start of their current date and time.
* ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention.


Valid choices:

* create_time
* ordinal """

    size = Size(
        data_key="size",
    )
    r""" Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size. """

    snaplock = fields.Nested("netapp_ontap.models.volume_snaplock.VolumeSnaplockSchema", data_key="snaplock", unknown=EXCLUDE)
    r""" The snaplock field of the volume. """

    snapmirror = fields.Nested("netapp_ontap.models.volume_snapmirror.VolumeSnapmirrorSchema", data_key="snapmirror", unknown=EXCLUDE)
    r""" The snapmirror field of the volume. """

    snapshot_count = Size(
        data_key="snapshot_count",
        validate=integer_validation(minimum=0, maximum=1023),
    )
    r""" Number of Snapshot copies in the volume. """

    snapshot_policy = fields.Nested("netapp_ontap.resources.snapshot_policy.SnapshotPolicySchema", data_key="snapshot_policy", unknown=EXCLUDE)
    r""" The snapshot_policy field of the volume. """

    space = fields.Nested("netapp_ontap.models.volume_space1.VolumeSpace1Schema", data_key="space", unknown=EXCLUDE)
    r""" The space field of the volume. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['error', 'mixed', 'offline', 'online', 'restricted']),
    )
    r""" Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.

Valid choices:

* error
* mixed
* offline
* online
* restricted """

    statistics = fields.Nested("netapp_ontap.models.volume_statistics.VolumeStatisticsSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the volume. """

    status = fields.List(fields.Str, data_key="status")
    r""" Describes the current status of a volume. """

    style = fields.Str(
        data_key="style",
        validate=enum_validation(['flexvol', 'flexgroup', 'flexgroup_constituent']),
    )
    r""" The style of the volume. If "style" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without "constituents_per_aggregate", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with "constituents_per_aggregate", creates a FlexGroup. Specifying a volume "style" creates a volume of that type. For example, if the style is "flexvol" you must specify a single aggregate. If the style is "flexgroup", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style "flexgroup_constiutent" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.

Valid choices:

* flexvol
* flexgroup
* flexgroup_constituent """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the volume. """

    tiering = fields.Nested("netapp_ontap.models.volume_tiering.VolumeTieringSchema", data_key="tiering", unknown=EXCLUDE)
    r""" The tiering field of the volume. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['rw', 'dp', 'ls']),
    )
    r""" Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.

Valid choices:

* rw
* dp
* ls """

    use_mirrored_aggregates = fields.Boolean(
        data_key="use_mirrored_aggregates",
    )
    r""" Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying "aggregates.name" or "aggregates.uuid". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.

Example: 028baa66-41bd-11e9-81d5-00a0986138f7 """

    @property
    def resource(self):
        return Volume

    gettable_fields = [
        "links",
        "access_time_enabled",
        "activity_tracking",
        "aggregates.links",
        "aggregates.name",
        "aggregates.uuid",
        "analytics",
        "anti_ransomware",
        "anti_ransomware_state",
        "application",
        "autosize",
        "clone",
        "cloud_retrieval_policy",
        "comment",
        "consistency_group",
        "constituents",
        "convert_unicode",
        "create_time",
        "efficiency",
        "encryption",
        "error_state",
        "files",
        "flash_pool",
        "flexcache_endpoint_type",
        "flexgroup",
        "guarantee",
        "is_object_store",
        "is_svm_root",
        "language",
        "max_dir_size",
        "metric",
        "movement",
        "name",
        "nas",
        "qos",
        "queue_for_encryption",
        "quota",
        "scheduled_snapshot_naming_scheme",
        "size",
        "snaplock",
        "snapmirror",
        "snapshot_count",
        "snapshot_policy.links",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "state",
        "statistics.cloud",
        "statistics.flexcache_raw",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "status",
        "style",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "tiering",
        "type",
        "uuid",
    ]
    """links,access_time_enabled,activity_tracking,aggregates.links,aggregates.name,aggregates.uuid,analytics,anti_ransomware,anti_ransomware_state,application,autosize,clone,cloud_retrieval_policy,comment,consistency_group,constituents,convert_unicode,create_time,efficiency,encryption,error_state,files,flash_pool,flexcache_endpoint_type,flexgroup,guarantee,is_object_store,is_svm_root,language,max_dir_size,metric,movement,name,nas,qos,queue_for_encryption,quota,scheduled_snapshot_naming_scheme,size,snaplock,snapmirror,snapshot_count,snapshot_policy.links,snapshot_policy.name,snapshot_policy.uuid,space,state,statistics.cloud,statistics.flexcache_raw,statistics.iops_raw,statistics.latency_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,status,style,svm.links,svm.name,svm.uuid,tiering,type,uuid,"""

    patchable_fields = [
        "access_time_enabled",
        "activity_tracking",
        "aggregates.name",
        "aggregates.uuid",
        "analytics",
        "anti_ransomware",
        "anti_ransomware_state",
        "application",
        "autosize",
        "clone",
        "cloud_retrieval_policy",
        "comment",
        "consistency_group",
        "constituents",
        "constituents_per_aggregate",
        "convert_unicode",
        "efficiency",
        "encryption",
        "error_state",
        "files",
        "flash_pool",
        "flexgroup",
        "guarantee",
        "max_dir_size",
        "movement",
        "name",
        "nas",
        "qos",
        "queue_for_encryption",
        "quota",
        "scheduled_snapshot_naming_scheme",
        "size",
        "snaplock",
        "snapmirror",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "state",
        "svm.name",
        "svm.uuid",
        "tiering",
    ]
    """access_time_enabled,activity_tracking,aggregates.name,aggregates.uuid,analytics,anti_ransomware,anti_ransomware_state,application,autosize,clone,cloud_retrieval_policy,comment,consistency_group,constituents,constituents_per_aggregate,convert_unicode,efficiency,encryption,error_state,files,flash_pool,flexgroup,guarantee,max_dir_size,movement,name,nas,qos,queue_for_encryption,quota,scheduled_snapshot_naming_scheme,size,snaplock,snapmirror,snapshot_policy.name,snapshot_policy.uuid,space,state,svm.name,svm.uuid,tiering,"""

    postable_fields = [
        "activity_tracking",
        "aggregates.name",
        "aggregates.uuid",
        "analytics",
        "anti_ransomware",
        "anti_ransomware_state",
        "application",
        "autosize",
        "clone",
        "cloud_retrieval_policy",
        "comment",
        "consistency_group",
        "constituents",
        "constituents_per_aggregate",
        "convert_unicode",
        "efficiency",
        "encryption",
        "error_state",
        "files",
        "flash_pool",
        "flexgroup",
        "guarantee",
        "language",
        "max_dir_size",
        "movement",
        "name",
        "nas",
        "qos",
        "quota",
        "scheduled_snapshot_naming_scheme",
        "size",
        "snaplock",
        "snapmirror",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "state",
        "style",
        "svm.name",
        "svm.uuid",
        "tiering",
        "type",
        "use_mirrored_aggregates",
    ]
    """activity_tracking,aggregates.name,aggregates.uuid,analytics,anti_ransomware,anti_ransomware_state,application,autosize,clone,cloud_retrieval_policy,comment,consistency_group,constituents,constituents_per_aggregate,convert_unicode,efficiency,encryption,error_state,files,flash_pool,flexgroup,guarantee,language,max_dir_size,movement,name,nas,qos,quota,scheduled_snapshot_naming_scheme,size,snaplock,snapmirror,snapshot_policy.name,snapshot_policy.uuid,space,state,style,svm.name,svm.uuid,tiering,type,use_mirrored_aggregates,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in Volume.get_collection(fields=field)]
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
            raise NetAppRestError("Volume modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class Volume(Resource):
    """Allows interaction with Volume objects on the host"""

    _schema = VolumeSchema
    _path = "/api/storage/volumes"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves volumes.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `is_svm_root`
* `analytics.*`
* `anti_ransomware.*`
* `application.*`
* `encryption.*`
* `queue_for_encryption`
* `convert_unicode`
* `clone.parent_snapshot.name`
* `clone.parent_snapshot.uuid`
* `clone.parent_svm.name`
* `clone.parent_svm.uuid`
* `clone.parent_volume.name`
* `clone.parent_volume.uuid`
* `clone.split_complete_percent`
* `clone.split_estimate`
* `clone.split_initiated`
* `efficiency.*`
* `error_state.*`
* `files.*`
* `max_dir_size`
* `nas.export_policy.id`
* `nas.gid`
* `nas.path`
* `nas.security_style`
* `nas.uid`
* `nas.unix_permissions`
* `nas.junction_parent.name`
* `nas.junction_parent.uuid`
* `snaplock.*`
* `restore_to.*`
* `snapshot_policy.uuid`
* `quota.*`
* `qos.*`
* `flexcache_endpoint_type`
* `space.block_storage_inactive_user_data`
* `space.capacity_tier_footprint`
* `space.performance_tier_footprint`
* `space.local_tier_footprint`
* `space.footprint`
* `space.over_provisioned`
* `space.metadata`
* `space.total_footprint`
* `space.dedupe_metafiles_footprint`
* `space.dedupe_metafiles_temporary_footprint`
* `space.delayed_free_footprint`
* `space.file_operation_metadata`
* `space.snapmirror_destination_footprint`
* `space.volume_guarantee_footprint`
* `space.cross_volume_dedupe_metafiles_footprint`
* `space.cross_volume_dedupe_metafiles_temporary_footprint`
* `space.snapshot_reserve_unusable`
* `space.snapshot_spill`
* `space.user_data`
* `space.logical_space.*`
* `space.snapshot.*`
* `space.used_by_afs`
* `space.afs_total`
* `space.available_percent`
* `space.full_threshold_percent`
* `space.nearly_full_threshold_percent`
* `space.overwrite_reserve`
* `space.overwrite_reserve_used`
* `space.size_available_for_snapshots`
* `space.percent_used`
* `space.fractional_reserve`
* `space.block_storage_inactive_user_data_percent`
* `space.physical_used`
* `space.physical_used_percent`
* `space.expected_available`
* `space.filesystem_size`
* `space.filesystem_size_fixed`
* `guarantee.*`
* `autosize.*`
* `movement.*`
* `statistics.*`
* `constituents.name`
* `constituents.space.size`
* `constituents.space.available`
* `constituents.space.used`
* `constituents.space.available_percent`
* `constituents.space.used_percent`
* `constituents.space.block_storage_inactive_user_data`
* `constituents.space.capacity_tier_footprint`
* `constituents.space.performance_tier_footprint`
* `constituents.space.local_tier_footprint`
* `constituents.space.footprint`
* `constituents.space.over_provisioned`
* `constituents.space.metadata`
* `constituents.space.total_footprint`
* `constituents.space.logical_space.reporting`
* `constituents.space.logical_space.enforcement`
* `constituents.space.logical_space.used_by_afs`
* `constituents.space.logical_space.available`
* `constituents.space.snapshot.used`
* `constituents.space.snapshot.reserve_percent`
* `constituents.space.snapshot.autodelete_enabled`
* `constituents.aggregates.name`
* `constituents.aggregates.uuid`
* `constituents.movement.destination_aggregate.name`
* `constituents.movement.destination_aggregate.uuid`
* `constituents.movement.state`
* `constituents.movement.percent_complete`
* `constituents.movement.cutover_window`
* `constituents.movement.tiering_policy`
### Related ONTAP commands
* `volume show`
* `volume clone show`
* `volume efficiency show`
* `volume encryption show`
* `volume flexcache show`
* `volume flexgroup show`
* `volume move show`
* `volume quota show`
* `volume show-space`
* `volume snaplock show`
* `security anti-ransomware volume show`
* `security anti-ransomware volume space show`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="volume show")
        def volume_show(
            fields: List[Choices.define(["access_time_enabled", "anti_ransomware_state", "cloud_retrieval_policy", "comment", "constituents_per_aggregate", "convert_unicode", "create_time", "flexcache_endpoint_type", "is_object_store", "is_svm_root", "language", "max_dir_size", "name", "queue_for_encryption", "scheduled_snapshot_naming_scheme", "size", "snapshot_count", "state", "status", "style", "type", "use_mirrored_aggregates", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of Volume resources

            Args:
                access_time_enabled: Indicates whether or not access time updates are enabled on the volume.
                anti_ransomware_state: The Anti-ransomware state of the volume. If no \"anti_ransomware_state\" property is specified, the volume inherits the value from its parent SVM's \"anti_ransomware_default_volume_state\" property. If this value is \"disabled\", Anti-ransomware is disabled on the volume. If this value is \"enabled\", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is \"dry_run\", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The \"dry_run\" state is same as the \"enabled\" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is \"paused\", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is \"disable_in_progress\", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is \"enable_paused\", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is \"dry_run_paused\", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only \"disabled\", \"enabled\" and \"dry_run\", whereas for PATCH, \"paused\" is also valid along with the three valid states for POST.
                cloud_retrieval_policy: This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are \"default\" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved. \"on_read\" policy retrieves tiered data for all client driven data reads. \"never\" policy never retrieves tiered data. \"promote\" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved. 
                comment: A comment for the volume. Valid in POST or PATCH.
                constituents_per_aggregate: Specifies the number of times to iterate over the aggregates listed with the \"aggregates.name\" or \"aggregates.uuid\" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the \"constituents_per_aggregate\" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list.
                convert_unicode: Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients.
                create_time: Creation time of the volume. This field is generated when the volume is created.
                flexcache_endpoint_type: FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.
                is_object_store: Specifies whether the volume is provisioned for an object store server.
                is_svm_root: Specifies whether the volume is a root volume of the SVM it belongs to.
                language: Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.
                max_dir_size: Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support.
                name: Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.
                queue_for_encryption: Specifies whether the volume is queued for encryption.
                scheduled_snapshot_naming_scheme: Naming Scheme for automatic Snapshot copies: * create_time - Automatic Snapshot copies are saved as per the start of their current date and time. * ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention. 
                size: Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size.
                snapshot_count: Number of Snapshot copies in the volume.
                state: Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.
                status: Describes the current status of a volume.
                style: The style of the volume. If \"style\" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without \"constituents_per_aggregate\", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with \"constituents_per_aggregate\", creates a FlexGroup. Specifying a volume \"style\" creates a volume of that type. For example, if the style is \"flexvol\" you must specify a single aggregate. If the style is \"flexgroup\", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style \"flexgroup_constiutent\" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.
                type: Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.
                use_mirrored_aggregates: Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying \"aggregates.name\" or \"aggregates.uuid\". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration.
                uuid: Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.
            """

            kwargs = {}
            if access_time_enabled is not None:
                kwargs["access_time_enabled"] = access_time_enabled
            if anti_ransomware_state is not None:
                kwargs["anti_ransomware_state"] = anti_ransomware_state
            if cloud_retrieval_policy is not None:
                kwargs["cloud_retrieval_policy"] = cloud_retrieval_policy
            if comment is not None:
                kwargs["comment"] = comment
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if convert_unicode is not None:
                kwargs["convert_unicode"] = convert_unicode
            if create_time is not None:
                kwargs["create_time"] = create_time
            if flexcache_endpoint_type is not None:
                kwargs["flexcache_endpoint_type"] = flexcache_endpoint_type
            if is_object_store is not None:
                kwargs["is_object_store"] = is_object_store
            if is_svm_root is not None:
                kwargs["is_svm_root"] = is_svm_root
            if language is not None:
                kwargs["language"] = language
            if max_dir_size is not None:
                kwargs["max_dir_size"] = max_dir_size
            if name is not None:
                kwargs["name"] = name
            if queue_for_encryption is not None:
                kwargs["queue_for_encryption"] = queue_for_encryption
            if scheduled_snapshot_naming_scheme is not None:
                kwargs["scheduled_snapshot_naming_scheme"] = scheduled_snapshot_naming_scheme
            if size is not None:
                kwargs["size"] = size
            if snapshot_count is not None:
                kwargs["snapshot_count"] = snapshot_count
            if state is not None:
                kwargs["state"] = state
            if status is not None:
                kwargs["status"] = status
            if style is not None:
                kwargs["style"] = style
            if type is not None:
                kwargs["type"] = type
            if use_mirrored_aggregates is not None:
                kwargs["use_mirrored_aggregates"] = use_mirrored_aggregates
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return Volume.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all Volume resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["Volume"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the attributes of a volume. For movement, use the "validate_only" field on the request to validate but not perform the operation. The PATCH API can be used to enable or disable quotas for a FlexVol or a FlexGroup volume. An empty path in PATCH deactivates and unmounts the volume. Taking a volume offline removes its junction path.
<br>A PATCH request for volume encryption performs conversion/rekey operations asynchronously. You can retrieve the conversion/rekey progress details by calling a GET request on the corresponding volume endpoint.
### Optional properties
* `queue_for_encryption` - Queue volumes for encryption when `encryption.enabled=true`.  If this option is not provided or is false, conversion of volumes starts immediately. When there are volumes in the queue and less than four encryptions are running, volumes are encrypted in the order in which they are queued.
* `encryption.action` - You can pause an ongoing rekey/conversion operation or resume a paused rekey/conversion operation using this field.  The following actions are supported for this field: &dash; conversion_pause - Pause an encryption conversion operation currently in progress &dash; conversion_resume - Resume a paused encryption conversion operation &dash; rekey_pause - Pause an encryption rekey operation currently in progress &dash; rekey_resume - Resume a paused encryption rekey operation
### Related ONTAP commands
* `volume unmount`
* `volume mount`
* `volume online`
* `volume offline`
* `volume modify`
* `volume clone modify`
* `volume efficiency modify`
* `volume quota on`
* `volume quota off`
* `volume snaplock modify`
* `volume encryption conversion start`
* `volume encryption rekey start`
* `security anti-ransomware volume enable`
* `security anti-ransomware volume disable`
* `security anti-ransomware volume dry-run`
* `security anti-ransomware volume pause`
* `security anti-ransomware volume resume`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["Volume"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["Volume"], NetAppResponse]:
        r"""Creates a volume on a specified SVM and storage aggregates.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the volume.
* `name` - Name of the volume.
* `aggregates.name` or `aggregates.uuid` - Existing aggregates in which to create the volume.
### Default property values
* `state` -  _online_
* `size` - _20MB_
* `style` - _flexvol_
* `type` - _rw_
* `encryption.enabled` - _false_
* `snapshot_policy.name` - _default_
* `gaurantee.type` - _volume_
* `anti_ransomware.state` - _default_
### Related ONTAP commands
* `volume create`
* `volume clone create`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["Volume"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a volume. If the UUID belongs to a volume, all of its blocks are freed and returned to its containing aggregate. If a volume is online, it is offlined before deletion. If a volume is mounted, unmount the volume by specifying the nas.path as empty before deleting it using the DELETE operation.
### Related ONTAP commands
* `volume delete`
* `volume clone delete`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves volumes.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `is_svm_root`
* `analytics.*`
* `anti_ransomware.*`
* `application.*`
* `encryption.*`
* `queue_for_encryption`
* `convert_unicode`
* `clone.parent_snapshot.name`
* `clone.parent_snapshot.uuid`
* `clone.parent_svm.name`
* `clone.parent_svm.uuid`
* `clone.parent_volume.name`
* `clone.parent_volume.uuid`
* `clone.split_complete_percent`
* `clone.split_estimate`
* `clone.split_initiated`
* `efficiency.*`
* `error_state.*`
* `files.*`
* `max_dir_size`
* `nas.export_policy.id`
* `nas.gid`
* `nas.path`
* `nas.security_style`
* `nas.uid`
* `nas.unix_permissions`
* `nas.junction_parent.name`
* `nas.junction_parent.uuid`
* `snaplock.*`
* `restore_to.*`
* `snapshot_policy.uuid`
* `quota.*`
* `qos.*`
* `flexcache_endpoint_type`
* `space.block_storage_inactive_user_data`
* `space.capacity_tier_footprint`
* `space.performance_tier_footprint`
* `space.local_tier_footprint`
* `space.footprint`
* `space.over_provisioned`
* `space.metadata`
* `space.total_footprint`
* `space.dedupe_metafiles_footprint`
* `space.dedupe_metafiles_temporary_footprint`
* `space.delayed_free_footprint`
* `space.file_operation_metadata`
* `space.snapmirror_destination_footprint`
* `space.volume_guarantee_footprint`
* `space.cross_volume_dedupe_metafiles_footprint`
* `space.cross_volume_dedupe_metafiles_temporary_footprint`
* `space.snapshot_reserve_unusable`
* `space.snapshot_spill`
* `space.user_data`
* `space.logical_space.*`
* `space.snapshot.*`
* `space.used_by_afs`
* `space.afs_total`
* `space.available_percent`
* `space.full_threshold_percent`
* `space.nearly_full_threshold_percent`
* `space.overwrite_reserve`
* `space.overwrite_reserve_used`
* `space.size_available_for_snapshots`
* `space.percent_used`
* `space.fractional_reserve`
* `space.block_storage_inactive_user_data_percent`
* `space.physical_used`
* `space.physical_used_percent`
* `space.expected_available`
* `space.filesystem_size`
* `space.filesystem_size_fixed`
* `guarantee.*`
* `autosize.*`
* `movement.*`
* `statistics.*`
* `constituents.name`
* `constituents.space.size`
* `constituents.space.available`
* `constituents.space.used`
* `constituents.space.available_percent`
* `constituents.space.used_percent`
* `constituents.space.block_storage_inactive_user_data`
* `constituents.space.capacity_tier_footprint`
* `constituents.space.performance_tier_footprint`
* `constituents.space.local_tier_footprint`
* `constituents.space.footprint`
* `constituents.space.over_provisioned`
* `constituents.space.metadata`
* `constituents.space.total_footprint`
* `constituents.space.logical_space.reporting`
* `constituents.space.logical_space.enforcement`
* `constituents.space.logical_space.used_by_afs`
* `constituents.space.logical_space.available`
* `constituents.space.snapshot.used`
* `constituents.space.snapshot.reserve_percent`
* `constituents.space.snapshot.autodelete_enabled`
* `constituents.aggregates.name`
* `constituents.aggregates.uuid`
* `constituents.movement.destination_aggregate.name`
* `constituents.movement.destination_aggregate.uuid`
* `constituents.movement.state`
* `constituents.movement.percent_complete`
* `constituents.movement.cutover_window`
* `constituents.movement.tiering_policy`
### Related ONTAP commands
* `volume show`
* `volume clone show`
* `volume efficiency show`
* `volume encryption show`
* `volume flexcache show`
* `volume flexgroup show`
* `volume move show`
* `volume quota show`
* `volume show-space`
* `volume snaplock show`
* `security anti-ransomware volume show`
* `security anti-ransomware volume space show`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a volume. The GET API can be used to retrieve the quota state for a FlexVol or a FlexGroup volume.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `is_svm_root`
* `analytics.*`
* `anti_ransomware.*`
* `application.*`
* `encryption.*`
* `convert_unicode`
* `clone.parent_snapshot.name`
* `clone.parent_snapshot.uuid`
* `clone.parent_svm.name`
* `clone.parent_svm.uuid`
* `clone.parent_volume.name`
* `clone.parent_volume.uuid`
* `clone.split_complete_percent`
* `clone.split_estimate`
* `clone.split_initiated`
* `efficiency.*`
* `error_state.*`
* `files.*`
* `max_dir_size`
* `nas.export_policy.id`
* `nas.gid`
* `nas.path`
* `nas.security_style`
* `nas.uid`
* `nas.unix_permissions`
* `nas.junction_parent.name`
* `nas.junction_parent.uuid`
* `snaplock.*`
* `restore_to.*`
* `snapshot_policy.uuid`
* `quota.*`
* `qos.*`
* `flexcache_endpoint_type`
* `space.block_storage_inactive_user_data`
* `space.capacity_tier_footprint`
* `space.performance_tier_footprint`
* `space.local_tier_footprint`
* `space.footprint`
* `space.over_provisioned`
* `space.metadata`
* `space.total_footprint`
* `space.dedupe_metafiles_footprint`
* `space.dedupe_metafiles_temporary_footprint`
* `space.delayed_free_footprint`
* `space.file_operation_metadata`
* `space.snapmirror_destination_footprint`
* `space.volume_guarantee_footprint`
* `space.cross_volume_dedupe_metafiles_footprint`
* `space.cross_volume_dedupe_metafiles_temporary_footprint`
* `space.snapshot_reserve_unusable`
* `space.snapshot_spill`
* `space.user_data`
* `space.logical_space.*`
* `space.snapshot.*`
* `space.used_by_afs`
* `space.afs_total`
* `space.available_percent`
* `space.full_threshold_percent`
* `space.nearly_full_threshold_percent`
* `space.overwrite_reserve`
* `space.overwrite_reserve_used`
* `space.size_available_for_snapshots`
* `space.percent_used`
* `space.fractional_reserve`
* `space.block_storage_inactive_user_data_percent`
* `space.physical_used`
* `space.physical_used_percent`
* `space.expected_available`
* `space.filesystem_size`
* `space.filesystem_size_fixed`
* `guarantee.*`
* `autosize.*`
* `movement.*`
* `statistics.*`
### Related ONTAP commands
* `volume show`
* `volume clone show`
* `volume efficiency show`
* `volume encryption show`
* `volume flexcache show`
* `volume flexgroup show`
* `volume move show`
* `volume quota show`
* `volume show-space`
* `volume snaplock show`
* `security anti-ransomware volume show`
* `security anti-ransomware volume attack generate-report`
* `security anti-ransomware volume space show`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
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
        r"""Creates a volume on a specified SVM and storage aggregates.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the volume.
* `name` - Name of the volume.
* `aggregates.name` or `aggregates.uuid` - Existing aggregates in which to create the volume.
### Default property values
* `state` -  _online_
* `size` - _20MB_
* `style` - _flexvol_
* `type` - _rw_
* `encryption.enabled` - _false_
* `snapshot_policy.name` - _default_
* `gaurantee.type` - _volume_
* `anti_ransomware.state` - _default_
### Related ONTAP commands
* `volume create`
* `volume clone create`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="volume create")
        async def volume_create(
        ) -> ResourceTable:
            """Create an instance of a Volume resource

            Args:
                links: 
                access_time_enabled: Indicates whether or not access time updates are enabled on the volume.
                activity_tracking: 
                aggregates: Aggregate hosting the volume. Required on POST.
                analytics: 
                anti_ransomware: 
                anti_ransomware_state: The Anti-ransomware state of the volume. If no \"anti_ransomware_state\" property is specified, the volume inherits the value from its parent SVM's \"anti_ransomware_default_volume_state\" property. If this value is \"disabled\", Anti-ransomware is disabled on the volume. If this value is \"enabled\", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is \"dry_run\", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The \"dry_run\" state is same as the \"enabled\" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is \"paused\", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is \"disable_in_progress\", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is \"enable_paused\", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is \"dry_run_paused\", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only \"disabled\", \"enabled\" and \"dry_run\", whereas for PATCH, \"paused\" is also valid along with the three valid states for POST.
                application: 
                autosize: 
                clone: 
                cloud_retrieval_policy: This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are \"default\" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved. \"on_read\" policy retrieves tiered data for all client driven data reads. \"never\" policy never retrieves tiered data. \"promote\" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved. 
                comment: A comment for the volume. Valid in POST or PATCH.
                consistency_group: 
                constituents: 
                constituents_per_aggregate: Specifies the number of times to iterate over the aggregates listed with the \"aggregates.name\" or \"aggregates.uuid\" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the \"constituents_per_aggregate\" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list.
                convert_unicode: Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients.
                create_time: Creation time of the volume. This field is generated when the volume is created.
                efficiency: 
                encryption: 
                error_state: 
                files: 
                flash_pool: 
                flexcache_endpoint_type: FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.
                flexgroup: 
                guarantee: 
                is_object_store: Specifies whether the volume is provisioned for an object store server.
                is_svm_root: Specifies whether the volume is a root volume of the SVM it belongs to.
                language: Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.
                max_dir_size: Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support.
                metric: 
                movement: 
                name: Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.
                nas: 
                qos: 
                queue_for_encryption: Specifies whether the volume is queued for encryption.
                quota: 
                scheduled_snapshot_naming_scheme: Naming Scheme for automatic Snapshot copies: * create_time - Automatic Snapshot copies are saved as per the start of their current date and time. * ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention. 
                size: Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size.
                snaplock: 
                snapmirror: 
                snapshot_count: Number of Snapshot copies in the volume.
                snapshot_policy: 
                space: 
                state: Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.
                statistics: 
                status: Describes the current status of a volume.
                style: The style of the volume. If \"style\" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without \"constituents_per_aggregate\", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with \"constituents_per_aggregate\", creates a FlexGroup. Specifying a volume \"style\" creates a volume of that type. For example, if the style is \"flexvol\" you must specify a single aggregate. If the style is \"flexgroup\", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style \"flexgroup_constiutent\" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.
                svm: 
                tiering: 
                type: Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.
                use_mirrored_aggregates: Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying \"aggregates.name\" or \"aggregates.uuid\". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration.
                uuid: Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if access_time_enabled is not None:
                kwargs["access_time_enabled"] = access_time_enabled
            if activity_tracking is not None:
                kwargs["activity_tracking"] = activity_tracking
            if aggregates is not None:
                kwargs["aggregates"] = aggregates
            if analytics is not None:
                kwargs["analytics"] = analytics
            if anti_ransomware is not None:
                kwargs["anti_ransomware"] = anti_ransomware
            if anti_ransomware_state is not None:
                kwargs["anti_ransomware_state"] = anti_ransomware_state
            if application is not None:
                kwargs["application"] = application
            if autosize is not None:
                kwargs["autosize"] = autosize
            if clone is not None:
                kwargs["clone"] = clone
            if cloud_retrieval_policy is not None:
                kwargs["cloud_retrieval_policy"] = cloud_retrieval_policy
            if comment is not None:
                kwargs["comment"] = comment
            if consistency_group is not None:
                kwargs["consistency_group"] = consistency_group
            if constituents is not None:
                kwargs["constituents"] = constituents
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if convert_unicode is not None:
                kwargs["convert_unicode"] = convert_unicode
            if create_time is not None:
                kwargs["create_time"] = create_time
            if efficiency is not None:
                kwargs["efficiency"] = efficiency
            if encryption is not None:
                kwargs["encryption"] = encryption
            if error_state is not None:
                kwargs["error_state"] = error_state
            if files is not None:
                kwargs["files"] = files
            if flash_pool is not None:
                kwargs["flash_pool"] = flash_pool
            if flexcache_endpoint_type is not None:
                kwargs["flexcache_endpoint_type"] = flexcache_endpoint_type
            if flexgroup is not None:
                kwargs["flexgroup"] = flexgroup
            if guarantee is not None:
                kwargs["guarantee"] = guarantee
            if is_object_store is not None:
                kwargs["is_object_store"] = is_object_store
            if is_svm_root is not None:
                kwargs["is_svm_root"] = is_svm_root
            if language is not None:
                kwargs["language"] = language
            if max_dir_size is not None:
                kwargs["max_dir_size"] = max_dir_size
            if metric is not None:
                kwargs["metric"] = metric
            if movement is not None:
                kwargs["movement"] = movement
            if name is not None:
                kwargs["name"] = name
            if nas is not None:
                kwargs["nas"] = nas
            if qos is not None:
                kwargs["qos"] = qos
            if queue_for_encryption is not None:
                kwargs["queue_for_encryption"] = queue_for_encryption
            if quota is not None:
                kwargs["quota"] = quota
            if scheduled_snapshot_naming_scheme is not None:
                kwargs["scheduled_snapshot_naming_scheme"] = scheduled_snapshot_naming_scheme
            if size is not None:
                kwargs["size"] = size
            if snaplock is not None:
                kwargs["snaplock"] = snaplock
            if snapmirror is not None:
                kwargs["snapmirror"] = snapmirror
            if snapshot_count is not None:
                kwargs["snapshot_count"] = snapshot_count
            if snapshot_policy is not None:
                kwargs["snapshot_policy"] = snapshot_policy
            if space is not None:
                kwargs["space"] = space
            if state is not None:
                kwargs["state"] = state
            if statistics is not None:
                kwargs["statistics"] = statistics
            if status is not None:
                kwargs["status"] = status
            if style is not None:
                kwargs["style"] = style
            if svm is not None:
                kwargs["svm"] = svm
            if tiering is not None:
                kwargs["tiering"] = tiering
            if type is not None:
                kwargs["type"] = type
            if use_mirrored_aggregates is not None:
                kwargs["use_mirrored_aggregates"] = use_mirrored_aggregates
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = Volume(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create Volume: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the attributes of a volume. For movement, use the "validate_only" field on the request to validate but not perform the operation. The PATCH API can be used to enable or disable quotas for a FlexVol or a FlexGroup volume. An empty path in PATCH deactivates and unmounts the volume. Taking a volume offline removes its junction path.
<br>A PATCH request for volume encryption performs conversion/rekey operations asynchronously. You can retrieve the conversion/rekey progress details by calling a GET request on the corresponding volume endpoint.
### Optional properties
* `queue_for_encryption` - Queue volumes for encryption when `encryption.enabled=true`.  If this option is not provided or is false, conversion of volumes starts immediately. When there are volumes in the queue and less than four encryptions are running, volumes are encrypted in the order in which they are queued.
* `encryption.action` - You can pause an ongoing rekey/conversion operation or resume a paused rekey/conversion operation using this field.  The following actions are supported for this field: &dash; conversion_pause - Pause an encryption conversion operation currently in progress &dash; conversion_resume - Resume a paused encryption conversion operation &dash; rekey_pause - Pause an encryption rekey operation currently in progress &dash; rekey_resume - Resume a paused encryption rekey operation
### Related ONTAP commands
* `volume unmount`
* `volume mount`
* `volume online`
* `volume offline`
* `volume modify`
* `volume clone modify`
* `volume efficiency modify`
* `volume quota on`
* `volume quota off`
* `volume snaplock modify`
* `volume encryption conversion start`
* `volume encryption rekey start`
* `security anti-ransomware volume enable`
* `security anti-ransomware volume disable`
* `security anti-ransomware volume dry-run`
* `security anti-ransomware volume pause`
* `security anti-ransomware volume resume`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="volume modify")
        async def volume_modify(
        ) -> ResourceTable:
            """Modify an instance of a Volume resource

            Args:
                access_time_enabled: Indicates whether or not access time updates are enabled on the volume.
                query_access_time_enabled: Indicates whether or not access time updates are enabled on the volume.
                anti_ransomware_state: The Anti-ransomware state of the volume. If no \"anti_ransomware_state\" property is specified, the volume inherits the value from its parent SVM's \"anti_ransomware_default_volume_state\" property. If this value is \"disabled\", Anti-ransomware is disabled on the volume. If this value is \"enabled\", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is \"dry_run\", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The \"dry_run\" state is same as the \"enabled\" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is \"paused\", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is \"disable_in_progress\", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is \"enable_paused\", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is \"dry_run_paused\", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only \"disabled\", \"enabled\" and \"dry_run\", whereas for PATCH, \"paused\" is also valid along with the three valid states for POST.
                query_anti_ransomware_state: The Anti-ransomware state of the volume. If no \"anti_ransomware_state\" property is specified, the volume inherits the value from its parent SVM's \"anti_ransomware_default_volume_state\" property. If this value is \"disabled\", Anti-ransomware is disabled on the volume. If this value is \"enabled\", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is \"dry_run\", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The \"dry_run\" state is same as the \"enabled\" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is \"paused\", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is \"disable_in_progress\", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is \"enable_paused\", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is \"dry_run_paused\", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only \"disabled\", \"enabled\" and \"dry_run\", whereas for PATCH, \"paused\" is also valid along with the three valid states for POST.
                cloud_retrieval_policy: This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are \"default\" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved. \"on_read\" policy retrieves tiered data for all client driven data reads. \"never\" policy never retrieves tiered data. \"promote\" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved. 
                query_cloud_retrieval_policy: This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are \"default\" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved. \"on_read\" policy retrieves tiered data for all client driven data reads. \"never\" policy never retrieves tiered data. \"promote\" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved. 
                comment: A comment for the volume. Valid in POST or PATCH.
                query_comment: A comment for the volume. Valid in POST or PATCH.
                constituents_per_aggregate: Specifies the number of times to iterate over the aggregates listed with the \"aggregates.name\" or \"aggregates.uuid\" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the \"constituents_per_aggregate\" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list.
                query_constituents_per_aggregate: Specifies the number of times to iterate over the aggregates listed with the \"aggregates.name\" or \"aggregates.uuid\" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the \"constituents_per_aggregate\" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list.
                convert_unicode: Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients.
                query_convert_unicode: Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients.
                create_time: Creation time of the volume. This field is generated when the volume is created.
                query_create_time: Creation time of the volume. This field is generated when the volume is created.
                flexcache_endpoint_type: FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.
                query_flexcache_endpoint_type: FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.
                is_object_store: Specifies whether the volume is provisioned for an object store server.
                query_is_object_store: Specifies whether the volume is provisioned for an object store server.
                is_svm_root: Specifies whether the volume is a root volume of the SVM it belongs to.
                query_is_svm_root: Specifies whether the volume is a root volume of the SVM it belongs to.
                language: Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.
                query_language: Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.
                max_dir_size: Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support.
                query_max_dir_size: Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support.
                name: Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.
                query_name: Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.
                queue_for_encryption: Specifies whether the volume is queued for encryption.
                query_queue_for_encryption: Specifies whether the volume is queued for encryption.
                scheduled_snapshot_naming_scheme: Naming Scheme for automatic Snapshot copies: * create_time - Automatic Snapshot copies are saved as per the start of their current date and time. * ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention. 
                query_scheduled_snapshot_naming_scheme: Naming Scheme for automatic Snapshot copies: * create_time - Automatic Snapshot copies are saved as per the start of their current date and time. * ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention. 
                size: Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size.
                query_size: Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size.
                snapshot_count: Number of Snapshot copies in the volume.
                query_snapshot_count: Number of Snapshot copies in the volume.
                state: Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.
                query_state: Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.
                status: Describes the current status of a volume.
                query_status: Describes the current status of a volume.
                style: The style of the volume. If \"style\" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without \"constituents_per_aggregate\", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with \"constituents_per_aggregate\", creates a FlexGroup. Specifying a volume \"style\" creates a volume of that type. For example, if the style is \"flexvol\" you must specify a single aggregate. If the style is \"flexgroup\", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style \"flexgroup_constiutent\" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.
                query_style: The style of the volume. If \"style\" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without \"constituents_per_aggregate\", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with \"constituents_per_aggregate\", creates a FlexGroup. Specifying a volume \"style\" creates a volume of that type. For example, if the style is \"flexvol\" you must specify a single aggregate. If the style is \"flexgroup\", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style \"flexgroup_constiutent\" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.
                type: Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.
                query_type: Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.
                use_mirrored_aggregates: Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying \"aggregates.name\" or \"aggregates.uuid\". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration.
                query_use_mirrored_aggregates: Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying \"aggregates.name\" or \"aggregates.uuid\". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration.
                uuid: Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.
                query_uuid: Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.
            """

            kwargs = {}
            changes = {}
            if query_access_time_enabled is not None:
                kwargs["access_time_enabled"] = query_access_time_enabled
            if query_anti_ransomware_state is not None:
                kwargs["anti_ransomware_state"] = query_anti_ransomware_state
            if query_cloud_retrieval_policy is not None:
                kwargs["cloud_retrieval_policy"] = query_cloud_retrieval_policy
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = query_constituents_per_aggregate
            if query_convert_unicode is not None:
                kwargs["convert_unicode"] = query_convert_unicode
            if query_create_time is not None:
                kwargs["create_time"] = query_create_time
            if query_flexcache_endpoint_type is not None:
                kwargs["flexcache_endpoint_type"] = query_flexcache_endpoint_type
            if query_is_object_store is not None:
                kwargs["is_object_store"] = query_is_object_store
            if query_is_svm_root is not None:
                kwargs["is_svm_root"] = query_is_svm_root
            if query_language is not None:
                kwargs["language"] = query_language
            if query_max_dir_size is not None:
                kwargs["max_dir_size"] = query_max_dir_size
            if query_name is not None:
                kwargs["name"] = query_name
            if query_queue_for_encryption is not None:
                kwargs["queue_for_encryption"] = query_queue_for_encryption
            if query_scheduled_snapshot_naming_scheme is not None:
                kwargs["scheduled_snapshot_naming_scheme"] = query_scheduled_snapshot_naming_scheme
            if query_size is not None:
                kwargs["size"] = query_size
            if query_snapshot_count is not None:
                kwargs["snapshot_count"] = query_snapshot_count
            if query_state is not None:
                kwargs["state"] = query_state
            if query_status is not None:
                kwargs["status"] = query_status
            if query_style is not None:
                kwargs["style"] = query_style
            if query_type is not None:
                kwargs["type"] = query_type
            if query_use_mirrored_aggregates is not None:
                kwargs["use_mirrored_aggregates"] = query_use_mirrored_aggregates
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if access_time_enabled is not None:
                changes["access_time_enabled"] = access_time_enabled
            if anti_ransomware_state is not None:
                changes["anti_ransomware_state"] = anti_ransomware_state
            if cloud_retrieval_policy is not None:
                changes["cloud_retrieval_policy"] = cloud_retrieval_policy
            if comment is not None:
                changes["comment"] = comment
            if constituents_per_aggregate is not None:
                changes["constituents_per_aggregate"] = constituents_per_aggregate
            if convert_unicode is not None:
                changes["convert_unicode"] = convert_unicode
            if create_time is not None:
                changes["create_time"] = create_time
            if flexcache_endpoint_type is not None:
                changes["flexcache_endpoint_type"] = flexcache_endpoint_type
            if is_object_store is not None:
                changes["is_object_store"] = is_object_store
            if is_svm_root is not None:
                changes["is_svm_root"] = is_svm_root
            if language is not None:
                changes["language"] = language
            if max_dir_size is not None:
                changes["max_dir_size"] = max_dir_size
            if name is not None:
                changes["name"] = name
            if queue_for_encryption is not None:
                changes["queue_for_encryption"] = queue_for_encryption
            if scheduled_snapshot_naming_scheme is not None:
                changes["scheduled_snapshot_naming_scheme"] = scheduled_snapshot_naming_scheme
            if size is not None:
                changes["size"] = size
            if snapshot_count is not None:
                changes["snapshot_count"] = snapshot_count
            if state is not None:
                changes["state"] = state
            if status is not None:
                changes["status"] = status
            if style is not None:
                changes["style"] = style
            if type is not None:
                changes["type"] = type
            if use_mirrored_aggregates is not None:
                changes["use_mirrored_aggregates"] = use_mirrored_aggregates
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(Volume, "find"):
                resource = Volume.find(
                    **kwargs
                )
            else:
                resource = Volume()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify Volume: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a volume. If the UUID belongs to a volume, all of its blocks are freed and returned to its containing aggregate. If a volume is online, it is offlined before deletion. If a volume is mounted, unmount the volume by specifying the nas.path as empty before deleting it using the DELETE operation.
### Related ONTAP commands
* `volume delete`
* `volume clone delete`

### Learn more
* [`DOC /storage/volumes`](#docs-storage-storage_volumes)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="volume delete")
        async def volume_delete(
        ) -> None:
            """Delete an instance of a Volume resource

            Args:
                access_time_enabled: Indicates whether or not access time updates are enabled on the volume.
                anti_ransomware_state: The Anti-ransomware state of the volume. If no \"anti_ransomware_state\" property is specified, the volume inherits the value from its parent SVM's \"anti_ransomware_default_volume_state\" property. If this value is \"disabled\", Anti-ransomware is disabled on the volume. If this value is \"enabled\", Anti-ransomware is enabled on the volume and alerts are raised if any suspect is detected for those volumes. If this value is \"dry_run\", Anti-ransomware is enabled in the dry-run or learning mode on the volume. The \"dry_run\" state is same as the \"enabled\" state except that the analytics data is used here for learning. No alerts are raised for any detections or violations. If this value is \"paused\", Anti-ransomware is paused on the volume. Additionally, three more states are available, which are only valid for GET. If this value is \"disable_in_progress\", Anti-ransomware monitoring is being disabled and a cleanup operation is in effect. If this value is \"enable_paused\", Anti-ransomware is paused on the volume from its earlier enabled state. If this value is \"dry_run_paused\", Anti-ransomware monitoring is paused on the volume from its earlier dry_run state. For POST, the valid Anti-ransomware states are only \"disabled\", \"enabled\" and \"dry_run\", whereas for PATCH, \"paused\" is also valid along with the three valid states for POST.
                cloud_retrieval_policy: This parameter specifies the cloud retrieval policy for the volume. This policy determines which tiered out blocks to retrieve from the capacity tier to the performance tier. The available cloud retrieval policies are \"default\" policy retrieves tiered data based on the underlying tiering policy. If the tiering policy is 'auto', tiered data is retrieved only for random client driven data reads. If the tiering policy is 'none' or 'snapshot_only', tiered data is retrieved for random and sequential client driven data reads. If the tiering policy is 'all', tiered data is not retrieved. \"on_read\" policy retrieves tiered data for all client driven data reads. \"never\" policy never retrieves tiered data. \"promote\" policy retrieves all eligible tiered data automatically during the next scheduled scan. It is only supported when the tiering policy is 'none' or 'snapshot_only'. If the tiering policy is 'snapshot_only', the only data brought back is the data in the AFS. Data that is only in a snapshot copy stays in the cloud and if tiering policy is 'none' then all data is retrieved. 
                comment: A comment for the volume. Valid in POST or PATCH.
                constituents_per_aggregate: Specifies the number of times to iterate over the aggregates listed with the \"aggregates.name\" or \"aggregates.uuid\" when creating or expanding a FlexGroup volume. If a volume is being created on a single aggregate, the system creates a flexible volume if the \"constituents_per_aggregate\" field is not specified, or a FlexGroup volume if it is specified. If a volume is being created on multiple aggregates, the system always creates a FlexGroup volume. The root constituent of a FlexGroup volume is always placed on the first aggregate in the list.
                convert_unicode: Specifies whether directory Unicode format conversion is enabled when directories are accessed by NFS clients.
                create_time: Creation time of the volume. This field is generated when the volume is created.
                flexcache_endpoint_type: FlexCache endpoint type. <br>none &dash; The volume is neither a FlexCache nor origin of any FlexCache. <br>cache &dash; The volume is a FlexCache volume. <br>origin &dash; The volume is origin of a FlexCache volume.
                is_object_store: Specifies whether the volume is provisioned for an object store server.
                is_svm_root: Specifies whether the volume is a root volume of the SVM it belongs to.
                language: Language encoding setting for volume. If no language is specified, the volume inherits its SVM language encoding setting.
                max_dir_size: Maximum directory size. This value sets maximum size, in bytes, to which a directory can grow. The default maximum directory size for FlexVol volumes is model-dependent, and optimized for the size of system memory. Before increasing the maximum directory size, involve technical support.
                name: Volume name. The name of volume must start with an alphabetic character (a to z or A to Z) or an underscore (_). The name must be 197 or fewer characters in length for FlexGroups, and 203 or fewer characters in length for all other types of volumes. Volume names must be unique within an SVM. Required on POST.
                queue_for_encryption: Specifies whether the volume is queued for encryption.
                scheduled_snapshot_naming_scheme: Naming Scheme for automatic Snapshot copies: * create_time - Automatic Snapshot copies are saved as per the start of their current date and time. * ordinal - Latest automatic snapshot copy is saved as <scheduled_frequency>.0 and subsequent copies will follow the create_time naming convention. 
                size: Physical size of the volume, in bytes. The minimum size for a FlexVol volume is 20MB and the minimum size for a FlexGroup volume is 200MB per constituent. The recommended size for a FlexGroup volume is a minimum of 100GB per constituent. For all volumes, the default size is equal to the minimum size.
                snapshot_count: Number of Snapshot copies in the volume.
                state: Volume state. Client access is supported only when volume is online and junctioned. Taking volume to offline or restricted state removes its junction path and blocks client access. When volume is in restricted state some operations like parity reconstruction and iron on commit are allowed. The 'mixed' state applies to FlexGroup volumes only and cannot be specified as a target state. An 'error' state implies that the volume is not in a state to serve data.
                status: Describes the current status of a volume.
                style: The style of the volume. If \"style\" is not specified, the volume type is determined based on the specified aggregates. Specifying a single aggregate, without \"constituents_per_aggregate\", creates a flexible volume. Specifying multiple aggregates, or a single aggregate with \"constituents_per_aggregate\", creates a FlexGroup. Specifying a volume \"style\" creates a volume of that type. For example, if the style is \"flexvol\" you must specify a single aggregate. If the style is \"flexgroup\", the system either uses the specified aggregates or automatically provisions aggregates if there are no specified aggregates. The style \"flexgroup_constiutent\" is not supported when creating a volume.<br>flexvol &dash; flexible volumes and FlexClone volumes<br>flexgroup &dash; FlexGroup volumes<br>flexgroup_constituent &dash; FlexGroup constituents.
                type: Type of the volume.<br>rw &dash; read-write volume.<br>dp &dash; data-protection volume.<br>ls &dash; load-sharing `dp` volume. Valid in GET.
                use_mirrored_aggregates: Specifies whether mirrored aggregates are selected when provisioning a FlexGroup without specifying \"aggregates.name\" or \"aggregates.uuid\". Only mirrored aggregates are used if this parameter is set to 'true' and only unmirrored aggregates are used if this parameter is set to 'false'. Aggregate level mirroring for a FlexGroup can be changed by moving all of the constituents to the required aggregates. The default value is 'true' for a MetroCluster configuration and is 'false' for a non-MetroCluster configuration.
                uuid: Unique identifier for the volume. This corresponds to the instance-uuid that is exposed in the CLI and ONTAPI. It does not change due to a volume move.
            """

            kwargs = {}
            if access_time_enabled is not None:
                kwargs["access_time_enabled"] = access_time_enabled
            if anti_ransomware_state is not None:
                kwargs["anti_ransomware_state"] = anti_ransomware_state
            if cloud_retrieval_policy is not None:
                kwargs["cloud_retrieval_policy"] = cloud_retrieval_policy
            if comment is not None:
                kwargs["comment"] = comment
            if constituents_per_aggregate is not None:
                kwargs["constituents_per_aggregate"] = constituents_per_aggregate
            if convert_unicode is not None:
                kwargs["convert_unicode"] = convert_unicode
            if create_time is not None:
                kwargs["create_time"] = create_time
            if flexcache_endpoint_type is not None:
                kwargs["flexcache_endpoint_type"] = flexcache_endpoint_type
            if is_object_store is not None:
                kwargs["is_object_store"] = is_object_store
            if is_svm_root is not None:
                kwargs["is_svm_root"] = is_svm_root
            if language is not None:
                kwargs["language"] = language
            if max_dir_size is not None:
                kwargs["max_dir_size"] = max_dir_size
            if name is not None:
                kwargs["name"] = name
            if queue_for_encryption is not None:
                kwargs["queue_for_encryption"] = queue_for_encryption
            if scheduled_snapshot_naming_scheme is not None:
                kwargs["scheduled_snapshot_naming_scheme"] = scheduled_snapshot_naming_scheme
            if size is not None:
                kwargs["size"] = size
            if snapshot_count is not None:
                kwargs["snapshot_count"] = snapshot_count
            if state is not None:
                kwargs["state"] = state
            if status is not None:
                kwargs["status"] = status
            if style is not None:
                kwargs["style"] = style
            if type is not None:
                kwargs["type"] = type
            if use_mirrored_aggregates is not None:
                kwargs["use_mirrored_aggregates"] = use_mirrored_aggregates
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(Volume, "find"):
                resource = Volume.find(
                    **kwargs
                )
            else:
                resource = Volume()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete Volume: %s" % err)


