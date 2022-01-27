"""
pyape.errors
~~~~~~~~~~~~~~~~~~~

接管所有错误
"""

from flask import jsonify


def forbidden(e):
    response = jsonify({'error': True, 'code': 403, 'message': '403 forbidden'})
    response.status_code = 403
    return response


def page_not_found(e):
    response = jsonify({'error': True, 'code': 404, 'message': '404 not found'})
    response.status_code = 404
    return response


def method_not_allowed(e):
    response = jsonify({'error': True, 'code': 405, 'message': '405 method not allowed'})
    response.status_code = 405
    return response


def internal_server_error(e):
    response = jsonify({'error': True, 'code': 500, 'message': '500 internal server error'})
    response.status_code = 500
    return response


def init_app(pyape_app):
    pyape_app.register_error_handler(403, forbidden)
    pyape_app.register_error_handler(404, page_not_found)
    pyape_app.register_error_handler(405, method_not_allowed)
    pyape_app.register_error_handler(500, internal_server_error)
    # pyape_app.error_handler_spec[None][403] = forbidden
    # pyape_app.error_handler_spec[None][404] = page_not_found
    # pyape_app.error_handler_spec[None][405] = method_not_allowed
    # pyape_app.error_handler_spec[None][500] = internal_server_error
