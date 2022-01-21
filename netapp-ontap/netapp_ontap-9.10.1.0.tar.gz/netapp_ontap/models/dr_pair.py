r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DrPair", "DrPairSchema"]
__pdoc__ = {
    "DrPairSchema.resource": False,
    "DrPair": False,
}


class DrPairSchema(ResourceSchema):
    """The fields of the DrPair object"""

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the dr_pair. """

    partner = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="partner")
    r""" The partner field of the dr_pair. """

    @property
    def resource(self):
        return DrPair

    gettable_fields = [
        "node.links",
        "node.name",
        "node.uuid",
        "partner.links",
        "partner.name",
        "partner.uuid",
    ]
    """node.links,node.name,node.uuid,partner.links,partner.name,partner.uuid,"""

    patchable_fields = [
        "node.name",
        "node.uuid",
        "partner.name",
        "partner.uuid",
    ]
    """node.name,node.uuid,partner.name,partner.uuid,"""

    postable_fields = [
        "node.name",
        "node.uuid",
        "partner.name",
        "partner.uuid",
    ]
    """node.name,node.uuid,partner.name,partner.uuid,"""


class DrPair(Resource):

    _schema = DrPairSchema
