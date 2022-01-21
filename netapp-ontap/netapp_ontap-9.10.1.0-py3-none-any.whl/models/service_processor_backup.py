r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ServiceProcessorBackup", "ServiceProcessorBackupSchema"]
__pdoc__ = {
    "ServiceProcessorBackupSchema.resource": False,
    "ServiceProcessorBackup": False,
}


class ServiceProcessorBackupSchema(ResourceSchema):
    """The fields of the ServiceProcessorBackup object"""

    is_current = fields.Boolean(data_key="is_current")
    r""" Indicates whether the service processor is currently booted from the backup partition. """

    state = fields.Str(data_key="state")
    r""" Status of the backup partition.

Valid choices:

* installed
* corrupt
* updating
* auto_updating
* none """

    version = fields.Str(data_key="version")
    r""" Firmware version of the backup partition.

Example: 11.6 """

    @property
    def resource(self):
        return ServiceProcessorBackup

    gettable_fields = [
        "is_current",
        "state",
        "version",
    ]
    """is_current,state,version,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ServiceProcessorBackup(Resource):

    _schema = ServiceProcessorBackupSchema
