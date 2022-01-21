r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
LUN attributes are caller-defined name/value pairs optionally stored with a LUN. Attributes are available to persist small amounts of application-specific metadata. They are in no way interpreted by ONTAP.<br/>
Attribute names and values must be at least one byte and no more than 4091 bytes in length. The sum of the name and value lengths must be no more than 4092 bytes.<br/>
The LUN attributes REST API allows you to create, update, delete, and discover attributes for a LUN. The LUN REST API also allows you to set attributes when a LUN is first created.<br/>
## Examples
### Retrieving all attributes from a LUN
This example uses the LUN attribute REST endpoint with the `fields` query parameter to request the names and values.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunAttribute

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            LunAttribute.get_collection(
                "4bc204df-ecd8-4f35-8207-d0ccb4db3a90", fields="*"
            )
        )
    )

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LunAttribute(
        {
            "value": "value1",
            "name": "name1",
            "_links": {
                "self": {
                    "href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90/attributes/name1"
                }
            },
        }
    ),
    LunAttribute(
        {
            "value": "value2",
            "name": "name2",
            "_links": {
                "self": {
                    "href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90/attributes/name2"
                }
            },
        }
    ),
]

```
</div>
</div>

This example uses the LUN REST endpoint with the `fields` query parameter to request the attributes properties.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import Lun

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = Lun(uuid="4bc204df-ecd8-4f35-8207-d0ccb4db3a90")
    resource.get(fields="attributes")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
Lun(
    {
        "_links": {
            "self": {"href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90"}
        },
        "uuid": "4bc204df-ecd8-4f35-8207-d0ccb4db3a90",
        "attributes": [
            {
                "value": "name1",
                "name": "name1",
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90/attributes/name1"
                    }
                },
            },
            {
                "value": "value2",
                "name": "name2",
                "_links": {
                    "self": {
                        "href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90/attributes/name2"
                    }
                },
            },
        ],
        "name": "/vol/vol1/lun1",
    }
)

```
</div>
</div>

---
### Adding an attribute to a LUN
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunAttribute

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunAttribute("4bc204df-ecd8-4f35-8207-d0ccb4db3a90")
    resource.name = "name1"
    resource.value = "value1"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
LunAttribute(
    {
        "value": "value1",
        "name": "name1",
        "_links": {
            "self": {
                "href": "/api/storage/luns/4bc204df-ecd8-4f35-8207-d0ccb4db3a90/attributes/name1"
            }
        },
    }
)

```
</div>
</div>

---
### Modifying an attribute value for a LUN
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunAttribute

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunAttribute("4bc204df-ecd8-4f35-8207-d0ccb4db3a90", name="name1")
    resource.value = "newValue"
    resource.patch()

```

---
### Deleting an attribute from a LUN
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LunAttribute

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LunAttribute("4bc204df-ecd8-4f35-8207-d0ccb4db3a90", name="name1")
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


__all__ = ["LunAttribute", "LunAttributeSchema"]
__pdoc__ = {
    "LunAttributeSchema.resource": False,
    "LunAttribute.lun_attribute_show": False,
    "LunAttribute.lun_attribute_create": False,
    "LunAttribute.lun_attribute_modify": False,
    "LunAttribute.lun_attribute_delete": False,
}


class LunAttributeSchema(ResourceSchema):
    """The fields of the LunAttribute object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the lun_attribute. """

    lun = fields.Nested("netapp_ontap.models.lun_attribute_lun.LunAttributeLunSchema", data_key="lun", unknown=EXCLUDE)
    r""" The lun field of the lun_attribute. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=4091),
    )
    r""" The attribute name. Required in POST.


Example: name1 """

    value = fields.Str(
        data_key="value",
        validate=len_validation(minimum=1, maximum=4091),
    )
    r""" The attribute value. Required in POST; valid in PATCH.


