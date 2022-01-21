r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LunMovementPaths", "LunMovementPathsSchema"]
__pdoc__ = {
    "LunMovementPathsSchema.resource": False,
    "LunMovementPaths": False,
}


class LunMovementPathsSchema(ResourceSchema):
    """The fields of the LunMovementPaths object"""

    destination = fields.Str(data_key="destination")
    r""" The fully qualified path of the LUN movement destination composed of a "/vol" prefix, the volume name, the (optional) qtree name, and base name of the LUN.


Example: /vol/vol1/lun1 """

    source = fields.Str(data_key="source")
    r""" The fully qualified path of the LUN movement source composed of a "/vol" prefix, the volume name, the (optional) qtree name, and base name of the LUN.


Example: /vol/vol2/lun2 """

    @property
    def resource(self):
        return LunMovementPaths

    gettable_fields = [
        "destination",
        "source",
    ]
    """destination,source,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LunMovementPaths(Resource):

    _schema = LunMovementPathsSchema
