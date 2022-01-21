r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["Version", "VersionSchema"]
__pdoc__ = {
    "VersionSchema.resource": False,
    "Version": False,
}


class VersionSchema(ResourceSchema):
    """The fields of the Version object"""

    full = fields.Str(data_key="full")
    r""" The full cluster version string.

Example: NetApp Release 9.4.0: Sun Nov 05 18:20:57 UTC 2017 """

    generation = Size(data_key="generation")
    r""" The generation portion of the version.

Example: 9 """

    major = Size(data_key="major")
    r""" The major portion of the version.

Example: 4 """

    minor = Size(data_key="minor")
    r""" The minor portion of the version.

Example: 0 """

    @property
    def resource(self):
        return Version

    gettable_fields = [
        "full",
        "generation",
        "major",
        "minor",
    ]
    """full,generation,major,minor,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class Version(Resource):

    _schema = VersionSchema
