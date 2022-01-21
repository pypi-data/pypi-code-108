r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Href", "HrefSchema"]
__pdoc__ = {
    "HrefSchema.resource": False,
    "Href": False,
}


class HrefSchema(ResourceSchema):
    """The fields of the Href object"""

    href = fields.Str(data_key="href")
    r""" The href field of the href.

Example: /api/resourcelink """

    @property
    def resource(self):
        return Href

    gettable_fields = [
        "href",
    ]
    """href,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Href(Resource):

    _schema = HrefSchema
