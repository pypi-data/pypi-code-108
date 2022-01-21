r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Licensing allows you to tailor a system to meet an organization's specific needs. You can enable new features by purchasing a license from a NetApp sales associate. After installation of the license, the new feature is available immediately.
###
This interface manages licenses according to their supported feature. By default, the interface displays packages with installed licenses, but you can also return unlicensed packages.
###
Each feature has a compliance state that is indicated at the package level. Individual licenses also contain a compliance state indicated in the "licenses" array. The state of the package is determined by analyzing the underlying licenses according to the following criteria:

* Licensing terms
* Cluster state
### Licensing terms
The licensing terms define the conditions under which a package is considered "compliant". Individual licenses are evaluated based on the following:

* Scope
* Time period
* Usage
#### Scope
A package can be licensed under the following scopes:

* Site - Permits the feature to be used by any node in any cluster.
* Cluster - Permits the feature to be used by any node in a single specific cluster.
* Node - Permits the authorized node to use the feature. Within a cluster, if you don't supply every node with a valid license, the package state indicates "noncompliant". You must purchase a license for each node in a cluster for the package to be considered "compliant".
#### Time period
Some package licenses are only valid for a limited period of time. After a license has expired, the package state changes to "noncompliant". You need to purchase a new license for the package to return to a "compliant" state.
###
#### Usage
Some package licenses have additional terms that need to be maintained to keep a license in compliance. These conditions are defined by the individual license. For example, a license might define the maximum amount of storage that a node can allocate for the license to be "compliant".
###
### Cluster state
A cluster's state consists of the following:

* Node online status
* Node cluster membership
####
Some features require that a node be online to display a valid compliance state. If a node cannot be reached or is not known to the cluster, the individual license might indicate an "unknown" state.
####
_______
## Licensing keys
A license is issued in one of the following three formats:

  * 28-character key
  * NetApp License File Version 1 (NLFv1)
  * NetApp License File Version 2 (NLFv2)
#### Overview of NLFv1 and NLFv2 License Formats
NLFv1 and NLFv2 licenses are both JSON based files that allow features to be enabled.
####
The difference between the two formats is that a NLFv2 license allows multiple features to be enabled with a single file. A NLFv1 license is capable of enabling a single feature.
###
These licenses are identified, in the various methods, as follows:
###
| Format           | Identifying Keys                           |
| -----------------| -------------------------------------------|
| 28 Character Key | name / serial_number                       |
| NLFv1            | name / serial_number                       |
| NLFv2            | licenses.installed_license / serial_number |
###
The following is an example of a 28-character key:
####
```
AMEPOSOIKLKGEEEEDGNDEKSJDEEE
```
####
The following is an example of an NLFv1 key:
####
```JSON
{
  "statusResp": {
  "version": "1",
  "serialNumber": "123456789",
  "message": "Success",
  "licenses": {
    "capacity": "1",
    "type": "capacity",
    "licenseProtocol": "FABRICPOOL-TB",
    "package": "FabricPool",
    "licenseScope": "cluster"
  },
  "snStatus": "Active",
  "product": "fabricpool",
  "statusCode": "S007"
  },
  "Signature": "signatureABC"
}
```
####
The following is an example of an NLFv2 key:
####
```JSON
{
  "statusResp": {
  "version": "2",
  "serialNumber": "123456789",
  "message": "Success",
  "product": "Sample NLFv2 License",
  "licenses": {
    "capacity": "1",
    "type": "capacity",
    "HostID": "5554444",
    "package": [ "NFS", "CIFS" ],
    "licenseScope": "node"
  },
  "snStatus": "Active",
  "statusCode": "S007"
  },
  "Signature": "signatureABC"
}
```
###
You can use this API to submit any format to enable features.
###
_______
## Examples
### Retrieving a collection of licenses organized by package
This example retrieves a collection that contains one entry for each package (filtered to only the 'fabricpool' package).
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LicensePackage.get_collection(fields="*", name="fabricpool")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LicensePackage(
        {
            "scope": "cluster",
            "licenses": [
                {
                    "owner": "testcluster-1",
                    "capacity": {"maximum_size": 1099511627776, "used_size": 0},
                    "serial_number": "4149027342",
                }
            ],
            "state": "compliant",
            "name": "fabricpool",
            "_links": {"self": {"href": "/api/cluster/licensing/licenses/fabricpool"}},
        }
    )
]

