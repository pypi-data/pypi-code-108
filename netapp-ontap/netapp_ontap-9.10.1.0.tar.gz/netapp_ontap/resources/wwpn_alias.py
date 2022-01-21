r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
A worldwide port name (WWPN) is a unique 64-bit identifier for a Fibre Channel (FC) initiator. It is displayed as a 16-character hexadecimal value. SAN administrators might find it easier to identify FC initiators using an alias, especially in larger SANs.<br/>
The WWPN alias REST API allows you to create, delete, and discover aliases for WWPNs.<br/>
Multiple aliases can be created for a WWPN, but you cannot use the same alias for multiple WWPNs.<br/>
An alias can consist of up to 32 characters. Valid characters are:

* A through Z
* a through z
* numbers 0 through 9
* hyphen ("-")
* underscore ("_")
* left and right braces ("{", "}")
* period (".")
## Examples
### Creating a WWPN alias
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WwpnAlias

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = WwpnAlias()
    resource.svm = {"name": "svm1"}
    resource.wwpn = "50:0a:09:82:b4:30:25:05"
    resource.alias = "alias3"
    resource.post(hydrate=True)
    print(resource)

```

### Retrieving all properties of all WWPN aliases
The `fields` query parameter is used to request that all properties be returned.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WwpnAlias

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(WwpnAlias.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    WwpnAlias(
        {
            "wwpn": "20:00:00:50:56:b4:30:25",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/68589d3d-7efa-11e8-9eed-005056b43025"
                    }
                },
                "uuid": "68589d3d-7efa-11e8-9eed-005056b43025",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/network/fc/wwpn-aliases/68589d3d-7efa-11e8-9eed-005056b43025/alias1"
                }
            },
            "alias": "alias1",
        }
    ),
    WwpnAlias(
        {
            "wwpn": "50:0a:09:82:b4:30:25:00",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/68589d3d-7efa-11e8-9eed-005056b43025"
                    }
                },
                "uuid": "68589d3d-7efa-11e8-9eed-005056b43025",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/network/fc/wwpn-aliases/68589d3d-7efa-11e8-9eed-005056b43025/alias2"
                }
            },
            "alias": "alias2",
        }
    ),
]

```
</div>
</div>

---
### Retrieving all WWPN aliases named "alias1"
The `alias` query parameter is used to specify a query for the value "alias1".
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WwpnAlias

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(WwpnAlias.get_collection(alias="alias1")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    WwpnAlias(
        {
            "wwpn": "20:00:00:50:56:b4:30:25",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/68589d3d-7efa-11e8-9eed-005056b43025"
                    }
                },
                "uuid": "68589d3d-7efa-11e8-9eed-005056b43025",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/network/fc/wwpn-aliases/68589d3d-7efa-11e8-9eed-005056b43025/alias1"
                }
            },
            "alias": "alias1",
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific WWPN alias
The alias to be returned is identified by the UUID of its SVM and the alias name.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WwpnAlias

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = WwpnAlias(
        alias="alias2", **{"svm.uuid": "68589d3d-7efa-11e8-9eed-005056b43025"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    WwpnAlias(
        {
            "wwpn": "50:0a:09:82:b4:30:25:00",
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/68589d3d-7efa-11e8-9eed-005056b43025"
                    }
                },
                "uuid": "68589d3d-7efa-11e8-9eed-005056b43025",
                "name": "svm1",
            },
            "_links": {
                "self": {
                    "href": "/api/network/fc/wwpn-aliases/68589d3d-7efa-11e8-9eed-005056b43025/alias1"
                }
            },
            "alias": "alias2",
        }
    )
]

