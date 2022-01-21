r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareVolumeSuspectFiles", "AntiRansomwareVolumeSuspectFilesSchema"]
__pdoc__ = {
    "AntiRansomwareVolumeSuspectFilesSchema.resource": False,
    "AntiRansomwareVolumeSuspectFiles": False,
}


class AntiRansomwareVolumeSuspectFilesSchema(ResourceSchema):
    """The fields of the AntiRansomwareVolumeSuspectFiles object"""

    count = Size(data_key="count")
    r""" Total number of `suspect_files.format` files observed by the Anti-ransomware analytics engine on the volume. """

    format = fields.Str(data_key="format")
    r""" File formats observed by the Anti-ransomware analytics engine on the volume. """

    @property
    def resource(self):
        return AntiRansomwareVolumeSuspectFiles

    gettable_fields = [
        "count",
        "format",
    ]
    """count,format,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AntiRansomwareVolumeSuspectFiles(Resource):

    _schema = AntiRansomwareVolumeSuspectFilesSchema
