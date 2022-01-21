r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ZappNvmeRpoLocal", "ZappNvmeRpoLocalSchema"]
__pdoc__ = {
    "ZappNvmeRpoLocalSchema.resource": False,
    "ZappNvmeRpoLocal": False,
}


class ZappNvmeRpoLocalSchema(ResourceSchema):
    """The fields of the ZappNvmeRpoLocal object"""

    name = fields.Str(data_key="name")
    r""" The local RPO of the application.

Valid choices:

* hourly
* none """

    policy = fields.Str(data_key="policy")
    r""" The Snapshot copy policy to apply to each volume in the smart container. This property is only supported for smart containers. Usage: &lt;snapshot policy&gt; """

    @property
    def resource(self):
        return ZappNvmeRpoLocal

    gettable_fields = [
        "name",
        "policy",
    ]
    """name,policy,"""

    patchable_fields = [
        "name",
    ]
    """name,"""

    postable_fields = [
        "name",
        "policy",
    ]
    """name,policy,"""


class ZappNvmeRpoLocal(Resource):

    _schema = ZappNvmeRpoLocalSchema
