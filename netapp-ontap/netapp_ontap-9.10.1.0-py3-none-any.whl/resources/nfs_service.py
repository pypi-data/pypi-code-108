r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

### Retrieving an NFS configuration
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(list(NfsService.get_collection()))

```

### Retrieving the mount permissions for a specified volume for a given IP address.
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    print(
        list(
            NfsService.get_collection(
                fields="*",
                return_timeout=15,
                **{
                    "protocol_access_rules.volume": "testvol12",
                    "protocol_access_rules.client_ip": "1.2.3.4",
                    "protocol_access_rules.auth_type": "sys",
                    "svm.uuid": "525928e9-9f84-11eb-a89f-005056bb70a8",
                }
            )
        )
    )

```

### Creating an NFS configuration for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NfsService()
    resource.svm = {"uuid": "1cd8a442-86d1-11e0-ae1c-123478563412"}
    resource.protocol = {"v4_id_domain": "nfs-nsr-w01.rtp.netapp.com"}
    resource.vstorage_enabled = True
    resource.post(hydrate=True)
    print(resource)

```

### Updating an  NFS configuration for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NfsService(**{"svm.uuid": "4a415601-548c-11e8-a21d-0050568bcbc9"})
    resource.protocol = {"v4_id_domain": "nfs-nsr-w01.rtp.netapp.com"}
    resource.vstorage_enabled = False
    resource.patch()

```

### Deleting an NFS configuration for an SVM
```python
from netapp_ontap import HostConnection
from netapp_ontap.resources import NfsService

with HostConnection("<mgmt-ip>", username="admin", password="password", verify=False):
    resource = NfsService(**{"svm.uuid": "4a415601-548c-11e8-a21d-0050568bcbc9"})
    resource.delete()

```

## Performance monitoring
Performance of the SVM can be monitored by the `metric.*` and `statistics.*` properties. These show the performance of the SVM in terms of IOPS, latency and throughput. The `metric.*` properties denote an average whereas `statistics.*` properties denote a real-time monotonically increasing value aggregated across all nodes.
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


__all__ = ["NfsService", "NfsServiceSchema"]
__pdoc__ = {
    "NfsServiceSchema.resource": False,
    "NfsService.nfs_service_show": False,
    "NfsService.nfs_service_create": False,
    "NfsService.nfs_service_modify": False,
    "NfsService.nfs_service_delete": False,
}


