r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["SoftwareErrors", "SoftwareErrorsSchema"]
__pdoc__ = {
    "SoftwareErrorsSchema.resource": False,
    "SoftwareErrors": False,
}


class SoftwareErrorsSchema(ResourceSchema):
    """The fields of the SoftwareErrors object"""

    code = Size(data_key="code")
    r""" Error code of message

Example: 177 """

    message = fields.Str(data_key="message")
    r""" Error message

Example: Giveback of CFO aggregate is vetoed. Action: Use the "storage failover show-giveback" command to view detailed veto status information. Correct the vetoed update check. Use the "storage failover giveback -ofnode "node1" command to complete the giveback. """

    severity = fields.Str(data_key="severity")
    r""" Severity of error

Valid choices:

* informational
* warning
* error """

    @property
    def resource(self):
        return SoftwareErrors

    gettable_fields = [
        "code",
        "message",
        "severity",
    ]
    """code,message,severity,"""

    patchable_fields = [
    ]
    """"""

    postable_fields = [
    ]
    """"""


class SoftwareErrors(Resource):

    _schema = SoftwareErrorsSchema
