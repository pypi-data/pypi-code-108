r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareUpdateProgress", "FirmwareUpdateProgressSchema"]
__pdoc__ = {
    "FirmwareUpdateProgressSchema.resource": False,
    "FirmwareUpdateProgress": False,
}


class FirmwareUpdateProgressSchema(ResourceSchema):
    """The fields of the FirmwareUpdateProgress object"""

    job = fields.Nested("netapp_ontap.models.job_link.JobLinkSchema", unknown=EXCLUDE, data_key="job")
    r""" The job field of the firmware_update_progress. """

    update_states = fields.List(fields.Nested("netapp_ontap.models.firmware_update_progress_state.FirmwareUpdateProgressStateSchema", unknown=EXCLUDE), data_key="update_states")
    r""" The update_states field of the firmware_update_progress. """

    zip_file_name = fields.Str(data_key="zip_file_name")
    r""" The zip_file_name field of the firmware_update_progress.

Example: disk_firmware.zip """

    @property
    def resource(self):
        return FirmwareUpdateProgress

    gettable_fields = [
        "job",
        "update_states",
        "zip_file_name",
    ]
    """job,update_states,zip_file_name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareUpdateProgress(Resource):

    _schema = FirmwareUpdateProgressSchema
