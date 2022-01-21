r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Quotas are defined in quota rules specific to FlexVol volumes or FlexGroup volumes.  Each quota rule has a type. The type can be "user", "group", or "tree".</br>

* User rules must have the user property and qtree property.
* Group rules must have the group property and qtree property.
* Tree rules must have the qtree property and not have the user or group property.
## Quota policy rule APIs
The following APIs can be used to perform create, retrieve, modify, and delete operations related to quota policy rules.

* POST      /api/storage/quota/rules
* GET       /api/storage/quota/rules
* GET       /api/storage/quota/rules/{rule-uuid}
* PATCH     /api/storage/quota/rules/{rule-uuid}
* DELETE    /api/storage/quota/rules/{rule-uuid}
## Examples
### Retrieving all quota policy rules
This API is used to retrieve all quota policy rules.<br/>
The following example shows how to retrieve quota policy rules for FlexVol volumes and FlexGroup volumes.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(QuotaRule.get_collection()))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    QuotaRule(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/038545f8-9ff8-11e8-bce6-005056a73bed"
                    }
                },
                "uuid": "038545f8-9ff8-11e8-bce6-005056a73bed",
                "name": "svm1",
            },
            "uuid": "66319cbe-b837-11e8-9c5a-005056a7e88c",
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/ab3df793-0f02-43c6-9514-4f142fc8cc92"
                    }
                },
                "uuid": "ab3df793-0f02-43c6-9514-4f142fc8cc92",
                "name": "vol1",
            },
            "_links": {
                "self": {
                    "href": "/api/storage/quota/rules/66319cbe-b837-11e8-9c5a-005056a7e88c"
                }
            },
        }
    ),
    QuotaRule(
        {
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/038545f8-9ff8-11e8-bce6-005056a73bed"
                    }
                },
                "uuid": "038545f8-9ff8-11e8-bce6-005056a73bed",
                "name": "svm1",
            },
            "uuid": "dbd5b443-b7a4-11e8-bc58-005056a7e88c",
            "volume": {
                "_links": {
                    "self": {
                        "href": "/api/storage/volumes/ab3df793-0f02-43c6-9514-4f142fc8cc92"
                    }
                },
                "uuid": "ab3df793-0f02-43c6-9514-4f142fc8cc92",
                "name": "vol1",
            },
            "_links": {
                "self": {
                    "href": "/api/storage/quota/rules/dbd5b443-b7a4-11e8-bc58-005056a7e88c"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific quota policy rule
This API is used to retrieve a quota policy rule for a specific qtree.<br/>
The following example shows how to retrieve a quota policy user rule for a specific qtree.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="264a9e0b-2e03-11e9-a610-005056a7b72d")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "user",
        "files": {"soft_limit": 80, "hard_limit": 100},
        "users": [{"name": "fred"}],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/fd5db15a-15b9-11e9-a6ad-005056a760e0"}
            },
            "uuid": "fd5db15a-15b9-11e9-a6ad-005056a760e0",
            "name": "svm1",
        },
        "uuid": "264a9e0b-2e03-11e9-a610-005056a7b72d",
        "qtree": {
            "id": 1,
            "name": "qt1",
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/c1b64eea-ca8b-45ec-9397-ab489830d268/1"
                }
            },
        },
        "volume": {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/c1b64eea-ca8b-45ec-9397-ab489830d268"
                }
            },
            "uuid": "c1b64eea-ca8b-45ec-9397-ab489830d268",
            "name": "vol1",
        },
        "space": {"soft_limit": 51200, "hard_limit": 1222800},
        "user_mapping": True,
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/264a9e0b-2e03-11e9-a610-005056a7b72d"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving a quota policy multi-user rule at the volume level
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="0ab84fba-19aa-11e9-a04d-005056a72f42")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "user",
        "files": {"soft_limit": 80, "hard_limit": 100},
        "users": [{"name": "sam"}, {"name": "smith"}, {"id": "300010"}],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/fd5db15a-15b9-11e9-a6ad-005056a760e0"}
            },
            "uuid": "fd5db15a-15b9-11e9-a6ad-005056a760e0",
            "name": "svm1",
        },
        "uuid": "0ab84fba-19aa-11e9-a04d-005056a72f42",
        "volume": {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/c1b64eea-ca8b-45ec-9397-ab489830d268"
                }
            },
            "uuid": "c1b64eea-ca8b-45ec-9397-ab489830d268",
            "name": "vol1",
        },
        "space": {"soft_limit": 51200, "hard_limit": 1222800},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/0ab84fba-19aa-11e9-a04d-005056a72f42"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving a quota policy default tree rule
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="4a276b8c-1753-11e9-8101-005056a760e0")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "tree",
        "files": {"soft_limit": 10, "hard_limit": 20},
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/fd5db15a-15b9-11e9-a6ad-005056a760e0"}
            },
            "uuid": "fd5db15a-15b9-11e9-a6ad-005056a760e0",
            "name": "svm1",
        },
        "uuid": "4a276b8c-1753-11e9-8101-005056a760e0",
        "qtree": {"name": ""},
        "volume": {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/c1b64eea-ca8b-45ec-9397-ab489830d268"
                }
            },
            "uuid": "c1b64eea-ca8b-45ec-9397-ab489830d268",
            "name": "vol1",
        },
        "space": {"soft_limit": 51200, "hard_limit": 1034000},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/4a276b8c-1753-11e9-8101-005056a760e0"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving a quota policy tree rule for a specific qtree
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="49b1134f-19ab-11e9-a04d-005056a72f42")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "tree",
        "files": {"soft_limit": 40, "hard_limit": 100},
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/fd5db15a-15b9-11e9-a6ad-005056a760e0"}
            },
            "uuid": "fd5db15a-15b9-11e9-a6ad-005056a760e0",
            "name": "svm1",
        },
        "uuid": "49b1134f-19ab-11e9-a04d-005056a72f42",
        "qtree": {
            "id": 1,
            "name": "qt1",
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/c1b64eea-ca8b-45ec-9397-ab489830d268/1"
                }
            },
        },
        "volume": {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/c1b64eea-ca8b-45ec-9397-ab489830d268"
                }
            },
            "uuid": "c1b64eea-ca8b-45ec-9397-ab489830d268",
            "name": "vol1",
        },
        "space": {"soft_limit": 838861, "hard_limit": 1048576},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/49b1134f-19ab-11e9-a04d-005056a72f42"
            }
        },
    }
)

