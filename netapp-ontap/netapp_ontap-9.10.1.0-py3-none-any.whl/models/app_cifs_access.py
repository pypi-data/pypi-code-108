r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AppCifsAccess", "AppCifsAccessSchema"]
__pdoc__ = {
    "AppCifsAccessSchema.resource": False,
    "AppCifsAccess": False,
}


class AppCifsAccessSchema(ResourceSchema):
    """The fields of the AppCifsAccess object"""

    access = fields.Str(data_key="access")
    r""" The CIFS access granted to the user or group.

Valid choices:

* change
* full_control
* no_access
* read """

    user_or_group = fields.Str(data_key="user_or_group")
    r""" The name of the CIFS user or group that will be granted access. """

    @property
    def resource(self):
        return AppCifsAccess

    gettable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "access",
        "user_or_group",
    ]
    """access,user_or_group,"""


class AppCifsAccess(Resource):

    _schema = AppCifsAccessSchema
