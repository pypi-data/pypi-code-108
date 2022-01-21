r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A VMware virtual volume (vVol) binding is an association between a LUN of class `protocol_endpoint` and a LUN of class `vvol`. Class `protocol_endpoint` LUNs are mapped to igroups and granted access using the same configuration as class `regular` LUNs. When a class `vvol` LUN is bound to a mapped class `protocol_endpoint` LUN, VMware can access the class `vvol` LUN through the class `protocol_endpoint` LUN mapping.</br>
Class `protocol_endpoint` and `vvol` LUNs support many-to-many vVol bindings. A LUN of one class can be bound to zero or more LUNs of the opposite class.</br>
The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed.</br>
The vVol binding REST API allows you to create, delete, and discover vVol bindings.
## Examples
### Creating a vVol binding
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VvolBinding

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VvolBinding()
    resource.svm = {"name": "svm1"}
    resource.protocol_endpoint = {"name": "/vol/vol1/pe1"}
    resource.vvol = {"name": "/vol/vol1/vvol1"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Retrieving all vVol bindings
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VvolBinding

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(VvolBinding.get_collection()))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    VvolBinding(
        {
            "vvol": {
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/28c02623-42fa-4f5f-a984-a02044bfc005"
                    }
                },
                "uuid": "28c02623-42fa-4f5f-a984-a02044bfc005",
                "name": "/vol/vol1/vvol1",
            },
            "protocol_endpoint": {
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4"
                    }
                },
                "uuid": "2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4",
                "name": "/vol/vol1/pe1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/vvol-bindings/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4/28c02623-42fa-4f5f-a984-a02044bfc005"
                }
            },
        }
    ),
    VvolBinding(
        {
            "vvol": {
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/a8d4ba93-918f-40ad-a1e4-4d7b244bdcdf"
                    }
                },
                "uuid": "a8d4ba93-918f-40ad-a1e4-4d7b244bdcdf",
                "name": "/vol/vol1/vvol2",
            },
            "protocol_endpoint": {
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4"
                    }
                },
                "uuid": "2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4",
                "name": "/vol/vol1/pe1",
            },
            "_links": {
                "self": {
                    "href": "/api/protocols/san/vvol-bindings/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4/a8d4ba93-918f-40ad-a1e4-4d7b244bdcdf"
                }
            },
        }
    ),
]

```
</div>
</div>

---
### Retrieving a specific vVol binding
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VvolBinding

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VvolBinding(
        **{
            "vvol.uuid": "28c02623-42fa-4f5f-a984-a02044bfc005",
            "protocol_endpoint.uuid": "2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4",
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
VvolBinding(
    {
        "vvol": {
            "_links": {
                "self": {
                    "href": "/api/storage/luns/28c02623-42fa-4f5f-a984-a02044bfc005"
                }
            },
            "uuid": "28c02623-42fa-4f5f-a984-a02044bfc005",
            "name": "/vol/vol1/vvol1",
        },
        "protocol_endpoint": {
            "_links": {
                "self": {
                    "href": "/api/storage/luns/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4"
                }
            },
            "uuid": "2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4",
            "name": "/vol/vol1/pe1",
        },
        "id": 2411392,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/bf295ccc-a6bb-11eb-93e8-005056bb470f"}
            },
            "uuid": "bf295ccc-a6bb-11eb-93e8-005056bb470f",
            "name": "svm1",
        },
        "count": 1,
        "_links": {
            "self": {
                "href": "/api/protocols/san/vvol-bindings/2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4/28c02623-42fa-4f5f-a984-a02044bfc005"
            }
        },
        "is_optimal": True,
    }
)

```
</div>
</div>

