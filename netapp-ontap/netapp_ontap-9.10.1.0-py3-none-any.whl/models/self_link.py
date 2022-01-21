r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SelfLink", "SelfLinkSchema"]
__pdoc__ = {
    "SelfLinkSchema.resource": False,
    "SelfLink": False,
}


class SelfLinkSchema(ResourceSchema):
    """The fields of the SelfLink object"""

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the self_link. """

    @property
    def resource(self):
        return SelfLink

    gettable_fields = [
        "self_",
    ]
    """self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SelfLink(Resource):

    _schema = SelfLinkSchema
