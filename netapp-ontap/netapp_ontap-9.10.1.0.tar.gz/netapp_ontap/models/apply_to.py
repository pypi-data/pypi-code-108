r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplyTo", "ApplyToSchema"]
__pdoc__ = {
    "ApplyToSchema.resource": False,
    "ApplyTo": False,
}


class ApplyToSchema(ResourceSchema):
    """The fields of the ApplyTo object"""

    files = fields.Boolean(data_key="files")
    r""" Apply to Files """

    sub_folders = fields.Boolean(data_key="sub_folders")
    r""" Apply to all sub-folders """

    this_folder = fields.Boolean(data_key="this_folder")
    r""" Apply only to this folder """

    @property
    def resource(self):
        return ApplyTo

    gettable_fields = [
        "files",
        "sub_folders",
        "this_folder",
    ]
    """files,sub_folders,this_folder,"""

    patchable_fields = [
        "files",
        "sub_folders",
        "this_folder",
    ]
    """files,sub_folders,this_folder,"""

    postable_fields = [
        "files",
        "sub_folders",
        "this_folder",
    ]
    """files,sub_folders,this_folder,"""


class ApplyTo(Resource):

    _schema = ApplyToSchema
