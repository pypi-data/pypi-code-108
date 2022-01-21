r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API is used to retrieve and display relevant information pertaining to the SAML service provider configuration in the cluster. The POST request creates a SAML service provider configuration if there is none present.  The DELETE request removes the SAML service provider configuration.  The PATCH request enables and disables SAML in the cluster.  Various responses are shown in the examples below.
<br />
---
## Examples
### Retrieving the SAML service provider configuration in the cluster
The following output shows the SAML service provider configuration in the cluster.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecuritySamlSp

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecuritySamlSp()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
SecuritySamlSp(
    {
        "host": "172.21.74.181",
        "enabled": True,
        "certificate": {
            "ca": "cluster1",
            "common_name": "cluster1",
            "serial_number": "156F10C3EB4C51C1",
        },
        "idp_uri": "https://examplelab.customer.com/idp/Metadata",
        "_links": {"self": {"href": "/api/security/authentication/cluster/saml-sp"}},
    }
)

```
</div>
</div>

---
### Creating the SAML service provider configuration
The following output shows how to create a SAML service provider configuration in the cluster.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecuritySamlSp

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecuritySamlSp()
    resource.idp_uri = "https://examplelab.customer.com/idp/Metadata"
    resource.host = "172.21.74.181"
    resource.certificate = {"ca": "cluster1", "serial_number": "156F10C3EB4C51C1"}
    resource.post(hydrate=True)
    print(resource)

```

---
### Updating the SAML service provider configuration
The following output shows how to enable a SAML service provider configuration in the cluster.
<br/>Disabling the configuration requires the client to be authenticated through SAML prior to performing the operation.
<br />
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecuritySamlSp

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecuritySamlSp()
    resource.enabled = True
    resource.patch()

