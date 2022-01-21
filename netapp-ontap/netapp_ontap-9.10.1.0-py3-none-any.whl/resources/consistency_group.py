r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A consistency group is a group of volumes that supports capabilities such as creating a snapshot of all of its member volumes at the same point-in-time with a write-fence, thus ensuring a consistent image of the volumes at that time.
<br>Applications with datasets scoped to a single volume can have its contents saved to a Snapshot copy, replicated, or cloned in a crash-consistent manner implicitly with corresponding native ONTAP volume-granular operations. Applications with datasets spanning a group of multiple volumes must have such operations performed on the group. Typically, by first fencing writes to all the volumes in the group, flushing any writes pending in queues, executing the intended operation, that is, take Snapshot copy of every volume in the group and when that is complete, unfence and resume writes. A consistency group is the conventional mechanism for providing such group semantics.
## Consistency group  APIs
The following APIs are used to perform operations related to consistency groups:

* GET       /api/application/consistency-groups
* POST      /api/application/consistency-groups
* GET       /api/application/consistency-groups/{uuid}
* PATCH     /api/application/consistency-groups/{uuid}
* DELETE    /api/application/consistency-groups/{uuid}
## Examples
### Retrieving all consistency groups of an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="password", verify=False
):
    print(list(ConsistencyGroup.get_collection(**{"svm.name": "vs1"})))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    ConsistencyGroup(
        {
            "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
            "name": "vol1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/6f48d798-0a7f-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
    ConsistencyGroup(
        {
            "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
            "name": "parent_cg",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b22c85-0a82-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
    ConsistencyGroup(
        {
            "uuid": "c1b270b1-0a82-11ec-a449-005056bbcf9f",
            "name": "child_1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b270b1-0a82-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
    ConsistencyGroup(
        {
            "uuid": "c1b270c3-0a82-11ec-a449-005056bbcf9f",
            "name": "child_2",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b270c3-0a82-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving details of all consistency groups of an SVM
Retrieving details of the consistency groups for a specified SVM. These details are considered to be performant and will return within 1 second when 40 records or less are requested.<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    print(
        list(
            ConsistencyGroup.get_collection(
                fields="*", max_records=40, **{"svm.name": "vs1"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    ConsistencyGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"
                    }
                },
                "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
                "name": "vs1",
            },
            "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
            "replicated": False,
            "space": {"size": 108003328, "available": 107704320, "used": 299008},
            "name": "vol1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/6f48d798-0a7f-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
    ConsistencyGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"
                    }
                },
                "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
                "name": "vs1",
            },
            "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
            "replicated": False,
            "space": {"size": 83886080, "available": 78696448, "used": 995328},
            "consistency_groups": [
                {
                    "uuid": "c1b270b1-0a82-11ec-a449-005056bbcf9f",
                    "space": {"size": 41943040, "available": 39346176, "used": 499712},
                    "name": "child_1",
                    "_links": {
                        "self": {
                            "href": "/api/application/consistency-groups/c1b270b1-0a82-11ec-a449-005056bbcf9f"
                        }
                    },
                },
                {
                    "uuid": "c1b270c3-0a82-11ec-a449-005056bbcf9f",
                    "space": {"size": 41943040, "available": 39350272, "used": 495616},
                    "name": "child_2",
                    "_links": {
                        "self": {
                            "href": "/api/application/consistency-groups/c1b270c3-0a82-11ec-a449-005056bbcf9f"
                        }
                    },
                },
            ],
            "name": "parent_cg",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b22c85-0a82-11ec-a449-005056bbcf9f"
                }
            },
            "snapshot_policy": {
                "uuid": "a30bd0fe-067d-11ec-a449-005056bbcf9f",
                "name": "default-1weekly",
                "_links": {
                    "self": {
                        "href": "/api/storage/snapshot-policies/a30bd0fe-067d-11ec-a449-005056bbcf9f"
                    }
                },
            },
        }
    ),
    ConsistencyGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"
                    }
                },
                "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
                "name": "vs1",
            },
            "uuid": "c1b270b1-0a82-11ec-a449-005056bbcf9f",
            "space": {"size": 41943040, "available": 39346176, "used": 499712},
            "parent_consistency_group": {
                "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
                "name": "parent_cg",
                "_links": {
                    "self": {
                        "href": "/api/application/consistency-groups/c1b22c85-0a82-11ec-a449-005056bbcf9f"
                    }
                },
            },
            "name": "child_1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b270b1-0a82-11ec-a449-005056bbcf9f"
                }
            },
            "snapshot_policy": {
                "uuid": "a30b60a4-067d-11ec-a449-005056bbcf9f",
                "name": "default",
                "_links": {
                    "self": {
                        "href": "/api/storage/snapshot-policies/a30b60a4-067d-11ec-a449-005056bbcf9f"
                    }
                },
            },
        }
    ),
    ConsistencyGroup(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"
                    }
                },
                "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
                "name": "vs1",
            },
            "uuid": "c1b270c3-0a82-11ec-a449-005056bbcf9f",
            "space": {"size": 41943040, "available": 39350272, "used": 495616},
            "parent_consistency_group": {
                "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
                "name": "parent_cg",
                "_links": {
                    "self": {
                        "href": "/api/application/consistency-groups/c1b22c85-0a82-11ec-a449-005056bbcf9f"
                    }
                },
            },
            "name": "child_2",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b270c3-0a82-11ec-a449-005056bbcf9f"
                }
            },
            "snapshot_policy": {
                "uuid": "a30b60a4-067d-11ec-a449-005056bbcf9f",
                "name": "default",
                "_links": {
                    "self": {
                        "href": "/api/storage/snapshot-policies/a30b60a4-067d-11ec-a449-005056bbcf9f"
                    }
                },
            },
        }
    ),
]

