r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Azure Key Vault (AKV) is a cloud key management service (KMS) that provides a secure store for secrets. This feature
allows ONTAP to securely store its encryption keys using AKV.
In order to use AKV with ONTAP, you must first deploy an Azure application with the appropriate access to an AKV and then provide
ONTAP with the necessary details, such as key vault name, application ID so that ONTAP can communicate with the deployed Azure application.
The properties "state", "azure_reachability" and "ekmip_reachability" are considered advanced properties and are populated only when explicitly requested.
## Examples
### Creating an AKV for a cluster using the client secret authentication method
The example AKV is configured at the cluster-scope. Note the <i>return_records=true</i> query parameter is used to obtain the newly created key manager configuration.<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault()
    resource.client_id = "client1"
    resource.tenant_id = "tenant1"
    resource.name = "https:://mykeyvault.azure.vault.net/"
    resource.key_id = "https://keyvault-test.vault.azure.net/keys/key1/a8e619fd8f234db3b0b95c59540e2a74"
    resource.client_secret = "myclientPwd"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
AzureKeyVault(
    {
        "_links": {
            "self": {
                "href": "/api/security/azure-key-vaults/85619643-9a06-11ea-8d52-005056bbeba5"
            }
        },
        "key_id": "https://keyvault-test.vault.azure.net/keys/key1",
        "uuid": "85619643-9a06-11ea-8d52-005056bbeba5",
        "client_id": "client1",
        "tenant_id": "tenant1",
        "name": "https:://mykeyvault.azure.vault.net/",
    }
)

```
</div>
</div>

---
### Creating an AKV for an SVM using the certificate authentication method
The example AKV is configured for a specific SVM. Note the <i>return_records=true</i> query parameter is used to obtain the newly created key manager configuration.<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault()
    resource.svm = {"uuid": "4f7abf4c-9a07-11ea-8d52-005056bbeba5"}
    resource.client_id = "client1"
    resource.tenant_id = "tenant1"
    resource.name = "https:://mykeyvault.azure.vault.net/"
    resource.key_id = "https://keyvault-test.vault.azure.net/keys/key1"
    resource.client_certificate = "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"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
AzureKeyVault(
    {
        "_links": {
            "self": {
                "href": "/api/security/azure-key-vaults/024cd3cf-9a08-11ea-8d52-005056bbeba5"
            }
        },
        "key_id": "https://keyvault-test.vault.azure.net/keys/key1",
        "uuid": "024cd3cf-9a08-11ea-8d52-005056bbeba5",
        "client_id": "client1",
        "tenant_id": "tenant1",
        "svm": {"uuid": "4f7abf4c-9a07-11ea-8d52-005056bbeba5", "name": "vs0"},
        "name": "https:://mykeyvault.azure.vault.net/",
    }
)

```
</div>
</div>

