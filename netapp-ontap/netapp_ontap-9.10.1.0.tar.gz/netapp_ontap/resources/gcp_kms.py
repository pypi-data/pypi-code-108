r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
Google Cloud Key Management Services is a cloud key management service (KMS) that provides a secure store for encryption keys. This feature
allows ONTAP to securely store its encryption keys using Google Cloud KMS.
In order to use Google Cloud KMS with ONTAP, a user must first deploy a Google Cloud application with appropriate access to the Google Cloud KMS and then provide
ONTAP with the necessary details, such as, project ID, key ring name, location, key name and application credentials to allow ONTAP to communicate
with the deployed Google Cloud application.
The properties `state`, `google_reachability` and `ekmip_reachability` are considered advanced properties and are populated only when explicitly requested.
## Examples
### Enabling GCKMS for an SVM
The following example shows how to enable GCKMS at the SVM-scope. Note the <i>return_records=true</i> query parameter is used to obtain the newly created key manager configuration.<br/>
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms()
    resource.svm = {"uuid": "f36ff553-e713-11ea-bd56-005056bb4222"}
    resource.project_id = "testProj"
    resource.key_ring_name = "testKeyRing"
    resource.key_ring_location = "global"
    resource.key_name = "key1"
    resource.application_credentials = "myAppCred"
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
GcpKms(
    {
        "_links": {
            "self": {
                "href": "/api/security/gcp-kms/f72098a2-e908-11ea-bd56-005056bb4222"
            }
        },
        "key_name": "key1",
        "svm": {"uuid": "f36ff553-e713-11ea-bd56-005056bb4222", "name": "vs0"},
        "uuid": "f72098a2-e908-11ea-bd56-005056bb4222",
        "key_ring_name": "testKeyRing",
        "project_id": "testProj",
        "key_ring_location": "global",
    }
)

```
</div>
</div>

---
### Retrieving all GCKMS configurations
The following example shows how to retrieve all GCKMS configurations.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(GcpKms.get_collection(fields="*")))

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
[
    GcpKms(
        {
            "_links": {
                "self": {
                    "href": "/api/security/gcp-kms/f72098a2-e908-11ea-bd56-005056bb4222"
                }
            },
            "key_name": "key1",
            "scope": "svm",
            "svm": {"uuid": "f36ff553-e713-11ea-bd56-005056bb4222", "name": "vs0"},
            "uuid": "f72098a2-e908-11ea-bd56-005056bb4222",
            "key_ring_name": "testKeyRing",
            "project_id": "testProj",
            "key_ring_location": "global",
        }
    )
]

```
</div>
</div>

---
### Retrieving a specific GCKMS configuration
The following example shows how to retrieve information for a specific GCKMS configuration.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms(uuid="f72098a2-e908-11ea-bd56-005056bb4222")
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
GcpKms(
    {
        "_links": {
            "self": {
                "href": "/api/security/gcp-kms/f72098a2-e908-11ea-bd56-005056bb4222"
            }
        },
        "key_name": "key1",
        "scope": "svm",
        "svm": {"uuid": "f36ff553-e713-11ea-bd56-005056bb4222", "name": "vs0"},
        "uuid": "f72098a2-e908-11ea-bd56-005056bb4222",
        "key_ring_name": "testKeyRing",
        "project_id": "testProj",
        "key_ring_location": "global",
    }
)

```
</div>
</div>

---
### Retrieving a specific GCKMS's advanced properties
The following example shows how to retrieve advanced properties for a specific GCKMS configuration.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms(uuid="f72098a2-e908-11ea-bd56-005056bb4222")
    resource.get(fields="state,google_reachability,ekmip_reachability")
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
GcpKms(
    {
        "_links": {
            "self": {
                "href": "/api/security/gcp-kms/f72098a2-e908-11ea-bd56-005056bb4222"
            }
        },
        "google_reachability": {"code": 0, "message": "", "reachable": True},
        "uuid": "f72098a2-e908-11ea-bd56-005056bb4222",
        "state": {
            "code": 65537708,
            "cluster_state": False,
            "message": "The Google Cloud Key Management Service key protection is unavailable on the following nodes: cluster1-node1.",
        },
        "ekmip_reachability": [
            {
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/d208115f-7721-11eb-bf83-005056bb150e"
                        }
                    },
                    "uuid": "d208115f-7721-11eb-bf83-005056bb150e",
                    "name": "node1",
                },
                "code": 0,
                "message": "",
                "reachable": True,
            },
            {
                "node": {
                    "_links": {
                        "self": {
                            "href": "/api/cluster/nodes/e208115f-7721-11eb-bf83-005056bb150e"
                        }
                    },
                    "uuid": "e208115f-7721-11eb-bf83-005056bb150e",
                    "name": "node2",
                },
                "code": 0,
                "message": "",
                "reachable": True,
            },
        ],
    }
)

```
</div>
</div>

