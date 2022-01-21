r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SnapmirrorDestinationCreationStorageService", "SnapmirrorDestinationCreationStorageServiceSchema"]
__pdoc__ = {
    "SnapmirrorDestinationCreationStorageServiceSchema.resource": False,
    "SnapmirrorDestinationCreationStorageService": False,
}


class SnapmirrorDestinationCreationStorageServiceSchema(ResourceSchema):
    """The fields of the SnapmirrorDestinationCreationStorageService object"""

    enabled = fields.Boolean(data_key="enabled")
    r""" This property indicates whether to create the destination endpoint using storage service. """

    enforce_performance = fields.Boolean(data_key="enforce_performance")
    r""" Optional property to enforce storage service performance on the destination endpoint. This property is applicable to FlexVol volume, FlexGroup volume, and Consistency Group endpoints. """

    name = fields.Str(data_key="name")
    r""" Optional property to specify the storage service name for the destination endpoint. This property is considered when the property "create_destination.storage_service.enabled" is set to "true". When the property "create_destination.storage_service.enabled" is set to "true" and the "create_destination.storage_service.name" for the endpoint is not specified, then ONTAP selects the highest storage service available on the cluster to provision the destination endpoint. This property is applicable to FlexVol volume, FlexGroup volume, and Consistency Group endpoints.

Valid choices:

* extreme
* performance
* value """

    @property
    def resource(self):
        return SnapmirrorDestinationCreationStorageService

    gettable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""

    patchable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""

    postable_fields = [
        "enabled",
        "enforce_performance",
        "name",
    ]
    """enabled,enforce_performance,name,"""


class SnapmirrorDestinationCreationStorageService(Resource):

    _schema = SnapmirrorDestinationCreationStorageServiceSchema
