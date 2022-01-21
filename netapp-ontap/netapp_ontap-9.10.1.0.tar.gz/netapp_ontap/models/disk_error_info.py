r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["DiskErrorInfo", "DiskErrorInfoSchema"]
__pdoc__ = {
    "DiskErrorInfoSchema.resource": False,
    "DiskErrorInfo": False,
}


class DiskErrorInfoSchema(ResourceSchema):
    """The fields of the DiskErrorInfo object"""

    reason = fields.Nested("netapp_ontap.models.error.ErrorSchema", unknown=EXCLUDE, data_key="reason")
    r""" The message and code detailing the error state of this disk. """

    type = fields.Str(data_key="type")
    r""" Disk error type.

Valid choices:

* onepath
* onedomain
* control
* foreign
* toobig
* toosmall
* invalidblocksize
* targetasymmap
* deviceassymmap
* failovermisconfig
* unknown
* netapp
* fwdownrev
* qualfail
* diskfail
* notallflashdisk """

    @property
    def resource(self):
        return DiskErrorInfo

    gettable_fields = [
        "reason",
        "type",
    ]
    """reason,type,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class DiskErrorInfo(Resource):

    _schema = DiskErrorInfoSchema
