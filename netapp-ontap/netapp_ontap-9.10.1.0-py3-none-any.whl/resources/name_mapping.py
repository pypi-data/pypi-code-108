r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Name mapping is used to map CIFS identities to UNIX identities, Kerberos identities to UNIX identities, and UNIX identities to CIFS identities. It needs this information to obtain user credentials and provide proper file access regardless of whether they are connecting from an NFS client or a CIFS client. </br>
The system keeps a set of conversion rules for each Storage Virtual Machine (SVM). Each rule consists of two pieces: a pattern and a replacement. Conversions start at the beginning of the appropriate list and perform a substitution based on the first matching rule. The pattern is a UNIX-style regular expression. The replacement is a string containing escape sequences representing subexpressions from the pattern, as in the UNIX sed program.</br>
Name mappings are applied in the order in which they occur in the priority list; for example, a name mapping that occurs at position 2 in the priority list is applied before a name mapping that occurs at position 3. Each mapping direction (Kerberos-to-UNIX, Windows-to-UNIX, and UNIX-to-Windows) has its own priority list. You are prevented from creating two name mappings with the same pattern.<p/>
## Examples
### Creating a name-mapping with client_match as the ip-address
Use the following API to create a name-mapping. Note the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NameMapping()
    resource.client_match = "10.254.101.111/28"
    resource.direction = "win_unix"
    resource.index = 1
    resource.pattern = "ENGCIFS_AD_USER"
    resource.replacement = "unix_user1"
    resource.svm = {"name": "vs1", "uuid": "f71d3640-0226-11e9-8526-000c290a8c4b"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
NameMapping(
    {
        "direction": "win_unix",
        "client_match": "10.254.101.111/28",
        "svm": {"uuid": "f71d3640-0226-11e9-8526-000c290a8c4b", "name": "vs1"},
        "pattern": "ENGCIFS_AD_USER",
        "index": 1,
        "replacement": "unix_user1",
    }
)

```
</div>
</div>

### Creating a name-mapping with client_match as the hostname
Use the following API to create a name-mapping. Note the <i>return_records=true</i> query parameter is used to obtain the newly created entry in the response.
<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NameMapping()
    resource.client_match = "google.com"
    resource.direction = "win_unix"
    resource.index = 2
    resource.pattern = "ENGCIFS_AD_USER"
    resource.replacement = "unix_user1"
    resource.svm = {"name": "vs1", "uuid": "f71d3640-0226-11e9-8526-000c290a8c4b"}
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
NameMapping(
    {
        "direction": "win_unix",
        "client_match": "google.com",
        "svm": {"uuid": "f71d3640-0226-11e9-8526-000c290a8c4b", "name": "vs1"},
        "pattern": "ENGCIFS_AD_USER",
        "index": 2,
        "replacement": "unix_user1",
    }
)

```
</div>
</div>

### Retrieving all name-mapping configurations for all SVMs in the cluster
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NameMapping.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    NameMapping(
        {
            "direction": "win_unix",
            "client_match": "10.254.101.111/28",
            "svm": {"uuid": "f71d3640-0226-11e9-8526-000c290a8c4b", "name": "vs1"},
            "pattern": "ENGCIFS_AD_USER",
            "index": 1,
            "replacement": "unix_user1",
        }
    ),
    NameMapping(
        {
            "direction": "win_unix",
            "client_match": "google.com",
            "svm": {"uuid": "f71d3640-0226-11e9-8526-000c290a8c4b", "name": "vs1"},
            "pattern": "ENGCIFS_AD_USER",
            "index": 2,
            "replacement": "unix_user1",
        }
    ),
]

```
</div>
</div>

### Retrieving a name-mapping configuration for a specific SVM, and for the specified direction and index
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NameMapping(
        index=1,
        direction="win_unix",
        **{"svm.uuid": "f71d3640-0226-11e9-8526-000c290a8c4b"}
    )
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
NameMapping(
    {
        "direction": "win_unix",
        "client_match": "10.254.101.111/28",
        "svm": {"uuid": "f71d3640-0226-11e9-8526-000c290a8c4b", "name": "vs1"},
        "pattern": "ENGCIFS_AD_USER",
        "index": 1,
        "replacement": "unix_user1",
    }
)

```
</div>
</div>

