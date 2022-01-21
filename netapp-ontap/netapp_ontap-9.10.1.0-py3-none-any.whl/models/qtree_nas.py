r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QtreeNas", "QtreeNasSchema"]
__pdoc__ = {
    "QtreeNasSchema.resource": False,
    "QtreeNas": False,
}


class QtreeNasSchema(ResourceSchema):
    """The fields of the QtreeNas object"""

    path = fields.Str(data_key="path")
    r""" Client visible path to the qtree. This field is not available if the volume does not have a junction-path configured. Not valid in POST or PATCH.

Example: /volume3/qtree1 """

    @property
    def resource(self):
        return QtreeNas

    gettable_fields = [
        "path",
    ]
    """path,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class QtreeNas(Resource):

    _schema = QtreeNasSchema
