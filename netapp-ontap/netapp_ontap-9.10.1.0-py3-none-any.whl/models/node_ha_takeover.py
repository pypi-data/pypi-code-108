r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeHaTakeover", "NodeHaTakeoverSchema"]
__pdoc__ = {
    "NodeHaTakeoverSchema.resource": False,
    "NodeHaTakeover": False,
}


class NodeHaTakeoverSchema(ResourceSchema):
    """The fields of the NodeHaTakeover object"""

    failure = fields.Nested("netapp_ontap.models.node_ha_takeover_failure.NodeHaTakeoverFailureSchema", unknown=EXCLUDE, data_key="failure")
    r""" The failure field of the node_ha_takeover. """

    state = fields.Str(data_key="state")
    r""" The state field of the node_ha_takeover.

Valid choices:

* not_possible
* not_attempted
* in_takeover
* in_progress
* failed """

    @property
    def resource(self):
        return NodeHaTakeover

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


class NodeHaTakeover(Resource):

    _schema = NodeHaTakeoverSchema
