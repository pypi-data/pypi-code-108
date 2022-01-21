r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

## Retrieving a collection of cloud targets
The cloud targets GET API retrieves all cloud targets defined in the cluster.
## Creating cloud targets
The cluster administrator tells ONTAP how to connect to a cloud target. The following pre-requisites must be met before creating an object store configuration in ONTAP.
A valid data bucket or container must be created with the object store provider. This assumes that the user has valid account credentials with the object store provider to access the data bucket.
The ONTAP node must be able to connect to the object store. </br>
This includes:
  - Fast, reliable connectivity to the object store.
  - An inter-cluster LIF (logical interface) must be configured on the cluster. ONTAP verifies connectivity prior to saving this configuration information.
  - If SSL/TLS authentication is required, then valid certificates must be installed.
  - FabricPool license (required for all object stores except SGWS).
## Deleting cloud targets
If a cloud target is used by an aggregate, then the aggregate must be deleted before the cloud target can be deleted.
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


__all__ = ["CloudTarget", "CloudTargetSchema"]
__pdoc__ = {
    "CloudTargetSchema.resource": False,
    "CloudTarget.cloud_target_show": False,
    "CloudTarget.cloud_target_create": False,
    "CloudTarget.cloud_target_modify": False,
    "CloudTarget.cloud_target_delete": False,
}


class CloudTargetSchema(ResourceSchema):
    """The fields of the CloudTarget object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the cloud_target. """

    access_key = fields.Str(
        data_key="access_key",
    )
    r""" Access key ID for AWS_S3 and other S3 compatible provider types. """

    authentication_type = fields.Str(
        data_key="authentication_type",
        validate=enum_validation(['key', 'cap', 'ec2_iam', 'gcp_sa', 'azure_msi']),
    )
    r""" Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.

Valid choices:

* key
* cap
* ec2_iam
* gcp_sa
* azure_msi """

    azure_account = fields.Str(
        data_key="azure_account",
    )
    r""" Azure account """

    azure_private_key = fields.Str(
        data_key="azure_private_key",
    )
    r""" Azure access key """

    cap_url = fields.Str(
        data_key="cap_url",
    )
    r""" This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.

Example: https://123.45.67.89:1234/CAP/api/v1/credentials?agency=myagency&mission=mymission&role=myrole """

    certificate_validation_enabled = fields.Boolean(
        data_key="certificate_validation_enabled",
    )
    r""" Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types. """

    cluster = fields.Nested("netapp_ontap.models.cloud_target_cluster.CloudTargetClusterSchema", data_key="cluster", unknown=EXCLUDE)
    r""" The cluster field of the cloud_target. """

    container = fields.Str(
        data_key="container",
    )
    r""" Data bucket/container name. For FabricLink, a wildcard character "*" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.

Example: bucket1 """

    ipspace = fields.Nested("netapp_ontap.resources.ipspace.IpspaceSchema", data_key="ipspace", unknown=EXCLUDE)
    r""" The ipspace field of the cloud_target. """

    name = fields.Str(
        data_key="name",
    )
    r""" Cloud target name """

    owner = fields.Str(
        data_key="owner",
        validate=enum_validation(['fabricpool', 'snapmirror', 's3_snapmirror']),
    )
    r""" Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.

Valid choices:

* fabricpool
* snapmirror
* s3_snapmirror """

    port = Size(
        data_key="port",
    )
    r""" Port number of the object store that ONTAP uses when establishing a connection. Required in POST. """

    provider_type = fields.Str(
        data_key="provider_type",
    )
    r""" Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed. """

    secret_password = fields.Str(
        data_key="secret_password",
    )
    r""" Secret access key for AWS_S3 and other S3 compatible provider types. """

    server = fields.Str(
        data_key="server",
    )
    r""" Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a "blob.core.windows.net" or a "blob.core.usgovcloudapi.net", then a value of azure-account followed by a period is added in front of the server. """

    server_side_encryption = fields.Str(
        data_key="server_side_encryption",
        validate=enum_validation(['none', 'sse_s3']),
    )
    r""" Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of "sse_s3" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.

Valid choices:

* none
* sse_s3 """

    snapmirror_use = fields.Str(
        data_key="snapmirror_use",
        validate=enum_validation(['data', 'metadata']),
    )
    r""" Use of the cloud target by SnapMirror.

Valid choices:

* data
* metadata """

    ssl_enabled = fields.Boolean(
        data_key="ssl_enabled",
    )
    r""" SSL/HTTPS enabled or not """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the cloud_target. """

    url_style = fields.Str(
        data_key="url_style",
        validate=enum_validation(['path_style', 'virtual_hosted_style']),
    )
    r""" URL style used to access S3 bucket.