```

---
### Deleting the SAML service provider configuration
---
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SecuritySamlSp

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SecuritySamlSp()
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


__all__ = ["SecuritySamlSp", "SecuritySamlSpSchema"]
__pdoc__ = {
    "SecuritySamlSpSchema.resource": False,
    "SecuritySamlSp.security_saml_sp_show": False,
    "SecuritySamlSp.security_saml_sp_create": False,
    "SecuritySamlSp.security_saml_sp_modify": False,
    "SecuritySamlSp.security_saml_sp_delete": False,
}


class SecuritySamlSpSchema(ResourceSchema):
    """The fields of the SecuritySamlSp object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the security_saml_sp. """

    certificate = fields.Nested("netapp_ontap.models.security_saml_sp_certificate.SecuritySamlSpCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the security_saml_sp. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" The SAML service provider is enabled.  Valid for PATCH and GET operations only. """

    host = fields.Str(
        data_key="host",
    )
    r""" The SAML service provider host. """

    idp_uri = fields.Str(
        data_key="idp_uri",
    )
    r""" The identity provider (IdP) metadata location. Required for POST operations.

Example: https://idp.example.com/FederationMetadata/2007-06/FederationMetadata.xml """

    @property
    def resource(self):
        return SecuritySamlSp

    gettable_fields = [
        "links",
        "certificate",
        "enabled",
        "host",
        "idp_uri",
    ]
    """links,certificate,enabled,host,idp_uri,"""

    patchable_fields = [
        "enabled",
    ]
    """enabled,"""

    postable_fields = [
        "certificate",
        "host",
        "idp_uri",
    ]
    """certificate,host,idp_uri,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SecuritySamlSp.get_collection(fields=field)]
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
            raise NetAppRestError("SecuritySamlSp modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SecuritySamlSp(Resource):
    """Allows interaction with SecuritySamlSp objects on the host"""

    _schema = SecuritySamlSpSchema
    _path = "/api/security/authentication/cluster/saml-sp"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves a SAML service provider configuration.
### Learn more
* [`DOC /security/authentication/cluster/saml-sp`](#docs-security-security_authentication_cluster_saml-sp)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security saml sp show")
        def security_saml_sp_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single SecuritySamlSp resource

            Args:
                enabled: The SAML service provider is enabled.  Valid for PATCH and GET operations only.
                host: The SAML service provider host.
                idp_uri: The identity provider (IdP) metadata location. Required for POST operations.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if host is not None:
                kwargs["host"] = host
            if idp_uri is not None:
                kwargs["idp_uri"] = idp_uri
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = SecuritySamlSp(
                **kwargs
            )
            resource.get()
            return [resource]

    def post(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Creates a SAML service provider configuration. Note that "common_name" is mutually exclusive with "serial_number" and "ca" in POST. SAML will initially be disabled, requiring a patch to set "enabled" to "true", so that the user has time to complete the setup of the IdP.
### Required properties
* `idp_uri`
### Optional properties
* `certificate`
* `enabled`
* `host`

### Learn more
* [`DOC /security/authentication/cluster/saml-sp`](#docs-security-security_authentication_cluster_saml-sp)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security saml sp create")
        async def security_saml_sp_create(
        ) -> ResourceTable:
            """Create an instance of a SecuritySamlSp resource

            Args:
                links: 
                certificate: 
                enabled: The SAML service provider is enabled.  Valid for PATCH and GET operations only.
                host: The SAML service provider host.
                idp_uri: The identity provider (IdP) metadata location. Required for POST operations.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if certificate is not None:
                kwargs["certificate"] = certificate
            if enabled is not None:
                kwargs["enabled"] = enabled
            if host is not None:
                kwargs["host"] = host
            if idp_uri is not None:
                kwargs["idp_uri"] = idp_uri

            resource = SecuritySamlSp(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SecuritySamlSp: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates a SAML service provider configuration.
### Learn more
* [`DOC /security/authentication/cluster/saml-sp`](#docs-security-security_authentication_cluster_saml-sp)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security saml sp modify")
        async def security_saml_sp_modify(
        ) -> ResourceTable:
            """Modify an instance of a SecuritySamlSp resource

            Args:
                enabled: The SAML service provider is enabled.  Valid for PATCH and GET operations only.
                query_enabled: The SAML service provider is enabled.  Valid for PATCH and GET operations only.
                host: The SAML service provider host.
                query_host: The SAML service provider host.
                idp_uri: The identity provider (IdP) metadata location. Required for POST operations.
                query_idp_uri: The identity provider (IdP) metadata location. Required for POST operations.
            """

            kwargs = {}
            changes = {}
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_host is not None:
                kwargs["host"] = query_host
            if query_idp_uri is not None:
                kwargs["idp_uri"] = query_idp_uri

            if enabled is not None:
                changes["enabled"] = enabled
            if host is not None:
                changes["host"] = host
            if idp_uri is not None:
                changes["idp_uri"] = idp_uri

            if hasattr(SecuritySamlSp, "find"):
                resource = SecuritySamlSp.find(
                    **kwargs
                )
            else:
                resource = SecuritySamlSp()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SecuritySamlSp: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a SAML service provider configuration.
### Learn more
* [`DOC /security/authentication/cluster/saml-sp`](#docs-security-security_authentication_cluster_saml-sp)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="security saml sp delete")
        async def security_saml_sp_delete(
        ) -> None:
            """Delete an instance of a SecuritySamlSp resource

            Args:
                enabled: The SAML service provider is enabled.  Valid for PATCH and GET operations only.
                host: The SAML service provider host.
                idp_uri: The identity provider (IdP) metadata location. Required for POST operations.
            """

            kwargs = {}
            if enabled is not None:
                kwargs["enabled"] = enabled
            if host is not None:
                kwargs["host"] = host
            if idp_uri is not None:
                kwargs["idp_uri"] = idp_uri

            if hasattr(SecuritySamlSp, "find"):
                resource = SecuritySamlSp.find(
                    **kwargs
                )
            else:
                resource = SecuritySamlSp()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SecuritySamlSp: %s" % err)


