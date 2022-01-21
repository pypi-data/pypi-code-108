r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Uri", "UriSchema"]
__pdoc__ = {
    "UriSchema.resource": False,
    "Uri": False,
}


class UriSchema(ResourceSchema):
    """The fields of the Uri object"""

    fragment = fields.Str(data_key="fragment")
    r""" The fragment field of the uri.

Example: top """

    host = fields.Str(data_key="host")
    r""" The host field of the uri.

Example: 10.1.1.1 """

    path = fields.Str(data_key="path")
    r""" The path field of the uri.

Example: /api/cluster """

    port = Size(data_key="port")
    r""" The port field of the uri.

Example: 433 """

    query = fields.Str(data_key="query")
    r""" The query field of the uri.

Example: key1=value1 """

    scheme = fields.Str(data_key="scheme")
    r""" The scheme field of the uri.

Example: https """

    userinfo = fields.Str(data_key="userinfo")
    r""" The userinfo field of the uri.

Example: john.doe """

    @property
    def resource(self):
        return Uri

    gettable_fields = [
        "fragment",
        "host",
        "path",
        "port",
        "query",
        "scheme",
        "userinfo",
    ]
    """fragment,host,path,port,query,scheme,userinfo,"""

    patchable_fields = [
        "fragment",
        "host",
        "path",
        "port",
        "query",
        "scheme",
        "userinfo",
    ]
    """fragment,host,path,port,query,scheme,userinfo,"""

    postable_fields = [
        "fragment",
        "host",
        "path",
        "port",
        "query",
        "scheme",
        "userinfo",
    ]
    """fragment,host,path,port,query,scheme,userinfo,"""


class Uri(Resource):

    _schema = UriSchema