```
</div>
</div>

### Retrieving details of non-nested consistency groups
Retrieves details of the consistency groups without nested consistency groups, or only the parent consistency group for a number of consistency groups of a specified SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    print(
        list(
            ConsistencyGroup.get_collection(
                **{"svm.name": "vs1", "parent_consistency_group.uuid": "null"}
            )
        )
    )

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    ConsistencyGroup(
        {
            "svm": {"name": "vs1"},
            "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
            "name": "vol1",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/6f48d798-0a7f-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
    ConsistencyGroup(
        {
            "svm": {"name": "vs1"},
            "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
            "name": "parent_cg",
            "_links": {
                "self": {
                    "href": "/api/application/consistency-groups/c1b22c85-0a82-11ec-a449-005056bbcf9f"
                }
            },
        }
    ),
]

```
</div>
</div>

### Creating a single consistency group with a new SAN volume
Provisions an application with one consistency group, each with one new SAN volumes, with one LUN, an igroup and no explicit Snapshot copy policy, FabricPool tiering policy, storage service, and QoS policy specification. The igroup to map a LUN to is specified at LUN-granularity.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup()
    resource.svm = {"name": "vs1"}
    resource.luns = [
        {
            "name": "/vol/vol1/lun1",
            "space": {"size": "100mb"},
            "os_type": "linux",
            "lun_maps": [
                {
                    "igroup": {
                        "name": "igroup1",
                        "initiators": [
                            {
                                "name": "iqn.2021-07.com.netapp.englab.gdl:scspr2429998001"
                            }
                        ],
                    }
                }
            ],
        }
    ]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
ConsistencyGroup(
    {
        "luns": [
            {
                "os_type": "linux",
                "lun_maps": [
                    {
                        "igroup": {
                            "initiators": [
                                {
                                    "name": "iqn.2021-07.com.netapp.englab.gdl:scspr2429998001"
                                }
                            ],
                            "name": "igroup1",
                        }
                    }
                ],
                "space": {"size": 104857600},
                "name": "/vol/vol1/lun1",
            }
        ],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"}
            },
            "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
            "name": "vs1",
        },
        "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
        "name": "vol1",
    }
)