```
</div>
</div>

---
### Retrieving a quota policy group rule for a specific qtree
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="b9236852-19ab-11e9-a04d-005056a72f42")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example5_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example5_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example5_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "group",
        "files": {"soft_limit": 200, "hard_limit": 250},
        "group": {"name": "group1"},
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/fd5db15a-15b9-11e9-a6ad-005056a760e0"}
            },
            "uuid": "fd5db15a-15b9-11e9-a6ad-005056a760e0",
            "name": "svm1",
        },
        "uuid": "b9236852-19ab-11e9-a04d-005056a72f42",
        "qtree": {
            "id": 1,
            "name": "qt1",
            "_links": {
                "self": {
                    "href": "/api/storage/qtrees/c1b64eea-ca8b-45ec-9397-ab489830d268/1"
                }
            },
        },
        "volume": {
            "_links": {
                "self": {
                    "href": "/api/storage/volumes/c1b64eea-ca8b-45ec-9397-ab489830d268"
                }
            },
            "uuid": "c1b64eea-ca8b-45ec-9397-ab489830d268",
            "name": "vol1",
        },
        "space": {"soft_limit": 1572864, "hard_limit": 2097152},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/b9236852-19ab-11e9-a04d-005056a72f42"
            }
        },
    }
)

```
</div>
</div>

