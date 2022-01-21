r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateDataEncryption", "AggregateDataEncryptionSchema"]
__pdoc__ = {
    "AggregateDataEncryptionSchema.resource": False,
    "AggregateDataEncryption": False,
}


class AggregateDataEncryptionSchema(ResourceSchema):
    """The fields of the AggregateDataEncryption object"""

    drive_protection_enabled = fields.Boolean(data_key="drive_protection_enabled")
    r""" Specifies whether the aggregate uses self-encrypting drives with data protection enabled. """

    software_encryption_enabled = fields.Boolean(data_key="software_encryption_enabled")
    r""" Specifies whether NetApp aggregate encryption is enabled. All data in the aggregate is encrypted. """

    @property
    def resource(self):
        return AggregateDataEncryption

    gettable_fields = [
        "drive_protection_enabled",
        "software_encryption_enabled",
    ]
    """drive_protection_enabled,software_encryption_enabled,"""

    patchable_fields = [
        "software_encryption_enabled",
    ]
    """software_encryption_enabled,"""

    postable_fields = [
        "software_encryption_enabled",
    ]
    """software_encryption_enabled,"""


class AggregateDataEncryption(Resource):

    _schema = AggregateDataEncryptionSchema
