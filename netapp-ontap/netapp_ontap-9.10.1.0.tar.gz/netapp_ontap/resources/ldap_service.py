r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
LDAP servers are used to centrally maintain user information. LDAP configurations must be set up
to lookup information stored in the LDAP directory on the external LDAP servers. This API is used to retrieve and manage
LDAP server configurations.
## Retrieving LDAP information
The LDAP GET endpoint retrieves all of the LDAP configurations in the cluster.
## Examples
### Retrieving all of the fields for all LDAP configurations
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LdapService.get_collection(fields="**")))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    LdapService(
        {
            "min_bind_level": "anonymous",
            "try_channel_binding": True,
            "_links": {
                "self": {
                    "href": "/api/name-services/ldap/179d3c85-7053-11e8-b9b8-005056b41bd1"
                }
            },
            "group_scope": "subtree",
            "ldaps_enabled": False,
            "bind_as_cifs_server": False,
            "port": 389,
            "group_membership_filter": "",
            "use_start_tls": True,
            "base_scope": "subtree",
            "bind_dn": "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com",
            "is_netgroup_byhost_enabled": False,
            "session_security": "none",
            "is_owner": True,
            "netgroup_byhost_scope": "subtree",
            "base_dn": "dc=domainA,dc=example,dc=com",
            "netgroup_scope": "subtree",
            "schema": "ad_idmu",
            "query_timeout": 3,
            "user_scope": "subtree",
            "referral_enabled": False,
            "status": {
                "state": "down",
                "code": 4915258,
                "message": "The LDAP configuration is invalid. Verify that the AD domain or servers are reachable and that the network configuration is correct",
                "dn_message": ["No LDAP DN configured"],
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/179d3c85-7053-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1",
                "name": "vs1",
            },
            "servers": ["10.10.10.10", "domainB.example.com"],
        }
    ),
    LdapService(
        {
            "min_bind_level": "simple",
            "try_channel_binding": True,
            "_links": {
                "self": {
                    "href": "/api/name-services/ldap/6a52023b-7066-11e8-b9b8-005056b41bd1"
                }
            },
            "group_scope": "subtree",
            "ldaps_enabled": False,
            "bind_as_cifs_server": False,
            "port": 389,
            "group_membership_filter": "",
            "use_start_tls": True,
            "base_scope": "subtree",
            "bind_dn": "cn=Administrators,cn=users,dc=domainB,dc=example,dc=com",
            "is_netgroup_byhost_enabled": False,
            "session_security": "sign",
            "is_owner": True,
            "netgroup_byhost_scope": "subtree",
            "base_dn": "dc=domainB,dc=example,dc=com",
            "netgroup_scope": "subtree",
            "schema": "rfc_2307",
            "query_timeout": 0,
            "user_scope": "subtree",
            "referral_enabled": False,
            "status": {
                "state": "up",
                "code": 0,
                "message": 'Successfully connected to LDAP server "172.20.192.44".',
                "dn_message": ["All the configured DNs are available."],
            },
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/6a52023b-7066-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "6a52023b-7066-11e8-b9b8-005056b41bd1",
                "name": "vs2",
            },
            "servers": ["11.11.11.11"],
        }
    ),
]

```
</div>
</div>

---
### Retrieving all of the LDAP configurations that have the *use_start_tls* set to *true*
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(LdapService.get_collection(use_start_tls=True)))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    LdapService(
        {
            "_links": {
                "self": {
                    "href": "/api/name-services/ldap/6a52023b-7066-11e8-b9b8-005056b41bd1"
                }
            },
            "use_start_tls": True,
            "svm": {
                "_links": {
                    "self": {
                        "href": "/api/svm/svms/6a52023b-7066-11e8-b9b8-005056b41bd1"
                    }
                },
                "uuid": "6a52023b-7066-11e8-b9b8-005056b41bd1",
                "name": "vs2",
            },
        }
    )
]

```
</div>
</div>

---
### Retrieving the LDAP configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
LdapService(
    {
        "min_bind_level": "anonymous",
        "try_channel_binding": True,
        "_links": {
            "self": {
                "href": "/api/name-services/ldap/179d3c85-7053-11e8-b9b8-005056b41bd1"
            }
        },
        "ldaps_enabled": False,
        "bind_as_cifs_server": True,
        "port": 389,
        "use_start_tls": True,
        "base_scope": "subtree",
        "bind_dn": "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com",
        "session_security": "none",
        "is_owner": True,
        "base_dn": "dc=domainA,dc=example,dc=com",
        "schema": "ad_idmu",
        "query_timeout": 3,
        "referral_enabled": False,
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/179d3c85-7053-11e8-b9b8-005056b41bd1"}
            },
            "uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1",
            "name": "vs1",
        },
        "servers": ["10.10.10.10", "domainB.example.com"],
    }
)

```
</div>
</div>

---
### Retrieving all the fields of the LDAP configuration of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.get(fields="**")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
LdapService(
    {
        "min_bind_level": "anonymous",
        "try_channel_binding": True,
        "_links": {
            "self": {
                "href": "/api/name-services/ldap/179d3c85-7053-11e8-b9b8-005056b41bd1"
            }
        },
        "group_scope": "subtree",
        "ldaps_enabled": False,
        "bind_as_cifs_server": True,
        "port": 389,
        "group_membership_filter": "",
        "use_start_tls": True,
        "base_scope": "subtree",
        "bind_dn": "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com",
        "is_netgroup_byhost_enabled": False,
        "session_security": "none",
        "is_owner": True,
        "netgroup_byhost_scope": "subtree",
        "base_dn": "dc=domainA,dc=example,dc=com",
        "netgroup_scope": "subtree",
        "schema": "ad_idmu",
        "query_timeout": 3,
        "user_scope": "subtree",
        "referral_enabled": False,
        "status": {
            "state": "down",
            "code": 4915258,
            "message": "The LDAP configuration is invalid. Verify that the AD domain or servers are reachable and that the network configuration is correct",
            "dn_message": ["No LDAP DN configured"],
        },
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/179d3c85-7053-11e8-b9b8-005056b41bd1"}
            },
            "uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1",
            "name": "vs1",
        },
        "servers": ["10.10.10.10", "domainB.example.com"],
    }
)

```
</div>
</div>

---
### Retrieving the LDAP server status of a specific SVM
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService(**{"svm.uuid": "9e4a2e3b-f66f-11ea-aec8-0050568e155c"})
    resource.get(fields="status")
    print(resource)

