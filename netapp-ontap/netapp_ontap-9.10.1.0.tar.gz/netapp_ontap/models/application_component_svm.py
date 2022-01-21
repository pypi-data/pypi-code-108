r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationComponentSvm", "ApplicationComponentSvmSchema"]
__pdoc__ = {
    "ApplicationComponentSvmSchema.resource": False,
    "ApplicationComponentSvm": False,
}


class ApplicationComponentSvmSchema(ResourceSchema):
    """The fields of the ApplicationComponentSvm object"""

    name = fields.Str(data_key="name")
    r""" SVM name """

    uuid = fields.Str(data_key="uuid")
    r""" SVM UUID """

    @property
    def resource(self):
        return ApplicationComponentSvm

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationComponentSvm(Resource):

    _schema = ApplicationComponentSvmSchema