```
</div>
</div>

### Creating an Application with two consistency groups with existing SAN volumes
Provisions an application with two consistency groups, each with two existing SAN volumes, a Snapshot copy policy at application-granularity, and a distinct consistency group granular Snapshot copy policy.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup()
    resource.svm = {"name": "vs1"}
    resource.name = "parent_cg"
    resource.snapshot_policy = {"name": "default-1weekly"}
    resource.consistency_groups = [
        {
            "name": "child_1",
            "snapshot_policy": {"name": "default"},
            "volumes": [
                {"name": "existing_vol1", "provisioning_options": {"action": "add"}},
                {"name": "existing_vol2", "provisioning_options": {"action": "add"}},
            ],
        },
        {
            "name": "child_2",
            "snapshot_policy": {"name": "default"},
            "volumes": [
                {"name": "existing_vol3", "provisioning_options": {"action": "add"}},
                {"name": "existing_vol4", "provisioning_options": {"action": "add"}},
            ],
        },
    ]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
ConsistencyGroup(
    {
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"}
            },
            "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
            "name": "vs1",
        },
        "uuid": "c1b22c85-0a82-11ec-a449-005056bbcf9f",
        "consistency_groups": [
            {
                "uuid": "c1b270b1-0a82-11ec-a449-005056bbcf9f",
                "volumes": [{"name": "existing_vol1"}, {"name": "existing_vol2"}],
                "name": "child_1",
                "snapshot_policy": {"name": "default"},
            },
            {
                "uuid": "c1b270c3-0a82-11ec-a449-005056bbcf9f",
                "volumes": [{"name": "existing_vol3"}, {"name": "existing_vol4"}],
                "name": "child_2",
                "snapshot_policy": {"name": "default"},
            },
        ],
        "name": "parent_cg",
        "snapshot_policy": {"name": "default-1weekly"},
    }
)

```
</div>
</div>

### Retrieving specific details of an existing consistency group
Retrieves the details of an existing consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup(uuid="6f48d798-0a7f-11ec-a449-005056bbcf9f")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
ConsistencyGroup(
    {
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"}
            },
            "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
            "name": "vs1",
        },
        "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
        "replicated": False,
        "space": {"size": 108003328, "available": 107724800, "used": 278528},
        "name": "vol1",
        "_links": {
            "self": {
                "href": "/api/application/consistency-groups/6f48d798-0a7f-11ec-a449-005056bbcf9f"
            }
        },
    }
)

```
</div>
</div>

### Retrieving all details of an existing consistency group
Retrieves all details of an existing consistency group. These details are not considered to be performant and are not guaranteed to return within one second.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup(uuid="6f48d798-0a7f-11ec-a449-005056bbcf9f")
    resource.get(fields="**")
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
ConsistencyGroup(
    {
        "luns": [
            {
                "os_type": "linux",
                "lun_maps": [
                    {
                        "igroup": {
                            "os_type": "linux",
                            "initiators": [
                                {
                                    "name": "iqn.2021-07.com.netapp.englab.gdl:scspr2429998001"
                                }
                            ],
                            "uuid": "6f4a4b86-0a7f-11ec-a449-005056bbcf9f",
                            "protocol": "mixed",
                            "name": "igroup1",
                        },
                        "logical_unit_number": 0,
                    }
                ],
                "uuid": "6f51748a-0a7f-11ec-a449-005056bbcf9f",
                "create_time": "2021-08-31T13:18:24-04:00",
                "space": {"size": 104857600, "used": 0},
                "name": "/vol/vol1/lun1",
                "serial_number": "wIqM6]RfQK3t",
            }
        ],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/4853f97a-0a63-11ec-a449-005056bbcf9f"}
            },
            "uuid": "4853f97a-0a63-11ec-a449-005056bbcf9f",
            "name": "vs1",
        },
        "uuid": "6f48d798-0a7f-11ec-a449-005056bbcf9f",
        "replicated": False,
        "tiering": {"policy": "none"},
        "space": {"size": 108003328, "available": 107569152, "used": 434176},
        "volumes": [
            {
                "uuid": "6f516c6c-0a7f-11ec-a449-005056bbcf9f",
                "tiering": {"policy": "none"},
                "space": {"size": 108003328, "available": 107569152, "used": 434176},
                "comment": "",
                "qos": {
                    "policy": {
                        "uuid": "b7189398-e572-48ab-8f69-82cd46580812",
                        "name": "extreme-fixed",
                        "_links": {
                            "self": {
                                "href": "/api/storage/qos/policies/b7189398-e572-48ab-8f69-82cd46580812"
                            }
                        },
                    }
                },
                "name": "vol1",
                "snapshot_policy": {
                    "uuid": "a30b60a4-067d-11ec-a449-005056bbcf9f",
                    "name": "default",
                },
            }
        ],
        "qos": {
            "policy": {
                "uuid": "b7189398-e572-48ab-8f69-82cd46580812",
                "name": "extreme-fixed",
                "_links": {
                    "self": {
                        "href": "/api/storage/qos/policies/b7189398-e572-48ab-8f69-82cd46580812"
                    }
                },
            }
        },
        "name": "vol1",
        "_links": {
            "self": {
                "href": "/api/application/consistency-groups/6f48d798-0a7f-11ec-a449-005056bbcf9f?fields=**"
            }
        },
    }
)

```
</div>
</div>