---
### Creating a quota policy rule
This API is used to create a new quota policy rule. When an explicit rule or a qtree-scoped rule of a type is created on a volume, a default rule of the same type is automatically added if it does not already exist on the volume. <br/>
The following example shows how to create a quota policy user rule using POST.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule()
    resource.svm = {"name": "svm1"}
    resource.volume = {"name": "vol1"}
    resource.type = "user"
    resource.users = [{"name": "jsmith"}]
    resource.qtree = {"name": "qt1"}
    resource.user_mapping = "on"
    resource.space = {"hard_limit": 8192, "soft_limit": 1024}
    resource.files = {"hard_limit": 20, "soft_limit": 10}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example6_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example6_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example6_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "user",
        "files": {"soft_limit": 10, "hard_limit": 20},
        "users": [{"name": "jsmith"}],
        "svm": {"name": "svm1"},
        "uuid": "3220eea6-5049-11e9-bfb7-005056a7f717",
        "qtree": {"name": "qt1"},
        "volume": {"name": "fv"},
        "space": {"soft_limit": 1024, "hard_limit": 8192},
        "user_mapping": True,
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/3220eea6-5049-11e9-bfb7-005056a7f717"
            }
        },
    }
)

```
</div>
</div>

---
### Creating a quota policy group rule using POST.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule()
    resource.svm = {"name": "svm1"}
    resource.volume = {"name": "vol1"}
    resource.type = "group"
    resource.group = {"name": "test_group1"}
    resource.qtree = {"name": "qt1"}
    resource.space = {"hard_limit": 8192, "soft_limit": 1024}
    resource.files = {"hard_limit": 20, "soft_limit": 10}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "group",
        "files": {"soft_limit": 10, "hard_limit": 20},
        "group": {"name": "test_group1"},
        "svm": {"name": "svm1"},
        "uuid": "3b130f7d-504a-11e9-bfb7-005056a7f717",
        "qtree": {"name": "qt1"},
        "volume": {"name": "fv"},
        "space": {"soft_limit": 1024, "hard_limit": 8192},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/3b130f7d-504a-11e9-bfb7-005056a7f717"
            }
        },
    }
)

```
</div>
</div>

---
### Creating a quota policy tree rule using POST
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule()
    resource.svm = {"name": "svm1"}
    resource.volume = {"name": "vol1"}
    resource.type = "tree"
    resource.qtree = {"name": "qt1"}
    resource.space = {"hard_limit": 8192, "soft_limit": 1024}
    resource.files = {"hard_limit": 20, "soft_limit": 10}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example8_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example8_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example8_result" class="try_it_out_content">
```
QuotaRule(
    {
        "type": "tree",
        "files": {"soft_limit": 10, "hard_limit": 20},
        "svm": {"name": "svm1"},
        "uuid": "e5eb03be-504a-11e9-bfb7-005056a7f717",
        "qtree": {"name": "qt1"},
        "volume": {"name": "fv"},
        "space": {"soft_limit": 1024, "hard_limit": 8192},
        "_links": {
            "self": {
                "href": "/api/storage/quota/rules/e5eb03be-504a-11e9-bfb7-005056a7f717"
            }
        },
    }
)

```
</div>
</div>

---
### Updating the quota policy rule
This API is used to update a quota policy rule.<br/>
The following example shows how to update a quota policy rule.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="364d38eb-8e87-11e8-a806-005056a7e73a")
    resource.space = {"hard_limit": 16554, "soft_limit": 8192}
    resource.files = {"hard_limit": 40, "soft_limit": 20}
    resource.patch()

