r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FlexcachePrepopulate", "FlexcachePrepopulateSchema"]
__pdoc__ = {
    "FlexcachePrepopulateSchema.resource": False,
    "FlexcachePrepopulate": False,
}


class FlexcachePrepopulateSchema(ResourceSchema):
    """The fields of the FlexcachePrepopulate object"""

    dir_paths = fields.List(fields.Str, data_key="dir_paths")
    r""" The dir_paths field of the flexcache_prepopulate. """

    exclude_dir_paths = fields.List(fields.Str, data_key="exclude_dir_paths")
    r""" The exclude_dir_paths field of the flexcache_prepopulate. """

    recurse = fields.Boolean(data_key="recurse")
    r""" Specifies whether or not the prepopulate action should search through the `dir_paths` recursively. If not set, the default value _true_ is used. """

    @property
    def resource(self):
        return FlexcachePrepopulate

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "dir_paths",
        "exclude_dir_paths",
        "recurse",
    ]
    """dir_paths,exclude_dir_paths,recurse,"""

    postable_fields = [
        "dir_paths",
        "exclude_dir_paths",
        "recurse",
    ]
    """dir_paths,exclude_dir_paths,recurse,"""


class FlexcachePrepopulate(Resource):

    _schema = FlexcachePrepopulateSchema
