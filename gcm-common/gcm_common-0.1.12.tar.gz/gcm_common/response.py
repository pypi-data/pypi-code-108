import json
from functools import singledispatch

from flask import jsonify, Response

from .exception import MException


@singledispatch
def to_serializable(rv):
    """
    Define a generic serializable function.
    """
    pass


@to_serializable.register(float)
def ts_dict(rv):
    """Register the `float` type
    for the generic serializable function.
    :param rv: object to be serialized
    :type rv: float
    :returns: flask Response object
    """
    response = {
        'code': 0,
        'desc': "",
        'result': str(rv)
    }
    return jsonify(response)


@to_serializable.register(dict)
def ts_dict(rv):
    """Register the `dict` type
    for the generic serializable function.
    :param rv: object to be serialized
    :type rv: dict
    :returns: flask Response object
    """
    response = {
        'code': 0,
        'desc': "",
        'result': json.dumps(rv)
        # 'result': rv
    }
    return jsonify(response)


@to_serializable.register(list)
def ts_list(rv):
    """Register the `list` type
    for the generic serializable function.
    :param rv: objects to be serialized
    :type rv: list
    :returns: flask Response object
    """
    return Response(json.dumps(rv, indent=4, sort_keys=True))


class JSONResponse(Response):
    """
    Custom `Response` class that will be
    used as the default one for the application.
    All responses will be of type
    `application-json`.
    """

    @classmethod
    def force_type(cls, rv, environ=None):
        rv = to_serializable(rv)
        return super(JSONResponse, cls).force_type(rv, environ)


def json_error_handler(app):
    @app.errorhandler(MException)
    def handle_invalid_usage(error):
        """
        Custom `Exception` class that will be
        used as the default one for the application.
        Returns pretty formatted JSON error
        with detailed information.

        :message: error message
        :code: response status code
        :type: error type
        """

        response = jsonify(error.to_dict())
        response.code = error.code
        return response

    @app.errorhandler(Exception)
    def handle_exception(error):
        """
        Handle unknown Exception
        """

        return jsonify({
            'code': 1,
            'desc': 'Алдаа гарлаа. Дахин оролдоно уу.'
        })
