r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VdiOnNasDesktops", "VdiOnNasDesktopsSchema"]
__pdoc__ = {
    "VdiOnNasDesktopsSchema.resource": False,
    "VdiOnNasDesktops": False,
}


class VdiOnNasDesktopsSchema(ResourceSchema):
    """The fields of the VdiOnNasDesktops object"""

    count = Size(data_key="count")
    r""" The number of desktops to support. """

    size = Size(data_key="size")
    r""" The size of the desktops. Usage: {&lt;integer&gt;[KB|MB|GB|TB|PB]} """

    storage_service = fields.Nested("netapp_ontap.models.vdi_on_nas_desktops_storage_service.VdiOnNasDesktopsStorageServiceSchema", unknown=EXCLUDE, data_key="storage_service")
    r""" The storage_service field of the vdi_on_nas_desktops. """

    @property
    def resource(self):
        return VdiOnNasDesktops

    gettable_fields = [
        "count",
        "size",
        "storage_service",
    ]
    """count,size,storage_service,"""

    patchable_fields = [
        "count",
        "storage_service",
    ]
    """count,storage_service,"""

    postable_fields = [
        "count",
        "size",
        "storage_service",
    ]
    """count,size,storage_service,"""


class VdiOnNasDesktops(Resource):

    _schema = VdiOnNasDesktopsSchema
