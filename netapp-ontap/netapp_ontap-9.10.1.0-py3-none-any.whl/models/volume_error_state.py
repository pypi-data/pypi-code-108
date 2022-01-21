r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["VolumeErrorState", "VolumeErrorStateSchema"]
__pdoc__ = {
    "VolumeErrorStateSchema.resource": False,
    "VolumeErrorState": False,
}


class VolumeErrorStateSchema(ResourceSchema):
    """The fields of the VolumeErrorState object"""

    has_bad_blocks = fields.Boolean(data_key="has_bad_blocks")
    r""" Indicates whether the volume has any corrupt data blocks. If the damaged data block is accessed, an IO error, such as EIO for NFS or STATUS_FILE_CORRUPT for CIFS, is returned. """

    is_inconsistent = fields.Boolean(data_key="is_inconsistent")
    r""" Indicates whether the file system has any inconsistencies.<br>true &dash; File system is inconsistent.<br>false &dash; File system in not inconsistent. """

    @property
    def resource(self):
        return VolumeErrorState

    gettable_fields = [
        "has_bad_blocks",
        "is_inconsistent",
    ]
    """has_bad_blocks,is_inconsistent,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class VolumeErrorState(Resource):

    _schema = VolumeErrorStateSchema
