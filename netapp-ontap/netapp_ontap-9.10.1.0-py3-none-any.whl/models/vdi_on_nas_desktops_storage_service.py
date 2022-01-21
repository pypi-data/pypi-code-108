r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VdiOnNasDesktopsStorageService", "VdiOnNasDesktopsStorageServiceSchema"]
__pdoc__ = {
    "VdiOnNasDesktopsStorageServiceSchema.resource": False,
    "VdiOnNasDesktopsStorageService": False,
}


class VdiOnNasDesktopsStorageServiceSchema(ResourceSchema):
    """The fields of the VdiOnNasDesktopsStorageService object"""

    name = fields.Str(data_key="name")
    r""" The storage service of the desktops.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return VdiOnNasDesktopsStorageService

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
    ]
    """name,"""


class VdiOnNasDesktopsStorageService(Resource):

    _schema = VdiOnNasDesktopsStorageServiceSchema
