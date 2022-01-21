r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationProtectionGroupsRpoLocal", "ApplicationProtectionGroupsRpoLocalSchema"]
__pdoc__ = {
    "ApplicationProtectionGroupsRpoLocalSchema.resource": False,
    "ApplicationProtectionGroupsRpoLocal": False,
}


class ApplicationProtectionGroupsRpoLocalSchema(ResourceSchema):
    """The fields of the ApplicationProtectionGroupsRpoLocal object"""

    description = fields.Str(data_key="description")
    r""" A detailed description of the local RPO. This includes details on the Snapshot copy schedule. """

    name = fields.Str(data_key="name")
    r""" The local RPO of the component. This indicates how often component Snapshot copies are automatically created.

Valid choices:

* none
* hourly
* 6_hourly
* 15_minutely """

    @property
    def resource(self):
        return ApplicationProtectionGroupsRpoLocal

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


class ApplicationProtectionGroupsRpoLocal(Resource):

    _schema = ApplicationProtectionGroupsRpoLocalSchema
