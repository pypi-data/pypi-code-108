r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ServiceProcessorPrimary", "ServiceProcessorPrimarySchema"]
__pdoc__ = {
    "ServiceProcessorPrimarySchema.resource": False,
    "ServiceProcessorPrimary": False,
}


class ServiceProcessorPrimarySchema(ResourceSchema):
    """The fields of the ServiceProcessorPrimary object"""

    is_current = fields.Boolean(data_key="is_current")
    r""" Indicates whether the service processor is currently booted from the primary partition. """

    state = fields.Str(data_key="state")
    r""" Status of the primary partition.

Valid choices:

* installed
* corrupt
* updating
* auto_updating
* none """

    version = fields.Str(data_key="version")
    r""" Firmware version of the primary partition.

Example: 11.6 """

    @property
    def resource(self):
        return ServiceProcessorPrimary

    gettable_fields = [
        "is_current",
        "state",
        "version",
    ]
    """is_current,state,version,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class ServiceProcessorPrimary(Resource):

    _schema = ServiceProcessorPrimarySchema
