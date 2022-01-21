r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ChassisNodePcis", "ChassisNodePcisSchema"]
__pdoc__ = {
    "ChassisNodePcisSchema.resource": False,
    "ChassisNodePcis": False,
}


class ChassisNodePcisSchema(ResourceSchema):
    """The fields of the ChassisNodePcis object"""

    cards = fields.List(fields.Nested("netapp_ontap.models.chassis_node_pcis_cards.ChassisNodePcisCardsSchema", unknown=EXCLUDE), data_key="cards")
    r""" The cards field of the chassis_node_pcis. """

    @property
    def resource(self):
        return ChassisNodePcis

    gettable_fields = [
        "cards",
    ]
    """cards,"""

    patchable_fields = [
        "cards",
    ]
    """cards,"""

    postable_fields = [
        "cards",
    ]
    """cards,"""


class ChassisNodePcis(Resource):

    _schema = ChassisNodePcisSchema
