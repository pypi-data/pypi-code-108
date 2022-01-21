r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FcPortTransceiver", "FcPortTransceiverSchema"]
__pdoc__ = {
    "FcPortTransceiverSchema.resource": False,
    "FcPortTransceiver": False,
}


class FcPortTransceiverSchema(ResourceSchema):
    """The fields of the FcPortTransceiver object"""

    capabilities = fields.List(Size, data_key="capabilities")
    r""" The speeds of which the transceiver is capable in gigabits per second. """

    form_factor = fields.Str(data_key="form_factor")
    r""" The form factor of the transceiver. Possible values are:
- _sfp_ - Small Form Factor - Pluggable
- _sff_ - Small Form Factor
- _unknown_ - Unknown


Valid choices:

* sfp
* sff
* unknown """

    manufacturer = fields.Str(data_key="manufacturer")
    r""" The manufacturer of the transceiver.


Example: Acme, Inc. """

    part_number = fields.Str(data_key="part_number")
    r""" The part number of the transceiver. """

    @property
    def resource(self):
        return FcPortTransceiver

    gettable_fields = [
        "capabilities",
        "form_factor",
        "manufacturer",
        "part_number",
    ]
    """capabilities,form_factor,manufacturer,part_number,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class FcPortTransceiver(Resource):

    _schema = FcPortTransceiverSchema
