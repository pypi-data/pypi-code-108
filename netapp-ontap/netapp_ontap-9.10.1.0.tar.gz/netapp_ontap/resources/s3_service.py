r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Overview
An S3 server is an object store server that is compatible with the Amazon S3 protocol. In the initial version, only a subset of the protocol features necessary to support Fabric Pool capacity tier usecases are implemented. S3 server allows you to store objects in ONTAP using Amazon S3 protocol. This feature can be used as a target object store server for ONTAP FabricPools.
## Performance monitoring
Performance of the SVM can be monitored by the `metric.*` and `statistics.*` properties. These show the performance of the SVM in terms of IOPS, latency and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
## Examples
### Retrieving all of the S3 configurations
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(S3Service.get_collection(fields="*", return_timeout=15)))

```
<div class="try_it_out">
<input id="example0_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example0_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example0_result" class="try_it_out_content">
```
[
    S3Service(
        {
            "enabled": False,
            "svm": {"uuid": "cf90b8f2-8071-11e9-8190-0050568eae21", "name": "vs2"},
            "comment": "S3 server",
            "name": "s1",
        }
    ),
    S3Service(
        {
            "enabled": True,
            "buckets": [
                {
                    "uuid": "e08665af-8114-11e9-8190-0050568eae21",
                    "logical_used_size": 157286400,
                    "volume": {
                        "uuid": "de146bff-8114-11e9-8190-0050568eae21",
                        "name": "fg_oss_1559026220",
                    },
                    "comment": "s3 bucket",
                    "size": 209715200,
                    "encryption": {"enabled": False},
                    "name": "bucket-1",
                },
                {
                    "uuid": "fb1912ef-8114-11e9-8190-0050568eae21",
                    "logical_used_size": 78643200,
                    "volume": {
                        "uuid": "f9b1cdd0-8114-11e9-8190-0050568eae21",
                        "name": "fg_oss_1559026269",
                    },
                    "comment": "s3 bucket",
                    "size": 104857600,
                    "encryption": {"enabled": False},
                    "name": "bucket-2",
                },
            ],
            "users": [
                {
                    "comment": "S3 user",
                    "name": "user-1",
                    "access_key": "3333_w162ypaTi7_aAQuJo76Z16zc9Gz_W3IN83bDQWkcCN3jYU_z_xn20XATMKKa90509KCH__r4lh1IPU58vf1QlWAJt8k2F1BPjPtM6CsDRX_dOP_QZkF5N9fBuz3",
                },
                {
                    "comment": "",
                    "name": "user-2",
                    "access_key": "g6T24qhH92dOA6gc1WTcDO_2oNZhQ6Drl2zu5_s5Id_QK1wLgghgxsD2xP1xqG7oX1T_9AI0D39q65CY3FAg0CbAtVU_903bSnCnht3xqjbrF5_3Cs9RnY8nE_az1Ltc",
                },
            ],
            "svm": {"uuid": "d7f1219c-7f8e-11e9-9124-0050568eae21", "name": "vs1"},
            "comment": "S3 server",
            "name": "Server-1",
        }
    ),
]

