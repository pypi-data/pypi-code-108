r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This endpoint is used to retrieve or modify the SSH security configuration to an SVM.<br/>
The SSH security algorithms include key exchange algorithms, ciphers for payload encryption, MAC algorithms, and the maximum authentication retry attempts allowed before closing the connection. svm.uuid corresponds to the UUID of the SVM for which the SSH security setting is being retrieved or modified and it is obtained from the response body of a GET operation performed on the <i>api/security/ssh/svms</i> API.
## Examples
### Updating the SSH security parameters
Specify the algorithms in the body of the PATCH request.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SvmSshServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SvmSshServer(**{"svm.uuid": "02c9e252-41be-11e9-81d5-00a0986138f7"})
    resource.ciphers = ["aes256_ctr", "aes192_ctr"]
    resource.key_exchange_algorithms = [
        "diffie_hellman_group_exchange_sha256",
        "diffie_hellman_group14_sha1",
    ]
    resource.mac_algorithms = ["hmac_sha2_512_etm", "umac_128_etm"]
    resource.max_authentication_retry_count = 3
    resource.patch()

```

### Retrieving the SSH security configuration of an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import SvmSshServer

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = SvmSshServer(**{"svm.uuid": "02c9e252-41be-11e9-81d5-00a0986138f7"})
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
SvmSshServer(
    {
        "mac_algorithms": ["hmac_sha2_512_etm", "umac_128_etm"],
        "ciphers": ["aes256_ctr", "aes192_ctr"],
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/02c9e252-41be-11e9-81d5-00a0986138f7"}
            },
            "uuid": "02c9e252-41be-11e9-81d5-00a0986138f7",
            "name": "svm1",
        },
        "max_authentication_retry_count": 3,
        "key_exchange_algorithms": [
            "diffie_hellman_group_exchange_sha256",
            "diffie_hellman_group14_sha1",
        ],
        "_links": {
            "self": {
                "href": "/api/security/ssh/svms/02c9e252-41be-11e9-81d5-00a0986138f7"
            }
        },
    }
)

```
</div>
</div>

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


__all__ = ["SvmSshServer", "SvmSshServerSchema"]
__pdoc__ = {
    "SvmSshServerSchema.resource": False,
    "SvmSshServer.svm_ssh_server_show": False,
    "SvmSshServer.svm_ssh_server_create": False,
    "SvmSshServer.svm_ssh_server_modify": False,
    "SvmSshServer.svm_ssh_server_delete": False,
}


class SvmSshServerSchema(ResourceSchema):
    """The fields of the SvmSshServer object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the svm_ssh_server. """

    ciphers = fields.List(fields.Str, data_key="ciphers")
    r""" Ciphers for encrypting the data.

Example: ["aes256_ctr","aes192_ctr","aes128_ctr"] """

    key_exchange_algorithms = fields.List(fields.Str, data_key="key_exchange_algorithms")
    r""" Key exchange algorithms.

Example: ["diffie_hellman_group_exchange_sha256","diffie_hellman_group14_sha1"] """

    mac_algorithms = fields.List(fields.Str, data_key="mac_algorithms")
    r""" MAC algorithms.

Example: ["hmac_sha1","hmac_sha2_512_etm"] """

    max_authentication_retry_count = Size(
        data_key="max_authentication_retry_count",
        validate=integer_validation(minimum=2, maximum=6),
    )
    r""" Maximum authentication retries allowed before closing the connection. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the svm_ssh_server. """

    @property
    def resource(self):
        return SvmSshServer

    gettable_fields = [
        "links",
        "ciphers",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,ciphers,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "ciphers",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "svm.name",
        "svm.uuid",
    ]
    """ciphers,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,svm.name,svm.uuid,"""

    postable_fields = [
        "ciphers",
        "key_exchange_algorithms",
        "mac_algorithms",
        "max_authentication_retry_count",
        "svm.name",
        "svm.uuid",
    ]
    """ciphers,key_exchange_algorithms,mac_algorithms,max_authentication_retry_count,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SvmSshServer.get_collection(fields=field)]
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
            raise NetAppRestError("SvmSshServer modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SvmSshServer(Resource):
    """Allows interaction with SvmSshServer objects on the host"""

    _schema = SvmSshServerSchema
    _path = "/api/security/ssh/svms"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the SSH server configuration for all the SVMs.
### Related ONTAP commands
* `security ssh`

### Learn more
* [`DOC /security/ssh/svms`](#docs-security-security_ssh_svms)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm ssh server show")
        def svm_ssh_server_show(
            fields: List[Choices.define(["ciphers", "key_exchange_algorithms", "mac_algorithms", "max_authentication_retry_count", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SvmSshServer resources

            Args:
                ciphers: Ciphers for encrypting the data.
                key_exchange_algorithms: Key exchange algorithms.
                mac_algorithms: MAC algorithms.
                max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
            """

            kwargs = {}
            if ciphers is not None:
                kwargs["ciphers"] = ciphers
            if key_exchange_algorithms is not None:
                kwargs["key_exchange_algorithms"] = key_exchange_algorithms
            if mac_algorithms is not None:
                kwargs["mac_algorithms"] = mac_algorithms
            if max_authentication_retry_count is not None:
                kwargs["max_authentication_retry_count"] = max_authentication_retry_count
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SvmSshServer.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SvmSshServer resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SvmSshServer"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SSH server configuration for the specified SVM.
### Optional parameters
* `ciphers` - Encryption algorithms for the payload
* `key_exchange_algorithms` - SSH key exchange algorithms
* `mac_algorithms` - MAC algorithms
* `max_authentication_retry_count` - Maximum authentication retries allowed before closing the connection
### Related ONTAP commands
* `security ssh`

