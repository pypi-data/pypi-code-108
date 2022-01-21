r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SwitchSnmp", "SwitchSnmpSchema"]
__pdoc__ = {
    "SwitchSnmpSchema.resource": False,
    "SwitchSnmp": False,
}


class SwitchSnmpSchema(ResourceSchema):
    """The fields of the SwitchSnmp object"""

    user = fields.Str(data_key="user")
    r""" Community String or SNMPv3 Username. """

    version = fields.Str(data_key="version")
    r""" SNMP Version.

Valid choices:

* snmpv1
* snmpv2c
* snmpv3 """

    @property
    def resource(self):
        return SwitchSnmp

    gettable_fields = [
        "user",
        "version",
    ]
    """user,version,"""

    patchable_fields = [
        "user",
        "version",
    ]
    """user,version,"""

    postable_fields = [
        "user",
        "version",
    ]
    """user,version,"""


class SwitchSnmp(Resource):

    _schema = SwitchSnmpSchema
