r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationCifsPropertiesServer", "ApplicationCifsPropertiesServerSchema"]
__pdoc__ = {
    "ApplicationCifsPropertiesServerSchema.resource": False,
    "ApplicationCifsPropertiesServer": False,
}


class ApplicationCifsPropertiesServerSchema(ResourceSchema):
    """The fields of the ApplicationCifsPropertiesServer object"""

    name = fields.Str(data_key="name")
    r""" Server name """

    @property
    def resource(self):
        return ApplicationCifsPropertiesServer

    gettable_fields = [
        "name",
    ]
    """name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationCifsPropertiesServer(Resource):

    _schema = ApplicationCifsPropertiesServerSchema
