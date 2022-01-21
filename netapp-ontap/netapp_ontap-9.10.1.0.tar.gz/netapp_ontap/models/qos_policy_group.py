r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["QosPolicyGroup", "QosPolicyGroupSchema"]
__pdoc__ = {
    "QosPolicyGroupSchema.resource": False,
    "QosPolicyGroup": False,
}


class QosPolicyGroupSchema(ResourceSchema):
    """The fields of the QosPolicyGroup object"""

    links = fields.Nested("netapp_ontap.models.self_link.SelfLinkSchema", unknown=EXCLUDE, data_key="_links")
    r""" The links field of the qos_policy_group. """

    name = fields.Str(data_key="name")
    r""" The QoS policy group name. This is mutually exclusive with UUID and other QoS attributes during POST and PATCH.

Example: performance """

    uuid = fields.Str(data_key="uuid")
    r""" The QoS policy group UUID. This is mutually exclusive with name and other QoS attributes during POST and PATCH.

Example: 1cd8a442-86d1-11e0-ae1c-123478563412 """

    @property
    def resource(self):
        return QosPolicyGroup

    gettable_fields = [
        "links",
        "name",
        "uuid",
    ]
    """links,name,uuid,"""

    patchable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class QosPolicyGroup(Resource):

    _schema = QosPolicyGroupSchema