### Learn more
* [`DOC /security/ssh/svms/{svm.uuid}`](#docs-security-security_ssh_svms_{svm.uuid})"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)



    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the SSH server configuration for all the SVMs.
### Related ONTAP commands
* `security ssh`

### Learn more
* [`DOC /security/ssh/svms`](#docs-security-security_ssh_svms)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the SSH server configuration for the specified SVM.
### Related ONTAP commands
* `security ssh`

### Learn more
* [`DOC /security/ssh/svms/{svm.uuid}`](#docs-security-security_ssh_svms_{svm.uuid})"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the SSH server configuration for the specified SVM.
### Optional parameters
* `ciphers` - Encryption algorithms for the payload
* `key_exchange_algorithms` - SSH key exchange algorithms
* `mac_algorithms` - MAC algorithms
* `max_authentication_retry_count` - Maximum authentication retries allowed before closing the connection
### Related ONTAP commands
* `security ssh`

### Learn more
* [`DOC /security/ssh/svms/{svm.uuid}`](#docs-security-security_ssh_svms_{svm.uuid})"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="svm ssh server modify")
        async def svm_ssh_server_modify(
        ) -> ResourceTable:
            """Modify an instance of a SvmSshServer resource

            Args:
                ciphers: Ciphers for encrypting the data.
                query_ciphers: Ciphers for encrypting the data.
                key_exchange_algorithms: Key exchange algorithms.
                query_key_exchange_algorithms: Key exchange algorithms.
                mac_algorithms: MAC algorithms.
                query_mac_algorithms: MAC algorithms.
                max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
                query_max_authentication_retry_count: Maximum authentication retries allowed before closing the connection.
            """

            kwargs = {}
            changes = {}
            if query_ciphers is not None:
                kwargs["ciphers"] = query_ciphers
            if query_key_exchange_algorithms is not None:
                kwargs["key_exchange_algorithms"] = query_key_exchange_algorithms
            if query_mac_algorithms is not None:
                kwargs["mac_algorithms"] = query_mac_algorithms
            if query_max_authentication_retry_count is not None:
                kwargs["max_authentication_retry_count"] = query_max_authentication_retry_count

            if ciphers is not None:
                changes["ciphers"] = ciphers
            if key_exchange_algorithms is not None:
                changes["key_exchange_algorithms"] = key_exchange_algorithms
            if mac_algorithms is not None:
                changes["mac_algorithms"] = mac_algorithms
            if max_authentication_retry_count is not None:
                changes["max_authentication_retry_count"] = max_authentication_retry_count

            if hasattr(SvmSshServer, "find"):
                resource = SvmSshServer.find(
                    **kwargs
                )
            else:
                resource = SvmSshServer()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SvmSshServer: %s" % err)