```
</div>
</div>

### Retrieving all S3 configurations for a particular SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service(**{"svm.uuid": "24c2567a-f269-11e8-8852-0050568e5298"})
    resource.get(fields="*")
    print(resource)

```
<div class="try_it_out">
<input id="example1_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example1_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example1_result" class="try_it_out_content">
```
S3Service(
    {
        "enabled": True,
        "buckets": [
            {
                "uuid": "e08665af-8114-11e9-8190-0050568eae21",
                "logical_used_size": 157286400,
                "policy": {
                    "statements": [
                        {
                            "principals": ["mike"],
                            "effect": "deny",
                            "resources": [
                                "bucket-1/policy-docs/*",
                                "bucket-1/confidential-*",
                            ],
                            "actions": ["*Object"],
                            "sid": "DenyAccessToGetPutDeleteObjectForMike",
                        },
                        {
                            "principals": ["*"],
                            "effect": "allow",
                            "resources": ["bucket-1/readme"],
                            "actions": ["GetObject"],
                            "sid": "AccessToGetObjectForAnonymousUser",
                        },
                    ]
                },
                "volume": {
                    "uuid": "de146bff-8114-11e9-8190-0050568eae21",
                    "name": "fg_oss_1559026220",
                },
                "comment": "s3 bucket",
                "size": 209715200,
                "encryption": {"enabled": False},
                "name": "bucket-1",
            },
            {
                "uuid": "fb1912ef-8114-11e9-8190-0050568eae21",
                "logical_used_size": 1075838976,
                "volume": {
                    "uuid": "f9b1cdd0-8114-11e9-8190-0050568eae21",
                    "name": "fg_oss_1559026269",
                },
                "comment": "s3 bucket",
                "size": 1677721600,
                "encryption": {"enabled": False},
                "name": "bucket-2",
            },
        ],
        "users": [
            {
                "comment": "s3 user",
                "name": "user-1",
                "access_key": "3333_w162ypaTi7_aAQuJo76Z16zc9Gz_W3IN83bDQWkcCN3jYU_z_xn20XATMKKa90509KCH__r4lh1IPU58vf1QlWAJt8k2F1BPjPtM6CsDRX_dOP_QZkF5N9fBuz3",
            },
            {
                "comment": "",
                "name": "user-2",
                "access_key": "g6T24qhH92dOA6gc1WTcDO_2oNZhQ6Drl2zu5_s5Id_QK1wLgghgxsD2xP1xqG7oX1T_9AI0D39q65CY3FAg0CbAtVU_903bSnCnht3xqjbrF5_3Cs9RnY8nE_az1Ltc",
            },
        ],
        "svm": {"uuid": "d7f1219c-7f8e-11e9-9124-0050568eae21", "name": "vs1"},
        "comment": "S3 server",
        "name": "Server-1",
    }
)

```
</div>
</div>

### Creating an S3 server, users, and buckets configurations with required fields specified
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service()
    resource.buckets = [{"name": "bucket-1"}, {"name": "bucket-2"}]
    resource.enabled = True
    resource.name = "Server-1"
    resource.svm = {"uuid": "d49ef663-7f8e-11e9-9b2c-0050568e4594"}
    resource.users = [{"name": "user-1"}, {"name": "user-2"}]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example2_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example2_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example2_result" class="try_it_out_content">
```
S3Service(
    {
        "users": [
            {
                "name": "user-1",
                "access_key": "x129aL0q9bu3J_4_2S0OcU34AA5DJXXB_j9R34_60tqiqAS5_c8PAgN6Lg1zkv_76P4IxNWir9st9uhhgldb31u364Cczq_c39C1fUP7HDheUmYY6u4xt61_N7Sw6c33",
            },
            {
                "name": "user-2",
                "access_key": "nntYZrNN65mKn57yS04o1sDp_D0AY58jdwCW573_5x2OPW09AbyFl86DB7r30N2373_bA12n08aovQp8ySItRss9AjsYoSj7TsIiHOW_Y21DaqYPl5I2a849b11y8X4c",
            },
        ],
        "_links": {"self": {"href": "/api/protocols/s3/services/"}},
    }
)

```
</div>
</div>

