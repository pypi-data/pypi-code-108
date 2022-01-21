r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["EmsDestinationCertificate", "EmsDestinationCertificateSchema"]
__pdoc__ = {
    "EmsDestinationCertificateSchema.resource": False,
    "EmsDestinationCertificate": False,
}


class EmsDestinationCertificateSchema(ResourceSchema):
    """The fields of the EmsDestinationCertificate object"""

    ca = fields.Str(data_key="ca")
    r""" Client certificate issuing CA

Example: VeriSign """

    serial_number = fields.Str(data_key="serial_number")
    r""" Client certificate serial number

Example: 1234567890 """

    @property
    def resource(self):
        return EmsDestinationCertificate

    gettable_fields = [
        "ca",
        "serial_number",
    ]
    """ca,serial_number,"""

    patchable_fields = [
        "ca",
        "serial_number",
    ]
    """ca,serial_number,"""

    postable_fields = [
        "ca",
        "serial_number",
    ]
    """ca,serial_number,"""


class EmsDestinationCertificate(Resource):

    _schema = EmsDestinationCertificateSchema
