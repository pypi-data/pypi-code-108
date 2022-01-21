r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSvm", "ApplicationSvmSchema"]
__pdoc__ = {
    "ApplicationSvmSchema.resource": False,
    "ApplicationSvm": False,
}


class ApplicationSvmSchema(ResourceSchema):
    """The fields of the ApplicationSvm object"""

    name = fields.Str(data_key="name")
    r""" SVM Name. Either the SVM name or UUID must be provided to create an application. """

    uuid = fields.Str(data_key="uuid")
    r""" SVM UUID. Either the SVM name or UUID must be provided to create an application. """

    @property
    def resource(self):
        return ApplicationSvm

    gettable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
        "name",
        "uuid",
    ]
    """name,uuid,"""


class ApplicationSvm(Resource):

    _schema = ApplicationSvmSchema
