r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["LicenseCompliance", "LicenseComplianceSchema"]
__pdoc__ = {
    "LicenseComplianceSchema.resource": False,
    "LicenseCompliance": False,
}


class LicenseComplianceSchema(ResourceSchema):
    """The fields of the LicenseCompliance object"""

    state = fields.Str(data_key="state")
    r""" Compliance state of the license.

Valid choices:

* compliant
* noncompliant
* unlicensed
* unknown """

    @property
    def resource(self):
        return LicenseCompliance

    gettable_fields = [
        "state",
    ]
    """state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class LicenseCompliance(Resource):

    _schema = LicenseComplianceSchema
