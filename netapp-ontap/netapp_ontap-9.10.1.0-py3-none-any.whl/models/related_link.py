r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["RelatedLink", "RelatedLinkSchema"]
__pdoc__ = {
    "RelatedLinkSchema.resource": False,
    "RelatedLink": False,
}


class RelatedLinkSchema(ResourceSchema):
    """The fields of the RelatedLink object"""

    related = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="related")
    r""" The related field of the related_link. """

    @property
    def resource(self):
        return RelatedLink

    gettable_fields = [
        "related",
    ]
    """related,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class RelatedLink(Resource):

    _schema = RelatedLinkSchema
