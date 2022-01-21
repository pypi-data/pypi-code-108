r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VscanOnDemandScope", "VscanOnDemandScopeSchema"]
__pdoc__ = {
    "VscanOnDemandScopeSchema.resource": False,
    "VscanOnDemandScope": False,
}


class VscanOnDemandScopeSchema(ResourceSchema):
    """The fields of the VscanOnDemandScope object"""

    exclude_extensions = fields.List(fields.Str, data_key="exclude_extensions")
    r""" List of file extensions for which scanning is not performed.

Example: ["mp3","mp4"] """

    exclude_paths = fields.List(fields.Str, data_key="exclude_paths")
    r""" List of file paths for which scanning must not be performed.

Example: ["/vol1/cold-files/","/vol1/cifs/names"] """

    include_extensions = fields.List(fields.Str, data_key="include_extensions")
    r""" List of file extensions to be scanned.

Example: ["vmdk","mp*"] """

    max_file_size = Size(data_key="max_file_size")
    r""" Maximum file size, in bytes, allowed for scanning.

Example: 10737418240 """

    scan_without_extension = fields.Boolean(data_key="scan_without_extension")
    r""" Specifies whether or not files without any extension can be scanned. """

    @property
    def resource(self):
        return VscanOnDemandScope

    gettable_fields = [
        "exclude_extensions",
        "exclude_paths",
        "include_extensions",
        "max_file_size",
        "scan_without_extension",
    ]
    """exclude_extensions,exclude_paths,include_extensions,max_file_size,scan_without_extension,"""

    patchable_fields = [
        "exclude_extensions",
        "exclude_paths",
        "include_extensions",
        "max_file_size",
        "scan_without_extension",
    ]
    """exclude_extensions,exclude_paths,include_extensions,max_file_size,scan_without_extension,"""

    postable_fields = [
        "exclude_extensions",
        "exclude_paths",
        "include_extensions",
        "max_file_size",
        "scan_without_extension",
    ]
    """exclude_extensions,exclude_paths,include_extensions,max_file_size,scan_without_extension,"""


class VscanOnDemandScope(Resource):

    _schema = VscanOnDemandScopeSchema
