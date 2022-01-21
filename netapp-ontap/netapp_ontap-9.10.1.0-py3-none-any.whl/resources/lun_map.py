r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A LUN map is an association between a LUN and an initiator group. When a LUN is mapped to an initiator group, the initiator group's initiators are granted access to the LUN. The relationship between an initiator group and a LUN is many initiator groups to many LUNs.<br/>
A LUN map also configures the cluster nodes from which network paths to the LUN are advertised via the SAN protocols as part of the Selective LUN Map (SLM) functionality of ONTAP. These nodes are referred to as the reporting nodes of a LUN map. For further information, see [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes).<br/>
The LUN map REST API allows you to create, delete, and discover LUN maps, and manage the reporting nodes of a LUN map.
## Examples
### Creating a LUN map
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunMap()
    resource.svm = {"name": "svm1"}
    resource.igroup = {"name": "igroup1"}
    resource.lun = {"name": "/vol/vol1/lun1"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all of the LUN maps
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LunMap.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    LunMap(
        {
            "lun": {
                "name": "/vol/vol1/lun1",
                "uuid": "a60d9862-9bee-49a6-8162-20d2421bb1a6",
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/a60d9862-9bee-49a6-8162-20d2421bb1a6"
                    }
                },
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/03157e81-24c5-11e9-9ec1-005056bba643"
                    }
                },
                "uuid": "03157e81-24c5-11e9-9ec1-005056bba643",
                "name": "svm1",
            },
            "igroup": {
                "uuid": "40d98b2c-24c5-11e9-9ec1-005056bba643",
                "name": "ig1",
                "_links": {
                    "self": {
                        "href": "/api/protocols/san/igroups/40d98b2c-24c5-11e9-9ec1-005056bba643"
                    }
                },
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/lun-maps/a60d9862-9bee-49a6-8162-20d2421bb1a6/40d98b2c-24c5-11e9-9ec1-005056bba643"
                }
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific LUN map
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunMap(
        **{
            "igroup.uuid": "40d98b2c-24c5-11e9-9ec1-005056bba643",
            "lun.uuid": "a60d9862-9bee-49a6-8162-20d2421bb1a6",
        }
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
LunMap(
    {
        "lun": {
            "node": {
                "name": "node1",
                "uuid": "7d8607ea-24c1-11e9-9ec1-005056bba643",
                "_links": {
                    "self": {
                        "href": "/api/cluster/nodes/7d8607ea-24c1-11e9-9ec1-005056bba643"
                    }
                },
            },
            "name": "/vol/vol1/lun1",
            "uuid": "a60d9862-9bee-49a6-8162-20d2421bb1a6",
            "_links": {
                "self": {
                    "href": "/api/storage/luns/a60d9862-9bee-49a6-8162-20d2421bb1a6"
                }
            },
        },
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/03157e81-24c5-11e9-9ec1-005056bba643"}
            },
            "uuid": "03157e81-24c5-11e9-9ec1-005056bba643",
            "name": "svm1",
        },
        "igroup": {
            "os_type": "linux",
            "uuid": "40d98b2c-24c5-11e9-9ec1-005056bba643",
            "protocol": "mixed",
            "name": "ig1",
            "_links": {
                "self": {
                    "href": "/api/protocols/san/igroups/40d98b2c-24c5-11e9-9ec1-005056bba643"
                }
            },
        },
        "reporting_nodes": [
            {
                "uuid": "11a465f5-2ac0-11eb-a303-005056bb1e81",
                "name": "node1",
                "_links": {
                    "node": {
                        "href": "/cluster/nodes/11a465f5-2ac0-11eb-a303-005056bb1e81"
                    },
                    "self": {
                        "href": "/api/protocols/san/lun-maps/a60d9862-9bee-49a6-8162-20d2421bb1a6/40d98b2c-24c5-11e9-9ec1-005056bba643/reporting-nodes/11a465f5-2ac0-11eb-a303-005056bb1e81"
                    },
                },
            },
            {
                "uuid": "6c7cb50f-2abf-11eb-9840-005056bbd490",
                "name": "node2",
                "_links": {
                    "node": {
                        "href": "/cluster/nodes/6c7cb50f-2abf-11eb-9840-005056bbd490"
                    },
                    "self": {
                        "href": "/api/protocols/san/lun-maps/a60d9862-9bee-49a6-8162-20d2421bb1a6/40d98b2c-24c5-11e9-9ec1-005056bba643/reporting-nodes/6c7cb50f-2abf-11eb-9840-005056bbd490"
                    },
                },
            },
        ],
        "logical_unit_number": 0,
        "_links": {
            "self": {
                "href": "/api/protocols/san/lun-maps/a60d9862-9bee-49a6-8162-20d2421bb1a6/40d98b2c-24c5-11e9-9ec1-005056bba643"
            }
        },
    }
)

