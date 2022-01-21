r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AntiRansomwareSuspectFile", "AntiRansomwareSuspectFileSchema"]
__pdoc__ = {
    "AntiRansomwareSuspectFileSchema.resource": False,
    "AntiRansomwareSuspectFile": False,
}


class AntiRansomwareSuspectFileSchema(ResourceSchema):
    """The fields of the AntiRansomwareSuspectFile object"""

    format = fields.Str(data_key="format")
    r""" File format of the suspected file.

Example: pdf """

    name = fields.Str(data_key="name")
    r""" Name of the suspected file.

Example: test_file """

    path = fields.Str(data_key="path")
    r""" Path of the suspected file.

Example: d1/d2/d3 """

    suspect_time = ImpreciseDateTime(data_key="suspect_time")
    r""" Time when the file was detected as a potential suspect in date-time format.

Example: 2021-05-12T15:00:16.000+0000 """

    @property
    def resource(self):
        return AntiRansomwareSuspectFile

    gettable_fields = [
        "format",
        "name",
        "path",
        "suspect_time",
    ]
    """format,name,path,suspect_time,"""

    patchable_fields = [
        "format",
        "name",
        "path",
    ]
    """format,name,path,"""

    postable_fields = [
        "format",
        "name",
        "path",
    ]
    """format,name,path,"""


class AntiRansomwareSuspectFile(Resource):

    _schema = AntiRansomwareSuspectFileSchema