---
### Updating the application credentials of a specific GCKMS configuration
The following example shows how to update the application credentials for a specific GCKMS configuration.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms(uuid="f72098a2-e908-11ea-bd56-005056bb4222")
    resource.application_credentials = "newAppCred"
    resource.patch()

```

---
### Deleting a specific GCKMS configuration
The following example shows how to delete a specific GCKMS configuration.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms(uuid="f72098a2-e908-11ea-bd56-005056bb4222")
    resource.delete()

```

---
### Restoring keys from KMIP server
The following example shows how to retore keys for a GCKMS configuration.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import GcpKms

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = GcpKms(uuid="33820b57-ec90-11ea-875e-005056bbf3f0")
    resource.restore()

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


__all__ = ["GcpKms", "GcpKmsSchema"]
__pdoc__ = {
    "GcpKmsSchema.resource": False,
    "GcpKms.gcp_kms_show": False,
    "GcpKms.gcp_kms_create": False,
    "GcpKms.gcp_kms_modify": False,
    "GcpKms.gcp_kms_delete": False,
}


class GcpKmsSchema(ResourceSchema):
    """The fields of the GcpKms object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the gcp_kms. """

    application_credentials = fields.Str(
        data_key="application_credentials",
    )
    r""" Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.

Example: { type: service_account, project_id: project-id, private_key_id: key-id, private_key: -----BEGIN PRIVATE KEY-----
private-key
-----END PRIVATE KEY-----
, client_email: service-account-email, client_id: client-id, auth_uri: https://accounts.google.com/o/oauth2/auth, token_uri: https://accounts.google.com/o/oauth2/token, auth_provider_x509_cert_url: https://www.googleapis.com/oauth2/v1/certs, client_x509_cert_url: https://www.googleapis.com/robot/v1/metadata/x509/service-account-email } """

    ekmip_reachability = fields.List(fields.Nested("netapp_ontap.models.ekmip_server_connectivity.EkmipServerConnectivitySchema", unknown=EXCLUDE), data_key="ekmip_reachability")
    r""" The ekmip_reachability field of the gcp_kms. """

    google_reachability = fields.Nested("netapp_ontap.models.gcp_connectivity.GcpConnectivitySchema", data_key="google_reachability", unknown=EXCLUDE)
    r""" The google_reachability field of the gcp_kms. """

    key_name = fields.Str(
        data_key="key_name",
    )
    r""" Key Identifier of Google Cloud KMS key encryption key.

Example: cryptokey1 """

    key_ring_location = fields.Str(
        data_key="key_ring_location",
    )
    r""" Google Cloud KMS key ring location.

Example: global """

    key_ring_name = fields.Str(
        data_key="key_ring_name",
    )
    r""" Google Cloud KMS key ring name of the deployed Google Cloud application.

Example: gcpapp1-keyring """

    project_id = fields.Str(
        data_key="project_id",
    )
    r""" Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.

Example: gcpapp1 """

    proxy_host = fields.Str(
        data_key="proxy_host",
    )
    r""" Proxy host name.

Example: proxy.eng.com """

    proxy_password = fields.Str(
        data_key="proxy_password",
    )
    r""" Proxy password. Password is not audited.

Example: proxypassword """

    proxy_port = Size(
        data_key="proxy_port",
    )
    r""" Proxy port number.

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

    state = fields.Nested("netapp_ontap.models.gcp_kms_state.GcpKmsStateSchema", data_key="state", unknown=EXCLUDE)
    r""" The state field of the gcp_kms. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the gcp_kms. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" A unique identifier for the Google Cloud KMS.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return GcpKms

    gettable_fields = [
        "links",
        "ekmip_reachability",
        "google_reachability",
        "key_name",
        "key_ring_location",
        "key_ring_name",
        "project_id",
        "proxy_host",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "scope",
        "state",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "uuid",
    ]
    """links,ekmip_reachability,google_reachability,key_name,key_ring_location,key_ring_name,project_id,proxy_host,proxy_port,proxy_type,proxy_username,scope,state,svm.links,svm.name,svm.uuid,uuid,"""

    patchable_fields = [
        "application_credentials",
        "key_name",
        "key_ring_location",
        "key_ring_name",
        "project_id",
        "proxy_host",
        "proxy_password",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "svm.name",
        "svm.uuid",
    ]
    """application_credentials,key_name,key_ring_location,key_ring_name,project_id,proxy_host,proxy_password,proxy_port,proxy_type,proxy_username,svm.name,svm.uuid,"""

    postable_fields = [
        "application_credentials",
        "key_name",
        "key_ring_location",
        "key_ring_name",
        "project_id",
        "proxy_host",
        "proxy_password",
        "proxy_port",
        "proxy_type",
        "proxy_username",
        "svm.name",
        "svm.uuid",
    ]
    """application_credentials,key_name,key_ring_location,key_ring_name,project_id,proxy_host,proxy_password,proxy_port,proxy_type,proxy_username,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in GcpKms.get_collection(fields=field)]
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
            raise NetAppRestError("GcpKms modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class GcpKms(Resource):
    """Allows interaction with GcpKms objects on the host"""

    _schema = GcpKmsSchema
    _path = "/api/security/gcp-kms"
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
        r"""Retrieves Google Cloud KMS configurations for all clusters and SVMs.