---
### Updating a specific name-mapping configuration
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NameMapping(
        index=1,
        direction="win_unix",
        **{"svm.uuid": "f71d3640-0226-11e9-8526-000c290a8c4b"}
    )
    resource.client_match = "10.254.101.222/28"
    resource.pattern = "ENGCIFS_LOCAL_USER"
    resource.replacement = "pcuser"
    resource.patch()

```

---
### Removing a specific name-mapping configuration
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NameMapping

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NameMapping(
        index=1,
        direction="win_unix",
        **{"svm.uuid": "f71d3640-0226-11e9-8526-000c290a8c4b"}
    )
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


__all__ = ["NameMapping", "NameMappingSchema"]
__pdoc__ = {
    "NameMappingSchema.resource": False,
    "NameMapping.name_mapping_show": False,
    "NameMapping.name_mapping_create": False,
    "NameMapping.name_mapping_modify": False,
    "NameMapping.name_mapping_delete": False,
}


class NameMappingSchema(ResourceSchema):
    """The fields of the NameMapping object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the name_mapping. """

    client_match = fields.Str(
        data_key="client_match",
    )
    r""" Client workstation IP Address which is matched when searching for the pattern.
  You can specify the value in any of the following formats:

* As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24
* As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64
* As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0
* As a hostname


Example: 10.254.101.111/28 """

    direction = fields.Str(
        data_key="direction",
        validate=enum_validation(['win_unix', 'unix_win', 'krb_unix']),
    )
    r""" Direction in which the name mapping is applied. The possible values are:

  * krb_unix  - Kerberos principal name to UNIX user name
  * win_unix  - Windows user name to UNIX user name
  * unix_win  - UNIX user name to Windows user name mapping


Valid choices:

* win_unix
* unix_win
* krb_unix """

    index = Size(
        data_key="index",
        validate=integer_validation(minimum=1, maximum=2147483647),
    )
    r""" Position in the list of name mappings.

Example: 1 """

    pattern = fields.Str(
        data_key="pattern",
        validate=len_validation(minimum=1, maximum=256),
    )
    r""" Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.

Example: ENGCIFS_AD_USER """

    replacement = fields.Str(
        data_key="replacement",
        validate=len_validation(minimum=1, maximum=256),
    )
    r""" The name that is used as a replacement, if the pattern associated with this entry matches.

Example: unix_user1 """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the name_mapping. """

    @property
    def resource(self):
        return NameMapping

    gettable_fields = [
        "links",
        "client_match",
        "direction",
        "index",
        "pattern",
        "replacement",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,client_match,direction,index,pattern,replacement,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "client_match",
        "pattern",
        "replacement",
        "svm.name",
        "svm.uuid",
    ]
    """client_match,pattern,replacement,svm.name,svm.uuid,"""

    postable_fields = [
        "client_match",
        "direction",
        "index",
        "pattern",
        "replacement",
        "svm.name",
        "svm.uuid",
    ]
    """client_match,direction,index,pattern,replacement,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NameMapping.get_collection(fields=field)]
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
            raise NetAppRestError("NameMapping modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NameMapping(Resource):
    r""" Name mapping is used to map CIFS identities to UNIX identities, Kerberos identities to UNIX identities, and UNIX identities to CIFS identities. It needs this information to obtain user credentials and provide proper file access regardless of whether they are connecting from an NFS client or a CIFS client. """

    _schema = NameMappingSchema
    _path = "/api/name-services/name-mappings"
    _keys = ["svm.uuid", "direction", "index"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the name mapping configuration for all SVMs.
### Related ONTAP commands
* `vserver name-mapping show`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="name mapping show")
        def name_mapping_show(
            fields: List[Choices.define(["client_match", "direction", "index", "pattern", "replacement", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NameMapping resources

            Args:
                client_match: Client workstation IP Address which is matched when searching for the pattern.   You can specify the value in any of the following formats: * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a hostname 
                direction: Direction in which the name mapping is applied. The possible values are:   * krb_unix  - Kerberos principal name to UNIX user name   * win_unix  - Windows user name to UNIX user name   * unix_win  - UNIX user name to Windows user name mapping 
                index: Position in the list of name mappings.
                pattern: Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.
                replacement: The name that is used as a replacement, if the pattern associated with this entry matches.
            """

            kwargs = {}
            if client_match is not None:
                kwargs["client_match"] = client_match
            if direction is not None:
                kwargs["direction"] = direction
            if index is not None:
                kwargs["index"] = index
            if pattern is not None:
                kwargs["pattern"] = pattern
            if replacement is not None:
                kwargs["replacement"] = replacement
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NameMapping.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NameMapping resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NameMapping"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the name mapping configuration of an SVM. The positions can be swapped by providing the `new_index` property.
Swapping is not allowed for entries that have `client_match` property configured.
### Related ONTAP commands
* `vserver name-mapping insert`
* `vserver name-mapping modify`
* `vserver name-mapping swap`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NameMapping"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NameMapping"], NetAppResponse]:
        r"""Creates name mappings for an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the name mapping.
* `index` - Name mapping's position in the priority list.
* `direction` - Direction of the name mapping.
* `pattern` - Pattern to match to. Maximum length is 256 characters.
* `replacement` - Replacement pattern to match to. Maximum length is 256 characters.
### Recommended optional properties
* `client_match` - Hostname or IP address added to match the pattern to the client's workstation IP address.
### Related ONTAP commands
* `vserver name-mapping create`
* `vserver name-mapping insert`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
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
        records: Iterable["NameMapping"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the name mapping configuration.
### Related ONTAP commands
* `vserver name-mapping delete`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the name mapping configuration for all SVMs.
### Related ONTAP commands
* `vserver name-mapping show`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the name mapping configuration of an SVM.
### Related ONTAP commands
* `vserver name-mapping show`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
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
        r"""Creates name mappings for an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create the name mapping.
* `index` - Name mapping's position in the priority list.
* `direction` - Direction of the name mapping.
* `pattern` - Pattern to match to. Maximum length is 256 characters.
* `replacement` - Replacement pattern to match to. Maximum length is 256 characters.
### Recommended optional properties
* `client_match` - Hostname or IP address added to match the pattern to the client's workstation IP address.
### Related ONTAP commands
* `vserver name-mapping create`
* `vserver name-mapping insert`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="name mapping create")
        async def name_mapping_create(
        ) -> ResourceTable:
            """Create an instance of a NameMapping resource

            Args:
                links: 
                client_match: Client workstation IP Address which is matched when searching for the pattern.   You can specify the value in any of the following formats: * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a hostname 
                direction: Direction in which the name mapping is applied. The possible values are:   * krb_unix  - Kerberos principal name to UNIX user name   * win_unix  - Windows user name to UNIX user name   * unix_win  - UNIX user name to Windows user name mapping 
                index: Position in the list of name mappings.
                pattern: Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.
                replacement: The name that is used as a replacement, if the pattern associated with this entry matches.
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if client_match is not None:
                kwargs["client_match"] = client_match
            if direction is not None:
                kwargs["direction"] = direction
            if index is not None:
                kwargs["index"] = index
            if pattern is not None:
                kwargs["pattern"] = pattern
            if replacement is not None:
                kwargs["replacement"] = replacement
            if svm is not None:
                kwargs["svm"] = svm

            resource = NameMapping(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NameMapping: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the name mapping configuration of an SVM. The positions can be swapped by providing the `new_index` property.
Swapping is not allowed for entries that have `client_match` property configured.
### Related ONTAP commands
* `vserver name-mapping insert`
* `vserver name-mapping modify`
* `vserver name-mapping swap`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="name mapping modify")
        async def name_mapping_modify(
        ) -> ResourceTable:
            """Modify an instance of a NameMapping resource

            Args:
                client_match: Client workstation IP Address which is matched when searching for the pattern.   You can specify the value in any of the following formats: * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a hostname 
                query_client_match: Client workstation IP Address which is matched when searching for the pattern.   You can specify the value in any of the following formats: * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a hostname 
                direction: Direction in which the name mapping is applied. The possible values are:   * krb_unix  - Kerberos principal name to UNIX user name   * win_unix  - Windows user name to UNIX user name   * unix_win  - UNIX user name to Windows user name mapping 
                query_direction: Direction in which the name mapping is applied. The possible values are:   * krb_unix  - Kerberos principal name to UNIX user name   * win_unix  - Windows user name to UNIX user name   * unix_win  - UNIX user name to Windows user name mapping 
                index: Position in the list of name mappings.
                query_index: Position in the list of name mappings.
                pattern: Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.
                query_pattern: Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.
                replacement: The name that is used as a replacement, if the pattern associated with this entry matches.
                query_replacement: The name that is used as a replacement, if the pattern associated with this entry matches.
            """

            kwargs = {}
            changes = {}
            if query_client_match is not None:
                kwargs["client_match"] = query_client_match
            if query_direction is not None:
                kwargs["direction"] = query_direction
            if query_index is not None:
                kwargs["index"] = query_index
            if query_pattern is not None:
                kwargs["pattern"] = query_pattern
            if query_replacement is not None:
                kwargs["replacement"] = query_replacement

            if client_match is not None:
                changes["client_match"] = client_match
            if direction is not None:
                changes["direction"] = direction
            if index is not None:
                changes["index"] = index
            if pattern is not None:
                changes["pattern"] = pattern
            if replacement is not None:
                changes["replacement"] = replacement

            if hasattr(NameMapping, "find"):
                resource = NameMapping.find(
                    **kwargs
                )
            else:
                resource = NameMapping()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NameMapping: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the name mapping configuration.
### Related ONTAP commands
* `vserver name-mapping delete`
### Learn more
* [`DOC /name-services/name-mappings`](#docs-name-services-name-services_name-mappings)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="name mapping delete")
        async def name_mapping_delete(
        ) -> None:
            """Delete an instance of a NameMapping resource

            Args:
                client_match: Client workstation IP Address which is matched when searching for the pattern.   You can specify the value in any of the following formats: * As an IPv4 address with a subnet mask expressed as a number of bits; for instance, 10.1.12.0/24 * As an IPv6 address with a subnet mask expressed as a number of bits; for instance, fd20:8b1e:b255:4071::/64 * As an IPv4 address with a network mask; for instance, 10.1.16.0/255.255.255.0 * As a hostname 
                direction: Direction in which the name mapping is applied. The possible values are:   * krb_unix  - Kerberos principal name to UNIX user name   * win_unix  - Windows user name to UNIX user name   * unix_win  - UNIX user name to Windows user name mapping 
                index: Position in the list of name mappings.
                pattern: Pattern used to match the name while searching for a name that can be used as a replacement. The pattern is a UNIX-style regular expression. Regular expressions are case-insensitive when mapping from Windows to UNIX, and they are case-sensitive for mappings from Kerberos to UNIX and UNIX to Windows.
                replacement: The name that is used as a replacement, if the pattern associated with this entry matches.
            """

            kwargs = {}
            if client_match is not None:
                kwargs["client_match"] = client_match
            if direction is not None:
                kwargs["direction"] = direction
            if index is not None:
                kwargs["index"] = index
            if pattern is not None:
                kwargs["pattern"] = pattern
            if replacement is not None:
                kwargs["replacement"] = replacement

            if hasattr(NameMapping, "find"):
                resource = NameMapping.find(
                    **kwargs
                )
            else:
                resource = NameMapping()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NameMapping: %s" % err)