Example: value1 """

    @property
    def resource(self):
        return LunAttribute

    gettable_fields = [
        "links",
        "lun",
        "name",
        "value",
    ]
    """links,lun,name,value,"""

    patchable_fields = [
        "lun",
        "value",
    ]
    """lun,value,"""

    postable_fields = [
        "lun",
        "name",
        "value",
    ]
    """lun,name,value,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LunAttribute.get_collection(fields=field)]
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
            raise NetAppRestError("LunAttribute modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LunAttribute(Resource):
    r""" A name/value pair optionally stored with the LUN. Attributes are available to callers to persist small amounts of application-specific metadata. They are in no way interpreted by ONTAP.<br/>
Attribute names and values must be at least one byte and no more than 4091 bytes in length. The sum of the name and value lengths must be no more than 4092 bytes. """

    _schema = LunAttributeSchema
    _path = "/api/storage/luns/{lun[uuid]}/attributes"
    _keys = ["lun.uuid", "name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves LUN attributes.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun attribute show")
        def lun_attribute_show(
            lun_uuid,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            value: Choices.define(_get_field_list("value"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["name", "value", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LunAttribute resources

            Args:
                name: The attribute name. Required in POST. 
                value: The attribute value. Required in POST; valid in PATCH. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if value is not None:
                kwargs["value"] = value
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LunAttribute.get_collection(
                lun_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LunAttribute resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LunAttribute"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a LUN attribute value.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["LunAttribute"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LunAttribute"], NetAppResponse]:
        r"""Adds an attribute to a LUN.
### Required properties
* `name` - The name of the attribute to add.
* `value` - The value of the attribute to add.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
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
        records: Iterable["LunAttribute"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a LUN attribute.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves LUN attributes.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a LUN attribute.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
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
        r"""Adds an attribute to a LUN.
### Required properties
* `name` - The name of the attribute to add.
* `value` - The value of the attribute to add.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun attribute create")
        async def lun_attribute_create(
            lun_uuid,
            links: dict = None,
            lun: dict = None,
            name: str = None,
            value: str = None,
        ) -> ResourceTable:
            """Create an instance of a LunAttribute resource

            Args:
                links: 
                lun: 
                name: The attribute name. Required in POST. 
                value: The attribute value. Required in POST; valid in PATCH. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if lun is not None:
                kwargs["lun"] = lun
            if name is not None:
                kwargs["name"] = name
            if value is not None:
                kwargs["value"] = value

            resource = LunAttribute(
                lun_uuid,
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LunAttribute: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a LUN attribute value.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun attribute modify")
        async def lun_attribute_modify(
            lun_uuid,
            name: str = None,
            query_name: str = None,
            value: str = None,
            query_value: str = None,
        ) -> ResourceTable:
            """Modify an instance of a LunAttribute resource

            Args:
                name: The attribute name. Required in POST. 
                query_name: The attribute name. Required in POST. 
                value: The attribute value. Required in POST; valid in PATCH. 
                query_value: The attribute value. Required in POST; valid in PATCH. 
            """

            kwargs = {}
            changes = {}
            if query_name is not None:
                kwargs["name"] = query_name
            if query_value is not None:
                kwargs["value"] = query_value

            if name is not None:
                changes["name"] = name
            if value is not None:
                changes["value"] = value

            if hasattr(LunAttribute, "find"):
                resource = LunAttribute.find(
                    lun_uuid,
                    **kwargs
                )
            else:
                resource = LunAttribute(lun_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LunAttribute: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a LUN attribute.
### Learn more
* [`DOC /storage/luns/{lun.uuid}/attributes`](#docs-SAN-storage_luns_{lun.uuid}_attributes)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="lun attribute delete")
        async def lun_attribute_delete(
            lun_uuid,
            name: str = None,
            value: str = None,
        ) -> None:
            """Delete an instance of a LunAttribute resource

            Args:
                name: The attribute name. Required in POST. 
                value: The attribute value. Required in POST; valid in PATCH. 
            """

            kwargs = {}
            if name is not None:
                kwargs["name"] = name
            if value is not None:
                kwargs["value"] = value

            if hasattr(LunAttribute, "find"):
                resource = LunAttribute.find(
                    lun_uuid,
                    **kwargs
                )
            else:
                resource = LunAttribute(lun_uuid,)
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LunAttribute: %s" % err)


