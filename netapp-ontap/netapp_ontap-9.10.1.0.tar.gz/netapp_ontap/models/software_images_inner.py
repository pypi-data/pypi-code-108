r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareImagesInner", "SoftwareImagesInnerSchema"]
__pdoc__ = {
    "SoftwareImagesInnerSchema.resource": False,
    "SoftwareImagesInner": False,
}


class SoftwareImagesInnerSchema(ResourceSchema):
    """The fields of the SoftwareImagesInner object"""

    package = fields.Str(data_key="package")
    r""" Package file name.

Example: image.tgz """

    @property
    def resource(self):
        return SoftwareImagesInner

    gettable_fields = [
        "package",
    ]
    """package,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwareImagesInner(Resource):

    _schema = SoftwareImagesInnerSchema
