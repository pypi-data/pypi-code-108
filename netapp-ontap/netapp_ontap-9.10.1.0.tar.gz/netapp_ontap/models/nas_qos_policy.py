r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasQosPolicy", "NasQosPolicySchema"]
__pdoc__ = {
    "NasQosPolicySchema.resource": False,
    "NasQosPolicy": False,
}


class NasQosPolicySchema(ResourceSchema):
    """The fields of the NasQosPolicy object"""

    name = fields.Str(data_key="name")
    r""" The name of an existing QoS policy. """

    uuid = fields.Str(data_key="uuid")
    r""" The UUID of an existing QoS policy. Usage: &lt;UUID&gt; """

    @property
    def resource(self):
        return NasQosPolicy

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class NasQosPolicy(Resource):

    _schema = NasQosPolicySchema
