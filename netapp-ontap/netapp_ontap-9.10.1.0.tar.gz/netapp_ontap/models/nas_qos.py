r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasQos", "NasQosSchema"]
__pdoc__ = {
    "NasQosSchema.resource": False,
    "NasQos": False,
}


class NasQosSchema(ResourceSchema):
    """The fields of the NasQos object"""

    policy = fields.Nested("netapp_ontap.models.nas_qos_policy.NasQosPolicySchema", unknown=EXCLUDE, data_key="policy")
    r""" The policy field of the nas_qos. """

    @property
    def resource(self):
        return NasQos

    gettable_fields = [
        "policy",
    ]
    """policy,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "policy",
    ]
    """policy,"""


class NasQos(Resource):

    _schema = NasQosSchema
