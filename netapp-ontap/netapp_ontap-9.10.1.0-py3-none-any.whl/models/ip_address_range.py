r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["IpAddressRange", "IpAddressRangeSchema"]
__pdoc__ = {
    "IpAddressRangeSchema.resource": False,
    "IpAddressRange": False,
}


class IpAddressRangeSchema(ResourceSchema):
    """The fields of the IpAddressRange object"""

    end = fields.Str(data_key="end")
    r""" The end field of the ip_address_range. """

    family = fields.Str(data_key="family")
    r""" The family field of the ip_address_range. """

    start = fields.Str(data_key="start")
    r""" The start field of the ip_address_range. """

    @property
    def resource(self):
        return IpAddressRange

    gettable_fields = [
        "end",
        "family",
        "start",
    ]
    """end,family,start,"""

    patchable_fields = [
        "end",
        "family",
        "start",
    ]
    """end,family,start,"""

    postable_fields = [
        "end",
        "family",
        "start",
    ]
    """end,family,start,"""


class IpAddressRange(Resource):

    _schema = IpAddressRangeSchema
