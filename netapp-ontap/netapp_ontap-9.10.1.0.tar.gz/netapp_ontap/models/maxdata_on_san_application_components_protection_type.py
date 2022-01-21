r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MaxdataOnSanApplicationComponentsProtectionType", "MaxdataOnSanApplicationComponentsProtectionTypeSchema"]
__pdoc__ = {
    "MaxdataOnSanApplicationComponentsProtectionTypeSchema.resource": False,
    "MaxdataOnSanApplicationComponentsProtectionType": False,
}


class MaxdataOnSanApplicationComponentsProtectionTypeSchema(ResourceSchema):
    """The fields of the MaxdataOnSanApplicationComponentsProtectionType object"""

    local_rpo = fields.Str(data_key="local_rpo")
    r""" The local rpo of the application component.

Valid choices:

* 6_hourly
* 15_minutely
* hourly
* none """

    remote_rpo = fields.Str(data_key="remote_rpo")
    r""" The remote rpo of the application component.

Valid choices:

* 6_hourly
* 15_minutely
* hourly
* none """

    @property
    def resource(self):
        return MaxdataOnSanApplicationComponentsProtectionType

    gettable_fields = [
        "local_rpo",
        "remote_rpo",
    ]
    """local_rpo,remote_rpo,"""

    patchable_fields = [
        "local_rpo",
        "remote_rpo",
    ]
    """local_rpo,remote_rpo,"""

    postable_fields = [
        "local_rpo",
        "remote_rpo",
    ]
    """local_rpo,remote_rpo,"""


class MaxdataOnSanApplicationComponentsProtectionType(Resource):

    _schema = MaxdataOnSanApplicationComponentsProtectionTypeSchema
