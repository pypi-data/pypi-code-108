import json

from nehushtan.httpd.NehushtanHTTPConstant import NehushtanHTTPConstant


class NehushtanHTTPResponseBuffer:
    """
    Since 0.4.0
    """

    BODY_DUMP_FORMAT_JSON = 'JSON'

    def __init__(self):
        self.http_code = 200
        self.http_code_message = 'OK'
        self.headers = {}
        self.__body = None
        self.body_dump_format = self.BODY_DUMP_FORMAT_JSON  # JSON, XML (planned only)
        self.encoding = None

    def set_encoding(self, encoding: str):
        self.encoding = encoding
        return self

    def set_http_code(self, code: int, message: str = None):
        self.http_code = code
        self.http_code_message = message
        return self

    def set_header(self, header_name: str, header_value: str):
        self.headers[header_name] = header_value
        return self

    def remove_header(self, header_name: str):
        del self.headers[header_name]
        return self

    def reset_body_as_string(self, init_string: str = ''):
        self.__body = init_string
        return self

    def append_string_to_body(self, appendix: str):
        if type(self.__body) is not str:
            raise TypeError('NehushtanHTTPResponseBuffer.append_string_to_body: body is not str')
        self.__body += appendix
        return self

    def get_body_as_string(self):
        if type(self.__body) is not str:
            if self.body_dump_format == self.BODY_DUMP_FORMAT_JSON:
                return self.get_body_as_json()
            raise TypeError('NehushtanHTTPResponseBuffer.get_body_as_string: body is not str')
        return self.__body

    def reset_body_as_dict(self, init_object: dict = None):
        if init_object is None:
            init_object = {}
        self.__body = init_object
        return self

    def get_body_as_dict(self) -> dict:
        if type(self.__body) is not dict:
            raise TypeError('NehushtanHTTPResponseBuffer.get_body_as_dict: body is not dict')
        return self.__body

    def reset_body_as_list(self, init_list: list = None):
        if init_list is None:
            init_list = []
        self.__body = init_list
        return self

    def get_body_as_list(self) -> list:
        if type(self.__body) is not list:
            raise TypeError('NehushtanHTTPResponseBuffer.get_body_as_list: body is not list')
        return self.__body

    def get_body_as_json(self) -> str:
        return json.dumps(self.__body)

    def refresh_content_length(self):
        s = self.get_body_as_string()
        if self.encoding is not None:
            s.encode(self.encoding)
        else:
            s.encode()
        self.set_header('Content-Length', '%i' % len(s))
        return self

    @staticmethod
    def make_for_redirect(url: str):
        return NehushtanHTTPResponseBuffer().set_http_code(302).set_header('Location', url)

    @staticmethod
    def make_for_json(anything):
        buffer = NehushtanHTTPResponseBuffer() \
            .set_http_code(200) \
            .set_header(NehushtanHTTPConstant.HEADER_CONTENT_TYPE, NehushtanHTTPConstant.HEADER_CONTENT_TYPE_VALUE_JSON)
        buffer.__body = anything
        buffer.refresh_content_length()
        return buffer
