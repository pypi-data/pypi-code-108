r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AutoUpdateInfoEula", "AutoUpdateInfoEulaSchema"]
__pdoc__ = {
    "AutoUpdateInfoEulaSchema.resource": False,
    "AutoUpdateInfoEula": False,
}


class AutoUpdateInfoEulaSchema(ResourceSchema):
    """The fields of the AutoUpdateInfoEula object"""

    accepted = fields.Boolean(data_key="accepted")
    r""" Flag indicating the End User License Agreement (EULA) acceptance. When the feature is enabled, it is assumed that the EULA is accepted.

Example: true """

    accepted_ip_address = fields.Str(data_key="accepted_ip_address")
    r""" IP Address from where the EULA was accepted.

Example: 192.168.1.125 """

    accepted_timestamp = ImpreciseDateTime(data_key="accepted_timestamp")
    r""" Date and time when the EULA was accepted.

Example: 2020-12-01T13:12:23.000+0000 """

    user_id_accepted = fields.Str(data_key="user_id_accepted")
    r""" User ID that provided the EULA acceptance.

Example: admin """

    @property
    def resource(self):
        return AutoUpdateInfoEula

    gettable_fields = [
        "accepted",
        "accepted_ip_address",
        "accepted_timestamp",
        "user_id_accepted",
    ]
    """accepted,accepted_ip_address,accepted_timestamp,user_id_accepted,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class AutoUpdateInfoEula(Resource):

    _schema = AutoUpdateInfoEulaSchema
