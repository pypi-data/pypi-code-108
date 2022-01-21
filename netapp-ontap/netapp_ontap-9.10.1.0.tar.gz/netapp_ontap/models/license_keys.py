r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LicenseKeys", "LicenseKeysSchema"]
__pdoc__ = {
    "LicenseKeysSchema.resource": False,
    "LicenseKeys": False,
}


class LicenseKeysSchema(ResourceSchema):
    """The fields of the LicenseKeys object"""

    keys = fields.List(fields.Str, data_key="keys")
    r""" The keys field of the license_keys. """

    @property
    def resource(self):
        return LicenseKeys

    gettable_fields = [
        "keys",
    ]
    """keys,"""

    patchable_fields = [
        "keys",
    ]
    """keys,"""

    postable_fields = [
        "keys",
    ]
    """keys,"""


class LicenseKeys(Resource):

    _schema = LicenseKeysSchema
