r"""
Copyright &copy; 2022 NetApp Inc.
All rights reserved.


"""

from marshmallow import EXCLUDE, fields  # type: ignore
from netapp_ontap.resource import Resource, ResourceSchema, ImpreciseDateTime, Size


__all__ = ["WebCsrfToken", "WebCsrfTokenSchema"]
__pdoc__ = {
    "WebCsrfTokenSchema.resource": False,
    "WebCsrfToken": False,
}


class WebCsrfTokenSchema(ResourceSchema):
    """The fields of the WebCsrfToken object"""

    concurrent_limit = Size(data_key="concurrent_limit")
    r""" Maximum number of concurrent CSRF tokens.

Example: 120 """

    idle_timeout = Size(data_key="idle_timeout")
    r""" Time for which an unused CSRF token is retained, in seconds. """

    max_timeout = Size(data_key="max_timeout")
    r""" Time for which an unused CSRF token, regardless of usage is retained, in seconds. """

    @property
    def resource(self):
        return WebCsrfToken

    gettable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""

    patchable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""

    postable_fields = [
        "concurrent_limit",
        "idle_timeout",
        "max_timeout",
    ]
    """concurrent_limit,idle_timeout,max_timeout,"""


class WebCsrfToken(Resource):

    _schema = WebCsrfTokenSchema
