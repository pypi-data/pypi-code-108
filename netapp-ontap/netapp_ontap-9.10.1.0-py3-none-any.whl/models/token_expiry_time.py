r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["TokenExpiryTime", "TokenExpiryTimeSchema"]
__pdoc__ = {
    "TokenExpiryTimeSchema.resource": False,
    "TokenExpiryTime": False,
}


class TokenExpiryTimeSchema(ResourceSchema):
    """The fields of the TokenExpiryTime object"""

    left = fields.Str(data_key="left")
    r""" Specifies the time remaining before the given token expires in ISO-8601 format. """

    limit = fields.Str(data_key="limit")
    r""" Specifies when the given token expires in ISO-8601 format. """

    @property
    def resource(self):
        return TokenExpiryTime

    gettable_fields = [
        "left",
        "limit",
    ]
    """left,limit,"""

    patchable_fields = [
        "limit",
    ]
    """limit,"""

    postable_fields = [
        "limit",
    ]
    """limit,"""


class TokenExpiryTime(Resource):

    _schema = TokenExpiryTimeSchema
