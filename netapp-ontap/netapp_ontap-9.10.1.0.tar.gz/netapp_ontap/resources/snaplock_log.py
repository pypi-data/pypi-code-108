r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.

The SnapLock log volume can be a SnapLock Compliance volume or SnapLock Enterprise volume. The SnapLock log infrastructure creates directories and files in this volume to store the SnapLock log records. The maximum log size specifies the maximum size of a log file that stores SnapLock log records. When the file reaches this size, the log infrastructure archives it and creates a new log file. The default retention period is the length of time the log file is retained, if the SnapLock log records that are stored in the file do not carry any retention period.
### Examples
1. Verifies that the audit log is configured for the specified SVM:
   <br/>
   ```
   GET "/api/storage/snaplock/audit-logs/?svm.name=VS0"
   ```
   <br/>
2. Verifies that the specified volume is an audit log volume:
   <br/>
   ```
   GET "/api/storage/snaplock/audit-logs/?log_volume.volume.name=VS0_ALOG"
   ```
   <br/>
### Examples
1. Creates a SnapLock log configuration by providing SVM name:
   <br/>
   ```
   POST "/api/storage/snaplock/audit-logs" '{"svm": {"name":"VS3"}, "log_volume": { "volume": { "name":"VS3_ALOG"}, "max_log_size":"20971520", "retention_period":"P30Y" }}'
   ```
   <br/>
2. Creates a SnapLock log configuration by providing SVM UUID:
   <br/>
   ```
   POST "/api/storage/snaplock/audit-logs" '{"svm": {"uuid":"bc744cc7-296d-11e9-a26f-0050568e5b05"}, "log_volume": { "volume": { "name":"VS3_ALOG"}, "max_log_size":"20971520", "retention_period":"P30Y" }}'
   ```
   <br/>
3. Creates a SnapLock log configuration without specifying a retention period:
   <br/>
   ```
   POST "/api/storage/snaplock/audit-logs" '{"svm": {"name":"VS3"}, "log_volume": {"volume": {"name":"VS3_ALOG"}}}'
   ```
   <br/>
### Examples
1. Updates the audit log volume:
   <br/>
   ```
   PATCH "/api/storage/snaplock/audit-logs/bc744cc7-296d-11e9-a26f-0050568e5b05" '{"log_volume":{"volume":{"name":"VS4_ALOG_NEW"}}}'
   ```
   <br/>
2. Updates the maximum size of the log file and the retention period:
   <br/>
   ```
   PATCH "/api/storage/snaplock/audit-logs/420cac7a-296a-11e9-a26f-0050568e5b05" '{"log_volume":{"max_log_size":"20971520", "retention_period":"P1Y"}}'
   ```
   <br/>
3. Archives all of the audit log files:
   <br/>
   ```
   PATCH "/api/storage/snaplock/audit-logs/c7e4fa7d-2968-11e9-a26f-0050568e5b05" '{"log_archive":{"archive":"true"}}'
   ```
   <br/>
