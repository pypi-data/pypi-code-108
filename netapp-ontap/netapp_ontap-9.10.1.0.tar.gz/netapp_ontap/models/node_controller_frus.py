r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeControllerFrus", "NodeControllerFrusSchema"]
__pdoc__ = {
    "NodeControllerFrusSchema.resource": False,
    "NodeControllerFrus": False,
}


class NodeControllerFrusSchema(ResourceSchema):
    """The fields of the NodeControllerFrus object"""

    id = fields.Str(data_key="id")
    r""" The id field of the node_controller_frus. """

    state = fields.Str(data_key="state")
    r""" The state field of the node_controller_frus.

Valid choices:

* ok
* error """

    type = fields.Str(data_key="type")
    r""" The type field of the node_controller_frus.

Valid choices:

* fan
* psu
* pcie
* disk
* nvs
* dimm
* controller """

    @property
    def resource(self):
        return NodeControllerFrus

    gettable_fields = [
        "id",
        "state",
        "type",
    ]
    """id,state,type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeControllerFrus(Resource):

    _schema = NodeControllerFrusSchema
