r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["FpolicyEngines", "FpolicyEnginesSchema"]
__pdoc__ = {
    "FpolicyEnginesSchema.resource": False,
    "FpolicyEngines": False,
}


class FpolicyEnginesSchema(ResourceSchema):
    """The fields of the FpolicyEngines object"""

    name = fields.Str(data_key="name")
    r""" Specifies the name to assign to the external server configuration.

Example: fp_ex_eng """

    port = Size(data_key="port")
    r""" Port number of the FPolicy server application.

Example: 9876 """

    primary_servers = fields.List(fields.Str, data_key="primary_servers")
    r""" The primary_servers field of the fpolicy_engines.

Example: ["10.132.145.20","10.140.101.109"] """

    secondary_servers = fields.List(fields.Str, data_key="secondary_servers")
    r""" The secondary_servers field of the fpolicy_engines.

Example: ["10.132.145.20","10.132.145.21"] """

    type = fields.Str(data_key="type")
    r""" The notification mode determines what ONTAP does after sending notifications to FPolicy servers.
  The possible values are:

    * synchronous  - After sending a notification, wait for a response from the FPolicy server.
    * asynchronous - After sending a notification, file request processing continues.


Valid choices:

* synchronous
* asynchronous """

    @property
    def resource(self):
        return FpolicyEngines

    gettable_fields = [
        "name",
        "port",
        "primary_servers",
        "secondary_servers",
        "type",
    ]
    """name,port,primary_servers,secondary_servers,type,"""

    patchable_fields = [
        "port",
        "primary_servers",
        "secondary_servers",
        "type",
    ]
    """port,primary_servers,secondary_servers,type,"""

    postable_fields = [
        "name",
        "port",
        "primary_servers",
        "secondary_servers",
        "type",
    ]
    """name,port,primary_servers,secondary_servers,type,"""


class FpolicyEngines(Resource):

    _schema = FpolicyEnginesSchema
