r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MccipPort", "MccipPortSchema"]
__pdoc__ = {
    "MccipPortSchema.resource": False,
    "MccipPort": False,
}


class MccipPortSchema(ResourceSchema):
    """The fields of the MccipPort object"""

    l3_config = fields.Nested("netapp_ontap.models.mccip_port_l3_config.MccipPortL3ConfigSchema", unknown=EXCLUDE, data_key="l3_config")
    r""" The l3_config field of the mccip_port. """

    name = fields.Str(data_key="name")
    r""" Port name

Example: e1b """

    node = fields.Nested("netapp_ontap.resources.node.NodeSchema", unknown=EXCLUDE, data_key="node")
    r""" The node field of the mccip_port. """

    uuid = fields.Str(data_key="uuid")
    r""" Port UUID """

    vlan_id = Size(data_key="vlan_id")
    r""" VLAN ID

Example: 200 """

    @property
    def resource(self):
        return MccipPort

    gettable_fields = [
        "l3_config",
        "name",
        "node.links",
        "node.name",
        "node.uuid",
        "uuid",
        "vlan_id",
    ]
    """l3_config,name,node.links,node.name,node.uuid,uuid,vlan_id,"""

    patchable_fields = [
        "l3_config",
        "name",
        "node.name",
        "node.uuid",
        "uuid",
        "vlan_id",
    ]
    """l3_config,name,node.name,node.uuid,uuid,vlan_id,"""

    postable_fields = [
        "l3_config",
        "name",
        "node.name",
        "node.uuid",
        "uuid",
        "vlan_id",
    ]
    """l3_config,name,node.name,node.uuid,uuid,vlan_id,"""


class MccipPort(Resource):

    _schema = MccipPortSchema
