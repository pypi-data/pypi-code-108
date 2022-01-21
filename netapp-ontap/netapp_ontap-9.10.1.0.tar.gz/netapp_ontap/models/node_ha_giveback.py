r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeHaGiveback", "NodeHaGivebackSchema"]
__pdoc__ = {
    "NodeHaGivebackSchema.resource": False,
    "NodeHaGiveback": False,
}


class NodeHaGivebackSchema(ResourceSchema):
    """The fields of the NodeHaGiveback object"""

    failure = fields.Nested("netapp_ontap.models.node_ha_giveback_failure.NodeHaGivebackFailureSchema", unknown=EXCLUDE, data_key="failure")
    r""" The failure field of the node_ha_giveback. """

    state = fields.Str(data_key="state")
    r""" The state field of the node_ha_giveback.

Valid choices:

* nothing_to_giveback
* not_attempted
* in_progress
* failed """

    @property
    def resource(self):
        return NodeHaGiveback

    gettable_fields = [
        "failure",
        "state",
    ]
    """failure,state,"""

    patchable_fields = [
        "failure",
        "state",
    ]
    """failure,state,"""

    postable_fields = [
        "failure",
        "state",
    ]
    """failure,state,"""


class NodeHaGiveback(Resource):

    _schema = NodeHaGivebackSchema
