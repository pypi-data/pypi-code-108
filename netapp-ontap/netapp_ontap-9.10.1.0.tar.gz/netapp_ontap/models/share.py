r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Share", "ShareSchema"]
__pdoc__ = {
    "ShareSchema.resource": False,
    "Share": False,
}


class ShareSchema(ResourceSchema):
    """The fields of the Share object"""

    name = fields.Str(data_key="name")
    r""" Displays the file or directory effective permission for the mentioned user, only for files and directories contained where the
specified path is relative to the root of the specified share. If this parameter is not specified, the SVM root volume is
taken as the default. If this parameter is specified, the effective share permission of the user is also displayed.
Wildcard query characters are not supported. """

    path = fields.Str(data_key="path")
    r""" Displays the CIFS share path. """

    @property
    def resource(self):
        return Share

    gettable_fields = [
        "name",
        "path",
    ]
    """name,path,"""

    patchable_fields = [
        "name",
        "path",
    ]
    """name,path,"""

    postable_fields = [
        "name",
        "path",
    ]
    """name,path,"""


class Share(Resource):

    _schema = ShareSchema