### Creating an S3 server, users, and buckets configurations
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service()
    resource.buckets = [
        {
            "aggregates": [
                {"name": "aggr1", "uuid": "1cd8a442-86d1-11e0-ae1c-123478563412"}
            ],
            "constituents_per_aggregate": 4,
            "name": "bucket-1",
            "size": "209715200",
            "policy": {
                "statements": [
                    {
                        "actions": ["*"],
                        "conditions": [
                            {
                                "operator": "ip_address",
                                "source_ips": ["1.1.1.1/23", "1.2.2.2/20"],
                            }
                        ],
                        "effect": "allow",
                        "resources": ["bucket-1", "bucket-1*"],
                        "sid": "fullAccessForAllPrincipalsToBucket",
                    }
                ]
            },
        },
        {
            "aggregates": [
                {"name": "aggr1", "uuid": "1cd8a442-86d1-11e0-ae1c-123478563412"},
                {"name": "aggr2", "uuid": "982fc4d0-d1a2-4da4-9c47-5b433f24757d"},
            ],
            "constituents_per_aggregate": 4,
            "name": "bucket-2",
        },
    ]
    resource.enabled = True
    resource.name = "Server-1"
    resource.svm = {"name": "vs1", "uuid": "d49ef663-7f8e-11e9-9b2c-0050568e4594"}
    resource.users = [{"name": "user-1"}, {"name": "user-2"}]
    resource.post(hydrate=True)
    print(resource)

```
<div class="try_it_out">
<input id="example3_try_it_out" type="checkbox", class="try_it_out_check">
<label for="example3_try_it_out" class="try_it_out_button">Try it out</label>
<div id="example3_result" class="try_it_out_content">
```
S3Service(
    {
        "users": [
            {
                "name": "user-1",
                "access_key": "x129aL0q9bu3J_4_2S0OcU34AA5DJXXB_j9R34_60tqiqAS5_c8PAgN6Lg1zkv_76P4IxNWir9st9uhhgldb31u364Cczq_c39C1fUP7HDheUmYY6u4xt61_N7Sw6c33",
            },
            {
                "name": "user-2",
                "access_key": "nntYZrNN65mKn57yS04o1sDp_D0AY58jdwCW573_5x2OPW09AbyFl86DB7r30N2373_bA12n08aovQp8ySItRss9AjsYoSj7TsIiHOW_Y21DaqYPl5I2a849b11y8X4c",
            },
        ],
        "_links": {"self": {"href": "/api/protocols/s3/services/"}},
    }
)

```
</div>
</div>

### Creating an S3 server configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service()
    resource.comment = "S3 server"
    resource.enabled = True
    resource.name = "Server-1"
    resource.svm = {"name": "vs1", "uuid": "db2ec036-8375-11e9-99e1-0050568e3ed9"}
    resource.post(hydrate=True)
    print(resource)

```

### Disable s3 server for the specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service(**{"svm.uuid": "03ce5c36-f269-11e8-8852-0050568e5298"})
    resource.enabled = False
    resource.patch()

```

### Deleting the S3 server for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service(**{"svm.uuid": "a425f10b-ad3b-11e9-b559-0050568e8222"})
    resource.delete(delete_all=False)

```

### Deleting all of the S3 server configuration for a specified SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import S3Service

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = S3Service(**{"svm.uuid": "03ce5c36-f269-11e8-8852-0050568e5298"})
    resource.delete(delete_all=True)

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


__all__ = ["S3Service", "S3ServiceSchema"]
__pdoc__ = {
    "S3ServiceSchema.resource": False,
    "S3Service.s3_service_show": False,
    "S3Service.s3_service_create": False,
    "S3Service.s3_service_modify": False,
    "S3Service.s3_service_delete": False,
}


