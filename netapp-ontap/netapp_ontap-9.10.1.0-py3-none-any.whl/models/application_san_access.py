r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["ApplicationSanAccess", "ApplicationSanAccessSchema"]
__pdoc__ = {
    "ApplicationSanAccessSchema.resource": False,
    "ApplicationSanAccess": False,
}


class ApplicationSanAccessSchema(ResourceSchema):
    """The fields of the ApplicationSanAccess object"""

    backing_storage = fields.Nested("netapp_ontap.models.application_san_access_backing_storage.ApplicationSanAccessBackingStorageSchema", unknown=EXCLUDE, data_key="backing_storage")
    r""" The backing_storage field of the application_san_access. """

    is_clone = fields.Boolean(data_key="is_clone")
    r""" Clone """

    lun_mappings = fields.List(fields.Nested("netapp_ontap.models.application_lun_mapping_object.ApplicationLunMappingObjectSchema", unknown=EXCLUDE), data_key="lun_mappings")
    r""" The lun_mappings field of the application_san_access. """

    serial_number = fields.Str(data_key="serial_number")
    r""" LUN serial number """

    @property
    def resource(self):
        return ApplicationSanAccess

    gettable_fields = [
        "backing_storage",
        "is_clone",
        "lun_mappings",
        "serial_number",
    ]
    """backing_storage,is_clone,lun_mappings,serial_number,"""

    patchable_fields = [
        "backing_storage",
        "lun_mappings",
    ]
    """backing_storage,lun_mappings,"""

    postable_fields = [
        "backing_storage",
        "lun_mappings",
    ]
    """backing_storage,lun_mappings,"""


class ApplicationSanAccess(Resource):

    _schema = ApplicationSanAccessSchema