```
<div class="try_it_out">
<input id="example4_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example4_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example4_result" class="try_it_out_content">
```
LdapService(
    {
        "status": {
            "state": "up",
            "code": 0,
            "message": 'Successfully connected to LDAP server "172.20.192.44".',
        },
        "svm": {"uuid": "9e4a2e3b-f66f-11ea-aec8-0050568e155c", "name": "vs2"},
    }
)

```
</div>
</div>

---
## Creating an LDAP configuration
The LDAP POST endpoint creates an LDAP configuration for the specified SVM.
## Examples
### Creating an LDAP configuration with all the fields specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService()
    resource.svm = {"uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"}
    resource.servers = ["10.10.10.10", "domainB.example.com"]
    resource.schema = "ad_idmu"
    resource.port = 389
    resource.ldaps_enabled = False
    resource.min_bind_level = "anonymous"
    resource.bind_dn = "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com"
    resource.bind_password = "abc"
    resource.base_dn = "dc=domainA,dc=example,dc=com"
    resource.base_scope = "subtree"
    resource.use_start_tls = False
    resource.session_security = "none"
    resource.referral_enabled = False
    resource.bind_as_cifs_server = False
    resource.query_timeout = 4
    resource.user_dn = "cn=abc,users,dc=com"
    resource.user_scope = "subtree"
    resource.group_dn = "cn=abc,users,dc=com"
    resource.group_scope = "subtree"
    resource.netgroup_dn = "cn=abc,users,dc=com"
    resource.netgroup_scope = "subtree"
    resource.netgroup_byhost_dn = "cn=abc,users,dc=com"
    resource.netgroup_byhost_scope = "subtree"
    resource.is_netgroup_byhost_enabled = False
    resource.group_membership_filter = ""
    resource.skip_config_validation = False
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating an LDAP configuration with Active Directory domain and preferred Active Directory servers specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService()
    resource.svm = {"name": "vs2"}
    resource.ad_domain = "domainA.example.com"
    resource.preferred_ad_servers = ["11.11.11.11"]
    resource.port = 389
    resource.ldaps_enabled = False
    resource.bind_dn = "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com"
    resource.bind_password = "abc"
    resource.base_dn = "dc=domainA,dc=example,dc=com"
    resource.session_security = "none"
    resource.referral_enabled = False
    resource.query_timeout = 3
    resource.post(hydrate=True)
    print(resource)

```

---
### Creating an LDAP configuration with a number of optional fields not specified
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService()
    resource.svm = {"name": "vs2"}
    resource.servers = ["11.11.11.11"]
    resource.port = 389
    resource.bind_dn = "cn=Administrators,cn=users,dc=domainA,dc=example,dc=com"
    resource.bind_password = "abc"
    resource.base_dn = "dc=domainA,dc=example,dc=com"
    resource.session_security = "none"
    resource.post(hydrate=True)
    print(resource)

```

---
## Updating an LDAP configuration
The LDAP PATCH endpoint updates the LDAP configuration for the specified SVM. The following example shows a PATCH operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
    resource.servers = ["55.55.55.55"]
    resource.schema = "ad_idmu"
    resource.port = 636
    resource.ldaps_enabled = True
    resource.use_start_tls = False
    resource.referral_enabled = False
    resource.patch()

```

---
## Deleting an LDAP configuration
The LDAP DELETE endpoint deletes the LDAP configuration for the specified SVM. The following example shows a DELETE operation:
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import LdapService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = LdapService(**{"svm.uuid": "179d3c85-7053-11e8-b9b8-005056b41bd1"})
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


__all__ = ["LdapService", "LdapServiceSchema"]
__pdoc__ = {
    "LdapServiceSchema.resource": False,
    "LdapService.ldap_service_show": False,
    "LdapService.ldap_service_create": False,
    "LdapService.ldap_service_modify": False,
    "LdapService.ldap_service_delete": False,
}