```
</div>
</div>

### Retrieving a collection of licenses installed with NLFv2
This example retrieves a collection of licenses that were installed by a NLFv2 formatted license.
####
**Note:** The license is referenced by the installed license "Core*Bundle" and the license serial number "4149026-97-8"
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            LicensePackage.get_collection(
                fields="*",
                serial_number="4149026-97-8",
                **{"licenses.installed_license": "Core*Bundle"}
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
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "nfs",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/nfs/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "cifs",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/cifs/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "iscsi",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/iscsi/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "snaprestore",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/snaprestore/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "flexclone",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/flexclone/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim2",
                    "active": False,
                    "compliance": {"state": "unlicensed"},
                },
                {
                    "evaluation": False,
                    "owner": "hbrock-vsim1",
                    "active": True,
                    "capacity": {"maximum_size": 10995116277760},
                    "host_id": "4149026-97-8",
                    "compliance": {"state": "compliant"},
                    "installed_license": "Core Bundle",
                    "serial_number": "4149026-97-8",
                },
            ],
            "state": "noncompliant",
            "name": "s3",
            "_links": {
                "self": {
                    "href": "/api/cluster/licensing/licenses/s3/?licenses.installed_license=Core*Bundle"
                }
            },
        }
    ),
]

```
</div>
</div>

### Retrieving a collection of installed licenses
This example retrieves a collection containing all packages (except base) that have installed licenses.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LicensePackage.get_collection(fields="*", name="!base")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "owner": "testcluster-1",
                    "serial_number": "1-81-0000000000000004149027492",
                }
            ],
            "state": "compliant",
            "name": "nfs",
            "_links": {"self": {"href": "/api/cluster/licensing/licenses/nfs"}},
        }
    ),
    LicensePackage(
        {
            "scope": "node",
            "licenses": [
                {
                    "owner": "testcluster-1",
                    "serial_number": "1-81-0000000000000004149027492",
                }
            ],
            "state": "compliant",
            "name": "cifs",
            "_links": {"self": {"href": "/api/cluster/licensing/licenses/cifs"}},
        }
    ),
]

```
</div>
</div>

### Retrieving a collection of unlicensed packages
By default, unlicensed packages are filtered from the collection output. This example shows how to use a query to retrieve unlicensed packages.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LicensePackage.get_collection(name="flexcache", state="unlicensed")))

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
[
    LicensePackage(
        {
            "name": "flexcache",
            "_links": {"self": {"href": "/api/cluster/licensing/licenses/flexcache"}},
        }
    )
]

```
</div>
</div>

### Installing a NLF license
This example installs a single NLFv1 license. A NLFv2 license installs using the same procedure.
###
**Note:** You must escape all the double quotes and backslash characters of the JSON license before it can be placed in the POST request.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage()
    resource.post(hydrate=True)
    print(resource)

```

### Installing a 28-character key
This example installs a single 28-character key formatted license.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage()
    resource.post(hydrate=True)
    print(resource)

```

### Installing multiple licenses with one API call
This example shows how multiple keys can be provided to install multiple features in a single API call.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage()
    resource.post(hydrate=True)
    print(resource)

```

### Retrieving information for a specific license package
This example shows how to retrieve information about the specific feature package `fabricpool`.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage(name="fabricpool")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example7_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example7_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example7_result" class="try_it_out_content">
```
LicensePackage(
    {
        "scope": "cluster",
        "licenses": [
            {
                "owner": "testcluster-1",
                "capacity": {"maximum_size": 109951162777600, "used_size": 0},
                "serial_number": "123456789",
            }
        ],
        "state": "compliant",
        "name": "fabricpool",
        "_links": {"self": {"href": "/api/cluster/licensing/licenses/fabricpool/"}},
    }
)

```
</div>
</div>

### Deleting a specific license
This example show how to delete a CIFS site license.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage(name="cifs")
    resource.delete(serial_number="1-80-000011")

```

### Deleting with a query
####
The following example shows how to delete all NFS licenses specified with the '*' query.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage(name="nfs")
    resource.delete(serial_number="*")