class NfsServiceSchema(ResourceSchema):
    """The fields of the NfsService object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the nfs_service. """

    access_cache_config = fields.Nested("netapp_ontap.models.nfs_service_access_cache_config.NfsServiceAccessCacheConfigSchema", data_key="access_cache_config", unknown=EXCLUDE)
    r""" The access_cache_config field of the nfs_service. """

    auth_sys_extended_groups_enabled = fields.Boolean(
        data_key="auth_sys_extended_groups_enabled",
    )
    r""" Specifies whether or not extended groups support over AUTH_SYS is enabled. """

    enabled = fields.Boolean(
        data_key="enabled",
    )
    r""" Specifies if the NFS service is administratively enabled. """

    extended_groups_limit = Size(
        data_key="extended_groups_limit",
        validate=integer_validation(minimum=32, maximum=1024),
    )
    r""" Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.

Example: 32 """

    metric = fields.Nested("netapp_ontap.models.performance_svm_nfs_metric.PerformanceSvmNfsMetricSchema", data_key="metric", unknown=EXCLUDE)
    r""" The metric field of the nfs_service. """

    positive_cached_credential_ttl = Size(
        data_key="positive_cached_credential_ttl",
        validate=integer_validation(minimum=60000, maximum=604800000),
    )
    r""" Specifies the time to live value (in msecs) of a positive cached credential

Example: 7200000 """

    protocol = fields.Nested("netapp_ontap.models.nfs_service_protocol.NfsServiceProtocolSchema", data_key="protocol", unknown=EXCLUDE)
    r""" The protocol field of the nfs_service. """

    protocol_access_rules = fields.Nested("netapp_ontap.models.nfs_service_protocol_access_rules.NfsServiceProtocolAccessRulesSchema", data_key="protocol_access_rules", unknown=EXCLUDE)
    r""" The protocol_access_rules field of the nfs_service. """

    qtree = fields.Nested("netapp_ontap.models.nfs_service_qtree.NfsServiceQtreeSchema", data_key="qtree", unknown=EXCLUDE)
    r""" The qtree field of the nfs_service. """

    rquota_enabled = fields.Boolean(
        data_key="rquota_enabled",
    )
    r""" Specifies whether or not the remote quota feature is enabled. """

    showmount_enabled = fields.Boolean(
        data_key="showmount_enabled",
    )
    r""" Specifies whether or not the showmount feature is enabled. """

    state = fields.Str(
        data_key="state",
        validate=enum_validation(['online', 'offline']),
    )
    r""" Specifies the state of the NFS service on the SVM. The following values are supported:

          * online - NFS server is ready to accept client requests.
          * offline - NFS server is not ready to accept client requests.


Valid choices:

* online
* offline """

    statistics = fields.Nested("netapp_ontap.models.performance_svm_nfs_statistics.PerformanceSvmNfsStatisticsSchema", data_key="statistics", unknown=EXCLUDE)
    r""" The statistics field of the nfs_service. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the nfs_service. """

    transport = fields.Nested("netapp_ontap.models.nfs_service_transport.NfsServiceTransportSchema", data_key="transport", unknown=EXCLUDE)
    r""" The transport field of the nfs_service. """

    vstorage_enabled = fields.Boolean(
        data_key="vstorage_enabled",
    )
    r""" Specifies whether or not the VMware vstorage feature is enabled. """

    @property
    def resource(self):
        return NfsService

    gettable_fields = [
        "links",
        "access_cache_config",
        "auth_sys_extended_groups_enabled",
        "enabled",
        "extended_groups_limit",
        "metric",
        "positive_cached_credential_ttl",
        "protocol",
        "protocol_access_rules",
        "qtree",
        "rquota_enabled",
        "showmount_enabled",
        "state",
        "statistics",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "transport",
        "vstorage_enabled",
    ]
    """links,access_cache_config,auth_sys_extended_groups_enabled,enabled,extended_groups_limit,metric,positive_cached_credential_ttl,protocol,protocol_access_rules,qtree,rquota_enabled,showmount_enabled,state,statistics,svm.links,svm.name,svm.uuid,transport,vstorage_enabled,"""

    patchable_fields = [
        "access_cache_config",
        "auth_sys_extended_groups_enabled",
        "enabled",
        "extended_groups_limit",
        "positive_cached_credential_ttl",
        "protocol",
        "protocol_access_rules",
        "qtree",
        "rquota_enabled",
        "showmount_enabled",
        "svm.name",
        "svm.uuid",
        "transport",
        "vstorage_enabled",
    ]
    """access_cache_config,auth_sys_extended_groups_enabled,enabled,extended_groups_limit,positive_cached_credential_ttl,protocol,protocol_access_rules,qtree,rquota_enabled,showmount_enabled,svm.name,svm.uuid,transport,vstorage_enabled,"""

    postable_fields = [
        "access_cache_config",
        "auth_sys_extended_groups_enabled",
        "enabled",
        "extended_groups_limit",
        "positive_cached_credential_ttl",
        "protocol",
        "protocol_access_rules",
        "qtree",
        "rquota_enabled",
        "showmount_enabled",
        "svm.name",
        "svm.uuid",
        "transport",
        "vstorage_enabled",
    ]
    """access_cache_config,auth_sys_extended_groups_enabled,enabled,extended_groups_limit,positive_cached_credential_ttl,protocol,protocol_access_rules,qtree,rquota_enabled,showmount_enabled,svm.name,svm.uuid,transport,vstorage_enabled,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in NfsService.get_collection(fields=field)]
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
            raise NetAppRestError("NfsService modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class NfsService(Resource):
    """Allows interaction with NfsService objects on the host"""

    _schema = NfsServiceSchema
    _path = "/api/protocols/nfs/services"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the NFS configuration of SVMs.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nfs show`
* `vserver nfs status`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nfs service show")
        def nfs_service_show(
            fields: List[Choices.define(["auth_sys_extended_groups_enabled", "enabled", "extended_groups_limit", "positive_cached_credential_ttl", "rquota_enabled", "showmount_enabled", "state", "vstorage_enabled", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of NfsService resources

            Args:
                auth_sys_extended_groups_enabled: Specifies whether or not extended groups support over AUTH_SYS is enabled.
                enabled: Specifies if the NFS service is administratively enabled. 
                extended_groups_limit: Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.
                positive_cached_credential_ttl: Specifies the time to live value (in msecs) of a positive cached credential
                rquota_enabled: Specifies whether or not the remote quota feature is enabled.
                showmount_enabled: Specifies whether or not the showmount feature is enabled.
                state: Specifies the state of the NFS service on the SVM. The following values are supported:           * online - NFS server is ready to accept client requests.           * offline - NFS server is not ready to accept client requests. 
                vstorage_enabled: Specifies whether or not the VMware vstorage feature is enabled.
            """

            kwargs = {}
            if auth_sys_extended_groups_enabled is not None:
                kwargs["auth_sys_extended_groups_enabled"] = auth_sys_extended_groups_enabled
            if enabled is not None:
                kwargs["enabled"] = enabled
            if extended_groups_limit is not None:
                kwargs["extended_groups_limit"] = extended_groups_limit
            if positive_cached_credential_ttl is not None:
                kwargs["positive_cached_credential_ttl"] = positive_cached_credential_ttl
            if rquota_enabled is not None:
                kwargs["rquota_enabled"] = rquota_enabled
            if showmount_enabled is not None:
                kwargs["showmount_enabled"] = showmount_enabled
            if state is not None:
                kwargs["state"] = state
            if vstorage_enabled is not None:
                kwargs["vstorage_enabled"] = vstorage_enabled
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return NfsService.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all NfsService resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["NfsService"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the NFS configuration of an SVM.
### Related ONTAP commands
* `vserver nfs modify`
* `vserver nfs on`
* `vserver nfs off`
* `vserver nfs start`
* `vserver nfs stop`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["NfsService"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["NfsService"], NetAppResponse]:
        r"""Creates an NFS configuration for an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which to create the NFS configuration.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `state` - online
* `transport.udp_enabled` - _true_
* `transport.tcp_enabled` - _true_
* `protocol.v3_enabled` - _true_
* `protocol.v3_64bit_identifiers_enabled` - _false_
* `protocol.v4_id_domain` - defaultv4iddomain.com
* `protocol.v4_64bit_identifiers_enabled` - _true_
* `protocol.v4_enabled` - _false_
* `protocol.v41_enabled` - _false_
* `protocol.v40_features.acl_enabled` - _false_
* `protocol.v40_features.read_delegation_enabled` - _false_
* `protocol.v40_features.write_delegation_enabled` - _false_
* `protocol.v41_features.acl_enabled` - _false_
* `protocol.v41_features.read_delegation_enabled` - _false_
* `protocol.v41_features.write_delegation_enabled` - _false_
* `protocol.v41_features.pnfs_enabled` - _false_
* `vstorage_enabled` - _false_
* `rquota_enabled` - _false_
* `showmount_enabled` - _true_
* `auth_sys_extended_groups_enabled` - _false_
* `extended_groups_limit` - _32_
* `positive_cached_credential_ttl` - _7200000_
* `qtree.export_enabled` - _false_
* `qtree.validate_export` - _true_
* `access_cache_config.ttl_positive` - _60_
* `access_cache_config.ttl_negative` - _30_
* `access_cache_config.ttl_failure` - _1_
* `access_cache_config.harvest_timeout` - _3600_
* `access_cache_config.isDnsTTLEnabled` - _false_
### Related ONTAP commands
* `vserver nfs create`
* `export-policy access-cache config show`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
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
        records: Iterable["NfsService"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the NFS configuration of an SVM.
### Related ONTAP commands
* `vserver nfs delete`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the NFS configuration of SVMs.
### Expensive properties
There is an added cost to retrieving values for these properties. They are not included by default in GET results and must be explicitly requested using the `fields` query parameter. See [`Requesting specific fields`](#Requesting_specific_fields) to learn more.
* `statistics.*`
* `metric.*`
### Related ONTAP commands
* `vserver nfs show`
* `vserver nfs status`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the NFS configuration of an SVM.
### Related ONTAP commands
* `vserver nfs show`
* `vserver nfs status`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
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
        r"""Creates an NFS configuration for an SVM.
### Required properties
* `svm.uuid` or `svm.name` - Existing SVM for which to create the NFS configuration.
### Default property values
If not specified in POST, the following default property values are assigned:
* `enabled` - _true_
* `state` - online
* `transport.udp_enabled` - _true_
* `transport.tcp_enabled` - _true_
* `protocol.v3_enabled` - _true_
* `protocol.v3_64bit_identifiers_enabled` - _false_
* `protocol.v4_id_domain` - defaultv4iddomain.com
* `protocol.v4_64bit_identifiers_enabled` - _true_
* `protocol.v4_enabled` - _false_
* `protocol.v41_enabled` - _false_
* `protocol.v40_features.acl_enabled` - _false_
* `protocol.v40_features.read_delegation_enabled` - _false_
* `protocol.v40_features.write_delegation_enabled` - _false_
* `protocol.v41_features.acl_enabled` - _false_
* `protocol.v41_features.read_delegation_enabled` - _false_
* `protocol.v41_features.write_delegation_enabled` - _false_
* `protocol.v41_features.pnfs_enabled` - _false_
* `vstorage_enabled` - _false_
* `rquota_enabled` - _false_
* `showmount_enabled` - _true_
* `auth_sys_extended_groups_enabled` - _false_
* `extended_groups_limit` - _32_
* `positive_cached_credential_ttl` - _7200000_
* `qtree.export_enabled` - _false_
* `qtree.validate_export` - _true_
* `access_cache_config.ttl_positive` - _60_
* `access_cache_config.ttl_negative` - _30_
* `access_cache_config.ttl_failure` - _1_
* `access_cache_config.harvest_timeout` - _3600_
* `access_cache_config.isDnsTTLEnabled` - _false_
### Related ONTAP commands
* `vserver nfs create`
* `export-policy access-cache config show`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nfs service create")
        async def nfs_service_create(
        ) -> ResourceTable:
            """Create an instance of a NfsService resource

            Args:
                links: 
                access_cache_config: 
                auth_sys_extended_groups_enabled: Specifies whether or not extended groups support over AUTH_SYS is enabled.
                enabled: Specifies if the NFS service is administratively enabled. 
                extended_groups_limit: Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.
                metric: 
                positive_cached_credential_ttl: Specifies the time to live value (in msecs) of a positive cached credential
                protocol: 
                protocol_access_rules: 
                qtree: 
                rquota_enabled: Specifies whether or not the remote quota feature is enabled.
                showmount_enabled: Specifies whether or not the showmount feature is enabled.
                state: Specifies the state of the NFS service on the SVM. The following values are supported:           * online - NFS server is ready to accept client requests.           * offline - NFS server is not ready to accept client requests. 
                statistics: 
                svm: 
                transport: 
                vstorage_enabled: Specifies whether or not the VMware vstorage feature is enabled.
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if access_cache_config is not None:
                kwargs["access_cache_config"] = access_cache_config
            if auth_sys_extended_groups_enabled is not None:
                kwargs["auth_sys_extended_groups_enabled"] = auth_sys_extended_groups_enabled
            if enabled is not None:
                kwargs["enabled"] = enabled
            if extended_groups_limit is not None:
                kwargs["extended_groups_limit"] = extended_groups_limit
            if metric is not None:
                kwargs["metric"] = metric
            if positive_cached_credential_ttl is not None:
                kwargs["positive_cached_credential_ttl"] = positive_cached_credential_ttl
            if protocol is not None:
                kwargs["protocol"] = protocol
            if protocol_access_rules is not None:
                kwargs["protocol_access_rules"] = protocol_access_rules
            if qtree is not None:
                kwargs["qtree"] = qtree
            if rquota_enabled is not None:
                kwargs["rquota_enabled"] = rquota_enabled
            if showmount_enabled is not None:
                kwargs["showmount_enabled"] = showmount_enabled
            if state is not None:
                kwargs["state"] = state
            if statistics is not None:
                kwargs["statistics"] = statistics
            if svm is not None:
                kwargs["svm"] = svm
            if transport is not None:
                kwargs["transport"] = transport
            if vstorage_enabled is not None:
                kwargs["vstorage_enabled"] = vstorage_enabled

            resource = NfsService(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create NfsService: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the NFS configuration of an SVM.
### Related ONTAP commands
* `vserver nfs modify`
* `vserver nfs on`
* `vserver nfs off`
* `vserver nfs start`
* `vserver nfs stop`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nfs service modify")
        async def nfs_service_modify(
        ) -> ResourceTable:
            """Modify an instance of a NfsService resource

            Args:
                auth_sys_extended_groups_enabled: Specifies whether or not extended groups support over AUTH_SYS is enabled.
                query_auth_sys_extended_groups_enabled: Specifies whether or not extended groups support over AUTH_SYS is enabled.
                enabled: Specifies if the NFS service is administratively enabled. 
                query_enabled: Specifies if the NFS service is administratively enabled. 
                extended_groups_limit: Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.
                query_extended_groups_limit: Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.
                positive_cached_credential_ttl: Specifies the time to live value (in msecs) of a positive cached credential
                query_positive_cached_credential_ttl: Specifies the time to live value (in msecs) of a positive cached credential
                rquota_enabled: Specifies whether or not the remote quota feature is enabled.
                query_rquota_enabled: Specifies whether or not the remote quota feature is enabled.
                showmount_enabled: Specifies whether or not the showmount feature is enabled.
                query_showmount_enabled: Specifies whether or not the showmount feature is enabled.
                state: Specifies the state of the NFS service on the SVM. The following values are supported:           * online - NFS server is ready to accept client requests.           * offline - NFS server is not ready to accept client requests. 
                query_state: Specifies the state of the NFS service on the SVM. The following values are supported:           * online - NFS server is ready to accept client requests.           * offline - NFS server is not ready to accept client requests. 
                vstorage_enabled: Specifies whether or not the VMware vstorage feature is enabled.
                query_vstorage_enabled: Specifies whether or not the VMware vstorage feature is enabled.
            """

            kwargs = {}
            changes = {}
            if query_auth_sys_extended_groups_enabled is not None:
                kwargs["auth_sys_extended_groups_enabled"] = query_auth_sys_extended_groups_enabled
            if query_enabled is not None:
                kwargs["enabled"] = query_enabled
            if query_extended_groups_limit is not None:
                kwargs["extended_groups_limit"] = query_extended_groups_limit
            if query_positive_cached_credential_ttl is not None:
                kwargs["positive_cached_credential_ttl"] = query_positive_cached_credential_ttl
            if query_rquota_enabled is not None:
                kwargs["rquota_enabled"] = query_rquota_enabled
            if query_showmount_enabled is not None:
                kwargs["showmount_enabled"] = query_showmount_enabled
            if query_state is not None:
                kwargs["state"] = query_state
            if query_vstorage_enabled is not None:
                kwargs["vstorage_enabled"] = query_vstorage_enabled

            if auth_sys_extended_groups_enabled is not None:
                changes["auth_sys_extended_groups_enabled"] = auth_sys_extended_groups_enabled
            if enabled is not None:
                changes["enabled"] = enabled
            if extended_groups_limit is not None:
                changes["extended_groups_limit"] = extended_groups_limit
            if positive_cached_credential_ttl is not None:
                changes["positive_cached_credential_ttl"] = positive_cached_credential_ttl
            if rquota_enabled is not None:
                changes["rquota_enabled"] = rquota_enabled
            if showmount_enabled is not None:
                changes["showmount_enabled"] = showmount_enabled
            if state is not None:
                changes["state"] = state
            if vstorage_enabled is not None:
                changes["vstorage_enabled"] = vstorage_enabled

            if hasattr(NfsService, "find"):
                resource = NfsService.find(
                    **kwargs
                )
            else:
                resource = NfsService()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify NfsService: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the NFS configuration of an SVM.
### Related ONTAP commands
* `vserver nfs delete`
### Learn more
* [`DOC /protocols/nfs/services`](#docs-NAS-protocols_nfs_services)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="nfs service delete")
        async def nfs_service_delete(
        ) -> None:
            """Delete an instance of a NfsService resource

            Args:
                auth_sys_extended_groups_enabled: Specifies whether or not extended groups support over AUTH_SYS is enabled.
                enabled: Specifies if the NFS service is administratively enabled. 
                extended_groups_limit: Specifies the maximum auxillary groups supported over AUTH_SYS and RPCSEC_GSS.
                positive_cached_credential_ttl: Specifies the time to live value (in msecs) of a positive cached credential
                rquota_enabled: Specifies whether or not the remote quota feature is enabled.
                showmount_enabled: Specifies whether or not the showmount feature is enabled.
                state: Specifies the state of the NFS service on the SVM. The following values are supported:           * online - NFS server is ready to accept client requests.           * offline - NFS server is not ready to accept client requests. 
                vstorage_enabled: Specifies whether or not the VMware vstorage feature is enabled.
            """

            kwargs = {}
            if auth_sys_extended_groups_enabled is not None:
                kwargs["auth_sys_extended_groups_enabled"] = auth_sys_extended_groups_enabled
            if enabled is not None:
                kwargs["enabled"] = enabled
            if extended_groups_limit is not None:
                kwargs["extended_groups_limit"] = extended_groups_limit
            if positive_cached_credential_ttl is not None:
                kwargs["positive_cached_credential_ttl"] = positive_cached_credential_ttl
            if rquota_enabled is not None:
                kwargs["rquota_enabled"] = rquota_enabled
            if showmount_enabled is not None:
                kwargs["showmount_enabled"] = showmount_enabled
            if state is not None:
                kwargs["state"] = state
            if vstorage_enabled is not None:
                kwargs["vstorage_enabled"] = vstorage_enabled

            if hasattr(NfsService, "find"):
                resource = NfsService.find(
                    **kwargs
                )
            else:
                resource = NfsService()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete NfsService: %s" % err)


