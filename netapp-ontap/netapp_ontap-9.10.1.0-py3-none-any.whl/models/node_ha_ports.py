r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NodeHaPorts", "NodeHaPortsSchema"]
__pdoc__ = {
    "NodeHaPortsSchema.resource": False,
    "NodeHaPorts": False,
}


class NodeHaPortsSchema(ResourceSchema):
    """The fields of the NodeHaPorts object"""

    number = Size(data_key="number")
    r""" HA port number

Example: 0 """

    state = fields.Str(data_key="state")
    r""" HA port state:

* <i>down</i> - Logical HA link is down.
* <i>initialized</i> - Logical HA link is initialized. The physical link is up, but the subnet manager hasn’t started to configure the port.
* <i>armed</i> - Logical HA link is armed. The physical link is up and the subnet manager started but did not yet complete configuring the port.
* <i>active</i> - Logical HA link is active.
* <i>reserved</i> - Logical HA link is active, but the physical link is down.


Valid choices:

* down
* initialized
* armed
* active
* reserved """

    @property
    def resource(self):
        return NodeHaPorts

    gettable_fields = [
        "number",
        "state",
    ]
    """number,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class NodeHaPorts(Resource):

    _schema = NodeHaPortsSchema
