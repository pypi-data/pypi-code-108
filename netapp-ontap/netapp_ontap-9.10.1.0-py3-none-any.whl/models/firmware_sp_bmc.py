r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FirmwareSpBmc", "FirmwareSpBmcSchema"]
__pdoc__ = {
    "FirmwareSpBmcSchema.resource": False,
    "FirmwareSpBmc": False,
}


class FirmwareSpBmcSchema(ResourceSchema):
    """The fields of the FirmwareSpBmc object"""

    autoupdte = fields.Boolean(data_key="autoupdte")
    r""" The autoupdte field of the firmware_sp_bmc.

Example: false """

    end_time = ImpreciseDateTime(data_key="end_time")
    r""" The end_time field of the firmware_sp_bmc.

Example: 2020-05-17T20:00:00.000+0000 """

    fw_type = fields.Str(data_key="fw_type")
    r""" The fw_type field of the firmware_sp_bmc.

Valid choices:

* SP
* BMC """

    image = fields.Str(data_key="image")
    r""" The image field of the firmware_sp_bmc.

Valid choices:

* primary
* backup """

    in_progress = fields.Boolean(data_key="in_progress")
    r""" The in_progress field of the firmware_sp_bmc. """

    is_current = fields.Boolean(data_key="is_current")
    r""" The is_current field of the firmware_sp_bmc.

Example: true """

    last_update_state = fields.Str(data_key="last_update_state")
    r""" The last_update_state field of the firmware_sp_bmc.

Valid choices:

* passed
* failed """

    percent_done = Size(data_key="percent_done")
    r""" The percent_done field of the firmware_sp_bmc.

Example: 100 """

    running_version = fields.Str(data_key="running_version")
    r""" The running_version field of the firmware_sp_bmc.

Example: 1.2.3.4 """

    start_time = ImpreciseDateTime(data_key="start_time")
    r""" The start_time field of the firmware_sp_bmc.

Example: 2020-05-17T20:00:00.000+0000 """

    state = fields.Str(data_key="state")
    r""" The state field of the firmware_sp_bmc.

Valid choices:

* installed
* corrupt
* updating
* autoupdating
* none """

    @property
    def resource(self):
        return FirmwareSpBmc

    gettable_fields = [
        "autoupdte",
        "end_time",
        "fw_type",
        "image",
        "in_progress",
        "is_current",
        "last_update_state",
        "percent_done",
        "running_version",
        "start_time",
        "state",
    ]
    """autoupdte,end_time,fw_type,image,in_progress,is_current,last_update_state,percent_done,running_version,start_time,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FirmwareSpBmc(Resource):

    _schema = FirmwareSpBmcSchema