```
</div>
</div>

---
### Deleting a WWPN alias
The alias to delete is identified by the UUID of its SVM and the alias name.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WwpnAlias

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = WwpnAlias(
        alias="alias2", **{"svm.uuid": "68589d3d-7efa-11e8-9eed-005056b43025"}
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


__all__ = ["WwpnAlias", "WwpnAliasSchema"]
__pdoc__ = {
    "WwpnAliasSchema.resource": False,
    "WwpnAlias.wwpn_alias_show": False,
    "WwpnAlias.wwpn_alias_create": False,
    "WwpnAlias.wwpn_alias_modify": False,
    "WwpnAlias.wwpn_alias_delete": False,
}


class WwpnAliasSchema(ResourceSchema):
    """The fields of the WwpnAlias object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the wwpn_alias. """

    alias = fields.Str(
        data_key="alias",
    )
    r""" The FC WWPN alias. Required in POST.


Example: host1 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the wwpn_alias. """

    wwpn = fields.Str(
        data_key="wwpn",
    )
    r""" The FC initiator WWPN. Required in POST.


Example: 2f:a0:00:a0:98:0b:56:13 """

    @property
    def resource(self):
        return WwpnAlias

    gettable_fields = [
        "links",
        "alias",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "wwpn",
    ]
    """links,alias,svm.links,svm.name,svm.uuid,wwpn,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "alias",
        "svm.name",
        "svm.uuid",
        "wwpn",
    ]
    """alias,svm.name,svm.uuid,wwpn,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in WwpnAlias.get_collection(fields=field)]
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
            raise NetAppRestError("WwpnAlias modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class WwpnAlias(Resource):
    r""" A Fibre Channel (FC) world wide port name (WWPN) alias. A WWPN is a unique 64-bit identifier for an FC initiator. It is displayed as a 16-character hexadecimal value. SAN administrators may find it easier to identify FC initiators using an alias, especially in larger SANs. """

    _schema = WwpnAliasSchema
    _path = "/api/network/fc/wwpn-aliases"
    _keys = ["svm.uuid", "alias"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves FC WWPN aliases.
### Related ONTAP commands
* `vserver fcp wwpn-alias show`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="wwpn alias show")
        def wwpn_alias_show(
            fields: List[Choices.define(["alias", "wwpn", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of WwpnAlias resources

            Args:
                alias: The FC WWPN alias. Required in POST. 
                wwpn: The FC initiator WWPN. Required in POST. 
            """

            kwargs = {}
            if alias is not None:
                kwargs["alias"] = alias
            if wwpn is not None:
                kwargs["wwpn"] = wwpn
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return WwpnAlias.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all WwpnAlias resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["WwpnAlias"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["WwpnAlias"], NetAppResponse]:
        r"""Creates an FC WWPN alias.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC alias.
* `alias` - Name of the FC alias.
* `wwpn` - FC WWPN for which to create the alias.
### Related ONTAP commands
* `vserver fcp wwpn-alias set`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
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
        records: Iterable["WwpnAlias"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC WWPN alias.
### Related ONTAP commands
* `vserver fcp wwpn-alias remove`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves FC WWPN aliases.
### Related ONTAP commands
* `vserver fcp wwpn-alias show`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an FC WWPN alias.
### Related ONTAP commands
* `vserver fcp wwpn-alias show`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
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
        r"""Creates an FC WWPN alias.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the FC alias.
* `alias` - Name of the FC alias.
* `wwpn` - FC WWPN for which to create the alias.
### Related ONTAP commands
* `vserver fcp wwpn-alias set`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="wwpn alias create")
        async def wwpn_alias_create(
        ) -> ResourceTable:
            """Create an instance of a WwpnAlias resource

            Args:
                links: 
                alias: The FC WWPN alias. Required in POST. 
                svm: 
                wwpn: The FC initiator WWPN. Required in POST. 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if alias is not None:
                kwargs["alias"] = alias
            if svm is not None:
                kwargs["svm"] = svm
            if wwpn is not None:
                kwargs["wwpn"] = wwpn

            resource = WwpnAlias(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create WwpnAlias: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an FC WWPN alias.
### Related ONTAP commands
* `vserver fcp wwpn-alias remove`
### Learn more
* [`DOC /network/fc/wwpn-aliases`](#docs-SAN-network_fc_wwpn-aliases)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="wwpn alias delete")
        async def wwpn_alias_delete(
        ) -> None:
            """Delete an instance of a WwpnAlias resource

            Args:
                alias: The FC WWPN alias. Required in POST. 
                wwpn: The FC initiator WWPN. Required in POST. 
            """

            kwargs = {}
            if alias is not None:
                kwargs["alias"] = alias
            if wwpn is not None:
                kwargs["wwpn"] = wwpn

            if hasattr(WwpnAlias, "find"):
                resource = WwpnAlias.find(
                    **kwargs
                )
            else:
                resource = WwpnAlias()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete WwpnAlias: %s" % err)


