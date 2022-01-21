r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["MongoDbOnSanProtectionType", "MongoDbOnSanProtectionTypeSchema"]
__pdoc__ = {
    "MongoDbOnSanProtectionTypeSchema.resource": False,
    "MongoDbOnSanProtectionType": False,
}


class MongoDbOnSanProtectionTypeSchema(ResourceSchema):
    """The fields of the MongoDbOnSanProtectionType object"""

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
        return MongoDbOnSanProtectionType

    gettable_fields = [
        "local_rpo",
        "remote_rpo",
    ]
    """local_rpo,remote_rpo,"""

    patchable_fields = [
        "local_rpo",
    ]
    """local_rpo,"""

    postable_fields = [
        "local_rpo",
        "remote_rpo",
    ]
    """local_rpo,remote_rpo,"""


class MongoDbOnSanProtectionType(Resource):

    _schema = MongoDbOnSanProtectionTypeSchema