---
### Deleting a vVol binding
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import VvolBinding

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = VvolBinding(
        **{
            "vvol.uuid": "28c02623-42fa-4f5f-a984-a02044bfc005",
            "protocol_endpoint.uuid": "2aab57f3-dc5d-491e-80d2-15c7ed5dd5c4",
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


__all__ = ["VvolBinding", "VvolBindingSchema"]
__pdoc__ = {
    "VvolBindingSchema.resource": False,
    "VvolBinding.vvol_binding_show": False,
    "VvolBinding.vvol_binding_create": False,
    "VvolBinding.vvol_binding_modify": False,
    "VvolBinding.vvol_binding_delete": False,
}


class VvolBindingSchema(ResourceSchema):
    """The fields of the VvolBinding object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the vvol_binding. """

    count = Size(
        data_key="count",
    )
    r""" The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed.


Example: 1 """

    id = Size(
        data_key="id",
    )
    r""" The identifier assigned to the vVol binding. The bind identifier is unique amongst all class `vvol` LUNs bound to the same class `protocol_endpoint` LUN.


Example: 1 """

    is_optimal = fields.Boolean(
        data_key="is_optimal",
    )
    r""" Indicates if the class `procotol_endpoint` LUN and the class `vvol` LUN are on the same cluster node.


Example: true """

    protocol_endpoint = fields.Nested("netapp_ontap.resources.lun.LunSchema", data_key="protocol_endpoint", unknown=EXCLUDE)
    r""" The protocol_endpoint field of the vvol_binding. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the vvol_binding. """

    vvol = fields.Nested("netapp_ontap.resources.lun.LunSchema", data_key="vvol", unknown=EXCLUDE)
    r""" The vvol field of the vvol_binding. """

    @property
    def resource(self):
        return VvolBinding

    gettable_fields = [
        "links",
        "count",
        "id",
        "is_optimal",
        "protocol_endpoint.links",
        "protocol_endpoint.name",
        "protocol_endpoint.uuid",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "vvol.links",
        "vvol.name",
        "vvol.uuid",
    ]
    """links,count,id,is_optimal,protocol_endpoint.links,protocol_endpoint.name,protocol_endpoint.uuid,svm.links,svm.name,svm.uuid,vvol.links,vvol.name,vvol.uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "protocol_endpoint.name",
        "protocol_endpoint.uuid",
        "svm.name",
        "svm.uuid",
        "vvol.name",
        "vvol.uuid",
    ]
    """protocol_endpoint.name,protocol_endpoint.uuid,svm.name,svm.uuid,vvol.name,vvol.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in VvolBinding.get_collection(fields=field)]
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
            raise NetAppRestError("VvolBinding modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class VvolBinding(Resource):
    r""" A VMware virtual volume (vVol) binding is an association between a LUN of class `protocol_endpoint` and a LUN of class `vvol`. Class `protocol_endpoint` LUNs are mapped to igroups and granted access using the same configuration as class `regular` LUNs. When a class `vvol` LUN is bound to a mapped class `protocol_endpoint` LUN, VMware can access the class `vvol` LUN through the class `protocol_endpoint` LUN mapping.</br>
Class `protocol_endpoint` and `vvol` LUNs support many-to-many vVol bindings. A LUN of one class can be bound to zero or more LUNs of the opposite class.</br>
The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed. """

    _schema = VvolBindingSchema
    _path = "/api/protocols/san/vvol-bindings"
    _keys = ["protocol_endpoint.uuid", "vvol.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves vVol bindings.
### Related ONTAP commands
* `lun bind show`
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)

### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vvol binding show")
        def vvol_binding_show(
            fields: List[Choices.define(["count", "id", "is_optimal", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of VvolBinding resources

            Args:
                count: The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed. 
                id: The identifier assigned to the vVol binding. The bind identifier is unique amongst all class `vvol` LUNs bound to the same class `protocol_endpoint` LUN. 
                is_optimal: Indicates if the class `procotol_endpoint` LUN and the class `vvol` LUN are on the same cluster node. 
            """

            kwargs = {}
            if count is not None:
                kwargs["count"] = count
            if id is not None:
                kwargs["id"] = id
            if is_optimal is not None:
                kwargs["is_optimal"] = is_optimal
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return VvolBinding.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all VvolBinding resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["VvolBinding"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["VvolBinding"], NetAppResponse]:
        r"""Creates a vVol binding. The binding between any two specific LUNs is reference counted. When a binding is created that already exists, the binding count is incremented.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the vVol binding.
* `protocol_endpoint.uuid` or `protocol_endpoint.name` - Existing class `protocol_endpoint` LUN to bind to the specified class `vvol` LUN.
* `vvol.uuid` or `vvol.name` - Existing class `vvol` LUN to bind to the specified class `protocol_endpoint` LUN.
### Related ONTAP commands
* `lun bind create`
### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)
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
        records: Iterable["VvolBinding"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a vVol binding. The binding between any two specific LUNs is reference counted. When a binding is deleted, the binding count is decremented, but the LUNs remain bound if the resultant reference count is greater than zero. When the binding count reaches zero, the binding is destroyed.
### Related ONTAP commands
* `lun bind destroy`
### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves vVol bindings.
### Related ONTAP commands
* `lun bind show`
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)

### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a vVol binding.
### Related ONTAP commands
* `lun bind show`
### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)
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
        r"""Creates a vVol binding. The binding between any two specific LUNs is reference counted. When a binding is created that already exists, the binding count is incremented.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the vVol binding.
* `protocol_endpoint.uuid` or `protocol_endpoint.name` - Existing class `protocol_endpoint` LUN to bind to the specified class `vvol` LUN.
* `vvol.uuid` or `vvol.name` - Existing class `vvol` LUN to bind to the specified class `protocol_endpoint` LUN.
### Related ONTAP commands
* `lun bind create`
### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vvol binding create")
        async def vvol_binding_create(
        ) -> ResourceTable:
            """Create an instance of a VvolBinding resource

            Args:
                links: 
                count: The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed. 
                id: The identifier assigned to the vVol binding. The bind identifier is unique amongst all class `vvol` LUNs bound to the same class `protocol_endpoint` LUN. 
                is_optimal: Indicates if the class `procotol_endpoint` LUN and the class `vvol` LUN are on the same cluster node. 
                protocol_endpoint: 
                svm: 
                vvol: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if count is not None:
                kwargs["count"] = count
            if id is not None:
                kwargs["id"] = id
            if is_optimal is not None:
                kwargs["is_optimal"] = is_optimal
            if protocol_endpoint is not None:
                kwargs["protocol_endpoint"] = protocol_endpoint
            if svm is not None:
                kwargs["svm"] = svm
            if vvol is not None:
                kwargs["vvol"] = vvol

            resource = VvolBinding(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create VvolBinding: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a vVol binding. The binding between any two specific LUNs is reference counted. When a binding is deleted, the binding count is decremented, but the LUNs remain bound if the resultant reference count is greater than zero. When the binding count reaches zero, the binding is destroyed.
### Related ONTAP commands
* `lun bind destroy`
### Learn more
* [`DOC /protocols/san/vvol-bindings`](#docs-SAN-protocols_san_vvol-bindings)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="vvol binding delete")
        async def vvol_binding_delete(
        ) -> None:
            """Delete an instance of a VvolBinding resource

            Args:
                count: The vVol binding between any two specific LUNs is reference counted. When a REST POST is executed for a vVol binding that already exists, the vVol binding reference count is incremented. When a REST DELETE is executed, the vVol binding reference count is decremented. Only when the vVol binding count reaches zero, or the query parameter `delete_all_references` is supplied, is the vVol binding destroyed. 
                id: The identifier assigned to the vVol binding. The bind identifier is unique amongst all class `vvol` LUNs bound to the same class `protocol_endpoint` LUN. 
                is_optimal: Indicates if the class `procotol_endpoint` LUN and the class `vvol` LUN are on the same cluster node. 
            """

            kwargs = {}
            if count is not None:
                kwargs["count"] = count
            if id is not None:
                kwargs["id"] = id
            if is_optimal is not None:
                kwargs["is_optimal"] = is_optimal

            if hasattr(VvolBinding, "find"):
                resource = VvolBinding.find(
                    **kwargs
                )
            else:
                resource = VvolBinding()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete VvolBinding: %s" % err)


