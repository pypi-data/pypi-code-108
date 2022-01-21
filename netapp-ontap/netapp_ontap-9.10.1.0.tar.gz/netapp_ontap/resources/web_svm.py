r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

You can use this API to update and retrieve the web services security configuration for each data SVM.</br>
## Updating the web services security configuration
The following fields can be used to update the web services security configuration:

* certificate.uuid
* client_enabled
* ocsp_enabled
When updating the certificate, the certificate UUID of an existing certificate known to ONTAP must
be provided. The certificate must be of type "server".</br>
A "client-ca" certificate must be installed on ONTAP to enable "client_enabled".</br>
## Examples
### Retrieving the web services security configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WebSvm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = WebSvm("3c1b259d-5789-a2eb-9301-10705682b34f")
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
WebSvm(
    {
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/3c1b259d-5789-a2eb-9301-10705682b34f"}
            },
            "uuid": "3c1b259d-5789-a2eb-9301-10705682b34f",
            "name": "svm2",
        },
        "certificate": {
            "name": "cert1",
            "uuid": "a3bb219d-4382-1fe0-9c06-1070568ea23d",
            "_links": {
                "self": {
                    "href": "/api/security/certificates/a3bb219d-4382-1fe0-9c06-1070568ea23d"
                }
            },
        },
        "client_enabled": False,
        "ocsp_enabled": False,
        "_links": {
            "self": {"href": "/api/svm/svms/3c1b259d-5789-a2eb-9301-10705682b34f/web"}
        },
    }
)

```
</div>
</div>

### Updating the web services security configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import WebSvm

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = WebSvm("3c1b259d-5789-a2eb-9301-10705682b34f")
    resource.certificate = {"uuid": "56da2799-13bc-2ae4-0c16-0c71244ea2ca"}
    resource.patch()

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


__all__ = ["WebSvm", "WebSvmSchema"]
__pdoc__ = {
    "WebSvmSchema.resource": False,
    "WebSvm.web_svm_show": False,
    "WebSvm.web_svm_create": False,
    "WebSvm.web_svm_modify": False,
    "WebSvm.web_svm_delete": False,
}


class WebSvmSchema(ResourceSchema):
    """The fields of the WebSvm object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the web_svm. """

    certificate = fields.Nested("netapp_ontap.models.web_certificate.WebCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the web_svm. """

    client_enabled = fields.Boolean(
        data_key="client_enabled",
    )
    r""" Indicates whether client authentication is enabled. """

    ocsp_enabled = fields.Boolean(
        data_key="ocsp_enabled",
    )
    r""" Indicates whether online certificate status protocol verification is enabled. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the web_svm. """

    @property
    def resource(self):
        return WebSvm

    gettable_fields = [
        "links",
        "certificate",
        "client_enabled",
        "ocsp_enabled",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,certificate,client_enabled,ocsp_enabled,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "certificate",
        "client_enabled",
        "ocsp_enabled",
        "svm.name",
        "svm.uuid",
    ]
    """certificate,client_enabled,ocsp_enabled,svm.name,svm.uuid,"""

    postable_fields = [
        "certificate",
        "client_enabled",
        "ocsp_enabled",
        "svm.name",
        "svm.uuid",
    ]
    """certificate,client_enabled,ocsp_enabled,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in WebSvm.get_collection(fields=field)]
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
            raise NetAppRestError("WebSvm modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class WebSvm(Resource):
    """Allows interaction with WebSvm objects on the host"""

    _schema = WebSvmSchema
    _path = "/api/svm/svms/{svm[uuid]}/web"
    _keys = ["svm.uuid"]







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the web services security configuration.
### Learn more
* [`DOC /svm/svms/{svm.uuid}/web`](#docs-svm-svm_svms_{svm.uuid}_web)"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="web svm show")
        def web_svm_show(
            svm_uuid,
            client_enabled: Choices.define(_get_field_list("client_enabled"), cache_choices=True, inexact=True)=None,
            ocsp_enabled: Choices.define(_get_field_list("ocsp_enabled"), cache_choices=True, inexact=True)=None,
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single WebSvm resource

            Args:
                client_enabled: Indicates whether client authentication is enabled.
                ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
            """

            kwargs = {}
            if client_enabled is not None:
                kwargs["client_enabled"] = client_enabled
            if ocsp_enabled is not None:
                kwargs["ocsp_enabled"] = ocsp_enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = WebSvm(
                svm_uuid,
                **kwargs
            )
            resource.get()
            return [resource]


    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the web services security configuration.
### Learn more
* [`DOC /svm/svms/{svm.uuid}/web`](#docs-svm-svm_svms_{svm.uuid}_web)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="web svm modify")
        async def web_svm_modify(
            svm_uuid,
            client_enabled: bool = None,
            query_client_enabled: bool = None,
            ocsp_enabled: bool = None,
            query_ocsp_enabled: bool = None,
        ) -> ResourceTable:
            """Modify an instance of a WebSvm resource

            Args:
                client_enabled: Indicates whether client authentication is enabled.
                query_client_enabled: Indicates whether client authentication is enabled.
                ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
                query_ocsp_enabled: Indicates whether online certificate status protocol verification is enabled.
            """

            kwargs = {}
            changes = {}
            if query_client_enabled is not None:
                kwargs["client_enabled"] = query_client_enabled
            if query_ocsp_enabled is not None:
                kwargs["ocsp_enabled"] = query_ocsp_enabled

            if client_enabled is not None:
                changes["client_enabled"] = client_enabled
            if ocsp_enabled is not None:
                changes["ocsp_enabled"] = ocsp_enabled

            if hasattr(WebSvm, "find"):
                resource = WebSvm.find(
                    svm_uuid,
                    **kwargs
                )
            else:
                resource = WebSvm(svm_uuid,)
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify WebSvm: %s" % err)