```

---
### Deleting the quota policy rule
This API is used to delete a quota policy rule.<br/>
The following example shows how to delete a quota policy rule.
<br/>
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import QuotaRule

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = QuotaRule(uuid="364d38eb-8e87-11e8-a806-005056a7e73a")
    resource.delete()

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


__all__ = ["QuotaRule", "QuotaRuleSchema"]
__pdoc__ = {
    "QuotaRuleSchema.resource": False,
    "QuotaRule.quota_rule_show": False,
    "QuotaRule.quota_rule_create": False,
    "QuotaRule.quota_rule_modify": False,
    "QuotaRule.quota_rule_delete": False,
}


class QuotaRuleSchema(ResourceSchema):
    """The fields of the QuotaRule object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the quota_rule. """

    files = fields.Nested("netapp_ontap.models.quota_rule_files.QuotaRuleFilesSchema", data_key="files", unknown=EXCLUDE)
    r""" The files field of the quota_rule. """

    group = fields.Nested("netapp_ontap.models.quota_rule_group.QuotaRuleGroupSchema", data_key="group", unknown=EXCLUDE)
    r""" The group field of the quota_rule. """

    qtree = fields.Nested("netapp_ontap.models.quota_rule_qtree.QuotaRuleQtreeSchema", data_key="qtree", unknown=EXCLUDE)
    r""" The qtree field of the quota_rule. """

    space = fields.Nested("netapp_ontap.models.quota_rule_space.QuotaRuleSpaceSchema", data_key="space", unknown=EXCLUDE)
    r""" The space field of the quota_rule. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the quota_rule. """

    type = fields.Str(
        data_key="type",
        validate=enum_validation(['tree', 'user', 'group']),
    )
    r""" This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \"user\", \"group\" or \"tree\" values.

Valid choices:

* tree
* user
* group """

    user_mapping = fields.Boolean(
        data_key="user_mapping",
    )
    r""" This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only. """

    users = fields.List(fields.Nested("netapp_ontap.models.quota_rule_users.QuotaRuleUsersSchema", unknown=EXCLUDE), data_key="users")
    r""" This parameter specifies the target user to which the user quota policy rule applies. This parameter takes single or multiple user names or identifiers. This parameter is valid only for the POST operation of a user quota policy rule. If this parameter is used as an input to create a group or a tree quota policy rule, the POST operation will fail with an appropriate error. For POST, this input parameter takes either a user name or a user identifier, not both. For default quota rules, the user name must be chosen and specified as "". For explicit user quota rules, this parameter can indicate either a user name or user identifier. The user name can be a UNIX user name or a Windows user name. If a name contains a space, enclose the entire value in quotes. A UNIX user name cannot include a backslash (\) or an @ sign; user names with these characters are treated as Windows names. The user identifer can be a UNIX user identifier or a Windows security identifier. For multi-user quota, this parameter can contain multiple user targets separated by a comma. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.

Example: 5f1d13a7-f401-11e8-ac1a-005056a7c3b9 """

    volume = fields.Nested("netapp_ontap.resources.volume.VolumeSchema", data_key="volume", unknown=EXCLUDE)
    r""" The volume field of the quota_rule. """

    @property
    def resource(self):
        return QuotaRule

    gettable_fields = [
        "links",
        "files",
        "group",
        "qtree.links",
        "qtree.id",
        "qtree.name",
        "space",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "type",
        "user_mapping",
        "users",
        "uuid",
        "volume.links",
        "volume.name",
        "volume.uuid",
    ]
    """links,files,group,qtree.links,qtree.id,qtree.name,space,svm.links,svm.name,svm.uuid,type,user_mapping,users,uuid,volume.links,volume.name,volume.uuid,"""

    patchable_fields = [
        "files",
        "space",
        "user_mapping",
    ]
    """files,space,user_mapping,"""

    postable_fields = [
        "files",
        "group",
        "qtree.name",
        "space",
        "svm.name",
        "svm.uuid",
        "type",
        "user_mapping",
        "users",
        "volume.name",
        "volume.uuid",
    ]
    """files,group,qtree.name,space,svm.name,svm.uuid,type,user_mapping,users,volume.name,volume.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in QuotaRule.get_collection(fields=field)]
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
            raise NetAppRestError("QuotaRule modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class QuotaRule(Resource):
    """Allows interaction with QuotaRule objects on the host"""

    _schema = QuotaRuleSchema
    _path = "/api/storage/quota/rules"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves quota policy rules configured for all FlexVol volumes and FlexGroup volumes.
### Related ONTAP commands
* `quota policy rule show`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="quota rule show")
        def quota_rule_show(
            fields: List[Choices.define(["type", "user_mapping", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of QuotaRule resources

            Args:
                type: This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \\\"user\\\", \\\"group\\\" or \\\"tree\\\" values.
                user_mapping: This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only.
                uuid: Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.
            """

            kwargs = {}
            if type is not None:
                kwargs["type"] = type
            if user_mapping is not None:
                kwargs["user_mapping"] = user_mapping
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return QuotaRule.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all QuotaRule resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["QuotaRule"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates properties of a specific quota policy rule. <br>
Important notes:
* The quota resize functionality is supported with the PATCH operation.
* Quota resize allows you to modify the quota limits, directly in the filesystem.
* The quota must be enabled on a FlexVol or a FlexGroup volume for `quota resize` to take effect.
* If the quota is disabled on the volume, the quota policy rule PATCH API modifies the rule, but this does not affect the limits in the filesystem.
### Related ONTAP commands
* `quota policy rule modify`
* `quota resize`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["QuotaRule"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["QuotaRule"], NetAppResponse]:
        r"""Creates a quota policy rule for a FlexVol or a FlexGroup volume.<br/>
Important notes:
* Unlike CLI/ONTAPI, the `quota policy` input is not needed for POST.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the qtree.
* `volume.uuid` or `volume.name` - Existing volume in which to create the qtree.
* `type` - Quota type for the rule. This type can be `user`, `group`, or `tree`.
* `users.name` or `user.id` -  If the quota type is user, this property takes the user name or user ID. For default user quota rules, the user name must be specified as "".
* `group.name` or `group.id` - If the quota type is group, this property takes the group name or group ID. For default group quota rules, the group name must be specified as "".
* `qtree.name` - Qtree for which to create the rule. For default tree rules, the qtree name must be specified as "".
### Recommended optional properties
* `space.hard_limit` - Specifies the space hard limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes.
* `space.soft_limit` - Specifies the space soft limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes.
* `files.hard_limit` - Specifies the hard limit for files.
* `files.soft_limit` - Specifies the soft limit for files.
* `user_mapping` - Specifies the user_mapping. This property is valid only for quota policy rules of type `user`.
### Related ONTAP commands
* `quota policy rule create`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["QuotaRule"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a quota policy rule.
### Related ONTAP commands
* `quota policy rule delete`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves quota policy rules configured for all FlexVol volumes and FlexGroup volumes.
### Related ONTAP commands
* `quota policy rule show`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves properties for a specific quota policy rule.
### Related ONTAP commands
* `quota policy rule show`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
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
        r"""Creates a quota policy rule for a FlexVol or a FlexGroup volume.<br/>
Important notes:
* Unlike CLI/ONTAPI, the `quota policy` input is not needed for POST.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the qtree.
* `volume.uuid` or `volume.name` - Existing volume in which to create the qtree.
* `type` - Quota type for the rule. This type can be `user`, `group`, or `tree`.
* `users.name` or `user.id` -  If the quota type is user, this property takes the user name or user ID. For default user quota rules, the user name must be specified as "".
* `group.name` or `group.id` - If the quota type is group, this property takes the group name or group ID. For default group quota rules, the group name must be specified as "".
* `qtree.name` - Qtree for which to create the rule. For default tree rules, the qtree name must be specified as "".
### Recommended optional properties
* `space.hard_limit` - Specifies the space hard limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes.
* `space.soft_limit` - Specifies the space soft limit, in bytes. If less than 1024 bytes, the value is rounded up to 1024 bytes.
* `files.hard_limit` - Specifies the hard limit for files.
* `files.soft_limit` - Specifies the soft limit for files.
* `user_mapping` - Specifies the user_mapping. This property is valid only for quota policy rules of type `user`.
### Related ONTAP commands
* `quota policy rule create`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="quota rule create")
        async def quota_rule_create(
        ) -> ResourceTable:
            """Create an instance of a QuotaRule resource

            Args:
                links: 
                files: 
                group: 
                qtree: 
                space: 
                svm: 
                type: This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \\\"user\\\", \\\"group\\\" or \\\"tree\\\" values.
                user_mapping: This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only.
                users: This parameter specifies the target user to which the user quota policy rule applies. This parameter takes single or multiple user names or identifiers. This parameter is valid only for the POST operation of a user quota policy rule. If this parameter is used as an input to create a group or a tree quota policy rule, the POST operation will fail with an appropriate error. For POST, this input parameter takes either a user name or a user identifier, not both. For default quota rules, the user name must be chosen and specified as \"\". For explicit user quota rules, this parameter can indicate either a user name or user identifier. The user name can be a UNIX user name or a Windows user name. If a name contains a space, enclose the entire value in quotes. A UNIX user name cannot include a backslash (\\) or an @ sign; user names with these characters are treated as Windows names. The user identifer can be a UNIX user identifier or a Windows security identifier. For multi-user quota, this parameter can contain multiple user targets separated by a comma.
                uuid: Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.
                volume: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if files is not None:
                kwargs["files"] = files
            if group is not None:
                kwargs["group"] = group
            if qtree is not None:
                kwargs["qtree"] = qtree
            if space is not None:
                kwargs["space"] = space
            if svm is not None:
                kwargs["svm"] = svm
            if type is not None:
                kwargs["type"] = type
            if user_mapping is not None:
                kwargs["user_mapping"] = user_mapping
            if users is not None:
                kwargs["users"] = users
            if uuid is not None:
                kwargs["uuid"] = uuid
            if volume is not None:
                kwargs["volume"] = volume

            resource = QuotaRule(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create QuotaRule: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates properties of a specific quota policy rule. <br>
Important notes:
* The quota resize functionality is supported with the PATCH operation.
* Quota resize allows you to modify the quota limits, directly in the filesystem.
* The quota must be enabled on a FlexVol or a FlexGroup volume for `quota resize` to take effect.
* If the quota is disabled on the volume, the quota policy rule PATCH API modifies the rule, but this does not affect the limits in the filesystem.
### Related ONTAP commands
* `quota policy rule modify`
* `quota resize`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="quota rule modify")
        async def quota_rule_modify(
        ) -> ResourceTable:
            """Modify an instance of a QuotaRule resource

            Args:
                type: This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \\\"user\\\", \\\"group\\\" or \\\"tree\\\" values.
                query_type: This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \\\"user\\\", \\\"group\\\" or \\\"tree\\\" values.
                user_mapping: This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only.
                query_user_mapping: This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only.
                uuid: Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.
                query_uuid: Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.
            """

            kwargs = {}
            changes = {}
            if query_type is not None:
                kwargs["type"] = query_type
            if query_user_mapping is not None:
                kwargs["user_mapping"] = query_user_mapping
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if type is not None:
                changes["type"] = type
            if user_mapping is not None:
                changes["user_mapping"] = user_mapping
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(QuotaRule, "find"):
                resource = QuotaRule.find(
                    **kwargs
                )
            else:
                resource = QuotaRule()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify QuotaRule: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a quota policy rule.
### Related ONTAP commands
* `quota policy rule delete`

### Learn more
* [`DOC /storage/quota/rules`](#docs-storage-storage_quota_rules)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="quota rule delete")
        async def quota_rule_delete(
        ) -> None:
            """Delete an instance of a QuotaRule resource

            Args:
                type: This parameter specifies the quota policy rule type. This is required in POST only and can take either one of the \\\"user\\\", \\\"group\\\" or \\\"tree\\\" values.
                user_mapping: This parameter enables user mapping for user quota policy rules. This is valid in POST or PATCH for user quota policy rules only.
                uuid: Unique identifier for the quota policy rule. This field is generated when the quota policy rule is created.
            """

            kwargs = {}
            if type is not None:
                kwargs["type"] = type
            if user_mapping is not None:
                kwargs["user_mapping"] = user_mapping
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(QuotaRule, "find"):
                resource = QuotaRule.find(
                    **kwargs
                )
            else:
                resource = QuotaRule()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete QuotaRule: %s" % err)