```

### Deleting all licenses installed with NLFv2
####
The following example shows how to delete all licenses installed by a NLFv2 formatted license.
####
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LicensePackage

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LicensePackage()
    resource.delete(
        serial_number="4149026-97-8", **{"licenses.installed_license": "Core*Bundle"}
    )

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


__all__ = ["LicensePackage", "LicensePackageSchema"]
__pdoc__ = {
    "LicensePackageSchema.resource": False,
    "LicensePackage.license_package_show": False,
    "LicensePackage.license_package_create": False,
    "LicensePackage.license_package_modify": False,
    "LicensePackage.license_package_delete": False,
}


class LicensePackageSchema(ResourceSchema):
    """The fields of the LicensePackage object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the license_package. """

    keys = fields.List(fields.Str, data_key="keys")
    r""" The keys field of the license_package. """

    licenses = fields.List(fields.Nested("netapp_ontap.models.license.LicenseSchema", unknown=EXCLUDE), data_key="licenses")
    r""" Installed licenses of the package. """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the license.

Example: NFS """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['not_available', 'site', 'cluster', 'node']),
    )
    r""" Scope of the license.

Valid choices:

* not_available
* site
* cluster
* node """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['compliant', 'noncompliant', 'unlicensed', 'unknown']),
    )
    r""" Summary state of package based on all installed licenses.

Valid choices:

* compliant
* noncompliant
* unlicensed
* unknown """

    @property
    def resource(self):
        return LicensePackage

    gettable_fields = [
        "links",
        "licenses",
        "name",
        "scope",
        "state",
    ]
    """links,licenses,name,scope,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "keys",
    ]
    """keys,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LicensePackage.get_collection(fields=field)]
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
            raise NetAppRestError("LicensePackage modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LicensePackage(Resource):
    """Allows interaction with LicensePackage objects on the host"""

    _schema = LicensePackageSchema
    _path = "/api/cluster/licensing/licenses"
    _keys = ["name"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a collection of license packages.
####
**Note:** By default, the GET method only returns licensed packages. You must provide the following query "state=unlicensed" to retrieve unlicensed packages.
### Related ONTAP commands
* `system license show-status`
* `system license show`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="license package show")
        def license_package_show(
            fields: List[Choices.define(["keys", "name", "scope", "state", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LicensePackage resources

            Args:
                keys: 
                name: Name of the license.
                scope: Scope of the license.
                state: Summary state of package based on all installed licenses.
            """

            kwargs = {}
            if keys is not None:
                kwargs["keys"] = keys
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LicensePackage.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LicensePackage resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)


    @classmethod
    def post_collection(
        cls,
        records: Iterable["LicensePackage"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LicensePackage"], NetAppResponse]:
        r"""Installs one or more feature licenses.
### Required properties
* `keys` - Array containing a list of NLF or 28-character license keys.
### Related ONTAP commands
* `system license add`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["LicensePackage"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a license.
### Related ONTAP commands
* `system license delete`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a collection of license packages.
####
**Note:** By default, the GET method only returns licensed packages. You must provide the following query "state=unlicensed" to retrieve unlicensed packages.
### Related ONTAP commands
* `system license show-status`
* `system license show`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a specific license package.
####
**Note:** By default, the GET method only returns licensed packages. You must provide the following query "state=unlicensed" to retrieve unlicensed packages.
### Related ONTAP commands
* `system license show`
* `system license show-status`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
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
        r"""Installs one or more feature licenses.
### Required properties
* `keys` - Array containing a list of NLF or 28-character license keys.
### Related ONTAP commands
* `system license add`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="license package create")
        async def license_package_create(
        ) -> ResourceTable:
            """Create an instance of a LicensePackage resource

            Args:
                links: 
                keys: 
                licenses: Installed licenses of the package.
                name: Name of the license.
                scope: Scope of the license.
                state: Summary state of package based on all installed licenses.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if keys is not None:
                kwargs["keys"] = keys
            if licenses is not None:
                kwargs["licenses"] = licenses
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state

            resource = LicensePackage(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LicensePackage: %s" % err)
            return [resource]


    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a license.
### Related ONTAP commands
* `system license delete`

### Learn more
* [`DOC /cluster/licensing/licenses`](#docs-cluster-cluster_licensing_licenses)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="license package delete")
        async def license_package_delete(
        ) -> None:
            """Delete an instance of a LicensePackage resource

            Args:
                keys: 
                name: Name of the license.
                scope: Scope of the license.
                state: Summary state of package based on all installed licenses.
            """

            kwargs = {}
            if keys is not None:
                kwargs["keys"] = keys
            if name is not None:
                kwargs["name"] = name
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state

            if hasattr(LicensePackage, "find"):
                resource = LicensePackage.find(
                    **kwargs
                )
            else:
                resource = LicensePackage()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LicensePackage: %s" % err)


