r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


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


__all__ = ["ApplicationComponent", "ApplicationComponentSchema"]
__pdoc__ = {
    "ApplicationComponentSchema.resource": False,
    "ApplicationComponent.application_component_show": False,
    "ApplicationComponent.application_component_create": False,
    "ApplicationComponent.application_component_modify": False,
    "ApplicationComponent.application_component_delete": False,
}


class ApplicationComponentSchema(ResourceSchema):
    """The fields of the ApplicationComponent object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the application_component. """

    application = fields.Nested("netapp_ontap.models.application_component_application.ApplicationComponentApplicationSchema", data_key="application", unknown=EXCLUDE)
    r""" The application field of the application_component. """

    backing_storage = fields.Nested("netapp_ontap.models.application_backing_storage.ApplicationBackingStorageSchema", data_key="backing_storage", unknown=EXCLUDE)
    r""" The backing_storage field of the application_component. """

    cifs_access = fields.List(fields.Nested("netapp_ontap.models.application_cifs_properties.ApplicationCifsPropertiesSchema", unknown=EXCLUDE), data_key="cifs_access")
    r""" The cifs_access field of the application_component. """

    file_system = fields.Str(
        data_key="file_system",
        validate=enum_validation(['m1fs', 'xfs', 'generic']),
    )
    r""" Defines the type of file system that will be installed on this application component.

Valid choices:

* m1fs
* xfs
* generic """

    host_management_url = fields.Str(
        data_key="host_management_url",
    )
    r""" Host management URL """

    host_name = fields.Str(
        data_key="host_name",
    )
    r""" L2 Host FQDN """

    name = fields.Str(
        data_key="name",
    )
    r""" Application component name """

    nfs_access = fields.List(fields.Nested("netapp_ontap.models.application_nfs_properties.ApplicationNfsPropertiesSchema", unknown=EXCLUDE), data_key="nfs_access")
    r""" The nfs_access field of the application_component. """

    nvme_access = fields.List(fields.Nested("netapp_ontap.models.application_nvme_access.ApplicationNvmeAccessSchema", unknown=EXCLUDE), data_key="nvme_access")
    r""" The nvme_access field of the application_component. """

    protection_groups = fields.List(fields.Nested("netapp_ontap.models.application_protection_groups.ApplicationProtectionGroupsSchema", unknown=EXCLUDE), data_key="protection_groups")
    r""" The protection_groups field of the application_component. """

    san_access = fields.List(fields.Nested("netapp_ontap.models.application_san_access.ApplicationSanAccessSchema", unknown=EXCLUDE), data_key="san_access")
    r""" The san_access field of the application_component. """

    storage_service = fields.Nested("netapp_ontap.models.application_component_storage_service.ApplicationComponentStorageServiceSchema", data_key="storage_service", unknown=EXCLUDE)
    r""" The storage_service field of the application_component. """

    svm = fields.Nested("netapp_ontap.models.application_component_svm.ApplicationComponentSvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the application_component. """

    uuid = fields.Str(
        data_key="uuid",
    )
    r""" The application component UUID. Valid in URL. """

    @property
    def resource(self):
        return ApplicationComponent

    gettable_fields = [
        "links",
        "application",
        "backing_storage",
        "cifs_access",
        "file_system",
        "host_management_url",
        "host_name",
        "name",
        "nfs_access",
        "nvme_access",
        "protection_groups",
        "san_access",
        "storage_service",
        "svm",
        "uuid",
    ]
    """links,application,backing_storage,cifs_access,file_system,host_management_url,host_name,name,nfs_access,nvme_access,protection_groups,san_access,storage_service,svm,uuid,"""

    patchable_fields = [
        "application",
        "backing_storage",
        "cifs_access",
        "nfs_access",
        "nvme_access",
        "protection_groups",
        "san_access",
        "storage_service",
        "svm",
    ]
    """application,backing_storage,cifs_access,nfs_access,nvme_access,protection_groups,san_access,storage_service,svm,"""

    postable_fields = [
        "application",
        "backing_storage",
        "cifs_access",
        "nfs_access",
        "nvme_access",
        "protection_groups",
        "san_access",
        "storage_service",
        "svm",
    ]
    """application,backing_storage,cifs_access,nfs_access,nvme_access,protection_groups,san_access,storage_service,svm,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in ApplicationComponent.get_collection(fields=field)]
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
            raise NetAppRestError("ApplicationComponent modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class ApplicationComponent(Resource):
    r""" Application component """

    _schema = ApplicationComponentSchema
    _path = "/api/application/applications/{application[uuid]}/components"
    _keys = ["application.uuid", "uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves application components.
### Overview
The application component object exposes how to access an application. Most application interfaces abstract away the underlying ONTAP storage elements, but this interface exposes what is necessary to connect to and uses the storage that is provisioned for an application. See the application component model for a detailed description of each property.
### Query examples
Queries are limited on this API. Most of the details are nested under the `nfs_access`, `cifs_access`, or `san_access` properties, but those properties do not support queries, and properties nested under those properties cannot be requested individually in the current release.<br/>
The following query returns all application components with names beginning in _secondary_.<br/><br/>
```
GET /application/applications/{application.uuid}/components?name=secondary*
```
<br/>The following query returns all application components at the _extreme_ storage service.<br/><br/>
```
GET /application/applications/{application.uuid}/components?storage_service.name=extreme
```
### Learn more
* [`DOC /application`](#docs-application-overview)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="application component show")
        def application_component_show(
            application_uuid,
            file_system: Choices.define(_get_field_list("file_system"), cache_choices=True, inexact=True)=None,
            host_management_url: Choices.define(_get_field_list("host_management_url"), cache_choices=True, inexact=True)=None,
            host_name: Choices.define(_get_field_list("host_name"), cache_choices=True, inexact=True)=None,
            name: Choices.define(_get_field_list("name"), cache_choices=True, inexact=True)=None,
            uuid: Choices.define(_get_field_list("uuid"), cache_choices=True, inexact=True)=None,
            fields: List[Choices.define(["file_system", "host_management_url", "host_name", "name", "uuid", "*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of ApplicationComponent resources

            Args:
                file_system: Defines the type of file system that will be installed on this application component.
                host_management_url: Host management URL
                host_name: L2 Host FQDN
                name: Application component name
                uuid: The application component UUID. Valid in URL.
            """

            kwargs = {}
            if file_system is not None:
                kwargs["file_system"] = file_system
            if host_management_url is not None:
                kwargs["host_management_url"] = host_management_url
            if host_name is not None:
                kwargs["host_name"] = host_name
            if name is not None:
                kwargs["name"] = name
            if uuid is not None:
                kwargs["uuid"] = uuid
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return ApplicationComponent.get_collection(
                application_uuid,
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all ApplicationComponent resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)




    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves application components.
### Overview
The application component object exposes how to access an application. Most application interfaces abstract away the underlying ONTAP storage elements, but this interface exposes what is necessary to connect to and uses the storage that is provisioned for an application. See the application component model for a detailed description of each property.
### Query examples
Queries are limited on this API. Most of the details are nested under the `nfs_access`, `cifs_access`, or `san_access` properties, but those properties do not support queries, and properties nested under those properties cannot be requested individually in the current release.<br/>
The following query returns all application components with names beginning in _secondary_.<br/><br/>
```
GET /application/applications/{application.uuid}/components?name=secondary*
```
<br/>The following query returns all application components at the _extreme_ storage service.<br/><br/>
```
GET /application/applications/{application.uuid}/components?storage_service.name=extreme
```
### Learn more
* [`DOC /application`](#docs-application-overview)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves an application component.
### Overview
The application component object exposes how to access an application. Most application interfaces abstract away the underlying ONTAP storage elements, but this interface exposes what is necessary to connect to and uses the storage that is provisioned for an application. See the application component model for a detailed description of each property.
### Access
Each application component can be accessed via NFS, CIFS, or SAN. NFS and CIFS access can be enabled simultaneously. Each access section includes a `backing_storage` property. This property is used to correlate the storage elements with the access elements of the application. The `backing_storage` portion of the access section provides the `type` and `uuid` of the backing storage. There is another `backing_storage` property at the same level as the access properties which contains lists of backing storage elements corresponding to the types listed in the access section.
### Learn more
* [`DOC /application`](#docs-application-overview)
"""
        return super()._get(**kwargs)

    get.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get.__doc__)





