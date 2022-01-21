r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TapeDeviceDeviceNames", "TapeDeviceDeviceNamesSchema"]
__pdoc__ = {
    "TapeDeviceDeviceNamesSchema.resource": False,
    "TapeDeviceDeviceNames": False,
}


class TapeDeviceDeviceNamesSchema(ResourceSchema):
    """The fields of the TapeDeviceDeviceNames object"""

    no_rewind_device = fields.Str(data_key="no_rewind_device")
    r""" Device name for no rewind.

Example: nrst6l """

    rewind_device = fields.Str(data_key="rewind_device")
    r""" Device name for rewind.

Example: rst6l """

    unload_reload_device = fields.Str(data_key="unload_reload_device")
    r""" Device name for unload or reload operations.

Example: urst6l """

    @property
    def resource(self):
        return TapeDeviceDeviceNames

    gettable_fields = [
        "no_rewind_device",
        "rewind_device",
        "unload_reload_device",
    ]
    """no_rewind_device,rewind_device,unload_reload_device,"""

    patchable_fields = [
        "no_rewind_device",
        "rewind_device",
        "unload_reload_device",
    ]
    """no_rewind_device,rewind_device,unload_reload_device,"""

    postable_fields = [
        "no_rewind_device",
        "rewind_device",
        "unload_reload_device",
    ]
    """no_rewind_device,rewind_device,unload_reload_device,"""


class TapeDeviceDeviceNames(Resource):

    _schema = TapeDeviceDeviceNamesSchema