### Adding LUNs to an existing volume in an existing consistency group
Adds two NVMe namespaces to an existing volume in an existing consistency group, creates a new subsystem, and binds the new namespaces to it.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup(uuid="6f48d798-0a7f-11ec-a449-005056bbcf9f")
    resource.luns = [
        {
            "name": "/vol/vol1/new_luns",
            "provisioning_options": {"count": 2, "action": "create"},
            "space": {"size": "100mb"},
            "os_type": "linux",
            "lun_maps": [
                {
                    "igroup": {
                        "name": "igroup2",
                        "initiators": [{"name": "01:02:03:04:05:06:07:01"}],
                    }
                }
            ],
        }
    ]
    resource.patch()

```

### Restoring a consistency group to the contents of an existing snapshot
Restores an existing consistency group to the contents of an existing snapshot of the consistency group.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup(uuid="6f51748a-0a7f-11ec-a449-005056bbcf9f")
    resource.restore_to = {"snapshot": {"uuid": "92c6c770-17a1-11eb-b141-005056acd498"}}
    resource.patch()

```

### Deleting a consistency group
Deletes a consistency group, where all storage originally associated with that consistency group remains in place.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ConsistencyGroup

with HostConnection(
    "netapp-cluster.netapp.com", username="admin", password="netapp1!", verify=False
):
    resource = ConsistencyGroup(uuid="6f48d798-0a7f-11ec-a449-005056bbcf9f")
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


__all__ = ["ConsistencyGroup", "ConsistencyGroupSchema"]
__pdoc__ = {
    "ConsistencyGroupSchema.resource": False,
    "ConsistencyGroup.consistency_group_show": False,
    "ConsistencyGroup.consistency_group_create": False,
    "ConsistencyGroup.consistency_group_modify": False,
    "ConsistencyGroup.consistency_group_delete": False,
}


class ConsistencyGroupSchema(ResourceSchema):
    """The fields of the ConsistencyGroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the consistency_group. """

    consistency_groups = fields.List(fields.Nested("netapp_ontap.models.consistency_group_child.ConsistencyGroupChildSchema", unknown=EXCLUDE), data_key="consistency_groups")
    r""" A consistency group is a mutually exclusive aggregation of volumes or other consistency groups. A consistency group can only be associated with one direct parent consistency group. """

    luns = fields.List(fields.Nested("netapp_ontap.models.consistency_group_lun.ConsistencyGroupLunSchema", unknown=EXCLUDE), data_key="luns")
    r""" The LUNs array can be used to create or modify LUNs in a consistency group on a new or existing volume that is a member of the consistency group. LUNs are considered members of a consistency group if they are located on a volume that is a member of the consistency group. """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the consistency group. The consistency group name must be unique within an SVM.<br/>
If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. """

    namespaces = fields.List(fields.Nested("netapp_ontap.models.consistency_group_namespace.ConsistencyGroupNamespaceSchema", unknown=EXCLUDE), data_key="namespaces")
    r""" An NVMe namespace is a collection of addressable logical blocks presented to hosts connected to the SVM using the NVMe over Fabrics protocol.
