r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["AggregateWarningWarning", "AggregateWarningWarningSchema"]
__pdoc__ = {
    "AggregateWarningWarningSchema.resource": False,
    "AggregateWarningWarning": False,
}


class AggregateWarningWarningSchema(ResourceSchema):
    """The fields of the AggregateWarningWarning object"""

    arguments = fields.List(fields.Str, data_key="arguments")
    r""" Arguments present in the warning message encountered. """

    code = Size(data_key="code")
    r""" Warning code of the warning encountered. """

    message = fields.Str(data_key="message")
    r""" Details of the warning encountered by the aggregate simulate query. """

    @property
    def resource(self):
        return AggregateWarningWarning

    gettable_fields = [
        "arguments",
        "code",
        "message",
    ]
    """arguments,code,message,"""

    patchable_fields = [
        "arguments",
        "code",
        "message",
    ]
    """arguments,code,message,"""

    postable_fields = [
        "arguments",
        "code",
        "message",
    ]
    """arguments,code,message,"""


class AggregateWarningWarning(Resource):

    _schema = AggregateWarningWarningSchema
