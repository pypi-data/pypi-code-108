r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationRpoRemote", "ApplicationRpoRemoteSchema"]
__pdoc__ = {
    "ApplicationRpoRemoteSchema.resource": False,
    "ApplicationRpoRemote": False,
}


class ApplicationRpoRemoteSchema(ResourceSchema):
    """The fields of the ApplicationRpoRemote object"""

    description = fields.Str(data_key="description")
    r""" A detailed description of the remote RPO. """

    name = fields.Str(data_key="name")
    r""" The remote RPO of the application. A remote RPO of zero indicates that the application is synchronously replicated to another cluster.

Valid choices:

* 6_hourly
* 15_minutely
* hourly
* none
* zero """

    @property
    def resource(self):
        return ApplicationRpoRemote

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


class ApplicationRpoRemote(Resource):

    _schema = ApplicationRpoRemoteSchema
