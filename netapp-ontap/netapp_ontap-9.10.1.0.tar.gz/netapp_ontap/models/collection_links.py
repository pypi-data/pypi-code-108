r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["CollectionLinks", "CollectionLinksSchema"]
__pdoc__ = {
    "CollectionLinksSchema.resource": False,
    "CollectionLinks": False,
}


class CollectionLinksSchema(ResourceSchema):
    """The fields of the CollectionLinks object"""

    next = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="next")
    r""" The next field of the collection_links. """

    self_ = fields.Nested("netapp_ontap.models.href.HrefSchema", unknown=EXCLUDE, data_key="self")
    r""" The self_ field of the collection_links. """

    @property
    def resource(self):
        return CollectionLinks

    gettable_fields = [
        "next",
        "self_",
    ]
    """next,self_,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class CollectionLinks(Resource):

    _schema = CollectionLinksSchema
