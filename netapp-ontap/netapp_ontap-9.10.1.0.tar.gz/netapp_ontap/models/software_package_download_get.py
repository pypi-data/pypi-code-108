r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwarePackageDownloadGet", "SoftwarePackageDownloadGetSchema"]
__pdoc__ = {
    "SoftwarePackageDownloadGetSchema.resource": False,
    "SoftwarePackageDownloadGet": False,
}


class SoftwarePackageDownloadGetSchema(ResourceSchema):
    """The fields of the SoftwarePackageDownloadGet object"""

    code = Size(data_key="code")
    r""" Code corresponds to download message

Example: 10551496 """

    message = fields.Str(data_key="message")
    r""" Download progress details

Example: Package download in progress """

    state = fields.Str(data_key="state")
    r""" Download status of the package

Valid choices:

* not_started
* running
* success
* failure """

    @property
    def resource(self):
        return SoftwarePackageDownloadGet

    gettable_fields = [
        "code",
        "message",
        "state",
    ]
    """code,message,state,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwarePackageDownloadGet(Resource):

    _schema = SoftwarePackageDownloadGetSchema
