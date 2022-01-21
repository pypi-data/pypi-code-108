r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationRpoLocal", "ApplicationRpoLocalSchema"]
__pdoc__ = {
    "ApplicationRpoLocalSchema.resource": False,
    "ApplicationRpoLocal": False,
}


class ApplicationRpoLocalSchema(ResourceSchema):
    """The fields of the ApplicationRpoLocal object"""

    description = fields.Str(data_key="description")
    r""" A detailed description of the local RPO. This will include details about the Snapshot copy schedule. """

    name = fields.Str(data_key="name")
    r""" The local RPO of the application. This indicates how often application Snapshot copies are automatically created.

Valid choices:

* 6_hourly
* 15_minutely
* hourly
* none """

    @property
    def resource(self):
        return ApplicationRpoLocal

    gettable_fields = [
        "description",
        "name",
    ]
    """description,name,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ApplicationRpoLocal(Resource):

    _schema = ApplicationRpoLocalSchema
