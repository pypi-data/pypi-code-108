r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SqlOnSmbAccess", "SqlOnSmbAccessSchema"]
__pdoc__ = {
    "SqlOnSmbAccessSchema.resource": False,
    "SqlOnSmbAccess": False,
}


class SqlOnSmbAccessSchema(ResourceSchema):
    """The fields of the SqlOnSmbAccess object"""

    installer = fields.Str(data_key="installer")
    r""" SQL installer admin user name. """

    service_account = fields.Str(data_key="service_account")
    r""" SQL service account user name. """

    @property
    def resource(self):
        return SqlOnSmbAccess

    gettable_fields = [
        "installer",
        "service_account",
    ]
    """installer,service_account,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "installer",
        "service_account",
    ]
    """installer,service_account,"""


class SqlOnSmbAccess(Resource):

    _schema = SqlOnSmbAccessSchema