```
</div>
</div>

---
### Deleting a LUN map
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunMap

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunMap(
        **{
            "igroup.uuid": "40d98b2c-24c5-11e9-9ec1-005056bba643",
            "lun.uuid": "a60d9862-9bee-49a6-8162-20d2421bb1a6",
        }
    )
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


__all__ = ["LunMap", "LunMapSchema"]
__pdoc__ = {
    "LunMapSchema.resource": False,
    "LunMap.lun_map_show": False,
    "LunMap.lun_map_create": False,
    "LunMap.lun_map_modify": False,
    "LunMap.lun_map_delete": False,
}


class LunMapSchema(ResourceSchema):
    """The fields of the LunMap object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the lun_map. """

    igroup = fields.Nested("netapp_ontap.models.lun_map_igroup.LunMapIgroupSchema", data_key="igroup", unknown=EXCLUDE)
    r""" The igroup field of the lun_map. """

    logical_unit_number = Size(
        data_key="logical_unit_number",
        validate=integer_validation(minimum=0, maximum=4095),
    )
    r""" The logical unit number assigned to the LUN when mapped to the specified initiator group. The number is used to identify the LUN to initiators in the initiator group when communicating through Fibre Channel Protocol or iSCSI. Optional in POST; if no value is provided, ONTAP assigns the lowest available value.


Example: 1 """

    lun = fields.Nested("netapp_ontap.models.lun_map_lun.LunMapLunSchema", data_key="lun", unknown=EXCLUDE)
    r""" The lun field of the lun_map. """

    reporting_nodes = fields.List(fields.Nested("netapp_ontap.resources.lun_map_reporting_node.LunMapReportingNodeSchema", unknown=EXCLUDE), data_key="reporting_nodes")
    r""" The cluster nodes from which network paths to the mapped LUNs are advertised via the SAN protocols as part of the Selective LUN Map (SLM) feature of ONTAP.<br/>
When a LUN map is created, the cluster node hosting the LUN and its high availability (HA) partner are set as the default reporting node. In POST, the property `additional_reporting_node` may be used to add an additional node and its HA partner.<br/>
For further information, see [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes). """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the lun_map. """

    @property
    def resource(self):
        return LunMap

    gettable_fields = [
        "links",
        "igroup",
        "logical_unit_number",
        "lun",
        "reporting_nodes.links",
        "reporting_nodes.name",
        "reporting_nodes.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,igroup,logical_unit_number,lun,reporting_nodes.links,reporting_nodes.name,reporting_nodes.uuid,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "igroup",
        "lun",
        "svm.name",
        "svm.uuid",
    ]
    """igroup,lun,svm.name,svm.uuid,"""

    postable_fields = [
        "igroup",
        "logical_unit_number",
        "lun",
        "svm.name",
        "svm.uuid",
    ]
    """igroup,logical_unit_number,lun,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LunMap.get_collection(fields=field)]
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
            raise NetAppRestError("LunMap modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LunMap(Resource):
    r""" A LUN map is an association between a LUN and an initiator group. When a LUN is mapped to an initiator group, the initiator group's initiators are granted access to the LUN. The relationship between a LUN and an initiator group is many LUNs to many initiator groups. """

    _schema = LunMapSchema
    _path = "/api/protocols/san/lun-maps"
    _keys = ["lun.uuid", "igroup.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves LUN maps.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map show")
        def lun_map_show(
            fields: List[Choices.define(["logical_unit_number", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LunMap resources

            Args:
                logical_unit_number: The logical unit number assigned to the LUN when mapped to the specified initiator group. The number is used to identify the LUN to initiators in the initiator group when communicating through Fibre Channel Protocol or iSCSI. Optional in POST; if no value is provided, ONTAP assigns the lowest available value. 
            """

            kwargs = {}
            if logical_unit_number is not None:
                kwargs["logical_unit_number"] = logical_unit_number
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LunMap.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LunMap resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["LunMap"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LunMap"], NetAppResponse]:
        r"""Creates a LUN map.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the LUN map.
* `igroup.uuid` or `igroup.name` - Existing initiator group to map to the specified LUN.
* `lun.uuid` or `lun.name` - Existing LUN to map to the specified initiator group.
### Default property values
If not specified in POST, the following default property values are assigned.
* `logical_unit_number` - If no value is provided, ONTAP assigns the lowest available value.
### Related ONTAP commands
* `lun mapping create`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
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
        records: Iterable["LunMap"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a LUN map.
### Related ONTAP commands
* `lun mapping delete`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves LUN maps.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a LUN map.
### Related ONTAP commands
* `lun mapping show`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
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
        r"""Creates a LUN map.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the LUN map.
* `igroup.uuid` or `igroup.name` - Existing initiator group to map to the specified LUN.
* `lun.uuid` or `lun.name` - Existing LUN to map to the specified initiator group.
### Default property values
If not specified in POST, the following default property values are assigned.
* `logical_unit_number` - If no value is provided, ONTAP assigns the lowest available value.
### Related ONTAP commands
* `lun mapping create`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map create")
        async def lun_map_create(
        ) -> ResourceTable:
            """Create an instance of a LunMap resource

            Args:
                links: 
                igroup: 
                logical_unit_number: The logical unit number assigned to the LUN when mapped to the specified initiator group. The number is used to identify the LUN to initiators in the initiator group when communicating through Fibre Channel Protocol or iSCSI. Optional in POST; if no value is provided, ONTAP assigns the lowest available value. 
                lun: 
                reporting_nodes: The cluster nodes from which network paths to the mapped LUNs are advertised via the SAN protocols as part of the Selective LUN Map (SLM) feature of ONTAP.<br/> When a LUN map is created, the cluster node hosting the LUN and its high availability (HA) partner are set as the default reporting node. In POST, the property `additional_reporting_node` may be used to add an additional node and its HA partner.<br/> For further information, see [`DOC /protocols/san/lun-maps/{lun.uuid}/{igroup.uuid}/reporting-nodes`](#docs-SAN-protocols_san_lun-maps_{lun.uuid}_{igroup.uuid}_reporting-nodes). 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if igroup is not None:
                kwargs["igroup"] = igroup
            if logical_unit_number is not None:
                kwargs["logical_unit_number"] = logical_unit_number
            if lun is not None:
                kwargs["lun"] = lun
            if reporting_nodes is not None:
                kwargs["reporting_nodes"] = reporting_nodes
            if svm is not None:
                kwargs["svm"] = svm

            resource = LunMap(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LunMap: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a LUN map.
### Related ONTAP commands
* `lun mapping delete`
### Learn more
* [`DOC /protocols/san/lun-maps`](#docs-SAN-protocols_san_lun-maps)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun map delete")
        async def lun_map_delete(
        ) -> None:
            """Delete an instance of a LunMap resource

            Args:
                logical_unit_number: The logical unit number assigned to the LUN when mapped to the specified initiator group. The number is used to identify the LUN to initiators in the initiator group when communicating through Fibre Channel Protocol or iSCSI. Optional in POST; if no value is provided, ONTAP assigns the lowest available value. 
            """

            kwargs = {}
            if logical_unit_number is not None:
                kwargs["logical_unit_number"] = logical_unit_number

            if hasattr(LunMap, "find"):
                resource = LunMap.find(
                    **kwargs
                )
            else:
                resource = LunMap()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LunMap: %s" % err)