class S3ServiceSchema(ResourceSchema):
    """The fields of the S3Service object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the s3_service. """

    buckets = fields.List(fields.Nested("netapp_ontap.resources.s3_bucket.S3BucketSchema", unknown=EXCLUDE), data_key="buckets")
    r""" The buckets field of the s3_service. """

    certificate = fields.Nested("netapp_ontap.resources.security_certificate.SecurityCertificateSchema", data_key="certificate", unknown=EXCLUDE)
    r""" The certificate field of the s3_service. """

    comment = fields.Str(
        data_key="comment",
        validate=len_validation(minimum=0, maximum=256),
    )
    r""" Can contain any additional information about the server being created or modified.

Example: S3 server """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies whether the S3 server being created or modified should be up or down. """

    is_http_enabled = fields.Boolean(
        data_key="is_http_enabled",
    )
    r""" Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server. """

    is_https_enabled = fields.Boolean(
        data_key="is_https_enabled",
    )
    r""" Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server. """

    metric = fields.Nested("netapp_ontap.models.performance_metric_svm.PerformanceMetricSvmSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the s3_service. """

    name = fields.Str(
        data_key="name",
        validate=len_validation(minimum=1, maximum=253),
    )
    r""" Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, ".", and "-".

Example: Server-1 """

    port = Size(
        data_key="port",
    )
    r""" Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80. """

    secure_port = Size(
        data_key="secure_port",
    )
    r""" Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443. """

    statistics = fields.Nested("netapp_ontap.models.performance_metric_raw_svm.PerformanceMetricRawSvmSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the s3_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the s3_service. """

    users = fields.List(fields.Nested("netapp_ontap.resources.s3_user.S3UserSchema", unknown=EXCLUDE), data_key="users")
    r""" The users field of the s3_service. """

    @property
    def resource(self):
        return S3Service

    gettable_fields = [
        "links",
        "buckets",
        "certificate.links",
        "certificate.name",
        "certificate.uuid",
        "comment",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "metric.links",
        "metric.duration",
        "metric.iops",
        "metric.latency",
        "metric.status",
        "metric.throughput",
        "metric.timestamp",
        "name",
        "port",
        "secure_port",
        "statistics.iops_raw",
        "statistics.latency_raw",
        "statistics.status",
        "statistics.throughput_raw",
        "statistics.timestamp",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "users",
    ]
    """links,buckets,certificate.links,certificate.name,certificate.uuid,comment,enabled,is_http_enabled,is_https_enabled,metric.links,metric.duration,metric.iops,metric.latency,metric.status,metric.throughput,metric.timestamp,name,port,secure_port,statistics.iops_raw,statistics.latency_raw,statistics.status,statistics.throughput_raw,statistics.timestamp,svm.links,svm.name,svm.uuid,users,"""

    patchable_fields = [
        "certificate.name",
        "certificate.uuid",
        "comment",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "name",
        "port",
        "secure_port",
    ]
    """certificate.name,certificate.uuid,comment,enabled,is_http_enabled,is_https_enabled,name,port,secure_port,"""

    postable_fields = [
        "buckets",
        "certificate.name",
        "certificate.uuid",
        "comment",
        "enabled",
        "is_http_enabled",
        "is_https_enabled",
        "name",
        "port",
        "secure_port",
        "svm.name",
        "svm.uuid",
        "users",
    ]
    """buckets,certificate.name,certificate.uuid,comment,enabled,is_http_enabled,is_https_enabled,name,port,secure_port,svm.name,svm.uuid,users,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in S3Service.get_collection(fields=field)]
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
            raise NetAppRestError("S3Service modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class S3Service(Resource):
    r""" Specifies the S3 server configuration. """

    _schema = S3ServiceSchema
    _path = "/api/protocols/s3/services"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the S3 server configuration for all SVMs. Note that in order to retrieve S3 bucket policy conditions, 'fields' option should be set to '**'.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver object-store-server show`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 service show")
        def s3_service_show(
            fields: List[Choices.define(["comment", "enabled", "is_http_enabled", "is_https_enabled", "name", "port", "secure_port", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of S3Service resources

            Args:
                comment: Can contain any additional information about the server being created or modified.
                enabled: Specifies whether the S3 server being created or modified should be up or down.
                is_http_enabled: Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server.
                is_https_enabled: Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server.
                name: Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, \".\", and \"-\".
                port: Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80.
                secure_port: Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if enabled is not None:
                kwargs["enabled"] = enabled
            if is_http_enabled is not None:
                kwargs["is_http_enabled"] = is_http_enabled
            if is_https_enabled is not None:
                kwargs["is_https_enabled"] = is_https_enabled
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if secure_port is not None:
                kwargs["secure_port"] = secure_port
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return S3Service.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all S3Service resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["S3Service"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 Server configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server modify`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["S3Service"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["S3Service"], NetAppResponse]:
        r"""Creates an S3 server, users, and buckets configurations.
### Important notes
- Each SVM can have one S3 server configuration.
- One or more buckets and users can also be created using this end-point.
- If creating a user configuration fails, buckets are not created either and already created users are not saved.
- If creating a bucket configuration fails, all buckets already created are saved with no new buckets created.
### Required properties
* `svm.uuid` - Existing SVM in which to create an S3 server configuration.
### Recommended optional properties
* `enabled` - Specifies the state of the server created.
* `comment` - Any information related to the server created.
### Default property values
* `comment` - ""
* `enabled` - _true_
### Related ONTAP commands
* `vserver object-store-server create`
* `vserver object-store-server bucket create`
* `vserver object-store-server bucket policy statement create`
* `vserver object-store-server bucket policy-statement-condition create`
* `vserver object-store-server user create`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
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
        records: Iterable["S3Service"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 server configuration of an SVM. If the 'delete_all' parameter is set to false, only the S3 server is deleted. Otherwise S3 users and buckets present on the SVM are also deleted. Note that only empty buckets can be deleted. This endpoint returns the S3 server delete job-uuid in response. To monitor the job status follow /api/cluster/jobs/<job-uuid>.
### Related ONTAP commands
* `vserver object-store-server delete`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the S3 server configuration for all SVMs. Note that in order to retrieve S3 bucket policy conditions, 'fields' option should be set to '**'.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver object-store-server show`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the S3 Server configuration of an SVM. Note that in order to retrieve S3 bucket policy conditions, the 'fields' option should be set to '**'.
### Related ONTAP commands
* `vserver object-store-server show`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
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
        r"""Creates an S3 server, users, and buckets configurations.
### Important notes
- Each SVM can have one S3 server configuration.
- One or more buckets and users can also be created using this end-point.
- If creating a user configuration fails, buckets are not created either and already created users are not saved.
- If creating a bucket configuration fails, all buckets already created are saved with no new buckets created.
### Required properties
* `svm.uuid` - Existing SVM in which to create an S3 server configuration.
### Recommended optional properties
* `enabled` - Specifies the state of the server created.
* `comment` - Any information related to the server created.
### Default property values
* `comment` - ""
* `enabled` - _true_
### Related ONTAP commands
* `vserver object-store-server create`
* `vserver object-store-server bucket create`
* `vserver object-store-server bucket policy statement create`
* `vserver object-store-server bucket policy-statement-condition create`
* `vserver object-store-server user create`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 service create")
        async def s3_service_create(
        ) -> ResourceTable:
            """Create an instance of a S3Service resource

            Args:
                links: 
                buckets: 
                certificate: 
                comment: Can contain any additional information about the server being created or modified.
                enabled: Specifies whether the S3 server being created or modified should be up or down.
                is_http_enabled: Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server.
                is_https_enabled: Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server.
                metric: 
                name: Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, \".\", and \"-\".
                port: Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80.
                secure_port: Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443.
                statistics: 
                svm: 
                users: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if buckets is not None:
                kwargs["buckets"] = buckets
            if certificate is not None:
                kwargs["certificate"] = certificate
            if comment is not None:
                kwargs["comment"] = comment
            if enabled is not None:
                kwargs["enabled"] = enabled
            if is_http_enabled is not None:
                kwargs["is_http_enabled"] = is_http_enabled
            if is_https_enabled is not None:
                kwargs["is_https_enabled"] = is_https_enabled
            if metric is not None:
                kwargs["metric"] = metric
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if secure_port is not None:
                kwargs["secure_port"] = secure_port
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm
            if users is not None:
                kwargs["users"] = users

            resource = S3Service(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create S3Service: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the S3 Server configuration of an SVM.
### Related ONTAP commands
* `vserver object-store-server modify`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 service modify")
        async def s3_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a S3Service resource

            Args:
                comment: Can contain any additional information about the server being created or modified.
                query_comment: Can contain any additional information about the server being created or modified.
                enabled: Specifies whether the S3 server being created or modified should be up or down.
                query_enabled: Specifies whether the S3 server being created or modified should be up or down.
                is_http_enabled: Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server.
                query_is_http_enabled: Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server.
                is_https_enabled: Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server.
                query_is_https_enabled: Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server.
                name: Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, \".\", and \"-\".
                query_name: Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, \".\", and \"-\".
                port: Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80.
                query_port: Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80.
                secure_port: Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443.
                query_secure_port: Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443.
            """

            kwargs = {}
            changes = {}
            if query_comment is not None:
                kwargs["comment"] = query_comment
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_is_http_enabled is not None:
                kwargs["is_http_enabled"] = query_is_http_enabled
            if query_is_https_enabled is not None:
                kwargs["is_https_enabled"] = query_is_https_enabled
            if query_name is not None:
                kwargs["name"] = query_name
            if query_port is not None:
                kwargs["port"] = query_port
            if query_secure_port is not None:
                kwargs["secure_port"] = query_secure_port

            if comment is not None:
                changes["comment"] = comment
            if enabled is not None:
                changes["enabled"] = enabled
            if is_http_enabled is not None:
                changes["is_http_enabled"] = is_http_enabled
            if is_https_enabled is not None:
                changes["is_https_enabled"] = is_https_enabled
            if name is not None:
                changes["name"] = name
            if port is not None:
                changes["port"] = port
            if secure_port is not None:
                changes["secure_port"] = secure_port

            if hasattr(S3Service, "find"):
                resource = S3Service.find(
                    **kwargs
                )
            else:
                resource = S3Service()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify S3Service: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the S3 server configuration of an SVM. If the 'delete_all' parameter is set to false, only the S3 server is deleted. Otherwise S3 users and buckets present on the SVM are also deleted. Note that only empty buckets can be deleted. This endpoint returns the S3 server delete job-uuid in response. To monitor the job status follow /api/cluster/jobs/<job-uuid>.
### Related ONTAP commands
* `vserver object-store-server delete`
### Learn more
* [`DOC /protocols/s3/services`](#docs-object-store-protocols_s3_services)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="s3 service delete")
        async def s3_service_delete(
        ) -> None:
            """Delete an instance of a S3Service resource

            Args:
                comment: Can contain any additional information about the server being created or modified.
                enabled: Specifies whether the S3 server being created or modified should be up or down.
                is_http_enabled: Specifies whether HTTP is enabled on the S3 server being created or modified. By default, HTTP is disabled on the S3 server.
                is_https_enabled: Specifies whether HTTPS is enabled on the S3 server being created or modified. By default, HTTPS is enabled on the S3 server.
                name: Specifies the name of the S3 server. A server name can contain 1 to 253 characters using only the following combination of characters':' 0-9, A-Z, a-z, \".\", and \"-\".
                port: Specifies the HTTP listener port for the S3 server. By default, HTTP is enabled on port 80.
                secure_port: Specifies the HTTPS listener port for the S3 server. By default, HTTPS is enabled on port 443.
            """

            kwargs = {}
            if comment is not None:
                kwargs["comment"] = comment
            if enabled is not None:
                kwargs["enabled"] = enabled
            if is_http_enabled is not None:
                kwargs["is_http_enabled"] = is_http_enabled
            if is_https_enabled is not None:
                kwargs["is_https_enabled"] = is_https_enabled
            if name is not None:
                kwargs["name"] = name
            if port is not None:
                kwargs["port"] = port
            if secure_port is not None:
                kwargs["secure_port"] = secure_port

            if hasattr(S3Service, "find"):
                resource = S3Service.find(
                    **kwargs
                )
            else:
                resource = S3Service()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete S3Service: %s" % err)