Valid choices:

* path_style
* virtual_hosted_style """

    use_http_proxy = fields.Boolean(
        data_key="use_http_proxy",
    )
    r""" Use HTTP proxy when connecting to the object store. """

    used = Size(
        data_key="used",
    )
    r""" The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" Cloud target UUID """

    @property
    def resource(self):
        return CloudTarget

    gettable_fields = [
        "links",
        "access_key",
        "authentication_type",
        "azure_account",
        "cap_url",
        "certificate_validation_enabled",
        "cluster",
        "container",
        "ipspace.links",
        "ipspace.name",
        "ipspace.uuid",
        "name",
        "owner",
        "port",
        "provider_type",
        "server",
        "server_side_encryption",
        "snapmirror_use",
        "ssl_enabled",
        "svm.links",
        "svm.name",
        "svm.uuid",
        "url_style",
        "use_http_proxy",
        "used",
        "uuid",
    ]
    """links,access_key,authentication_type,azure_account,cap_url,certificate_validation_enabled,cluster,container,ipspace.links,ipspace.name,ipspace.uuid,name,owner,port,provider_type,server,server_side_encryption,snapmirror_use,ssl_enabled,svm.links,svm.name,svm.uuid,url_style,use_http_proxy,used,uuid,"""

    patchable_fields = [
        "access_key",
        "authentication_type",
        "azure_account",
        "azure_private_key",
        "cap_url",
        "certificate_validation_enabled",
        "cluster",
        "name",
        "port",
        "secret_password",
        "server",
        "server_side_encryption",
        "snapmirror_use",
        "ssl_enabled",
        "svm.name",
        "svm.uuid",
        "url_style",
        "use_http_proxy",
    ]
    """access_key,authentication_type,azure_account,azure_private_key,cap_url,certificate_validation_enabled,cluster,name,port,secret_password,server,server_side_encryption,snapmirror_use,ssl_enabled,svm.name,svm.uuid,url_style,use_http_proxy,"""

    postable_fields = [
        "access_key",
        "authentication_type",
        "azure_account",
        "azure_private_key",
        "cap_url",
        "certificate_validation_enabled",
        "cluster",
        "container",
        "ipspace.name",
        "ipspace.uuid",
        "name",
        "owner",
        "port",
        "provider_type",
        "secret_password",
        "server",
        "server_side_encryption",
        "snapmirror_use",
        "ssl_enabled",
        "svm.name",
        "svm.uuid",
        "url_style",
        "use_http_proxy",
    ]
    """access_key,authentication_type,azure_account,azure_private_key,cap_url,certificate_validation_enabled,cluster,container,ipspace.name,ipspace.uuid,name,owner,port,provider_type,secret_password,server,server_side_encryption,snapmirror_use,ssl_enabled,svm.name,svm.uuid,url_style,use_http_proxy,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in CloudTarget.get_collection(fields=field)]
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
            raise NetAppRestError("CloudTarget modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class CloudTarget(Resource):
    """Allows interaction with CloudTarget objects on the host"""

    _schema = CloudTargetSchema
    _path = "/api/cloud/targets"
    _keys = ["uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves the collection of cloud targets in the cluster.
### Related ONTAP commands
* `storage aggregate object-store config show`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud target show")
        def cloud_target_show(
            fields: List[Choices.define(["access_key", "authentication_type", "azure_account", "azure_private_key", "cap_url", "certificate_validation_enabled", "container", "name", "owner", "port", "provider_type", "secret_password", "server", "server_side_encryption", "snapmirror_use", "ssl_enabled", "url_style", "use_http_proxy", "used", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of CloudTarget resources

            Args:
                access_key: Access key ID for AWS_S3 and other S3 compatible provider types.
                authentication_type: Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.
                azure_account: Azure account
                azure_private_key: Azure access key
                cap_url: This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.
                certificate_validation_enabled: Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types.
                container: Data bucket/container name. For FabricLink, a wildcard character \"*\" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.
                name: Cloud target name
                owner: Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.
                port: Port number of the object store that ONTAP uses when establishing a connection. Required in POST.
                provider_type: Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed.
                secret_password: Secret access key for AWS_S3 and other S3 compatible provider types.
                server: Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a \"blob.core.windows.net\" or a \"blob.core.usgovcloudapi.net\", then a value of azure-account followed by a period is added in front of the server.
                server_side_encryption: Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of \"sse_s3\" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.
                snapmirror_use: Use of the cloud target by SnapMirror.
                ssl_enabled: SSL/HTTPS enabled or not
                url_style: URL style used to access S3 bucket.
                use_http_proxy: Use HTTP proxy when connecting to the object store.
                used: The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes.
                uuid: Cloud target UUID
            """

            kwargs = {}
            if access_key is not None:
                kwargs["access_key"] = access_key
            if authentication_type is not None:
                kwargs["authentication_type"] = authentication_type
            if azure_account is not None:
                kwargs["azure_account"] = azure_account
            if azure_private_key is not None:
                kwargs["azure_private_key"] = azure_private_key
            if cap_url is not None:
                kwargs["cap_url"] = cap_url
            if certificate_validation_enabled is not None:
                kwargs["certificate_validation_enabled"] = certificate_validation_enabled
            if container is not None:
                kwargs["container"] = container
            if name is not None:
                kwargs["name"] = name
            if owner is not None:
                kwargs["owner"] = owner
            if port is not None:
                kwargs["port"] = port
            if provider_type is not None:
                kwargs["provider_type"] = provider_type
            if secret_password is not None:
                kwargs["secret_password"] = secret_password
            if server is not None:
                kwargs["server"] = server
            if server_side_encryption is not None:
                kwargs["server_side_encryption"] = server_side_encryption
            if snapmirror_use is not None:
                kwargs["snapmirror_use"] = snapmirror_use
            if ssl_enabled is not None:
                kwargs["ssl_enabled"] = ssl_enabled
            if url_style is not None:
                kwargs["url_style"] = url_style
            if use_http_proxy is not None:
                kwargs["use_http_proxy"] = use_http_proxy
            if used is not None:
                kwargs["used"] = used
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return CloudTarget.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all CloudTarget resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["CloudTarget"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cloud target specified by the UUID with the fields in the body. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store config modify`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["CloudTarget"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["CloudTarget"], NetAppResponse]:
        r"""Creates a cloud target.
### Required properties
* `name` - Name for the cloud target.
* `owner` - Owner of the target: _fabricpool_, _snapmirror_.
* `provider_type` - Type of cloud provider: _AWS_S3_, _Azure_Cloud_, _SGWS_, _IBM_COS_, _AliCloud_, _GoogleCloud_, _ONTAP_S3_.
* `server` - Fully qualified domain name of the object store server. Required when `provider_type` is one of the following: _SGWS_, _IBM_COS_, _AliCloud_.
* `container` - Data bucket/container name.
* `access_key` - Access key ID if `provider_type` is not _Azure_Cloud_ and `authentication_type` is _key_.
* `secret_password` - Secret access key if `provider_type` is not _Azure_Cloud_ and `authentication_type` is _key_.
* `azure_account` - Azure account if `provider_type` is _Azure_Cloud_.
* `azure_private_key` - Azure access key if `provider_type` is _Azure_Cloud_.
* `cap_url` - Full URL of the request to a CAP server for retrieving temporary credentials if `authentication_type` is _cap_.
* `svm.name` or `svm.uuid` - Name or UUID of SVM if `owner` is _snapmirror_.
* `snapmirror_use` - Use of the cloud target if `owner` is _snapmirror_: data, metadata.
### Recommended optional properties
* `authentication_type` - Authentication used to access the target: _key_, _cap_, _ec2_iam_, _gcp_sa_, _azure_msi_.
* `ssl_enabled` - SSL/HTTPS enabled or disabled.
* `port` - Port number of the object store that ONTAP uses when establishing a connection.
* `ipspace` - IPspace to use in order to reach the cloud target.
* `use_http_proxy` - Use the HTTP proxy when connecting to the object store server.
### Default property values
* `authentication_type`
  - _ec2_iam_ - if running in Cloud Volumes ONTAP in AWS
  - _gcp_sa_ - if running in Cloud Volumes ONTAP in GCP
  - _azure_msi_ - if running in Cloud Volumes ONTAP in Azure
  - _key_  - in all other cases.
* `server`
  - _s3.amazonaws.com_ - if `provider_type` is _AWS_S3_
  - _blob.core.windows.net_ - if `provider_type` is _Azure_Cloud_
  - _storage.googleapis.com_ - if `provider_type` is _GoogleCloud_
* `ssl_enabled` - _true_
* `port`
  - _443_ if `ssl_enabled` is _true_
  - _80_ if `ssl_enabled` is _false_ and `provider_type` is not _SGWS_
  - _8084_ if `ssl_enabled` is _false_ and `provider_type` is _SGWS_
* `ipspace` - _Default_
* `certificate_validation_enabled` - _true_
* `ignore_warnings` - _false_
* `check_only` - _false_
* `use_http_proxy` - _false_
* `server_side_encryption`
  - _none_ - if `provider_type` is _ONTAP_S3_
  - _sse_s3_ - if `provider_type` is not _ONTAP_S3_
* `url_style`
  - _path_style_ - if `provider_type` is neither _AWS_S3_ nor _AliCloud_
  - _virtual_hosted_style_ - if `provider_type` is either _AWS_S3 or _AliCloud__
### Related ONTAP commands
* `storage aggregate object-store config create`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._post_collection(
            records, *args, hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    post_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post_collection.__doc__)

    @classmethod
    def delete_collection(
        cls,
        *args,
        records: Iterable["CloudTarget"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the cloud target specified by the UUID. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store config delete`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves the collection of cloud targets in the cluster.
### Related ONTAP commands
* `storage aggregate object-store config show`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves the cloud target specified by the UUID.
### Related ONTAP commands
* `storage aggregate object-store config show`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
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
        r"""Creates a cloud target.
### Required properties
* `name` - Name for the cloud target.
* `owner` - Owner of the target: _fabricpool_, _snapmirror_.
* `provider_type` - Type of cloud provider: _AWS_S3_, _Azure_Cloud_, _SGWS_, _IBM_COS_, _AliCloud_, _GoogleCloud_, _ONTAP_S3_.
* `server` - Fully qualified domain name of the object store server. Required when `provider_type` is one of the following: _SGWS_, _IBM_COS_, _AliCloud_.
* `container` - Data bucket/container name.
* `access_key` - Access key ID if `provider_type` is not _Azure_Cloud_ and `authentication_type` is _key_.
* `secret_password` - Secret access key if `provider_type` is not _Azure_Cloud_ and `authentication_type` is _key_.
* `azure_account` - Azure account if `provider_type` is _Azure_Cloud_.
* `azure_private_key` - Azure access key if `provider_type` is _Azure_Cloud_.
* `cap_url` - Full URL of the request to a CAP server for retrieving temporary credentials if `authentication_type` is _cap_.
* `svm.name` or `svm.uuid` - Name or UUID of SVM if `owner` is _snapmirror_.
* `snapmirror_use` - Use of the cloud target if `owner` is _snapmirror_: data, metadata.
### Recommended optional properties
* `authentication_type` - Authentication used to access the target: _key_, _cap_, _ec2_iam_, _gcp_sa_, _azure_msi_.
* `ssl_enabled` - SSL/HTTPS enabled or disabled.
* `port` - Port number of the object store that ONTAP uses when establishing a connection.
* `ipspace` - IPspace to use in order to reach the cloud target.
* `use_http_proxy` - Use the HTTP proxy when connecting to the object store server.
### Default property values
* `authentication_type`
  - _ec2_iam_ - if running in Cloud Volumes ONTAP in AWS
  - _gcp_sa_ - if running in Cloud Volumes ONTAP in GCP
  - _azure_msi_ - if running in Cloud Volumes ONTAP in Azure
  - _key_  - in all other cases.
* `server`
  - _s3.amazonaws.com_ - if `provider_type` is _AWS_S3_
  - _blob.core.windows.net_ - if `provider_type` is _Azure_Cloud_
  - _storage.googleapis.com_ - if `provider_type` is _GoogleCloud_
* `ssl_enabled` - _true_
* `port`
  - _443_ if `ssl_enabled` is _true_
  - _80_ if `ssl_enabled` is _false_ and `provider_type` is not _SGWS_
  - _8084_ if `ssl_enabled` is _false_ and `provider_type` is _SGWS_
* `ipspace` - _Default_
* `certificate_validation_enabled` - _true_
* `ignore_warnings` - _false_
* `check_only` - _false_
* `use_http_proxy` - _false_
* `server_side_encryption`
  - _none_ - if `provider_type` is _ONTAP_S3_
  - _sse_s3_ - if `provider_type` is not _ONTAP_S3_
* `url_style`
  - _path_style_ - if `provider_type` is neither _AWS_S3_ nor _AliCloud_
  - _virtual_hosted_style_ - if `provider_type` is either _AWS_S3 or _AliCloud__
### Related ONTAP commands
* `storage aggregate object-store config create`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud target create")
        async def cloud_target_create(
        ) -> ResourceTable:
            """Create an instance of a CloudTarget resource

            Args:
                links: 
                access_key: Access key ID for AWS_S3 and other S3 compatible provider types.
                authentication_type: Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.
                azure_account: Azure account
                azure_private_key: Azure access key
                cap_url: This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.
                certificate_validation_enabled: Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types.
                cluster: 
                container: Data bucket/container name. For FabricLink, a wildcard character \"*\" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.
                ipspace: 
                name: Cloud target name
                owner: Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.
                port: Port number of the object store that ONTAP uses when establishing a connection. Required in POST.
                provider_type: Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed.
                secret_password: Secret access key for AWS_S3 and other S3 compatible provider types.
                server: Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a \"blob.core.windows.net\" or a \"blob.core.usgovcloudapi.net\", then a value of azure-account followed by a period is added in front of the server.
                server_side_encryption: Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of \"sse_s3\" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.
                snapmirror_use: Use of the cloud target by SnapMirror.
                ssl_enabled: SSL/HTTPS enabled or not
                svm: 
                url_style: URL style used to access S3 bucket.
                use_http_proxy: Use HTTP proxy when connecting to the object store.
                used: The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes.
                uuid: Cloud target UUID
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if access_key is not None:
                kwargs["access_key"] = access_key
            if authentication_type is not None:
                kwargs["authentication_type"] = authentication_type
            if azure_account is not None:
                kwargs["azure_account"] = azure_account
            if azure_private_key is not None:
                kwargs["azure_private_key"] = azure_private_key
            if cap_url is not None:
                kwargs["cap_url"] = cap_url
            if certificate_validation_enabled is not None:
                kwargs["certificate_validation_enabled"] = certificate_validation_enabled
            if cluster is not None:
                kwargs["cluster"] = cluster
            if container is not None:
                kwargs["container"] = container
            if ipspace is not None:
                kwargs["ipspace"] = ipspace
            if name is not None:
                kwargs["name"] = name
            if owner is not None:
                kwargs["owner"] = owner
            if port is not None:
                kwargs["port"] = port
            if provider_type is not None:
                kwargs["provider_type"] = provider_type
            if secret_password is not None:
                kwargs["secret_password"] = secret_password
            if server is not None:
                kwargs["server"] = server
            if server_side_encryption is not None:
                kwargs["server_side_encryption"] = server_side_encryption
            if snapmirror_use is not None:
                kwargs["snapmirror_use"] = snapmirror_use
            if ssl_enabled is not None:
                kwargs["ssl_enabled"] = ssl_enabled
            if svm is not None:
                kwargs["svm"] = svm
            if url_style is not None:
                kwargs["url_style"] = url_style
            if use_http_proxy is not None:
                kwargs["use_http_proxy"] = use_http_proxy
            if used is not None:
                kwargs["used"] = used
            if uuid is not None:
                kwargs["uuid"] = uuid

            resource = CloudTarget(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create CloudTarget: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates the cloud target specified by the UUID with the fields in the body. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store config modify`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud target modify")
        async def cloud_target_modify(
        ) -> ResourceTable:
            """Modify an instance of a CloudTarget resource

            Args:
                access_key: Access key ID for AWS_S3 and other S3 compatible provider types.
                query_access_key: Access key ID for AWS_S3 and other S3 compatible provider types.
                authentication_type: Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.
                query_authentication_type: Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.
                azure_account: Azure account
                query_azure_account: Azure account
                azure_private_key: Azure access key
                query_azure_private_key: Azure access key
                cap_url: This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.
                query_cap_url: This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.
                certificate_validation_enabled: Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types.
                query_certificate_validation_enabled: Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types.
                container: Data bucket/container name. For FabricLink, a wildcard character \"*\" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.
                query_container: Data bucket/container name. For FabricLink, a wildcard character \"*\" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.
                name: Cloud target name
                query_name: Cloud target name
                owner: Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.
                query_owner: Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.
                port: Port number of the object store that ONTAP uses when establishing a connection. Required in POST.
                query_port: Port number of the object store that ONTAP uses when establishing a connection. Required in POST.
                provider_type: Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed.
                query_provider_type: Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed.
                secret_password: Secret access key for AWS_S3 and other S3 compatible provider types.
                query_secret_password: Secret access key for AWS_S3 and other S3 compatible provider types.
                server: Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a \"blob.core.windows.net\" or a \"blob.core.usgovcloudapi.net\", then a value of azure-account followed by a period is added in front of the server.
                query_server: Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a \"blob.core.windows.net\" or a \"blob.core.usgovcloudapi.net\", then a value of azure-account followed by a period is added in front of the server.
                server_side_encryption: Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of \"sse_s3\" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.
                query_server_side_encryption: Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of \"sse_s3\" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.
                snapmirror_use: Use of the cloud target by SnapMirror.
                query_snapmirror_use: Use of the cloud target by SnapMirror.
                ssl_enabled: SSL/HTTPS enabled or not
                query_ssl_enabled: SSL/HTTPS enabled or not
                url_style: URL style used to access S3 bucket.
                query_url_style: URL style used to access S3 bucket.
                use_http_proxy: Use HTTP proxy when connecting to the object store.
                query_use_http_proxy: Use HTTP proxy when connecting to the object store.
                used: The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes.
                query_used: The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes.
                uuid: Cloud target UUID
                query_uuid: Cloud target UUID
            """

            kwargs = {}
            changes = {}
            if query_access_key is not None:
                kwargs["access_key"] = query_access_key
            if query_authentication_type is not None:
                kwargs["authentication_type"] = query_authentication_type
            if query_azure_account is not None:
                kwargs["azure_account"] = query_azure_account
            if query_azure_private_key is not None:
                kwargs["azure_private_key"] = query_azure_private_key
            if query_cap_url is not None:
                kwargs["cap_url"] = query_cap_url
            if query_certificate_validation_enabled is not None:
                kwargs["certificate_validation_enabled"] = query_certificate_validation_enabled
            if query_container is not None:
                kwargs["container"] = query_container
            if query_name is not None:
                kwargs["name"] = query_name
            if query_owner is not None:
                kwargs["owner"] = query_owner
            if query_port is not None:
                kwargs["port"] = query_port
            if query_provider_type is not None:
                kwargs["provider_type"] = query_provider_type
            if query_secret_password is not None:
                kwargs["secret_password"] = query_secret_password
            if query_server is not None:
                kwargs["server"] = query_server
            if query_server_side_encryption is not None:
                kwargs["server_side_encryption"] = query_server_side_encryption
            if query_snapmirror_use is not None:
                kwargs["snapmirror_use"] = query_snapmirror_use
            if query_ssl_enabled is not None:
                kwargs["ssl_enabled"] = query_ssl_enabled
            if query_url_style is not None:
                kwargs["url_style"] = query_url_style
            if query_use_http_proxy is not None:
                kwargs["use_http_proxy"] = query_use_http_proxy
            if query_used is not None:
                kwargs["used"] = query_used
            if query_uuid is not None:
                kwargs["uuid"] = query_uuid

            if access_key is not None:
                changes["access_key"] = access_key
            if authentication_type is not None:
                changes["authentication_type"] = authentication_type
            if azure_account is not None:
                changes["azure_account"] = azure_account
            if azure_private_key is not None:
                changes["azure_private_key"] = azure_private_key
            if cap_url is not None:
                changes["cap_url"] = cap_url
            if certificate_validation_enabled is not None:
                changes["certificate_validation_enabled"] = certificate_validation_enabled
            if container is not None:
                changes["container"] = container
            if name is not None:
                changes["name"] = name
            if owner is not None:
                changes["owner"] = owner
            if port is not None:
                changes["port"] = port
            if provider_type is not None:
                changes["provider_type"] = provider_type
            if secret_password is not None:
                changes["secret_password"] = secret_password
            if server is not None:
                changes["server"] = server
            if server_side_encryption is not None:
                changes["server_side_encryption"] = server_side_encryption
            if snapmirror_use is not None:
                changes["snapmirror_use"] = snapmirror_use
            if ssl_enabled is not None:
                changes["ssl_enabled"] = ssl_enabled
            if url_style is not None:
                changes["url_style"] = url_style
            if use_http_proxy is not None:
                changes["use_http_proxy"] = use_http_proxy
            if used is not None:
                changes["used"] = used
            if uuid is not None:
                changes["uuid"] = uuid

            if hasattr(CloudTarget, "find"):
                resource = CloudTarget.find(
                    **kwargs
                )
            else:
                resource = CloudTarget()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify CloudTarget: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Deletes the cloud target specified by the UUID. This request starts a job and returns a link to that job.
### Related ONTAP commands
* `storage aggregate object-store config delete`

### Learn more
* [`DOC /cloud/targets`](#docs-cloud-cloud_targets)"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="cloud target delete")
        async def cloud_target_delete(
        ) -> None:
            """Delete an instance of a CloudTarget resource

            Args:
                access_key: Access key ID for AWS_S3 and other S3 compatible provider types.
                authentication_type: Authentication used to access the target. SnapMirror does not yet support CAP. Required in POST.
                azure_account: Azure account
                azure_private_key: Azure access key
                cap_url: This parameter is available only when auth-type is CAP. It specifies a full URL of the request to a CAP server for retrieving temporary credentials (access-key, secret-pasword, and session token) for accessing the object store.
                certificate_validation_enabled: Is SSL/TLS certificate validation enabled? The default value is true. This can only be modified for SGWS, IBM_COS, and ONTAP_S3 provider types.
                container: Data bucket/container name. For FabricLink, a wildcard character \"*\" can also be specified to indicate that all the buckets in an SVM can use the same target information. However, for containers other than ONTAP, an exact name should be specified.
                name: Cloud target name
                owner: Owner of the target. Allowed values are FabricPool, SnapMirror or S3_SnapMirror. A target can be used by only one feature.
                port: Port number of the object store that ONTAP uses when establishing a connection. Required in POST.
                provider_type: Type of cloud provider. Allowed values depend on owner type. For FabricPool, AliCloud, AWS_S3, Azure_Cloud, GoggleCloud, IBM_COS, SGWS, and ONTAP_S3 are allowed. For SnapMirror, the valid values are AWS_S3 or SGWS. For FabricLink, AWS_S3, SGWS, S3_Compatible, S3EMU, LOOPBACK and ONTAP_S3 are allowed.
                secret_password: Secret access key for AWS_S3 and other S3 compatible provider types.
                server: Fully qualified domain name of the object store server. Required on POST.  For Amazon S3, server name must be an AWS regional endpoint in the format s3.amazonaws.com or s3-<region>.amazonaws.com, for example, s3-us-west-2.amazonaws.com. The region of the server and the bucket must match. For Azure, if the server is a \"blob.core.windows.net\" or a \"blob.core.usgovcloudapi.net\", then a value of azure-account followed by a period is added in front of the server.
                server_side_encryption: Encryption of data at rest by the object store server for AWS_S3 and other S3 compatible provider types. This is an advanced property. In most cases it is best not to change default value of \"sse_s3\" for object store servers which support SSE-S3 encryption. The encryption is in addition to any encryption done by ONTAP at a volume or at an aggregate level. Note that changing this option does not change encryption of data which already exist in the object store.
                snapmirror_use: Use of the cloud target by SnapMirror.
                ssl_enabled: SSL/HTTPS enabled or not
                url_style: URL style used to access S3 bucket.
                use_http_proxy: Use HTTP proxy when connecting to the object store.
                used: The amount of cloud space used by all the aggregates attached to the target, in bytes. This field is only populated for FabricPool targets. The value is recalculated once every 5 minutes.
                uuid: Cloud target UUID
            """

            kwargs = {}
            if access_key is not None:
                kwargs["access_key"] = access_key
            if authentication_type is not None:
                kwargs["authentication_type"] = authentication_type
            if azure_account is not None:
                kwargs["azure_account"] = azure_account
            if azure_private_key is not None:
                kwargs["azure_private_key"] = azure_private_key
            if cap_url is not None:
                kwargs["cap_url"] = cap_url
            if certificate_validation_enabled is not None:
                kwargs["certificate_validation_enabled"] = certificate_validation_enabled
            if container is not None:
                kwargs["container"] = container
            if name is not None:
                kwargs["name"] = name
            if owner is not None:
                kwargs["owner"] = owner
            if port is not None:
                kwargs["port"] = port
            if provider_type is not None:
                kwargs["provider_type"] = provider_type
            if secret_password is not None:
                kwargs["secret_password"] = secret_password
            if server is not None:
                kwargs["server"] = server
            if server_side_encryption is not None:
                kwargs["server_side_encryption"] = server_side_encryption
            if snapmirror_use is not None:
                kwargs["snapmirror_use"] = snapmirror_use
            if ssl_enabled is not None:
                kwargs["ssl_enabled"] = ssl_enabled
            if url_style is not None:
                kwargs["url_style"] = url_style
            if use_http_proxy is not None:
                kwargs["use_http_proxy"] = use_http_proxy
            if used is not None:
                kwargs["used"] = used
            if uuid is not None:
                kwargs["uuid"] = uuid

            if hasattr(CloudTarget, "find"):
                resource = CloudTarget.find(
                    **kwargs
                )
            else:
                resource = CloudTarget()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete CloudTarget: %s" % err)


