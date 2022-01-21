r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["NasProtectionType", "NasProtectionTypeSchema"]
__pdoc__ = {
    "NasProtectionTypeSchema.resource": False,
    "NasProtectionType": False,
}


class NasProtectionTypeSchema(ResourceSchema):
    """The fields of the NasProtectionType object"""

    local_policy = fields.Str(data_key="local_policy")
    r""" The Snapshot copy policy to apply to each volume in the smart container. This property is only supported for smart containers. Usage: &lt;snapshot policy&gt; """

    local_rpo = fields.Str(data_key="local_rpo")
    r""" The local RPO of the application.

Valid choices:

* hourly
* none """

    remote_rpo = fields.Str(data_key="remote_rpo")
    r""" The remote RPO of the application.

Valid choices:

* none
* zero """

    @property
    def resource(self):
        return NasProtectionType

    gettable_fields = [
        "local_policy",
        "local_rpo",
        "remote_rpo",
    ]
    """local_policy,local_rpo,remote_rpo,"""

    patchable_fields = [
        "local_rpo",
    ]
    """local_rpo,"""

    postable_fields = [
        "local_policy",
        "local_rpo",
        "remote_rpo",
    ]
    """local_policy,local_rpo,remote_rpo,"""


class NasProtectionType(Resource):

    _schema = NasProtectionTypeSchema
