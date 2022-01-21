r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
This API configures data SVM account information at the Active Directory. For Active Directory domain-based authentication for cluster accounts, a data SVM must be configured and registered as a machine account at the Active Directory. All authentication requests are proxied through this SVM.
## Examples
### Creating a data SVM proxy for domain-based authentication for cluster accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterAdProxy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterAdProxy()
    resource.svm.uuid = "13f87d78-70c7-11e9-b722-0050568ec89f"
    resource.post(hydrate=True)
    print(resource)

```

### Updating a data SVM proxy for domain-based authentication for cluster accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterAdProxy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterAdProxy()
    resource.svm.uuid = "13f87d78-70c7-11e9-b722-0050568ec89f"
    resource.patch()

```

### Retrieving a data SVM proxy for domain-based authentication for cluster accounts
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import ClusterAdProxy

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = ClusterAdProxy()
    resource.get()
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
ClusterAdProxy(
    {
        "svm": {
            "_links": {
                "self": {"href": "/api/svm/svms/512eab7a-6bf9-11e9-a896-005056bb9ce1"}
            },
            "uuid": "512eab7a-6bf9-11e9-a896-005056bb9ce1",
            "name": "vs2",
        },
        "_links": {"self": {"href": "/api/security/authentication/cluster/ad-proxy"}},
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


__all__ = ["ClusterAdProxy", "ClusterAdProxySchema"]
__pdoc__ = {
    "ClusterAdProxySchema.resource": False,
    "ClusterAdProxy.cluster_ad_proxy_show": False,
    "ClusterAdProxy.cluster_ad_proxy_create": False,
    "ClusterAdProxy.cluster_ad_proxy_modify": False,
    "ClusterAdProxy.cluster_ad_proxy_delete": False,
}


class ClusterAdProxySchema(ResourceSchema):
    """The fields of the ClusterAdProxy object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cluster_ad_proxy. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the cluster_ad_proxy. """

    @property
    def resource(self):
        return ClusterAdProxy

    gettable_fields = [
        "links",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

    postable_fields = [
        "svm.name",
        "svm.uuid",
    ]
    """svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ClusterAdProxy.get_collection(fields=field)]
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
            raise NetAppRestError("ClusterAdProxy modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ClusterAdProxy(Resource):
    r""" The SVM configured as proxy for Active Directory authentication of cluster accounts. """

    _schema = ClusterAdProxySchema
    _path = "/api/security/authentication/cluster/ad-proxy"







    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves SVM information configured as an Active Directory domain-tunnel.
### Related ONTAP commands
* `security login domain-tunnel show`
### Learn more
* [`DOC /security/authentication/cluster/ad-proxy`](#docs-security-security_authentication_cluster_ad-proxy)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ad proxy show")
        def cluster_ad_proxy_show(
            fields: List[str] = None,
        ) -> ResourceTable:
            """Fetch a single ClusterAdProxy resource

            Args:
            """

            kwargs = {}
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            resource = ClusterAdProxy(
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
        r"""Configures a data SVM as a proxy for Active Directory based authentication for cluster user accounts.
### Required properties
* `svm.name` or `svm.uuid` - Name and UUID of the SVM for a cluster user account.
### Related ONTAP commands
* `security login domain-tunnel create`
### Learn more
* [`DOC /security/authentication/cluster/ad-proxy`](#docs-security-security_authentication_cluster_ad-proxy)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ad proxy create")
        async def cluster_ad_proxy_create(
        ) -> ResourceTable:
            """Create an instance of a ClusterAdProxy resource

            Args:
                links: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if svm is not None:
                kwargs["svm"] = svm

            resource = ClusterAdProxy(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create ClusterAdProxy: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the data SVM configured as a tunnel for Active Directory based authentication for cluster user accounts.
### Related ONTAP commands
* `security login domain-tunnel modify`
### Learn more
* [`DOC /security/authentication/cluster/ad-proxy`](#docs-security-security_authentication_cluster_ad-proxy)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ad proxy modify")
        async def cluster_ad_proxy_modify(
        ) -> ResourceTable:
            """Modify an instance of a ClusterAdProxy resource

            Args:
            """

            kwargs = {}
            changes = {}


            if hasattr(ClusterAdProxy, "find"):
                resource = ClusterAdProxy.find(
                    **kwargs
                )
            else:
                resource = ClusterAdProxy()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify ClusterAdProxy: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the data SVM configured as a tunnel for Active Directory based authentication for cluster user accounts.
### Related ONTAP commands
* `security login domain-tunnel delete`
### Learn more
* [`DOC /security/authentication/cluster/ad-proxy`](#docs-security-security_authentication_cluster_ad-proxy)
* [`DOC /security/accounts`](#docs-security-security_accounts)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cluster ad proxy delete")
        async def cluster_ad_proxy_delete(
        ) -> None:
            """Delete an instance of a ClusterAdProxy resource

            Args:
            """

            kwargs = {}

            if hasattr(ClusterAdProxy, "find"):
                resource = ClusterAdProxy.find(
                    **kwargs
                )
            else:
                resource = ClusterAdProxy()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete ClusterAdProxy: %s" % err)