4. Archives the specified audit log file:
   <br/>
   ```
   PATCH "/api/storage/snaplock/audit-logs/c7e4fa7d-2968-11e9-a26f-0050568e5b05" '{"log_archive":{"archive":"true","base_name":"privileged_delete"}}'
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


__all__ = ["SnaplockLog", "SnaplockLogSchema"]
__pdoc__ = {
    "SnaplockLogSchema.resource": False,
    "SnaplockLog.snaplock_log_show": False,
    "SnaplockLog.snaplock_log_create": False,
    "SnaplockLog.snaplock_log_modify": False,
    "SnaplockLog.snaplock_log_delete": False,
}


class SnaplockLogSchema(ResourceSchema):
    """The fields of the SnaplockLog object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", data_key="_links", unknown=EXCLUDE)
    r""" The links field of the snaplock_log. """

    log_archive = fields.Nested("netapp_ontap.models.snaplock_log_file.SnaplockLogFileSchema", data_key="log_archive", unknown=EXCLUDE)
    r""" The log_archive field of the snaplock_log. """

    log_files = fields.List(fields.Nested("netapp_ontap.models.snaplock_log_file.SnaplockLogFileSchema", unknown=EXCLUDE), data_key="log_files")
    r""" The log_files field of the snaplock_log. """

    log_volume = fields.Nested("netapp_ontap.models.snaplock_log_volume.SnaplockLogVolumeSchema", data_key="log_volume", unknown=EXCLUDE)
    r""" The log_volume field of the snaplock_log. """

    svm = fields.Nested("netapp_ontap.resources.svm.SvmSchema", data_key="svm", unknown=EXCLUDE)
    r""" The svm field of the snaplock_log. """

    @property
    def resource(self):
        return SnaplockLog

    gettable_fields = [
        "links",
        "log_archive",
        "log_files",
        "log_volume",
        "svm.links",
        "svm.name",
        "svm.uuid",
    ]
    """links,log_archive,log_files,log_volume,svm.links,svm.name,svm.uuid,"""

    patchable_fields = [
        "log_archive",
        "log_volume",
    ]
    """log_archive,log_volume,"""

    postable_fields = [
        "log_archive",
        "log_files",
        "log_volume",
        "svm.name",
        "svm.uuid",
    ]
    """log_archive,log_files,log_volume,svm.name,svm.uuid,"""

def _get_field_list(field: str) -> Callable[[], List]:
    def getter():
        return [getattr(r, field) for r in SnaplockLog.get_collection(fields=field)]
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
            raise NetAppRestError("SnaplockLog modify job failed")
        if job.state == "success":
            break
        await asyncio.sleep(1)

class SnaplockLog(Resource):
    """Allows interaction with SnaplockLog objects on the host"""

    _schema = SnaplockLogSchema
    _path = "/api/storage/snaplock/audit-logs"
    _keys = ["svm.uuid"]

    @classmethod
    def get_collection(
        cls,
        *args,
        connection: HostConnection = None,
        max_records: int = None,
        **kwargs
    ) -> Iterable["Resource"]:
        r"""Retrieves a list of SVMs configured with audit log volumes.
### Related ONTAP commands
* `snaplock log show`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._get_collection(*args, connection=connection, max_records=max_records, **kwargs)

    get_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._get_collection.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock log show")
        def snaplock_log_show(
            fields: List[Choices.define(["*"])]=None,
        ) -> ResourceTable:
            """Fetch a list of SnaplockLog resources

            Args:
            """

            kwargs = {}
            if fields is not None:
                fields = ",".join(fields)
                kwargs["fields"] = fields

            return SnaplockLog.get_collection(
                **kwargs
            )

    @classmethod
    def count_collection(
        cls,
        *args,
        connection: HostConnection = None,
        **kwargs
    ) -> int:
        """Returns a count of all SnaplockLog resources that match the provided query"""
        return super()._count_collection(*args, connection=connection, **kwargs)

    count_collection.__func__.__doc__ = "\n\n---\n" + inspect.cleandoc(Resource._count_collection.__doc__)

    @classmethod
    def patch_collection(
        cls,
        body: dict,
        *args,
        records: Iterable["SnaplockLog"] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates one of the following:
  - the audit log volume,
  - the attributes of the audit log volume present, or
  - archive the current audit log files
### Related ONTAP commands
* `snaplock log modify`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._patch_collection(
            body, *args, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    patch_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch_collection.__doc__)

    @classmethod
    def post_collection(
        cls,
        records: Iterable["SnaplockLog"],
        *args,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> Union[List["SnaplockLog"], NetAppResponse]:
        r"""Creates a SnapLock log configuration for an SVM. A SnapLock log configuration consists of a volume to store the log, the maximum size of the log file, and the default period of time for which the log file should be retained. The input parameter retention_period expects the duration in ISO 8601 format.
### Required properties
* `svm.uuid` or `svm.name` - Name or UUID of the SVM.
* `log_volume.volume.name` or `log_volume.volume.uuid` - Name or UUID of audit log volume.
### Recommended optional properties
* `log_volume.max_log_size` - Max log file size.
* `log_volume.volume.retention_period` - Retention period of log file.
### Default property values
If not specified in POST, the following default property values are assigned:
* `log_volume.retention_period` - _P6M_
* `log_volume.max_log_size` - _10MB_
### Related ONTAP commands
* `snaplock log create`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
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
        records: Iterable["SnaplockLog"] = None,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        connection: HostConnection = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Disassociates a SnapLock volume as the audit log volume for an SVM. This API closes all the active log files in the log volume and marks the volume as disabled for SnapLock logging.
### Related ONTAP commands
* `snaplock log delete`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._delete_collection(
            *args, body=body, records=records, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, connection=connection, **kwargs
        )

    delete_collection.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete_collection.__doc__)

    @classmethod
    def find(cls, *args, connection: HostConnection = None, **kwargs) -> Resource:
        r"""Retrieves a list of SVMs configured with audit log volumes.
### Related ONTAP commands
* `snaplock log show`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._find(*args, connection=connection, **kwargs)

    find.__func__.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._find.__doc__)

    def get(self, **kwargs) -> NetAppResponse:
        r"""Retrieves SnapLock logs for the specified SVM.
### Related ONTAP commands
* `snaplock log show`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
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
        r"""Creates a SnapLock log configuration for an SVM. A SnapLock log configuration consists of a volume to store the log, the maximum size of the log file, and the default period of time for which the log file should be retained. The input parameter retention_period expects the duration in ISO 8601 format.
### Required properties
* `svm.uuid` or `svm.name` - Name or UUID of the SVM.
* `log_volume.volume.name` or `log_volume.volume.uuid` - Name or UUID of audit log volume.
### Recommended optional properties
* `log_volume.max_log_size` - Max log file size.
* `log_volume.volume.retention_period` - Retention period of log file.
### Default property values
If not specified in POST, the following default property values are assigned:
* `log_volume.retention_period` - _P6M_
* `log_volume.max_log_size` - _10MB_
### Related ONTAP commands
* `snaplock log create`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._post(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    post.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._post.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock log create")
        async def snaplock_log_create(
        ) -> ResourceTable:
            """Create an instance of a SnaplockLog resource

            Args:
                links: 
                log_archive: 
                log_files: 
                log_volume: 
                svm: 
            """

            kwargs = {}
            if links is not None:
                kwargs["links"] = links
            if log_archive is not None:
                kwargs["log_archive"] = log_archive
            if log_files is not None:
                kwargs["log_files"] = log_files
            if log_volume is not None:
                kwargs["log_volume"] = log_volume
            if svm is not None:
                kwargs["svm"] = svm

            resource = SnaplockLog(
                **kwargs
            )
            try:
                response = resource.post(hydrate=True, poll=False)
                await _wait_for_job(response)
                resource.get()
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to create SnaplockLog: %s" % err)
            return [resource]

    def patch(
        self,
        hydrate: bool = False,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Updates one of the following:
  - the audit log volume,
  - the attributes of the audit log volume present, or
  - archive the current audit log files
### Related ONTAP commands
* `snaplock log modify`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._patch(
            hydrate=hydrate, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    patch.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._patch.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock log modify")
        async def snaplock_log_modify(
        ) -> ResourceTable:
            """Modify an instance of a SnaplockLog resource

            Args:
            """

            kwargs = {}
            changes = {}


            if hasattr(SnaplockLog, "find"):
                resource = SnaplockLog.find(
                    **kwargs
                )
            else:
                resource = SnaplockLog()
            try:
                for key, value in changes.items():
                    setattr(resource, key, value)
                response = resource.patch(poll=False)
                await _wait_for_job(response)
                resource.get(fields=",".join(changes.keys()))
                return [resource]
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to modify SnaplockLog: %s" % err)

    def delete(
        self,
        body: Union[Resource, dict] = None,
        poll: bool = True,
        poll_interval: Optional[int] = None,
        poll_timeout: Optional[int] = None,
        **kwargs
    ) -> NetAppResponse:
        r"""Disassociates a SnapLock volume as the audit log volume for an SVM. This API closes all the active log files in the log volume and marks the volume as disabled for SnapLock logging.
### Related ONTAP commands
* `snaplock log delete`
### Learn more
* [`DOC /storage/snaplock/audit-logs`](#docs-snaplock-storage_snaplock_audit-logs)
"""
        return super()._delete(
            body=body, poll=poll, poll_interval=poll_interval,
            poll_timeout=poll_timeout, **kwargs
        )

    delete.__doc__ += "\n\n---\n" + inspect.cleandoc(Resource._delete.__doc__)

    if RECLINE_INSTALLED:
        @recline.command(name="snaplock log delete")
        async def snaplock_log_delete(
        ) -> None:
            """Delete an instance of a SnaplockLog resource

            Args:
            """

            kwargs = {}

            if hasattr(SnaplockLog, "find"):
                resource = SnaplockLog.find(
                    **kwargs
                )
            else:
                resource = SnaplockLog()
            try:
                response = resource.delete(poll=False)
                await _wait_for_job(response)
            except NetAppRestError as err:
                raise ClicheCommandError("Unable to delete SnaplockLog: %s" % err)


