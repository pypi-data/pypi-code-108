"""
Nozomi
Request Data Module
author: hugh@blinkybeach.com
"""
from nozomi.http.parseable_data import ParseableData
from nozomi.http.headers import Headers
from nozomi.http.status_code import HTTPStatusCode
from nozomi.errors.bad_request import BadRequest
from nozomi.errors.error import NozomiError
from nozomi.data.xml import XML
import json


class RequestBody(ParseableData):

    def __init__(
        self,
        headers: Headers,
        request_body: bytes,
        max_content_length: int = 10000
    ) -> None:

        length = headers.value_for('content-length')
        if length is None:
            raise BadRequest('No content-length header found in your request.')

        try:
            content_length = int(length)
        except ValueError:
            raise BadRequest('Invalid content-length header value')

        if content_length > max_content_length:
            raise NozomiError('Content too large, max: {s}'.format(
                s=str(max_content_length)
            ), HTTPStatusCode.PAYLOAD_TOO_LARGE.value)

        try:
            string_data = request_body.decode('utf-8')
        except Exception:
            raise BadRequest('Unable to decode the body of your request with t\
he UTF-8 character set. UTF-8 required.')

        content_type = headers.value_for('content-type')
        if content_type is None:
            raise BadRequest('Could not find a content-type header in your req\
uest.')

        try:
            content_type_value = content_type.lower().split(';')[0]
        except Exception:
            raise BadRequest('Unable to parse your request\'s content-type hea\
der.')

        if content_type_value == 'application/json':
            try:
                json_data = json.loads(string_data)
            except Exception:
                raise BadRequest('Unable to parse your request body as json. P\
lease check the syntax of your request body.')
            return super().__init__(raw=json_data)

        if content_type_value == 'application/xml':
            try:
                xml_data = XML.xmlstring_to_data(string_data)
            except Exception:
                raise BadRequest('Unable to parse your request body as xml. Pl\
ease check the syntax of your request body.')
            return super().__init__(raw=xml_data)

        raise BadRequest('Invalid content type. Valid content types are applic\
ation/json and application/xml only.')
