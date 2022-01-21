r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationCifsPropertiesShare", "ApplicationCifsPropertiesShareSchema"]
__pdoc__ = {
    "ApplicationCifsPropertiesShareSchema.resource": False,
    "ApplicationCifsPropertiesShare": False,
}


class ApplicationCifsPropertiesShareSchema(ResourceSchema):
    """The fields of the ApplicationCifsPropertiesShare object"""

    name = fields.Str(data_key="name")
    r""" Share name """

    @property
    def resource(self):
        return ApplicationCifsPropertiesShare

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


class ApplicationCifsPropertiesShare(Resource):

    _schema = ApplicationCifsPropertiesShareSchema