class LdapServiceSchema(ResourceSchema):
    """The fields of the LdapService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the ldap_service. """

    ad_domain = fields.Str(
        data_key="ad_domain",
    )
    r""" This parameter specifies the name of the Active Directory domain
used to discover LDAP servers for use by this client.
This is mutually exclusive with `servers` during POST and PATCH. """

    base_dn = fields.Str(
        data_key="base_dn",
    )
    r""" Specifies the default base DN for all searches. """

    base_scope = fields.Str(
        data_key="base_scope",
        validate=enum_validation(['base', 'onelevel', 'subtree']),
    )
    r""" Specifies the default search scope for LDAP queries:

* base - search the named entry only
* onelevel - search all entries immediately below the DN
* subtree - search the named DN entry and the entire subtree below the DN


Valid choices:

* base
* onelevel
* subtree """

    bind_as_cifs_server = fields.Boolean(
        data_key="bind_as_cifs_server",
    )
    r""" Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. """

    bind_dn = fields.Str(
        data_key="bind_dn",
    )
    r""" Specifies the user that binds to the LDAP servers. """

    bind_password = fields.Str(
        data_key="bind_password",
    )
    r""" Specifies the bind password for the LDAP servers. """

    group_dn = fields.Str(
        data_key="group_dn",
    )
    r""" Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups. """

    group_membership_filter = fields.Str(
        data_key="group_membership_filter",
    )
    r""" Specifies the custom filter used for group membership lookups from an LDAP server. """

    group_scope = fields.Str(
        data_key="group_scope",
        validate=enum_validation(['base', 'onelevel', 'subtree']),
    )
    r""" Specifies the default search scope for LDAP for group lookups:

* base - search the named entry only
* onelevel - search all entries immediately below the DN
* subtree - search the named DN entry and the entire subtree below the DN


Valid choices:

* base
* onelevel
* subtree """

    is_netgroup_byhost_enabled = fields.Boolean(
        data_key="is_netgroup_byhost_enabled",
    )
    r""" Specifies whether or not netgroup by host querying is enabled. """

    is_owner = fields.Boolean(
        data_key="is_owner",
    )
    r""" Specifies whether or not the SVM owns the LDAP client configuration. """

    ldaps_enabled = fields.Boolean(
        data_key="ldaps_enabled",
    )
    r""" Specifies whether or not LDAPS is enabled. """

    min_bind_level = fields.Str(
        data_key="min_bind_level",
        validate=enum_validation(['anonymous', 'simple', 'sasl']),
    )
    r""" The minimum bind authentication level. Possible values are:

* anonymous - anonymous bind
* simple - simple bind
* sasl - Simple Authentication and Security Layer (SASL) bind


Valid choices:

* anonymous
* simple
* sasl """

    netgroup_byhost_dn = fields.Str(
        data_key="netgroup_byhost_dn",
    )
    r""" Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups. """

    netgroup_byhost_scope = fields.Str(
        data_key="netgroup_byhost_scope",
        validate=enum_validation(['base', 'onelevel', 'subtree']),
    )
    r""" Specifies the default search scope for LDAP for netgroup by host lookups:

* base - search the named entry only
* onelevel - search all entries immediately below the DN
* subtree - search the named DN entry and the entire subtree below the DN


Valid choices:

* base
* onelevel
* subtree """

    netgroup_dn = fields.Str(
        data_key="netgroup_dn",
    )
    r""" Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups. """

    netgroup_scope = fields.Str(
        data_key="netgroup_scope",
        validate=enum_validation(['base', 'onelevel', 'subtree']),
    )
    r""" Specifies the default search scope for LDAP for netgroup lookups:

* base - search the named entry only
* onelevel - search all entries immediately below the DN
* subtree - search the named DN entry and the entire subtree below the DN


Valid choices:

* base
* onelevel
* subtree """

    port = Size(
        data_key="port",
        validate=integer_validation(minimum=1, maximum=65535),
    )
    r""" The port used to connect to the LDAP Servers.

Example: 389 """

    preferred_ad_servers = fields.List(fields.Str, data_key="preferred_ad_servers")
    r""" The preferred_ad_servers field of the ldap_service. """

    query_timeout = Size(
        data_key="query_timeout",
    )
    r""" Specifies the maximum time to wait for a query response from the LDAP server, in seconds. """

    referral_enabled = fields.Boolean(
        data_key="referral_enabled",
    )
    r""" Specifies whether or not LDAP referral is enabled. """

    schema = fields.Str(
        data_key="schema",
    )
    r""" The name of the schema template used by the SVM.

* AD-IDMU - Active Directory Identity Management for UNIX
* AD-SFU - Active Directory Services for UNIX
* MS-AD-BIS - Active Directory Identity Management for UNIX
* RFC-2307 - Schema based on RFC 2307
* Custom schema """

    servers = fields.List(fields.Str, data_key="servers")
    r""" The servers field of the ldap_service. """

    session_security = fields.Str(
        data_key="session_security",
        validate=enum_validation(['none', 'sign', 'seal']),
    )
    r""" Specifies the level of security to be used for LDAP communications:

* none - no signing or sealing
* sign - sign LDAP traffic
* seal - seal and sign LDAP traffic


Valid choices:

* none
* sign
* seal """

    skip_config_validation = fields.Boolean(
        data_key="skip_config_validation",
    )
    r""" Indicates whether or not the validation for the specified LDAP configuration is disabled. """

    status = fields.Nested("netapp_ontap.models.ldap_status.LdapStatusSchema", data_key="status", unknown=EXCLUDE)
    r""" The status field of the ldap_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the ldap_service. """

    try_channel_binding = fields.Boolean(
        data_key="try_channel_binding",
    )
    r""" Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. """

    use_start_tls = fields.Boolean(
        data_key="use_start_tls",
    )
    r""" Specifies whether or not to use Start TLS over LDAP connections. """

    user_dn = fields.Str(
        data_key="user_dn",
    )
    r""" Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups. """

    user_scope = fields.Str(
        data_key="user_scope",
        validate=enum_validation(['base', 'onelevel', 'subtree']),
    )
    r""" Specifies the default search scope for LDAP for user lookups:

* base - search the named entry only
* onelevel - search all entries immediately below the DN
* subtree - search the named DN entry and the entire subtree below the DN


Valid choices:

* base
* onelevel
* subtree """

    @property
    def resource(self):
        return LdapService

    gettable_fields = [
        "links",
        "ad_domain",
        "base_dn",
        "base_scope",
        "bind_as_cifs_server",
        "bind_dn",
        "group_dn",
        "group_membership_filter",
        "group_scope",
        "is_netgroup_byhost_enabled",
        "is_owner",
        "ldaps_enabled",
        "min_bind_level",
        "netgroup_byhost_dn",
        "netgroup_byhost_scope",
        "netgroup_dn",
        "netgroup_scope",
        "port",
        "preferred_ad_servers",
        "query_timeout",
        "referral_enabled",
        "schema",
        "servers",
        "session_security",
        "status",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "try_channel_binding",
        "use_start_tls",
        "user_dn",
        "user_scope",
    ]
    """links,ad_domain,base_dn,base_scope,bind_as_cifs_server,bind_dn,group_dn,group_membership_filter,group_scope,is_netgroup_byhost_enabled,is_owner,ldaps_enabled,min_bind_level,netgroup_byhost_dn,netgroup_byhost_scope,netgroup_dn,netgroup_scope,port,preferred_ad_servers,query_timeout,referral_enabled,schema,servers,session_security,status,svm.links,svm.name,svm.uuid,try_channel_binding,use_start_tls,user_dn,user_scope,"""

    patchable_fields = [
        "ad_domain",
        "base_dn",
        "base_scope",
        "bind_as_cifs_server",
        "bind_dn",
        "bind_password",
        "group_dn",
        "group_membership_filter",
        "group_scope",
        "is_netgroup_byhost_enabled",
        "ldaps_enabled",
        "min_bind_level",
        "netgroup_byhost_dn",
        "netgroup_byhost_scope",
        "netgroup_dn",
        "netgroup_scope",
        "port",
        "preferred_ad_servers",
        "query_timeout",
        "referral_enabled",
        "schema",
        "servers",
        "session_security",
        "skip_config_validation",
        "status",
        "svm.name",
        "svm.uuid",
        "try_channel_binding",
        "use_start_tls",
        "user_dn",
        "user_scope",
    ]
    """ad_domain,base_dn,base_scope,bind_as_cifs_server,bind_dn,bind_password,group_dn,group_membership_filter,group_scope,is_netgroup_byhost_enabled,ldaps_enabled,min_bind_level,netgroup_byhost_dn,netgroup_byhost_scope,netgroup_dn,netgroup_scope,port,preferred_ad_servers,query_timeout,referral_enabled,schema,servers,session_security,skip_config_validation,status,svm.name,svm.uuid,try_channel_binding,use_start_tls,user_dn,user_scope,"""

    postable_fields = [
        "ad_domain",
        "base_dn",
        "base_scope",
        "bind_as_cifs_server",
        "bind_dn",
        "bind_password",
        "group_dn",
        "group_membership_filter",
        "group_scope",
        "is_netgroup_byhost_enabled",
        "ldaps_enabled",
        "min_bind_level",
        "netgroup_byhost_dn",
        "netgroup_byhost_scope",
        "netgroup_dn",
        "netgroup_scope",
        "port",
        "preferred_ad_servers",
        "query_timeout",
        "referral_enabled",
        "schema",
        "servers",
        "session_security",
        "skip_config_validation",
        "status",
        "svm.name",
        "svm.uuid",
        "try_channel_binding",
        "use_start_tls",
        "user_dn",
        "user_scope",
    ]
    """ad_domain,base_dn,base_scope,bind_as_cifs_server,bind_dn,bind_password,group_dn,group_membership_filter,group_scope,is_netgroup_byhost_enabled,ldaps_enabled,min_bind_level,netgroup_byhost_dn,netgroup_byhost_scope,netgroup_dn,netgroup_scope,port,preferred_ad_servers,query_timeout,referral_enabled,schema,servers,session_security,skip_config_validation,status,svm.name,svm.uuid,try_channel_binding,use_start_tls,user_dn,user_scope,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in LdapService.get_collection(fields=field)]
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
            raise NetAppRestError("LdapService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class LdapService(Resource):
    """Allows interaction with LdapService objects on the host"""

    _schema = LdapServiceSchema
    _path = "/api/name-services/ldap"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the LDAP configurations for all SVMs.

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ldap service show")
        def ldap_service_show(
            fields: List[Choices.define(["ad_domain", "base_dn", "base_scope", "bind_as_cifs_server", "bind_dn", "bind_password", "group_dn", "group_membership_filter", "group_scope", "is_netgroup_byhost_enabled", "is_owner", "ldaps_enabled", "min_bind_level", "netgroup_byhost_dn", "netgroup_byhost_scope", "netgroup_dn", "netgroup_scope", "port", "preferred_ad_servers", "query_timeout", "referral_enabled", "schema", "servers", "session_security", "skip_config_validation", "try_channel_binding", "use_start_tls", "user_dn", "user_scope", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of LdapService resources

            Args:
                ad_domain: This parameter specifies the name of the Active Directory domain used to discover LDAP servers for use by this client. This is mutually exclusive with `servers` during POST and PATCH. 
                base_dn: Specifies the default base DN for all searches.
                base_scope: Specifies the default search scope for LDAP queries: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                bind_as_cifs_server: Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. 
                bind_dn: Specifies the user that binds to the LDAP servers.
                bind_password: Specifies the bind password for the LDAP servers.
                group_dn: Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups.
                group_membership_filter: Specifies the custom filter used for group membership lookups from an LDAP server. 
                group_scope: Specifies the default search scope for LDAP for group lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                is_netgroup_byhost_enabled: Specifies whether or not netgroup by host querying is enabled. 
                is_owner: Specifies whether or not the SVM owns the LDAP client configuration. 
                ldaps_enabled: Specifies whether or not LDAPS is enabled. 
                min_bind_level: The minimum bind authentication level. Possible values are: * anonymous - anonymous bind * simple - simple bind * sasl - Simple Authentication and Security Layer (SASL) bind 
                netgroup_byhost_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups.
                netgroup_byhost_scope: Specifies the default search scope for LDAP for netgroup by host lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                netgroup_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups.
                netgroup_scope: Specifies the default search scope for LDAP for netgroup lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                port: The port used to connect to the LDAP Servers.
                preferred_ad_servers: 
                query_timeout: Specifies the maximum time to wait for a query response from the LDAP server, in seconds. 
                referral_enabled: Specifies whether or not LDAP referral is enabled. 
                schema: The name of the schema template used by the SVM. * AD-IDMU - Active Directory Identity Management for UNIX * AD-SFU - Active Directory Services for UNIX * MS-AD-BIS - Active Directory Identity Management for UNIX * RFC-2307 - Schema based on RFC 2307 * Custom schema 
                servers: 
                session_security: Specifies the level of security to be used for LDAP communications: * none - no signing or sealing * sign - sign LDAP traffic * seal - seal and sign LDAP traffic 
                skip_config_validation: Indicates whether or not the validation for the specified LDAP configuration is disabled. 
                try_channel_binding: Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. 
                use_start_tls: Specifies whether or not to use Start TLS over LDAP connections. 
                user_dn: Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups.
                user_scope: Specifies the default search scope for LDAP for user lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
            """

            kwargs = {}
            if ad_domain is not None:
                kwargs["ad_domain"] = ad_domain
            if base_dn is not None:
                kwargs["base_dn"] = base_dn
            if base_scope is not None:
                kwargs["base_scope"] = base_scope
            if bind_as_cifs_server is not None:
                kwargs["bind_as_cifs_server"] = bind_as_cifs_server
            if bind_dn is not None:
                kwargs["bind_dn"] = bind_dn
            if bind_password is not None:
                kwargs["bind_password"] = bind_password
            if group_dn is not None:
                kwargs["group_dn"] = group_dn
            if group_membership_filter is not None:
                kwargs["group_membership_filter"] = group_membership_filter
            if group_scope is not None:
                kwargs["group_scope"] = group_scope
            if is_netgroup_byhost_enabled is not None:
                kwargs["is_netgroup_byhost_enabled"] = is_netgroup_byhost_enabled
            if is_owner is not None:
                kwargs["is_owner"] = is_owner
            if ldaps_enabled is not None:
                kwargs["ldaps_enabled"] = ldaps_enabled
            if min_bind_level is not None:
                kwargs["min_bind_level"] = min_bind_level
            if netgroup_byhost_dn is not None:
                kwargs["netgroup_byhost_dn"] = netgroup_byhost_dn
            if netgroup_byhost_scope is not None:
                kwargs["netgroup_byhost_scope"] = netgroup_byhost_scope
            if netgroup_dn is not None:
                kwargs["netgroup_dn"] = netgroup_dn
            if netgroup_scope is not None:
                kwargs["netgroup_scope"] = netgroup_scope
            if port is not None:
                kwargs["port"] = port
            if preferred_ad_servers is not None:
                kwargs["preferred_ad_servers"] = preferred_ad_servers
            if query_timeout is not None:
                kwargs["query_timeout"] = query_timeout
            if referral_enabled is not None:
                kwargs["referral_enabled"] = referral_enabled
            if schema is not None:
                kwargs["schema"] = schema
            if servers is not None:
                kwargs["servers"] = servers
            if session_security is not None:
                kwargs["session_security"] = session_security
            if skip_config_validation is not None:
                kwargs["skip_config_validation"] = skip_config_validation
            if try_channel_binding is not None:
                kwargs["try_channel_binding"] = try_channel_binding
            if use_start_tls is not None:
                kwargs["use_start_tls"] = use_start_tls
            if user_dn is not None:
                kwargs["user_dn"] = user_dn
            if user_scope is not None:
                kwargs["user_scope"] = user_scope
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return LdapService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all LdapService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["LdapService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an LDAP configuration of an SVM.
### Important notes
* Both mandatory and optional parameters of the LDAP configuration can be updated.
* The LDAP servers and Active Directory domain are mutually exclusive fields. These fields cannot be empty. At any point in time, either the LDAP servers or Active Directory domain must be populated.
* IPv6 must be enabled if IPv6 family addresses are specified.<br/>
</br>Configuring more than one LDAP server is recommended to avoid a sinlge point of failure.
Both FQDNs and IP addresses are supported for the "servers" field.
The Active Directory domain or LDAP servers are validated as part of this operation.<br/>
LDAP validation fails in the following scenarios:<br/>
1. The server does not have LDAP installed.
2. The server or Active Directory domain is invalid.
3. The server or Active Directory domain is unreachable<br/>

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["LdapService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["LdapService"], NetAppResponse]:
        r"""Creates an LDAP configuration for an SVM.
### Important notes
* Each SVM can have one LDAP configuration.
* The LDAP servers and Active Directory domain are mutually exclusive fields. These fields cannot be empty. At any point in time, either the LDAP servers or Active Directory domain must be populated.
* LDAP configuration with Active Directory domain cannot be created on an admin SVM.
* IPv6 must be enabled if IPv6 family addresses are specified.</br>
#### The following parameters are optional:
- preferred AD servers
- schema
- port
- ldaps_enabled
- min_bind_level
- bind_password
- base_scope
- use_start_tls
- session_security
- referral_enabled
- bind_as_cifs_server
- query_timeout
- user_dn
- user_scope
- group_dn
- group_scope
- netgroup_dn
- netgroup_scope
- netgroup_byhost_dn
- netgroup_byhost_scope
- is_netgroup_byhost_enabled
- group_membership_filter
- skip_config_validation
- try_channel_binding</br>
Configuring more than one LDAP server is recommended to avoid a single point of failure.
Both FQDNs and IP addresses are supported for the "servers" field.
The Acitve Directory domain or LDAP servers are validated as part of this operation.</br>
LDAP validation fails in the following scenarios:<br/>
1. The server does not have LDAP installed.
2. The server or Active Directory domain is invalid.
3. The server or Active Directory domain is unreachable.<br/>

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["LdapService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the LDAP configuration of the specified SVM. LDAP can be removed as a source from the ns-switch if LDAP is not used as a source for lookups.

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the LDAP configurations for all SVMs.

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves LDAP configuration for an SVM. All parameters for the LDAP configuration are displayed by default.

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
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
        r"""Creates an LDAP configuration for an SVM.
### Important notes
* Each SVM can have one LDAP configuration.
* The LDAP servers and Active Directory domain are mutually exclusive fields. These fields cannot be empty. At any point in time, either the LDAP servers or Active Directory domain must be populated.
* LDAP configuration with Active Directory domain cannot be created on an admin SVM.
* IPv6 must be enabled if IPv6 family addresses are specified.</br>
#### The following parameters are optional:
- preferred AD servers
- schema
- port
- ldaps_enabled
- min_bind_level
- bind_password
- base_scope
- use_start_tls
- session_security
- referral_enabled
- bind_as_cifs_server
- query_timeout
- user_dn
- user_scope
- group_dn
- group_scope
- netgroup_dn
- netgroup_scope
- netgroup_byhost_dn
- netgroup_byhost_scope
- is_netgroup_byhost_enabled
- group_membership_filter
- skip_config_validation
- try_channel_binding</br>
Configuring more than one LDAP server is recommended to avoid a single point of failure.
Both FQDNs and IP addresses are supported for the "servers" field.
The Acitve Directory domain or LDAP servers are validated as part of this operation.</br>
LDAP validation fails in the following scenarios:<br/>
1. The server does not have LDAP installed.
2. The server or Active Directory domain is invalid.
3. The server or Active Directory domain is unreachable.<br/>

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ldap service create")
        async def ldap_service_create(
        ) -> ResourceTable:
            """Create an instance of a LdapService resource

            Args:
                links: 
                ad_domain: This parameter specifies the name of the Active Directory domain used to discover LDAP servers for use by this client. This is mutually exclusive with `servers` during POST and PATCH. 
                base_dn: Specifies the default base DN for all searches.
                base_scope: Specifies the default search scope for LDAP queries: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                bind_as_cifs_server: Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. 
                bind_dn: Specifies the user that binds to the LDAP servers.
                bind_password: Specifies the bind password for the LDAP servers.
                group_dn: Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups.
                group_membership_filter: Specifies the custom filter used for group membership lookups from an LDAP server. 
                group_scope: Specifies the default search scope for LDAP for group lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                is_netgroup_byhost_enabled: Specifies whether or not netgroup by host querying is enabled. 
                is_owner: Specifies whether or not the SVM owns the LDAP client configuration. 
                ldaps_enabled: Specifies whether or not LDAPS is enabled. 
                min_bind_level: The minimum bind authentication level. Possible values are: * anonymous - anonymous bind * simple - simple bind * sasl - Simple Authentication and Security Layer (SASL) bind 
                netgroup_byhost_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups.
                netgroup_byhost_scope: Specifies the default search scope for LDAP for netgroup by host lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                netgroup_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups.
                netgroup_scope: Specifies the default search scope for LDAP for netgroup lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                port: The port used to connect to the LDAP Servers.
                preferred_ad_servers: 
                query_timeout: Specifies the maximum time to wait for a query response from the LDAP server, in seconds. 
                referral_enabled: Specifies whether or not LDAP referral is enabled. 
                schema: The name of the schema template used by the SVM. * AD-IDMU - Active Directory Identity Management for UNIX * AD-SFU - Active Directory Services for UNIX * MS-AD-BIS - Active Directory Identity Management for UNIX * RFC-2307 - Schema based on RFC 2307 * Custom schema 
                servers: 
                session_security: Specifies the level of security to be used for LDAP communications: * none - no signing or sealing * sign - sign LDAP traffic * seal - seal and sign LDAP traffic 
                skip_config_validation: Indicates whether or not the validation for the specified LDAP configuration is disabled. 
                status: 
                svm: 
                try_channel_binding: Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. 
                use_start_tls: Specifies whether or not to use Start TLS over LDAP connections. 
                user_dn: Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups.
                user_scope: Specifies the default search scope for LDAP for user lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if ad_domain is not None:
                kwargs["ad_domain"] = ad_domain
            if base_dn is not None:
                kwargs["base_dn"] = base_dn
            if base_scope is not None:
                kwargs["base_scope"] = base_scope
            if bind_as_cifs_server is not None:
                kwargs["bind_as_cifs_server"] = bind_as_cifs_server
            if bind_dn is not None:
                kwargs["bind_dn"] = bind_dn
            if bind_password is not None:
                kwargs["bind_password"] = bind_password
            if group_dn is not None:
                kwargs["group_dn"] = group_dn
            if group_membership_filter is not None:
                kwargs["group_membership_filter"] = group_membership_filter
            if group_scope is not None:
                kwargs["group_scope"] = group_scope
            if is_netgroup_byhost_enabled is not None:
                kwargs["is_netgroup_byhost_enabled"] = is_netgroup_byhost_enabled
            if is_owner is not None:
                kwargs["is_owner"] = is_owner
            if ldaps_enabled is not None:
                kwargs["ldaps_enabled"] = ldaps_enabled
            if min_bind_level is not None:
                kwargs["min_bind_level"] = min_bind_level
            if netgroup_byhost_dn is not None:
                kwargs["netgroup_byhost_dn"] = netgroup_byhost_dn
            if netgroup_byhost_scope is not None:
                kwargs["netgroup_byhost_scope"] = netgroup_byhost_scope
            if netgroup_dn is not None:
                kwargs["netgroup_dn"] = netgroup_dn
            if netgroup_scope is not None:
                kwargs["netgroup_scope"] = netgroup_scope
            if port is not None:
                kwargs["port"] = port
            if preferred_ad_servers is not None:
                kwargs["preferred_ad_servers"] = preferred_ad_servers
            if query_timeout is not None:
                kwargs["query_timeout"] = query_timeout
            if referral_enabled is not None:
                kwargs["referral_enabled"] = referral_enabled
            if schema is not None:
                kwargs["schema"] = schema
            if servers is not None:
                kwargs["servers"] = servers
            if session_security is not None:
                kwargs["session_security"] = session_security
            if skip_config_validation is not None:
                kwargs["skip_config_validation"] = skip_config_validation
            if status is not None:
                kwargs["status"] = status
            if svm is not None:
                kwargs["svm"] = svm
            if try_channel_binding is not None:
                kwargs["try_channel_binding"] = try_channel_binding
            if use_start_tls is not None:
                kwargs["use_start_tls"] = use_start_tls
            if user_dn is not None:
                kwargs["user_dn"] = user_dn
            if user_scope is not None:
                kwargs["user_scope"] = user_scope

            resource = LdapService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create LdapService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates an LDAP configuration of an SVM.
### Important notes
* Both mandatory and optional parameters of the LDAP configuration can be updated.
* The LDAP servers and Active Directory domain are mutually exclusive fields. These fields cannot be empty. At any point in time, either the LDAP servers or Active Directory domain must be populated.
* IPv6 must be enabled if IPv6 family addresses are specified.<br/>
</br>Configuring more than one LDAP server is recommended to avoid a sinlge point of failure.
Both FQDNs and IP addresses are supported for the "servers" field.
The Active Directory domain or LDAP servers are validated as part of this operation.<br/>
LDAP validation fails in the following scenarios:<br/>
1. The server does not have LDAP installed.
2. The server or Active Directory domain is invalid.
3. The server or Active Directory domain is unreachable<br/>

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ldap service modify")
        async def ldap_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a LdapService resource

            Args:
                ad_domain: This parameter specifies the name of the Active Directory domain used to discover LDAP servers for use by this client. This is mutually exclusive with `servers` during POST and PATCH. 
                query_ad_domain: This parameter specifies the name of the Active Directory domain used to discover LDAP servers for use by this client. This is mutually exclusive with `servers` during POST and PATCH. 
                base_dn: Specifies the default base DN for all searches.
                query_base_dn: Specifies the default base DN for all searches.
                base_scope: Specifies the default search scope for LDAP queries: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                query_base_scope: Specifies the default search scope for LDAP queries: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                bind_as_cifs_server: Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. 
                query_bind_as_cifs_server: Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. 
                bind_dn: Specifies the user that binds to the LDAP servers.
                query_bind_dn: Specifies the user that binds to the LDAP servers.
                bind_password: Specifies the bind password for the LDAP servers.
                query_bind_password: Specifies the bind password for the LDAP servers.
                group_dn: Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups.
                query_group_dn: Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups.
                group_membership_filter: Specifies the custom filter used for group membership lookups from an LDAP server. 
                query_group_membership_filter: Specifies the custom filter used for group membership lookups from an LDAP server. 
                group_scope: Specifies the default search scope for LDAP for group lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                query_group_scope: Specifies the default search scope for LDAP for group lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                is_netgroup_byhost_enabled: Specifies whether or not netgroup by host querying is enabled. 
                query_is_netgroup_byhost_enabled: Specifies whether or not netgroup by host querying is enabled. 
                is_owner: Specifies whether or not the SVM owns the LDAP client configuration. 
                query_is_owner: Specifies whether or not the SVM owns the LDAP client configuration. 
                ldaps_enabled: Specifies whether or not LDAPS is enabled. 
                query_ldaps_enabled: Specifies whether or not LDAPS is enabled. 
                min_bind_level: The minimum bind authentication level. Possible values are: * anonymous - anonymous bind * simple - simple bind * sasl - Simple Authentication and Security Layer (SASL) bind 
                query_min_bind_level: The minimum bind authentication level. Possible values are: * anonymous - anonymous bind * simple - simple bind * sasl - Simple Authentication and Security Layer (SASL) bind 
                netgroup_byhost_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups.
                query_netgroup_byhost_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups.
                netgroup_byhost_scope: Specifies the default search scope for LDAP for netgroup by host lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                query_netgroup_byhost_scope: Specifies the default search scope for LDAP for netgroup by host lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                netgroup_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups.
                query_netgroup_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups.
                netgroup_scope: Specifies the default search scope for LDAP for netgroup lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                query_netgroup_scope: Specifies the default search scope for LDAP for netgroup lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                port: The port used to connect to the LDAP Servers.
                query_port: The port used to connect to the LDAP Servers.
                preferred_ad_servers: 
                query_preferred_ad_servers: 
                query_timeout: Specifies the maximum time to wait for a query response from the LDAP server, in seconds. 
                query_query_timeout: Specifies the maximum time to wait for a query response from the LDAP server, in seconds. 
                referral_enabled: Specifies whether or not LDAP referral is enabled. 
                query_referral_enabled: Specifies whether or not LDAP referral is enabled. 
                schema: The name of the schema template used by the SVM. * AD-IDMU - Active Directory Identity Management for UNIX * AD-SFU - Active Directory Services for UNIX * MS-AD-BIS - Active Directory Identity Management for UNIX * RFC-2307 - Schema based on RFC 2307 * Custom schema 
                query_schema: The name of the schema template used by the SVM. * AD-IDMU - Active Directory Identity Management for UNIX * AD-SFU - Active Directory Services for UNIX * MS-AD-BIS - Active Directory Identity Management for UNIX * RFC-2307 - Schema based on RFC 2307 * Custom schema 
                servers: 
                query_servers: 
                session_security: Specifies the level of security to be used for LDAP communications: * none - no signing or sealing * sign - sign LDAP traffic * seal - seal and sign LDAP traffic 
                query_session_security: Specifies the level of security to be used for LDAP communications: * none - no signing or sealing * sign - sign LDAP traffic * seal - seal and sign LDAP traffic 
                skip_config_validation: Indicates whether or not the validation for the specified LDAP configuration is disabled. 
                query_skip_config_validation: Indicates whether or not the validation for the specified LDAP configuration is disabled. 
                try_channel_binding: Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. 
                query_try_channel_binding: Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. 
                use_start_tls: Specifies whether or not to use Start TLS over LDAP connections. 
                query_use_start_tls: Specifies whether or not to use Start TLS over LDAP connections. 
                user_dn: Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups.
                query_user_dn: Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups.
                user_scope: Specifies the default search scope for LDAP for user lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                query_user_scope: Specifies the default search scope for LDAP for user lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
            """

            kwargs = {}
            changes = {}
            if query_ad_domain is not None:
                kwargs["ad_domain"] = query_ad_domain
            if query_base_dn is not None:
                kwargs["base_dn"] = query_base_dn
            if query_base_scope is not None:
                kwargs["base_scope"] = query_base_scope
            if query_bind_as_cifs_server is not None:
                kwargs["bind_as_cifs_server"] = query_bind_as_cifs_server
            if query_bind_dn is not None:
                kwargs["bind_dn"] = query_bind_dn
            if query_bind_password is not None:
                kwargs["bind_password"] = query_bind_password
            if query_group_dn is not None:
                kwargs["group_dn"] = query_group_dn
            if query_group_membership_filter is not None:
                kwargs["group_membership_filter"] = query_group_membership_filter
            if query_group_scope is not None:
                kwargs["group_scope"] = query_group_scope
            if query_is_netgroup_byhost_enabled is not None:
                kwargs["is_netgroup_byhost_enabled"] = query_is_netgroup_byhost_enabled
            if query_is_owner is not None:
                kwargs["is_owner"] = query_is_owner
            if query_ldaps_enabled is not None:
                kwargs["ldaps_enabled"] = query_ldaps_enabled
            if query_min_bind_level is not None:
                kwargs["min_bind_level"] = query_min_bind_level
            if query_netgroup_byhost_dn is not None:
                kwargs["netgroup_byhost_dn"] = query_netgroup_byhost_dn
            if query_netgroup_byhost_scope is not None:
                kwargs["netgroup_byhost_scope"] = query_netgroup_byhost_scope
            if query_netgroup_dn is not None:
                kwargs["netgroup_dn"] = query_netgroup_dn
            if query_netgroup_scope is not None:
                kwargs["netgroup_scope"] = query_netgroup_scope
            if query_port is not None:
                kwargs["port"] = query_port
            if query_preferred_ad_servers is not None:
                kwargs["preferred_ad_servers"] = query_preferred_ad_servers
            if query_query_timeout is not None:
                kwargs["query_timeout"] = query_query_timeout
            if query_referral_enabled is not None:
                kwargs["referral_enabled"] = query_referral_enabled
            if query_schema is not None:
                kwargs["schema"] = query_schema
            if query_servers is not None:
                kwargs["servers"] = query_servers
            if query_session_security is not None:
                kwargs["session_security"] = query_session_security
            if query_skip_config_validation is not None:
                kwargs["skip_config_validation"] = query_skip_config_validation
            if query_try_channel_binding is not None:
                kwargs["try_channel_binding"] = query_try_channel_binding
            if query_use_start_tls is not None:
                kwargs["use_start_tls"] = query_use_start_tls
            if query_user_dn is not None:
                kwargs["user_dn"] = query_user_dn
            if query_user_scope is not None:
                kwargs["user_scope"] = query_user_scope

            if ad_domain is not None:
                changes["ad_domain"] = ad_domain
            if base_dn is not None:
                changes["base_dn"] = base_dn
            if base_scope is not None:
                changes["base_scope"] = base_scope
            if bind_as_cifs_server is not None:
                changes["bind_as_cifs_server"] = bind_as_cifs_server
            if bind_dn is not None:
                changes["bind_dn"] = bind_dn
            if bind_password is not None:
                changes["bind_password"] = bind_password
            if group_dn is not None:
                changes["group_dn"] = group_dn
            if group_membership_filter is not None:
                changes["group_membership_filter"] = group_membership_filter
            if group_scope is not None:
                changes["group_scope"] = group_scope
            if is_netgroup_byhost_enabled is not None:
                changes["is_netgroup_byhost_enabled"] = is_netgroup_byhost_enabled
            if is_owner is not None:
                changes["is_owner"] = is_owner
            if ldaps_enabled is not None:
                changes["ldaps_enabled"] = ldaps_enabled
            if min_bind_level is not None:
                changes["min_bind_level"] = min_bind_level
            if netgroup_byhost_dn is not None:
                changes["netgroup_byhost_dn"] = netgroup_byhost_dn
            if netgroup_byhost_scope is not None:
                changes["netgroup_byhost_scope"] = netgroup_byhost_scope
            if netgroup_dn is not None:
                changes["netgroup_dn"] = netgroup_dn
            if netgroup_scope is not None:
                changes["netgroup_scope"] = netgroup_scope
            if port is not None:
                changes["port"] = port
            if preferred_ad_servers is not None:
                changes["preferred_ad_servers"] = preferred_ad_servers
            if query_timeout is not None:
                changes["query_timeout"] = query_timeout
            if referral_enabled is not None:
                changes["referral_enabled"] = referral_enabled
            if schema is not None:
                changes["schema"] = schema
            if servers is not None:
                changes["servers"] = servers
            if session_security is not None:
                changes["session_security"] = session_security
            if skip_config_validation is not None:
                changes["skip_config_validation"] = skip_config_validation
            if try_channel_binding is not None:
                changes["try_channel_binding"] = try_channel_binding
            if use_start_tls is not None:
                changes["use_start_tls"] = use_start_tls
            if user_dn is not None:
                changes["user_dn"] = user_dn
            if user_scope is not None:
                changes["user_scope"] = user_scope

            if hasattr(LdapService, "find"):
                resource = LdapService.find(
                    **kwargs
                )
            else:
                resource = LdapService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify LdapService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the LDAP configuration of the specified SVM. LDAP can be removed as a source from the ns-switch if LDAP is not used as a source for lookups.

### Learn more
* [`DOC /name-services/ldap`](#docs-name-services-name-services_ldap)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="ldap service delete")
        async def ldap_service_delete(
        ) -> None:
            """Delete an instance of a LdapService resource

            Args:
                ad_domain: This parameter specifies the name of the Active Directory domain used to discover LDAP servers for use by this client. This is mutually exclusive with `servers` during POST and PATCH. 
                base_dn: Specifies the default base DN for all searches.
                base_scope: Specifies the default search scope for LDAP queries: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                bind_as_cifs_server: Specifies whether or not CIFS server's credentials are used to bind to the LDAP server. 
                bind_dn: Specifies the user that binds to the LDAP servers.
                bind_password: Specifies the bind password for the LDAP servers.
                group_dn: Specifies the group Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for group lookups.
                group_membership_filter: Specifies the custom filter used for group membership lookups from an LDAP server. 
                group_scope: Specifies the default search scope for LDAP for group lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                is_netgroup_byhost_enabled: Specifies whether or not netgroup by host querying is enabled. 
                is_owner: Specifies whether or not the SVM owns the LDAP client configuration. 
                ldaps_enabled: Specifies whether or not LDAPS is enabled. 
                min_bind_level: The minimum bind authentication level. Possible values are: * anonymous - anonymous bind * simple - simple bind * sasl - Simple Authentication and Security Layer (SASL) bind 
                netgroup_byhost_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup by host lookups.
                netgroup_byhost_scope: Specifies the default search scope for LDAP for netgroup by host lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                netgroup_dn: Specifies the netgroup Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for netgroup lookups.
                netgroup_scope: Specifies the default search scope for LDAP for netgroup lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
                port: The port used to connect to the LDAP Servers.
                preferred_ad_servers: 
                query_timeout: Specifies the maximum time to wait for a query response from the LDAP server, in seconds. 
                referral_enabled: Specifies whether or not LDAP referral is enabled. 
                schema: The name of the schema template used by the SVM. * AD-IDMU - Active Directory Identity Management for UNIX * AD-SFU - Active Directory Services for UNIX * MS-AD-BIS - Active Directory Identity Management for UNIX * RFC-2307 - Schema based on RFC 2307 * Custom schema 
                servers: 
                session_security: Specifies the level of security to be used for LDAP communications: * none - no signing or sealing * sign - sign LDAP traffic * seal - seal and sign LDAP traffic 
                skip_config_validation: Indicates whether or not the validation for the specified LDAP configuration is disabled. 
                try_channel_binding: Specifies whether or not channel binding is attempted in the case of TLS/LDAPS. 
                use_start_tls: Specifies whether or not to use Start TLS over LDAP connections. 
                user_dn: Specifies the user Distinguished Name (DN) that is used as the starting point in the LDAP directory tree for user lookups.
                user_scope: Specifies the default search scope for LDAP for user lookups: * base - search the named entry only * onelevel - search all entries immediately below the DN * subtree - search the named DN entry and the entire subtree below the DN 
            """

            kwargs = {}
            if ad_domain is not None:
                kwargs["ad_domain"] = ad_domain
            if base_dn is not None:
                kwargs["base_dn"] = base_dn
            if base_scope is not None:
                kwargs["base_scope"] = base_scope
            if bind_as_cifs_server is not None:
                kwargs["bind_as_cifs_server"] = bind_as_cifs_server
            if bind_dn is not None:
                kwargs["bind_dn"] = bind_dn
            if bind_password is not None:
                kwargs["bind_password"] = bind_password
            if group_dn is not None:
                kwargs["group_dn"] = group_dn
            if group_membership_filter is not None:
                kwargs["group_membership_filter"] = group_membership_filter
            if group_scope is not None:
                kwargs["group_scope"] = group_scope
            if is_netgroup_byhost_enabled is not None:
                kwargs["is_netgroup_byhost_enabled"] = is_netgroup_byhost_enabled
            if is_owner is not None:
                kwargs["is_owner"] = is_owner
            if ldaps_enabled is not None:
                kwargs["ldaps_enabled"] = ldaps_enabled
            if min_bind_level is not None:
                kwargs["min_bind_level"] = min_bind_level
            if netgroup_byhost_dn is not None:
                kwargs["netgroup_byhost_dn"] = netgroup_byhost_dn
            if netgroup_byhost_scope is not None:
                kwargs["netgroup_byhost_scope"] = netgroup_byhost_scope
            if netgroup_dn is not None:
                kwargs["netgroup_dn"] = netgroup_dn
            if netgroup_scope is not None:
                kwargs["netgroup_scope"] = netgroup_scope
            if port is not None:
                kwargs["port"] = port
            if preferred_ad_servers is not None:
                kwargs["preferred_ad_servers"] = preferred_ad_servers
            if query_timeout is not None:
                kwargs["query_timeout"] = query_timeout
            if referral_enabled is not None:
                kwargs["referral_enabled"] = referral_enabled
            if schema is not None:
                kwargs["schema"] = schema
            if servers is not None:
                kwargs["servers"] = servers
            if session_security is not None:
                kwargs["session_security"] = session_security
            if skip_config_validation is not None:
                kwargs["skip_config_validation"] = skip_config_validation
            if try_channel_binding is not None:
                kwargs["try_channel_binding"] = try_channel_binding
            if use_start_tls is not None:
                kwargs["use_start_tls"] = use_start_tls
            if user_dn is not None:
                kwargs["user_dn"] = user_dn
            if user_scope is not None:
                kwargs["user_scope"] = user_scope

            if hasattr(LdapService, "find"):
                resource = LdapService.find(
                    **kwargs
                )
            else:
                resource = LdapService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete LdapService: %s" % err)