---
### Retrieving the AKVs configured for all clusters and SVMs
The following example shows how to retrieve all configured AKVs along with their configurations.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(AzureKeyVault.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
[
    AzureKeyVault(
        {
            "_links": {
                "self": {
                    "href": "/api/security/azure-key-vaults/024cd3cf-9a08-11ea-8d52-005056bbeba5"
                }
            },
            "key_id": "https://keyvault-test.vault.azure.net/keys/key1",
            "uuid": "024cd3cf-9a08-11ea-8d52-005056bbeba5",
            "authentication_method": "client_secret",
            "client_id": "client1",
            "tenant_id": "tenant1",
            "scope": "svm",
            "svm": {"uuid": "4f7abf4c-9a07-11ea-8d52-005056bbeba5", "name": "vs0"},
            "name": "https:://mykeyvault.azure.vault.net/",
        }
    ),
    AzureKeyVault(
        {
            "_links": {
                "self": {
                    "href": "/api/security/azure-key-vaults/85619643-9a06-11ea-8d52-005056bbeba5"
                }
            },
            "key_id": "https://keyvault-test.vault.azure.net/keys/key1",
            "uuid": "85619643-9a06-11ea-8d52-005056bbeba5",
            "authentication_method": "certificate",
            "client_id": "client1",
            "tenant_id": "tenant1",
            "scope": "cluster",
            "name": "https:://mykeyvault.azure.vault.net/",
        }
    ),
]

```
</div>
</div>

---
### Retrieving the AKV configured for a specific SVM
The following example retrieves a configured AKV for a specific SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
AzureKeyVault(
    {
        "_links": {
            "self": {
                "href": "/api/security/azure-key-vaults/85619643-9a06-11ea-8d52-005056bbeba5"
            }
        },
        "key_id": "https://keyvault-test.vault.azure.net/keys/key1",
        "uuid": "85619643-9a06-11ea-8d52-005056bbeba5",
        "authentication_method": "client_secret",
        "client_id": "client1",
        "tenant_id": "tenant1",
        "scope": "cluster",
        "name": "https:://mykeyvault.azure.vault.net/",
    }
)

```
</div>
</div>

---
### Retrieving the advanced properties of an AKV configured for a specific SVM
The following example retrieves the advanced properties of a configured AKV for a specific SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.get(fields='state,azure_reachability,ekmip_reachability"')
    print(resource)

```

---
### Updating the client secret of a specific SVM
The following example updates the client secret of a configured AKV for a specific SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.client_secret = "newSecret"
    resource.patch()

```

---
### Updating the client certificate and key of a specific SVM
The following example updates the client certificate and key of a configured AKV for a specific SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.client_certificate = "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"
    resource.patch()

```

---
### Deleting an AKV configuration for a specific SVM
The following example deletes a configured AKV for a specific SVM.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.delete()

```

---
### Restoring the keys for a specific SVM configured with an AKV
The following example restores all the keys of a specific SVM configured with an AKV.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.restore()

```
<div class="try_it_out">
<input id="example8_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example8_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example8_result" class="try_it_out_content">
```
AzureKeyVault({})

```
</div>
</div>

---
### Rekeying the internal key for a specific SVM configured with an AKV
The following example rekeys the internal key of a specific SVM configured with an AKV.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import AzureKeyVault

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = AzureKeyVault(uuid="85619643-9a06-11ea-8d52-005056bbeba5")
    resource.rekey_internal()

```
<div class="try_it_out">
<input id="example9_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example9_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example9_result" class="try_it_out_content">
```
AzureKeyVault({})

```
</div>
</div>

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


__all__ = ["AzureKeyVault", "AzureKeyVaultSchema"]
__pdoc__ = {
    "AzureKeyVaultSchema.resource": False,
    "AzureKeyVault.azure_key_vault_show": False,
    "AzureKeyVault.azure_key_vault_create": False,
    "AzureKeyVault.azure_key_vault_modify": False,
    "AzureKeyVault.azure_key_vault_delete": False,
}


class AzureKeyVaultSchema(ResourceSchema):
    """The fields of the AzureKeyVault object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the azure_key_vault. """

    authentication_method = fields.Str(
        data_key="authentication_method",
        validate=enum_validation(['client_secret', 'certificate']),
    )
    r""" Authentication method for the AKV instance.

Valid choices:

* client_secret
* certificate """

    azure_reachability = fields.Nested("netapp_ontap.models.azure_key_vault_connectivity.AzureKeyVaultConnectivitySchema", data_key="azure_reachability", unknown=EXCLUDE)
    r""" The azure_reachability field of the azure_key_vault. """

    client_certificate = fields.Str(
        data_key="client_certificate",
    )
    r""" PKCS12 Certificate used by the application to prove its identity to AKV.

Example: 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 """

    client_id = fields.Str(
        data_key="client_id",
    )
    r""" Application client ID of the deployed Azure application with appropriate access to an AKV.

Example: aaaaaaaa-bbbb-aaaa-bbbb-aaaaaaaaaaaa """

    client_secret = fields.Str(
        data_key="client_secret",
    )
    r""" Secret used by the application to prove its identity to AKV.

Example: abcdef """

    ekmip_reachability = fields.List(fields.Nested("netapp_ontap.models.ekmip_server_connectivity.EkmipServerConnectivitySchema", unknown=EXCLUDE), data_key="ekmip_reachability")
    r""" The ekmip_reachability field of the azure_key_vault. """

    key_id = fields.Str(
        data_key="key_id",
    )
    r""" Key Identifier of AKV key encryption key.

Example: https://keyvault1.vault.azure.net/keys/key1 """

    name = fields.Str(
        data_key="name",
    )
    r""" Name of the deployed AKV that will be used by ONTAP for storing keys.

Example: https://kmip-akv-keyvault.vault.azure.net/ """

    proxy_host = fields.Str(
        data_key="proxy_host",
    )
    r""" Proxy host.

Example: proxy.eng.com """

    proxy_password = fields.Str(
        data_key="proxy_password",
    )
    r""" Proxy password. Password is not audited.

Example: proxypassword """

    proxy_port = Size(
        data_key="proxy_port",
    )
    r""" Proxy port.

Example: 1234 """

    proxy_type = fields.Str(
        data_key="proxy_type",
        validate=enum_validation(['http', 'https']),
    )
    r""" Type of proxy.

Valid choices:

* http
* https """

    proxy_username = fields.Str(
        data_key="proxy_username",
    )
    r""" Proxy username.

Example: proxyuser """

    scope = fields.Str(
        data_key="scope",
        validate=enum_validation(['svm', 'cluster']),
    )
    r""" Set to "svm" for interfaces owned by an SVM. Otherwise, set to "cluster".

Valid choices:

* svm
* cluster """

    state = fields.Nested("netapp_ontap.models.azure_key_vault_state.AzureKeyVaultStateSchema", data_key="state", unknown=EXCLUDE)
    r""" The state field of the azure_key_vault. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the azure_key_vault. """

    tenant_id = fields.Str(
        data_key="tenant_id",
    )
    r""" Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.

Example: zzzzzzzz-yyyy-zzzz-yyyy-zzzzzzzzzzzz """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" A unique identifier for the Azure Key Vault (AKV).

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return AzureKeyVault

    gettable_fields = [
        "links",
        "authentication_method",
        "azure_reachability",
        "client_id",
        "ekmip_reachability",
        "key_id",
        "name",
        "proxy_host",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "scope",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "tenant_id",
        "uuid",
    ]
    """links,authentication_method,azure_reachability,client_id,ekmip_reachability,key_id,name,proxy_host,proxy_port,proxy_type,proxy_username,scope,state,svm.links,svm.name,svm.uuid,tenant_id,uuid,"""

    patchable_fields = [
        "authentication_method",
        "client_certificate",
        "client_id",
        "client_secret",
        "key_id",
        "proxy_host",
        "proxy_password",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "svm.name",
        "svm.uuid",
        "tenant_id",
    ]
    """authentication_method,client_certificate,client_id,client_secret,key_id,proxy_host,proxy_password,proxy_port,proxy_type,proxy_username,svm.name,svm.uuid,tenant_id,"""

    postable_fields = [
        "authentication_method",
        "client_certificate",
        "client_id",
        "client_secret",
        "key_id",
        "name",
        "proxy_host",
        "proxy_password",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "svm.name",
        "svm.uuid",
        "tenant_id",
    ]
    """authentication_method,client_certificate,client_id,client_secret,key_id,name,proxy_host,proxy_password,proxy_port,proxy_type,proxy_username,svm.name,svm.uuid,tenant_id,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in AzureKeyVault.get_collection(fields=field)]
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
            raise NetAppRestError("AzureKeyVault modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class AzureKeyVault(Resource):
    """Allows interaction with AzureKeyVault objects on the host"""

    _schema = AzureKeyVaultSchema
    _path = "/api/security/azure-key-vaults"
    _keys = ["uuid"]
    _action_form_data_parameters = { 'file':'file', }

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves AKVs configured for all clusters and SVMs.
### Related ONTAP commands
* `security key-manager external azure show`
* `security key-manager external azure check`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="azure key vault show")
        def azure_key_vault_show(
            fields: List[Choices.define(["authentication_method", "client_certificate", "client_id", "client_secret", "key_id", "name", "proxy_host", "proxy_password", "proxy_port", "proxy_type", "proxy_username", "scope", "tenant_id", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of AzureKeyVault resources

            Args:
                authentication_method: Authentication method for the AKV instance.
                client_certificate: PKCS12 Certificate used by the application to prove its identity to AKV.
                client_id: Application client ID of the deployed Azure application with appropriate access to an AKV.
                client_secret: Secret used by the application to prove its identity to AKV.
                key_id: Key Identifier of AKV key encryption key.
                name: Name of the deployed AKV that will be used by ONTAP for storing keys.
                proxy_host: Proxy host.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                tenant_id: Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
                uuid: A unique identifier for the Azure Key Vault (AKV).
            """

            kwargs = {}
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if client_certificate is not None:
                kwargs["client_certificate"] = client_certificate
            if client_id is not None:
                kwargs["client_id"] = client_id
            if client_secret is not None:
                kwargs["client_secret"] = client_secret
            if key_id is not None:
                kwargs["key_id"] = key_id
            if name is not None:
                kwargs["name"] = name
            if proxy_host is not None:
                kwargs["proxy_host"] = proxy_host
            if proxy_password is not None:
                kwargs["proxy_password"] = proxy_password
            if proxy_port is not None:
                kwargs["proxy_port"] = proxy_port
            if proxy_type is not None:
                kwargs["proxy_type"] = proxy_type
            if proxy_username is not None:
                kwargs["proxy_username"] = proxy_username
            if scope is not None:
                kwargs["scope"] = scope
            if tenant_id is not None:
                kwargs["tenant_id"] = tenant_id
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return AzureKeyVault.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all AzureKeyVault resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["AzureKeyVault"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the AKV configuration.
### Optional properties
* `client_secret` - New secret used to prove the application's identity to the AKV.
* `client_certificate` - New PKCS12 certificate used to prove the application's identity to the AKV.
* `key_id`- Key Identifier of the new AKV key encryption key.
* `proxy_type` - Type of proxy (http, https etc.) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
* `client_id` - Application (client) ID of the deployed Azure application with appropriate access to an AKV.
* `tenant_id` - Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
### Related ONTAP commands
* `security key-manager external azure update-client-secret`
* `security key-manager external azure update-credentials`
* `security key-manager external azure rekey-external`
* `security key-manager external azure update-config`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["AzureKeyVault"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["AzureKeyVault"], NetAppResponse]:
        r"""Configures the AKV configuration for all clusters and SVMs.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create a AKV.
* `client_id` - Application (client) ID of the deployed Azure application with appropriate access to an AKV.
* `tenant_id` - Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
* `client_secret` - Secret used by the application to prove its identity to AKV.
* `client_certificate` - PKCS12 Certificate used by the application to prove its identity to AKV.
* `key_id`- Key Identifier of AKV encryption key.
* `name` - Name of the deployed AKV used by ONTAP for storing keys.
### Optional properties
* `proxy_type` - Type of proxy (http, https etc.) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
### Related ONTAP commands
* `security key-manager external azure enable`
* `security key-manager external azure update-config`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["AzureKeyVault"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an AKV configuration.
### Related ONTAP commands
* `security key-manager external azure disable`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves AKVs configured for all clusters and SVMs.
### Related ONTAP commands
* `security key-manager external azure show`
* `security key-manager external azure check`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the AKV configuration for the SVM specified by the UUID.
### Related ONTAP commands
* `security key-manager external azure show`
* `security key-manager external azure check`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
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
        r"""Configures the AKV configuration for all clusters and SVMs.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create a AKV.
* `client_id` - Application (client) ID of the deployed Azure application with appropriate access to an AKV.
* `tenant_id` - Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
* `client_secret` - Secret used by the application to prove its identity to AKV.
* `client_certificate` - PKCS12 Certificate used by the application to prove its identity to AKV.
* `key_id`- Key Identifier of AKV encryption key.
* `name` - Name of the deployed AKV used by ONTAP for storing keys.
### Optional properties
* `proxy_type` - Type of proxy (http, https etc.) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
### Related ONTAP commands
* `security key-manager external azure enable`
* `security key-manager external azure update-config`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="azure key vault create")
        async def azure_key_vault_create(
        ) -> ResourceTable:
            """Create an instance of a AzureKeyVault resource

            Args:
                links: 
                authentication_method: Authentication method for the AKV instance.
                azure_reachability: 
                client_certificate: PKCS12 Certificate used by the application to prove its identity to AKV.
                client_id: Application client ID of the deployed Azure application with appropriate access to an AKV.
                client_secret: Secret used by the application to prove its identity to AKV.
                ekmip_reachability: 
                key_id: Key Identifier of AKV key encryption key.
                name: Name of the deployed AKV that will be used by ONTAP for storing keys.
                proxy_host: Proxy host.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                state: 
                svm: 
                tenant_id: Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
                uuid: A unique identifier for the Azure Key Vault (AKV).
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if azure_reachability is not None:
                kwargs["azure_reachability"] = azure_reachability
            if client_certificate is not None:
                kwargs["client_certificate"] = client_certificate
            if client_id is not None:
                kwargs["client_id"] = client_id
            if client_secret is not None:
                kwargs["client_secret"] = client_secret
            if ekmip_reachability is not None:
                kwargs["ekmip_reachability"] = ekmip_reachability
            if key_id is not None:
                kwargs["key_id"] = key_id
            if name is not None:
                kwargs["name"] = name
            if proxy_host is not None:
                kwargs["proxy_host"] = proxy_host
            if proxy_password is not None:
                kwargs["proxy_password"] = proxy_password
            if proxy_port is not None:
                kwargs["proxy_port"] = proxy_port
            if proxy_type is not None:
                kwargs["proxy_type"] = proxy_type
            if proxy_username is not None:
                kwargs["proxy_username"] = proxy_username
            if scope is not None:
                kwargs["scope"] = scope
            if state is not None:
                kwargs["state"] = state
            if svm is not None:
                kwargs["svm"] = svm
            if tenant_id is not None:
                kwargs["tenant_id"] = tenant_id
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = AzureKeyVault(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create AzureKeyVault: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the AKV configuration.
### Optional properties
* `client_secret` - New secret used to prove the application's identity to the AKV.
* `client_certificate` - New PKCS12 certificate used to prove the application's identity to the AKV.
* `key_id`- Key Identifier of the new AKV key encryption key.
* `proxy_type` - Type of proxy (http, https etc.) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
* `client_id` - Application (client) ID of the deployed Azure application with appropriate access to an AKV.
* `tenant_id` - Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
### Related ONTAP commands
* `security key-manager external azure update-client-secret`
* `security key-manager external azure update-credentials`
* `security key-manager external azure rekey-external`
* `security key-manager external azure update-config`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="azure key vault modify")
        async def azure_key_vault_modify(
        ) -> ResourceTable:
            """Modify an instance of a AzureKeyVault resource

            Args:
                authentication_method: Authentication method for the AKV instance.
                query_authentication_method: Authentication method for the AKV instance.
                client_certificate: PKCS12 Certificate used by the application to prove its identity to AKV.
                query_client_certificate: PKCS12 Certificate used by the application to prove its identity to AKV.
                client_id: Application client ID of the deployed Azure application with appropriate access to an AKV.
                query_client_id: Application client ID of the deployed Azure application with appropriate access to an AKV.
                client_secret: Secret used by the application to prove its identity to AKV.
                query_client_secret: Secret used by the application to prove its identity to AKV.
                key_id: Key Identifier of AKV key encryption key.
                query_key_id: Key Identifier of AKV key encryption key.
                name: Name of the deployed AKV that will be used by ONTAP for storing keys.
                query_name: Name of the deployed AKV that will be used by ONTAP for storing keys.
                proxy_host: Proxy host.
                query_proxy_host: Proxy host.
                proxy_password: Proxy password. Password is not audited.
                query_proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port.
                query_proxy_port: Proxy port.
                proxy_type: Type of proxy.
                query_proxy_type: Type of proxy.
                proxy_username: Proxy username.
                query_proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                query_scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                tenant_id: Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
                query_tenant_id: Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
                uuid: A unique identifier for the Azure Key Vault (AKV).
                query_uuid: A unique identifier for the Azure Key Vault (AKV).
            """

            kwargs = {}
            changes = {}
            if query_authentication_method is not None:
                kwargs["authentication_method"] = query_authentication_method
            if query_client_certificate is not None:
                kwargs["client_certificate"] = query_client_certificate
            if query_client_id is not None:
                kwargs["client_id"] = query_client_id
            if query_client_secret is not None:
                kwargs["client_secret"] = query_client_secret
            if query_key_id is not None:
                kwargs["key_id"] = query_key_id
            if query_name is not None:
                kwargs["name"] = query_name
            if query_proxy_host is not None:
                kwargs["proxy_host"] = query_proxy_host
            if query_proxy_password is not None:
                kwargs["proxy_password"] = query_proxy_password
            if query_proxy_port is not None:
                kwargs["proxy_port"] = query_proxy_port
            if query_proxy_type is not None:
                kwargs["proxy_type"] = query_proxy_type
            if query_proxy_username is not None:
                kwargs["proxy_username"] = query_proxy_username
            if query_scope is not None:
                kwargs["scope"] = query_scope
            if query_tenant_id is not None:
                kwargs["tenant_id"] = query_tenant_id
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if authentication_method is not None:
                changes["authentication_method"] = authentication_method
            if client_certificate is not None:
                changes["client_certificate"] = client_certificate
            if client_id is not None:
                changes["client_id"] = client_id
            if client_secret is not None:
                changes["client_secret"] = client_secret
            if key_id is not None:
                changes["key_id"] = key_id
            if name is not None:
                changes["name"] = name
            if proxy_host is not None:
                changes["proxy_host"] = proxy_host
            if proxy_password is not None:
                changes["proxy_password"] = proxy_password
            if proxy_port is not None:
                changes["proxy_port"] = proxy_port
            if proxy_type is not None:
                changes["proxy_type"] = proxy_type
            if proxy_username is not None:
                changes["proxy_username"] = proxy_username
            if scope is not None:
                changes["scope"] = scope
            if tenant_id is not None:
                changes["tenant_id"] = tenant_id
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(AzureKeyVault, "find"):
                resource = AzureKeyVault.find(
                    **kwargs
                )
            else:
                resource = AzureKeyVault()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify AzureKeyVault: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes an AKV configuration.
### Related ONTAP commands
* `security key-manager external azure disable`

### Learn more
* [`DOC /security/azure-key-vaults`](#docs-security-security_azure-key-vaults)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="azure key vault delete")
        async def azure_key_vault_delete(
        ) -> None:
            """Delete an instance of a AzureKeyVault resource

            Args:
                authentication_method: Authentication method for the AKV instance.
                client_certificate: PKCS12 Certificate used by the application to prove its identity to AKV.
                client_id: Application client ID of the deployed Azure application with appropriate access to an AKV.
                client_secret: Secret used by the application to prove its identity to AKV.
                key_id: Key Identifier of AKV key encryption key.
                name: Name of the deployed AKV that will be used by ONTAP for storing keys.
                proxy_host: Proxy host.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                tenant_id: Directory (tenant) ID of the deployed Azure application with appropriate access to an AKV.
                uuid: A unique identifier for the Azure Key Vault (AKV).
            """

            kwargs = {}
            if authentication_method is not None:
                kwargs["authentication_method"] = authentication_method
            if client_certificate is not None:
                kwargs["client_certificate"] = client_certificate
            if client_id is not None:
                kwargs["client_id"] = client_id
            if client_secret is not None:
                kwargs["client_secret"] = client_secret
            if key_id is not None:
                kwargs["key_id"] = key_id
            if name is not None:
                kwargs["name"] = name
            if proxy_host is not None:
                kwargs["proxy_host"] = proxy_host
            if proxy_password is not None:
                kwargs["proxy_password"] = proxy_password
            if proxy_port is not None:
                kwargs["proxy_port"] = proxy_port
            if proxy_type is not None:
                kwargs["proxy_type"] = proxy_type
            if proxy_username is not None:
                kwargs["proxy_username"] = proxy_username
            if scope is not None:
                kwargs["scope"] = scope
            if tenant_id is not None:
                kwargs["tenant_id"] = tenant_id
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(AzureKeyVault, "find"):
                resource = AzureKeyVault.find(
                    **kwargs
                )
            else:
                resource = AzureKeyVault()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete AzureKeyVault: %s" % err)

    def rekey_internal(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Rekeys the internal key in the key hierarchy for an SVM with an AKV configuration.
### Related ONTAP commands
* `security key-manager external azure rekey-internal`
"""
        return super()._action(
            "rekey_internal", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    rekey_internal.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)
    def restore(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Restore the keys for an SVM from a configured AKV.
### Related ONTAP commands
* `security key-manager external azure restore`
"""
        return super()._action(
            "restore", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    restore.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)

