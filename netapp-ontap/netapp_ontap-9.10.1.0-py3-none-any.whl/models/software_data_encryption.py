r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareDataEncryption", "SoftwareDataEncryptionSchema"]
__pdoc__ = {
    "SoftwareDataEncryptionSchema.resource": False,
    "SoftwareDataEncryption": False,
}


class SoftwareDataEncryptionSchema(ResourceSchema):
    """The fields of the SoftwareDataEncryption object"""

    conversion_enabled = fields.Boolean(data_key="conversion_enabled")
    r""" Indicates whether or not software encryption conversion is enabled on the cluster. A PATCH request initiates the conversion of all non-encrypted metadata volumes in the cluster to encrypted metadata volumes and all non-NAE aggregates to NAE aggregates. For the PATCH request to start, the cluster must have either an Onboard or an external key manager set up and the aggregates should either be empty or have only metadata volumes. No data volumes should be present in any of the aggregates in the cluster. For MetroCluster configurations, a PATCH request enables conversion on all the aggregates and metadata volumes of both local and remote clusters and is not allowed when the MetroCluster is in switchover state. """

    disabled_by_default = fields.Boolean(data_key="disabled_by_default")
    r""" Indicates whether or not default software data at rest encryption is disabled on the cluster. """

    @property
    def resource(self):
        return SoftwareDataEncryption

    gettable_fields = [
        "conversion_enabled",
        "disabled_by_default",
    ]
    """conversion_enabled,disabled_by_default,"""

    patchable_fields = [
        "conversion_enabled",
        "disabled_by_default",
    ]
    """conversion_enabled,disabled_by_default,"""

    postable_fields = [
    ]
    """"""


class SoftwareDataEncryption(Resource):

    _schema = SoftwareDataEncryptionSchema
