'''
A context parses input from the client and creates HTTP responses given a
response object, status and headers. The input and response object are encoded
and decoded according to the context.

Example:

    .. code-block:: python

        class ExampleResource(Resource):
            def post(self, request):
                ctx = JSONContext(request)

                return ctx.response(
                    body={'echo': ctx.data['user_message'],
                          status=HTTPStatus.CREATED,
                          headers={'some-header': 'example'}})
'''

import json
from http import HTTPStatus

from django.http import HttpResponse

from .problem import Problem
from .xml_helper import XMLHelper


class RequestContext:
    def __init__(self, request=None):
        if request is None:
            self.request = None
            self.data = None

        else:
            self.request = request

            try:
                self.data = self.decode(request.body)
            except Problem as p:
                raise p
            except Exception as ex:
                raise Problem.unsupported_media_type(
                    detail='%s: %s' % (type(ex).__name__, str(ex)))

    def response(self, body=None, status=HTTPStatus.OK, headers={}):
        content = self.encode(body) if body is not None else ''
        resp = HttpResponse(content=content,
                            content_type=self.content_type,
                            status=status)

        for key, value in headers.items():
            resp[key] = value

        return resp


class PlainContext(RequestContext):
    def __init__(self, content_type):
        self.content_type = content_type

    def encode(self, data):
        return data

    def decode(self, data):
        return data


class JSONContext(RequestContext):
    def decode(self, json_data):
        obj = json.loads(json_data)

        if not isinstance(obj, dict):
            raise Problem.bad_request(
                detail='toplevel JSON value must be an object')

        return obj

    def encode(self, data):
        return json.dumps(data) if data is not None else ''

    @property
    def content_type(self):
        return 'application/json'


class XMLContext(RequestContext):
    def decode(self, encoded_xml_data):
        try:
            return XMLHelper(encoded_xml_data.decode('utf-8'))
        except Exception:
            raise Problem.bad_request()

    def encode(self, xml):
        return xml.serialize(xml.root)

    @property
    def content_type(self):
        return 'application/xml'