In ONTAP, an NVMe namespace is located within a volume. Optionally, it can be located within a qtree in a volume.<br/>
An NVMe namespace is created to a specified size using thin or thick provisioning as determined by the volume on which it is created. NVMe namespaces support being cloned. An NVMe namespace cannot be renamed, resized, or moved to a different volume. NVMe namespaces do not support the assignment of a QoS policy for performance management, but a QoS policy can be assigned to the volume containing the namespace. See the NVMe namespace object model to learn more about each of the properties supported by the NVMe namespace REST API.<br/>
An NVMe namespace must be mapped to an NVMe subsystem to grant access to the subsystem's hosts. Hosts can then access the NVMe namespace and perform I/O using the NVMe over Fabrics protocol. """

    parent_consistency_group = fields.Nested("netapp_ontap.resources.consistency_group.ConsistencyGroupSchema", data_key="parent_consistency_group", unknown=EXCLUDE)
    r""" The parent_consistency_group field of the consistency_group. """

    provisioning_options = fields.Nested("netapp_ontap.models.consistency_group_provisioning_options.ConsistencyGroupProvisioningOptionsSchema", data_key="provisioning_options", unknown=EXCLUDE)
    r""" The provisioning_options field of the consistency_group. """

    qos = fields.Nested("netapp_ontap.models.consistency_group_qos.ConsistencyGroupQosSchema", data_key="qos", unknown=EXCLUDE)
    r""" The qos field of the consistency_group. """

    replicated = fields.Boolean(
        data_key="replicated",
    )
    r""" Indicates whether or not replication has been enabled on this consistency group. """

    replication_source = fields.Boolean(
        data_key="replication_source",
    )
    r""" Indicates whether or not this consistency group is the source for replication. """

    restore_to = fields.Nested("netapp_ontap.models.consistency_group_restore_to.ConsistencyGroupRestoreToSchema", data_key="restore_to", unknown=EXCLUDE)
    r""" The restore_to field of the consistency_group. """

    snapshot_policy = fields.Nested("netapp_ontap.resources.snapshot_policy.SnapshotPolicySchema", data_key="snapshot_policy", unknown=EXCLUDE)
    r""" The Snapshot copy policy of the consistency group.<br/>
This is the dedicated consistency group Snapshot copy policy, not an aggregation of the volume granular Snapshot copy policy. """

    space = fields.Nested("netapp_ontap.models.consistency_group_space.ConsistencyGroupSpaceSchema", data_key="space", unknown=EXCLUDE)
    r""" The space field of the consistency_group. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The Storage Virtual Machine (SVM) in which the consistency group is located. """

    tiering = fields.Nested("netapp_ontap.models.consistency_group_tiering.ConsistencyGroupTieringSchema", data_key="tiering", unknown=EXCLUDE)
    r""" The tiering field of the consistency_group. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created.


Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    volumes = fields.List(fields.Nested("netapp_ontap.models.consistency_group_volume.ConsistencyGroupVolumeSchema", unknown=EXCLUDE), data_key="volumes")
    r""" A consistency group is a mutually exclusive aggregation of volumes or other consistency groups. A volume can only be associated with one direct parent consistency group.<br/>
