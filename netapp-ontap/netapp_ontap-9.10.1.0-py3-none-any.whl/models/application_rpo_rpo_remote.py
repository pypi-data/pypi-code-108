r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationRpoRpoRemote", "ApplicationRpoRpoRemoteSchema"]
__pdoc__ = {
    "ApplicationRpoRpoRemoteSchema.resource": False,
    "ApplicationRpoRpoRemote": False,
}


class ApplicationRpoRpoRemoteSchema(ResourceSchema):
    """The fields of the ApplicationRpoRpoRemote object"""

    description = fields.Str(data_key="description")
    r""" A detailed description of the remote RPO. """

    name = fields.Str(data_key="name")
    r""" The remote RPO of the component. A remote RPO of zero indicates that the component is synchronously replicated to another cluster.

Valid choices:

* 6_hourly
* 15_minutely
* hourly
* none
* zero """

    @property
    def resource(self):
        return ApplicationRpoRpoRemote

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


class ApplicationRpoRpoRemote(Resource):

    _schema = ApplicationRpoRpoRemoteSchema
