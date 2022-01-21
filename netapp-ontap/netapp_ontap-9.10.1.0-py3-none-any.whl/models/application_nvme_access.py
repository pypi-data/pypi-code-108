r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationNvmeAccess", "ApplicationNvmeAccessSchema"]
__pdoc__ = {
    "ApplicationNvmeAccessSchema.resource": False,
    "ApplicationNvmeAccess": False,
}


class ApplicationNvmeAccessSchema(ResourceSchema):
    """The fields of the ApplicationNvmeAccess object"""

    backing_storage = fields.Nested("netapp_ontap.models.application_nvme_access_backing_storage.ApplicationNvmeAccessBackingStorageSchema", unknown=EXCLUDE, data_key="backing_storage")
    r""" The backing_storage field of the application_nvme_access. """

    is_clone = fields.Boolean(data_key="is_clone")
    r""" Clone """

    subsystem_map = fields.Nested("netapp_ontap.models.application_subsystem_map_object.ApplicationSubsystemMapObjectSchema", unknown=EXCLUDE, data_key="subsystem_map")
    r""" The subsystem_map field of the application_nvme_access. """

    @property
    def resource(self):
        return ApplicationNvmeAccess

    gettable_fields = [
        "backing_storage",
        "is_clone",
        "subsystem_map",
    ]
    """backing_storage,is_clone,subsystem_map,"""

    patchable_fields = [
        "backing_storage",
        "subsystem_map",
    ]
    """backing_storage,subsystem_map,"""

    postable_fields = [
        "backing_storage",
        "subsystem_map",
    ]
    """backing_storage,subsystem_map,"""


class ApplicationNvmeAccess(Resource):

    _schema = ApplicationNvmeAccessSchema