### Related ONTAP commands
* `security key-manager external gcp show`
* `security key-manager external gcp check`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="gcp kms show")
        def gcp_kms_show(
            fields: List[Choices.define(["application_credentials", "key_name", "key_ring_location", "key_ring_name", "project_id", "proxy_host", "proxy_password", "proxy_port", "proxy_type", "proxy_username", "scope", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of GcpKms resources

            Args:
                application_credentials: Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
                key_name: Key Identifier of Google Cloud KMS key encryption key.
                key_ring_location: Google Cloud KMS key ring location.
                key_ring_name: Google Cloud KMS key ring name of the deployed Google Cloud application.
                project_id: Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.
                proxy_host: Proxy host name.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port number.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                uuid: A unique identifier for the Google Cloud KMS.
            """

            kwargs = {}
            if application_credentials is not None:
                kwargs["application_credentials"] = application_credentials
            if key_name is not None:
                kwargs["key_name"] = key_name
            if key_ring_location is not None:
                kwargs["key_ring_location"] = key_ring_location
            if key_ring_name is not None:
                kwargs["key_ring_name"] = key_ring_name
            if project_id is not None:
                kwargs["project_id"] = project_id
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
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return GcpKms.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all GcpKms resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["GcpKms"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Google Cloud KMS configuration.
### Optional properties
* `key_name` - Key Identifier of the Google Cloud KMS key encryption key.
* `application_credentials` - New credentials used to verify the application's identity to the Google Cloud KMS.
* `proxy_type`` - Type of proxy (http/https) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
* `project_id` - Google Cloud project (application) ID of the deployed Google Cloud application with appropriate access to the Google Cloud KMS.
* `key_ring_name` - Google Cloud KMS key ring name of the deployed Google Cloud application with appropriate access to the specified Google Cloud KMS.
* `key_ring_location` - Google Cloud KMS key ring location.
### Related ONTAP commands
* `security key-manager external gcp update-credentials`
* `security key-manager external gcp rekey-external`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["GcpKms"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["GcpKms"], NetAppResponse]:
        r"""Configures the Google Cloud KMS configuration for the specified SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create a Google Cloud KMS.
* `project_id` - Google Cloud project (application) ID of the deployed Google Cloud application with appropriate access to the Google Cloud KMS.
* `key_ring_name` - Google Cloud KMS key ring name of the deployed Google Cloud application with appropriate access to the specified Google Cloud KMS.
* `key_ring_location` - Google Cloud KMS key ring location.
* `key_name`- Key Identifier of the Google Cloud KMS key encryption key.
* `application_credentials` - Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
### Optional properties
* `proxy_type`` - Type of proxy (http/https) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
### Related ONTAP commands
* `security key-manager external gcp enable`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["GcpKms"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Google Cloud KMS configuration.
### Related ONTAP commands
* `security key-manager external gcp disable`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves Google Cloud KMS configurations for all clusters and SVMs.
### Related ONTAP commands
* `security key-manager external gcp show`
* `security key-manager external gcp check`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the Google Cloud KMS configuration for the SVM specified by the UUID.
### Related ONTAP commands
* `security key-manager external gcp show`
* `security key-manager external gcp check`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
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
        r"""Configures the Google Cloud KMS configuration for the specified SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM in which to create a Google Cloud KMS.
* `project_id` - Google Cloud project (application) ID of the deployed Google Cloud application with appropriate access to the Google Cloud KMS.
* `key_ring_name` - Google Cloud KMS key ring name of the deployed Google Cloud application with appropriate access to the specified Google Cloud KMS.
* `key_ring_location` - Google Cloud KMS key ring location.
* `key_name`- Key Identifier of the Google Cloud KMS key encryption key.
* `application_credentials` - Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
### Optional properties
* `proxy_type`` - Type of proxy (http/https) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
### Related ONTAP commands
* `security key-manager external gcp enable`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="gcp kms create")
        async def gcp_kms_create(
        ) -> ResourceTable:
            """Create an instance of a GcpKms resource

            Args:
                links: 
                application_credentials: Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
                ekmip_reachability: 
                google_reachability: 
                key_name: Key Identifier of Google Cloud KMS key encryption key.
                key_ring_location: Google Cloud KMS key ring location.
                key_ring_name: Google Cloud KMS key ring name of the deployed Google Cloud application.
                project_id: Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.
                proxy_host: Proxy host name.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port number.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                state: 
                svm: 
                uuid: A unique identifier for the Google Cloud KMS.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if application_credentials is not None:
                kwargs["application_credentials"] = application_credentials
            if ekmip_reachability is not None:
                kwargs["ekmip_reachability"] = ekmip_reachability
            if google_reachability is not None:
                kwargs["google_reachability"] = google_reachability
            if key_name is not None:
                kwargs["key_name"] = key_name
            if key_ring_location is not None:
                kwargs["key_ring_location"] = key_ring_location
            if key_ring_name is not None:
                kwargs["key_ring_name"] = key_ring_name
            if project_id is not None:
                kwargs["project_id"] = project_id
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
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = GcpKms(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create GcpKms: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the Google Cloud KMS configuration.
### Optional properties
* `key_name` - Key Identifier of the Google Cloud KMS key encryption key.
* `application_credentials` - New credentials used to verify the application's identity to the Google Cloud KMS.
* `proxy_type`` - Type of proxy (http/https) if proxy configuration is used.
* `proxy_host` - Proxy hostname if proxy configuration is used.
* `proxy_port` - Proxy port number if proxy configuration is used.
* `proxy_username` - Proxy username if proxy configuration is used.
* `proxy_password` - Proxy password if proxy configuration is used.
* `project_id` - Google Cloud project (application) ID of the deployed Google Cloud application with appropriate access to the Google Cloud KMS.
* `key_ring_name` - Google Cloud KMS key ring name of the deployed Google Cloud application with appropriate access to the specified Google Cloud KMS.
* `key_ring_location` - Google Cloud KMS key ring location.
### Related ONTAP commands
* `security key-manager external gcp update-credentials`
* `security key-manager external gcp rekey-external`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="gcp kms modify")
        async def gcp_kms_modify(
        ) -> ResourceTable:
            """Modify an instance of a GcpKms resource

            Args:
                application_credentials: Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
                query_application_credentials: Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
                key_name: Key Identifier of Google Cloud KMS key encryption key.
                query_key_name: Key Identifier of Google Cloud KMS key encryption key.
                key_ring_location: Google Cloud KMS key ring location.
                query_key_ring_location: Google Cloud KMS key ring location.
                key_ring_name: Google Cloud KMS key ring name of the deployed Google Cloud application.
                query_key_ring_name: Google Cloud KMS key ring name of the deployed Google Cloud application.
                project_id: Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.
                query_project_id: Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.
                proxy_host: Proxy host name.
                query_proxy_host: Proxy host name.
                proxy_password: Proxy password. Password is not audited.
                query_proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port number.
                query_proxy_port: Proxy port number.
                proxy_type: Type of proxy.
                query_proxy_type: Type of proxy.
                proxy_username: Proxy username.
                query_proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                query_scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                uuid: A unique identifier for the Google Cloud KMS.
                query_uuid: A unique identifier for the Google Cloud KMS.
            """

            kwargs = {}
            changes = {}
            if query_application_credentials is not None:
                kwargs["application_credentials"] = query_application_credentials
            if query_key_name is not None:
                kwargs["key_name"] = query_key_name
            if query_key_ring_location is not None:
                kwargs["key_ring_location"] = query_key_ring_location
            if query_key_ring_name is not None:
                kwargs["key_ring_name"] = query_key_ring_name
            if query_project_id is not None:
                kwargs["project_id"] = query_project_id
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
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if application_credentials is not None:
                changes["application_credentials"] = application_credentials
            if key_name is not None:
                changes["key_name"] = key_name
            if key_ring_location is not None:
                changes["key_ring_location"] = key_ring_location
            if key_ring_name is not None:
                changes["key_ring_name"] = key_ring_name
            if project_id is not None:
                changes["project_id"] = project_id
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
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(GcpKms, "find"):
                resource = GcpKms.find(
                    **kwargs
                )
            else:
                resource = GcpKms()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify GcpKms: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes a Google Cloud KMS configuration.
### Related ONTAP commands
* `security key-manager external gcp disable`

### Learn more
* [`DOC /security/gcp-kms`](#docs-security-security_gcp-kms)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="gcp kms delete")
        async def gcp_kms_delete(
        ) -> None:
            """Delete an instance of a GcpKms resource

            Args:
                application_credentials: Google Cloud application's service account credentials required to access the specified KMS. It is a JSON file containing an email address and the private key of the service account holder.
                key_name: Key Identifier of Google Cloud KMS key encryption key.
                key_ring_location: Google Cloud KMS key ring location.
                key_ring_name: Google Cloud KMS key ring name of the deployed Google Cloud application.
                project_id: Google Cloud project (application) ID of the deployed Google Cloud application that has appropriate access to the Google Cloud KMS.
                proxy_host: Proxy host name.
                proxy_password: Proxy password. Password is not audited.
                proxy_port: Proxy port number.
                proxy_type: Type of proxy.
                proxy_username: Proxy username.
                scope: Set to \"svm\" for interfaces owned by an SVM. Otherwise, set to \"cluster\".
                uuid: A unique identifier for the Google Cloud KMS.
            """

            kwargs = {}
            if application_credentials is not None:
                kwargs["application_credentials"] = application_credentials
            if key_name is not None:
                kwargs["key_name"] = key_name
            if key_ring_location is not None:
                kwargs["key_ring_location"] = key_ring_location
            if key_ring_name is not None:
                kwargs["key_ring_name"] = key_ring_name
            if project_id is not None:
                kwargs["project_id"] = project_id
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
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(GcpKms, "find"):
                resource = GcpKms.find(
                    **kwargs
                )
            else:
                resource = GcpKms()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete GcpKms: %s" % err)

    def rekey_internal(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Rekeys the internal key in the key hierarchy for an SVM with a Google Cloud KMS configuration.
### Related ONTAP commands
* `security key-manager external gcp rekey-internal`
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
        r"""Restores the keys for an SVM from a configured Google Cloud KMS.
### Related ONTAP commands
* `security key-manager external gcp restore`
"""
        return super()._action(
            "restore", body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    restore.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._action.__doc__)