The volumes array can be used to create new volumes in the consistency group, add existing volumes to the consistency group, or modify existing volumes that are already members of the consistency group.<br/>
The total number of volumes across all child consistency groups contained in a consistency group is constrained by the same limit. """

    @property
    def resource(self):
        return ConsistencyGroup

    gettable_fields = [
        "links",
        "consistency_groups",
        "luns",
        "name",
        "parent_consistency_group.links",
        "parent_consistency_group.name",
        "parent_consistency_group.uuid",
        "provisioning_options",
        "qos",
        "replicated",
        "replication_source",
        "snapshot_policy.links",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "tiering",
        "uuid",
        "volumes",
    ]
    """links,consistency_groups,luns,name,parent_consistency_group.links,parent_consistency_group.name,parent_consistency_group.uuid,provisioning_options,qos,replicated,replication_source,snapshot_policy.links,snapshot_policy.name,snapshot_policy.uuid,space,svm.links,svm.name,svm.uuid,tiering,uuid,volumes,"""

    patchable_fields = [
        "luns",
        "namespaces",
        "parent_consistency_group.links",
        "parent_consistency_group.name",
        "parent_consistency_group.uuid",
        "provisioning_options",
        "qos",
        "restore_to",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "svm.name",
        "svm.uuid",
    ]
    """luns,namespaces,parent_consistency_group.links,parent_consistency_group.name,parent_consistency_group.uuid,provisioning_options,qos,restore_to,snapshot_policy.name,snapshot_policy.uuid,space,svm.name,svm.uuid,"""

    postable_fields = [
        "consistency_groups",
        "luns",
        "name",
        "parent_consistency_group.links",
        "parent_consistency_group.name",
        "parent_consistency_group.uuid",
        "provisioning_options",
        "qos",
        "snapshot_policy.name",
        "snapshot_policy.uuid",
        "space",
        "svm.name",
        "svm.uuid",
        "tiering",
        "volumes",
    ]
    """consistency_groups,luns,name,parent_consistency_group.links,parent_consistency_group.name,parent_consistency_group.uuid,provisioning_options,qos,snapshot_policy.name,snapshot_policy.uuid,space,svm.name,svm.uuid,tiering,volumes,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ConsistencyGroup.get_collection(fields=field)]
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
            raise NetAppRestError("ConsistencyGroup modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ConsistencyGroup(Resource):
    """Allows interaction with ConsistencyGroup objects on the host"""

    _schema = ConsistencyGroupSchema
    _path = "/api/application/consistency-groups"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieve details of a collection or a specific consistency group.
## Notes
When volume granular properties, such as, the storage SLC, Fabric Pool tiering are not the same for all the existing volumes of a consistency group, the corresponding property is not reported at consistency group granularity. It is only reported if all the volumes of the consistency group have the same value for that property.
<br>If this consistency group instance is part of a replication relationship, the "replicated" parameter will be true. Otherwise, it is false. Also, the "replicated" parameter will not be present in the output for Nested-consistency groups, it is included only for single and top-level consistency groups. If this consistency group instance is the source of a replication relationship, the "replication_source" parameter will be true. Otherwise, it is false.
## Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `volumes`
* `luns`
* `namespaces`

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group show")
        def consistency_group_show(
            fields: List[Choices.define(["name", "replicated", "replication_source", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ConsistencyGroup resources

            Args:
                name: Name of the consistency group. The consistency group name must be unique within an SVM.<br/> If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. 
                replicated: Indicates whether or not replication has been enabled on this consistency group. 
                replication_source: Indicates whether or not this consistency group is the source for replication. 
                uuid: The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if replicated is not None:
                kwargs["replicated"] = replicated
            if replication_source is not None:
                kwargs["replication_source"] = replication_source
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ConsistencyGroup.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ConsistencyGroup resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["ConsistencyGroup"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a consistency group.
<br>Note that this operation will never delete storage elements. You can specify only elements that should be added to the consistency group regardless of existing storage objects.
## Related ONTAP commands
N/A. There are no ONTAP commands for managing consistency groups.
## Examples:
### Adding namespaces to an existing volume in an existing consistency group
To add two NVMe Namespaces to an existing volume in an existing consistency group, create a new subsystem and bind the new namespaces to it.
```
curl -X PATCH -k -u admin:netapp1! 'https://netapp-cluster.netapp.com/api/application/consistency-groups/6f51748a-0a7f-11ec-a449-005056bbcf9f' -d '{ "namespaces": [ { "name": "/vol/vol1/new_namespace", "space": { "size": "10M" }, "os_type": "windows", "provisioning_options": { "count": 2 }, "subsystem_map": { "subsystem": { "name": "mySubsystem", "hosts": [ { "nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.host1" }, { "nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.host2" } ] } } } ] }'
#### Response:
```
{
  "job": {
    "uuid": "8c9cabf3-0a88-11ec-a449-005056bbcf9f",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/8c9cabf3-0a88-11ec-a449-005056bbcf9f"
      }
    }
  }
}
```

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["ConsistencyGroup"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["ConsistencyGroup"], NetAppResponse]:
        r"""Creates a consistency group with one or more consistency groups having:
* new SAN volumes,
* existing SAN, NVMe or NAS FlexVol volumes in a new or existing consistency group
## Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the group.
* `volumes`, `luns` or `namespaces`
## Naming Conventions
### Consistency groups
  * name or consistency_groups[].name, if specified
  * derived from volumes[0].name, if only one volume is specified, same as volume name
### Volume
  * volumes[].name, if specified
  * derived from volume prefix in luns[].name
  * derived from cg[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
### LUN
  * luns[].name, if specified
  * derived from volumes[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
### NVMe Namespace
  * namespaces[].name, if specified
  * derived from volumes[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
## Related ONTAP commands
There are no ONTAP commands for managing consistency group.

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["ConsistencyGroup"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a consistency group.
<br>Note this will not delete any associated volumes or LUNs. To remove those elements, you can use the appropriate object endpoint.
## Related ONTAP commands
There are no ONTAP commands for managing consistency groups.

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieve details of a collection or a specific consistency group.
## Notes
When volume granular properties, such as, the storage SLC, Fabric Pool tiering are not the same for all the existing volumes of a consistency group, the corresponding property is not reported at consistency group granularity. It is only reported if all the volumes of the consistency group have the same value for that property.
<br>If this consistency group instance is part of a replication relationship, the "replicated" parameter will be true. Otherwise, it is false. Also, the "replicated" parameter will not be present in the output for Nested-consistency groups, it is included only for single and top-level consistency groups. If this consistency group instance is the source of a replication relationship, the "replication_source" parameter will be true. Otherwise, it is false.
## Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `volumes`
* `luns`
* `namespaces`

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a single consistency group.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`DOC Requesting specific fields`](#docs-docs-Requesting-specific-fields) to learn more.
* `volumes`
* `luns`
* `namespaces`
## Related ONTAP commands
There are no ONTAP commands for managing consistency groups.

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
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
        r"""Creates a consistency group with one or more consistency groups having:
* new SAN volumes,
* existing SAN, NVMe or NAS FlexVol volumes in a new or existing consistency group
## Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the group.
* `volumes`, `luns` or `namespaces`
## Naming Conventions
### Consistency groups
  * name or consistency_groups[].name, if specified
  * derived from volumes[0].name, if only one volume is specified, same as volume name
### Volume
  * volumes[].name, if specified
  * derived from volume prefix in luns[].name
  * derived from cg[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
### LUN
  * luns[].name, if specified
  * derived from volumes[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
### NVMe Namespace
  * namespaces[].name, if specified
  * derived from volumes[].name, suffixed by "_#" where "#" is a system generated unique number
  * suffixed by "_#" where "#" is a system generated unique number, if provisioning_options.count is provided
## Related ONTAP commands
There are no ONTAP commands for managing consistency group.

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group create")
        async def consistency_group_create(
        ) -> ResourceTable:
            """Create an instance of a ConsistencyGroup resource

            Args:
                links: 
                consistency_groups: A consistency group is a mutually exclusive aggregation of volumes or other consistency groups. A consistency group can only be associated with one direct parent consistency group. 
                luns: The LUNs array can be used to create or modify LUNs in a consistency group on a new or existing volume that is a member of the consistency group. LUNs are considered members of a consistency group if they are located on a volume that is a member of the consistency group. 
                name: Name of the consistency group. The consistency group name must be unique within an SVM.<br/> If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. 
                namespaces: An NVMe namespace is a collection of addressable logical blocks presented to hosts connected to the SVM using the NVMe over Fabrics protocol. In ONTAP, an NVMe namespace is located within a volume. Optionally, it can be located within a qtree in a volume.<br/> An NVMe namespace is created to a specified size using thin or thick provisioning as determined by the volume on which it is created. NVMe namespaces support being cloned. An NVMe namespace cannot be renamed, resized, or moved to a different volume. NVMe namespaces do not support the assignment of a QoS policy for performance management, but a QoS policy can be assigned to the volume containing the namespace. See the NVMe namespace object model to learn more about each of the properties supported by the NVMe namespace REST API.<br/> An NVMe namespace must be mapped to an NVMe subsystem to grant access to the subsystem's hosts. Hosts can then access the NVMe namespace and perform I/O using the NVMe over Fabrics protocol. 
                parent_consistency_group: 
                provisioning_options: 
                qos: 
                replicated: Indicates whether or not replication has been enabled on this consistency group. 
                replication_source: Indicates whether or not this consistency group is the source for replication. 
                restore_to: 
                snapshot_policy: The Snapshot copy policy of the consistency group.<br/> This is the dedicated consistency group Snapshot copy policy, not an aggregation of the volume granular Snapshot copy policy. 
                space: 
                svm: The Storage Virtual Machine (SVM) in which the consistency group is located. 
                tiering: 
                uuid: The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created. 
                volumes: A consistency group is a mutually exclusive aggregation of volumes or other consistency groups. A volume can only be associated with one direct parent consistency group.<br/> The volumes array can be used to create new volumes in the consistency group, add existing volumes to the consistency group, or modify existing volumes that are already members of the consistency group.<br/> The total number of volumes across all child consistency groups contained in a consistency group is constrained by the same limit. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if consistency_groups is not None:
                kwargs["consistency_groups"] = consistency_groups
            if luns is not None:
                kwargs["luns"] = luns
            if name is not None:
                kwargs["name"] = name
            if namespaces is not None:
                kwargs["namespaces"] = namespaces
            if parent_consistency_group is not None:
                kwargs["parent_consistency_group"] = parent_consistency_group
            if provisioning_options is not None:
                kwargs["provisioning_options"] = provisioning_options
            if qos is not None:
                kwargs["qos"] = qos
            if replicated is not None:
                kwargs["replicated"] = replicated
            if replication_source is not None:
                kwargs["replication_source"] = replication_source
            if restore_to is not None:
                kwargs["restore_to"] = restore_to
            if snapshot_policy is not None:
                kwargs["snapshot_policy"] = snapshot_policy
            if space is not None:
                kwargs["space"] = space
            if svm is not None:
                kwargs["svm"] = svm
            if tiering is not None:
                kwargs["tiering"] = tiering
            if uuid is not None:
                kwargs["uuid"] = uuid
            if volumes is not None:
                kwargs["volumes"] = volumes

            resource = ConsistencyGroup(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ConsistencyGroup: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a consistency group.
<br>Note that this operation will never delete storage elements. You can specify only elements that should be added to the consistency group regardless of existing storage objects.
## Related ONTAP commands
N/A. There are no ONTAP commands for managing consistency groups.
## Examples:
### Adding namespaces to an existing volume in an existing consistency group
To add two NVMe Namespaces to an existing volume in an existing consistency group, create a new subsystem and bind the new namespaces to it.
```
curl -X PATCH -k -u admin:netapp1! 'https://netapp-cluster.netapp.com/api/application/consistency-groups/6f51748a-0a7f-11ec-a449-005056bbcf9f' -d '{ "namespaces": [ { "name": "/vol/vol1/new_namespace", "space": { "size": "10M" }, "os_type": "windows", "provisioning_options": { "count": 2 }, "subsystem_map": { "subsystem": { "name": "mySubsystem", "hosts": [ { "nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.host1" }, { "nqn": "nqn.1992-08.com.netapp:sn.d04594ef915b4c73b642169e72e4c0b1:subsystem.host2" } ] } } } ] }'
#### Response:
```
{
  "job": {
    "uuid": "8c9cabf3-0a88-11ec-a449-005056bbcf9f",
    "_links": {
      "self": {
        "href": "/api/cluster/jobs/8c9cabf3-0a88-11ec-a449-005056bbcf9f"
      }
    }
  }
}
```

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group modify")
        async def consistency_group_modify(
        ) -> ResourceTable:
            """Modify an instance of a ConsistencyGroup resource

            Args:
                name: Name of the consistency group. The consistency group name must be unique within an SVM.<br/> If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. 
                query_name: Name of the consistency group. The consistency group name must be unique within an SVM.<br/> If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. 
                replicated: Indicates whether or not replication has been enabled on this consistency group. 
                query_replicated: Indicates whether or not replication has been enabled on this consistency group. 
                replication_source: Indicates whether or not this consistency group is the source for replication. 
                query_replication_source: Indicates whether or not this consistency group is the source for replication. 
                uuid: The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created. 
                query_uuid: The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created. 
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_replicated is not None:
                kwargs["replicated"] = query_replicated
            if query_replication_source is not None:
                kwargs["replication_source"] = query_replication_source
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if name is not None:
                changes["name"] = name
            if replicated is not None:
                changes["replicated"] = replicated
            if replication_source is not None:
                changes["replication_source"] = replication_source
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(ConsistencyGroup, "find"):
                resource = ConsistencyGroup.find(
                    **kwargs
                )
            else:
                resource = ConsistencyGroup()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ConsistencyGroup: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a consistency group.
<br>Note this will not delete any associated volumes or LUNs. To remove those elements, you can use the appropriate object endpoint.
## Related ONTAP commands
There are no ONTAP commands for managing consistency groups.

### Learn more
* [`DOC /application/consistency-groups`](#docs-application-application_consistency-groups)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="consistency group delete")
        async def consistency_group_delete(
        ) -> None:
            """Delete an instance of a ConsistencyGroup resource

            Args:
                name: Name of the consistency group. The consistency group name must be unique within an SVM.<br/> If not provided and the consistency group contains only one volume, the name will be generated based on the volume name. If the consistency group contains more than one volume, the name is required. 
                replicated: Indicates whether or not replication has been enabled on this consistency group. 
                replication_source: Indicates whether or not this consistency group is the source for replication. 
                uuid: The unique identifier of the consistency group. The UUID is generated by ONTAP when the consistency group is created. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if replicated is not None:
                kwargs["replicated"] = replicated
            if replication_source is not None:
                kwargs["replication_source"] = replication_source
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(ConsistencyGroup, "find"):
                resource = ConsistencyGroup.find(
                    **kwargs
                )
            else:
                resource = ConsistencyGroup()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ConsistencyGroup: %s" % err)


