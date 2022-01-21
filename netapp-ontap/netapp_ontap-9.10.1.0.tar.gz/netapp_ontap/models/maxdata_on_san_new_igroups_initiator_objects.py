r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanNewIgroupsInitiatorObjects", "MaxdataOnSanNewIgroupsInitiatorObjectsSchema"]
__pdoc__ = {
    "MaxdataOnSanNewIgroupsInitiatorObjectsSchema.resource": False,
    "MaxdataOnSanNewIgroupsInitiatorObjects": False,
}


class MaxdataOnSanNewIgroupsInitiatorObjectsSchema(ResourceSchema):
    """The fields of the MaxdataOnSanNewIgroupsInitiatorObjects object"""

    comment = fields.Str(data_key="comment")
    r""" A comment available for use by the administrator. """

    name = fields.Str(data_key="name")
    r""" The WWPN, IQN, or Alias of the initiator. Mutually exclusive with nested igroups and the initiators array. """

    @property
    def resource(self):
        return MaxdataOnSanNewIgroupsInitiatorObjects

    gettable_fields = [
    ]
    """"""

    patchable_fields = [
        "comment",
        "name",
    ]
    """comment,name,"""

    postable_fields = [
        "comment",
        "name",
    ]
    """comment,name,"""


class MaxdataOnSanNewIgroupsInitiatorObjects(Resource):

    _schema = MaxdataOnSanNewIgroupsInitiatorObjectsSchema
