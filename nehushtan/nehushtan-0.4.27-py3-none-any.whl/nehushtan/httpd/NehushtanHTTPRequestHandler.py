import json
import re
import socketserver
from abc import abstractmethod
from http.server import BaseHTTPRequestHandler
from typing import Tuple, Union, Sequence, Dict
from urllib.parse import parse_qs

from nehushtan.helper.CommonHelper import CommonHelper
from nehushtan.httpd.NehushtanHTTPConstant import NehushtanHTTPConstant
from nehushtan.httpd.NehushtanHTTPResponseBuffer import NehushtanHTTPResponseBuffer
from nehushtan.httpd.exceptions.NehushtanHTTPError import NehushtanHTTPError
from nehushtan.httpd.exceptions.NehushtanRequestDeniedByFilterError import NehushtanRequestDeniedByFilterError
from nehushtan.httpd.exceptions.NehushtanRequestProcessTargetError import NehushtanRequestProcessTargetError


class NehushtanHTTPRequestHandler(BaseHTTPRequestHandler):
    """
    Since 0.4.0
    """

    def __init__(self, request: bytes, client_address: Tuple[str, int], server: socketserver.BaseServer):
        # fulfilled by calling method `parse_path`
        self.parsed_path = '/'
        self.parsed_query_dict = {}
        self.parsed_cookie_dict = {}
        # fulfilled by calling method `parse_body`
        self.raw_body = b''
        self.parsed_body_data = None
        # fulfilled after do_SPAM
        self.method = ''
        # Router Matched Data
        self.matched_arguments: Sequence[str] = []
        self.matched_keyed_arguments: Dict[str, str] = {}

        # self.__process_chain_base_class = CommonHelper.class_with_class_path(
        #     'nehushtan.httpd.NehushtanHTTPRequestProcessChain'
        # )
        self.__filter_base_class = CommonHelper.class_with_class_path(
            'nehushtan.httpd.NehushtanHTTPRequestFilter'
        )
        self.__controller_base_class = CommonHelper.class_with_class_path(
            'nehushtan.httpd.NehushtanHTTPRequestController'
        )
        self.__process_chain_share_data_dict = {}

        super().__init__(request, client_address, server)

    def get_process_chain_share_data_dict(self):
        return self.__process_chain_share_data_dict

    def prepare_path_and_queries(self):
        # self.path is like path=/ab/c/d?e=f
        parts = self.path.split('?')
        self.parsed_path = parts[0]
        if len(parts) > 1:
            parsed_query_dict = parse_qs(parts[1])
            for k, v in parsed_query_dict.items():
                if k.endswith('[]'):
                    self.parsed_query_dict[k.removesuffix('[]')] = v
                elif len(v) == 1:
                    self.parsed_query_dict[k] = v[0]
                else:
                    self.parsed_query_dict[k] = v

    def prepare_cookie(self):
        # cookie
        cookie = self.headers.get('Cookie', '')
        if cookie == '':
            return
        pairs = cookie.split(";")
        for pair in pairs:
            pair = pair.lstrip()
            if pair == '':
                continue
            parts = pair.split("=", 2)
            if len(parts) != 2:
                continue
            name = parts[0].encode('latin-1').decode('utf-8')
            value = parts[1].encode('latin-1').decode('utf-8')
            self.parsed_cookie_dict[name] = value

    def prepare_body(self, body_charset=None):
        length = int(self.headers.get('content-length', 0))
        self.raw_body = self.rfile.read(length)
        print(self.raw_body)

        content_type = self.headers.get('content-type', 'text/plain')
        print(content_type)

        if body_charset is None:
            found_charset = re.search(r'charset=(.+);?', content_type, re.I)
            if found_charset:
                body_charset = found_charset.group(1)
            else:
                body_charset = 'utf-8'

        print(body_charset)
        self.raw_body = self.raw_body.decode(body_charset)
        print(self.raw_body)

        if content_type.startswith('application/x-www-form-urlencoded'):
            parsed_body_dict = parse_qs(self.raw_body)
            self.parsed_body_data = {}
            for k, v in parsed_body_dict.items():
                if k.endswith('[]'):
                    self.parsed_body_data[k.removesuffix('[]')] = v
                elif len(v) == 1:
                    self.parsed_body_data[k] = v[0]
                else:
                    self.parsed_body_data[k] = v
        elif content_type.startswith('application/json'):
            self.parsed_body_data = json.loads(self.raw_body)
        elif content_type.startswith('multipart/form-data'):
            # TODO for multipart/form-data; boundary=something
            raise NotImplementedError('BODY for FORM multipart/form-data IS NOT IMPLEMENTED')
        else:
            self.parsed_body_data = None

        print(self.parsed_body_data, self.parsed_body_data.get('a', 'c'))

    def do_HEAD(self):
        """
        The HTTP HEAD method requests the headers
            that would be returned if the HEAD request's URL was instead requested with the HTTP GET method.
        For example, if a URL might produce a large download,
            a HEAD request could read its Content-Length header
            to check the filesize without actually downloading the file.

        Request has body	No
        Successful response has body	No
        """
        self.method = NehushtanHTTPConstant.METHOD_HEAD
        self.process_request()

    def do_GET(self):
        """
        Request has body	No
        Successful response has body	Yes
        """
        self.method = NehushtanHTTPConstant.METHOD_GET
        self.process_request()

    def do_POST(self):
        """
        @see https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods/POST

        The HTTP POST method sends data to the server.
        The type of the body of the request is indicated by the Content-Type header.

        The difference between PUT and POST is that PUT is idempotent:
            calling it once or several times successively has the same effect (that is no side effect),
            where successive identical POST may have additional effects, like passing an order several times.

        A POST request is typically sent via an HTML form and results in a change on the server.
        In this case, the content type is selected by putting the adequate string
            in the enctype attribute of the <form> element
            or the formenctype attribute of the <input> or <button> elements:

        - application/x-www-form-urlencoded:
            the keys and values are encoded in key-value tuples separated by '&',
            with a '=' between the key and the value.
            Non-alphanumeric characters in both keys and values are percent encoded:
                this is the reason why this type is not suitable to use with binary data
                (use multipart/form-data instead)
        - multipart/form-data:
            each value is sent as a block of data ("body part"),
            with a user agent-defined delimiter ("boundary") separating each part.
            The keys are given in the Content-Disposition header of each part.
        - text/plain

        When the POST request is sent via a method other than an HTML form
            — like via an XMLHttpRequest —
            the body can take any type.
        As described in the HTTP 1.1 specification,
            POST is designed to allow a uniform method to cover the following functions:

        - Annotation of existing resources
        - Posting a message to a bulletin board, newsgroup, mailing list, or similar group of articles;
        - Adding a new user through a signup modal;
        - Providing a block of data, such as the result of submitting a form, to a data-handling process;
        - Extending a database through an append operation.

        Request has body	Yes
        Successful response has body	Yes
        """
        self.method = NehushtanHTTPConstant.METHOD_POST
        self.process_request()

    def do_PUT(self):
        """
        The HTTP PUT request method creates a new resource
            or replaces a representation of the target resource with the request payload.

        The difference between PUT and POST is that PUT is idempotent:
            calling it once or several times successively has the same effect (that is no side effect),
            whereas successive identical POST requests may have additional effects,
            akin to placing an order several times.

        Request has body	Yes
        Successful response has body	No
        """
        self.method = NehushtanHTTPConstant.METHOD_PUT
        self.process_request()

    def do_DELETE(self):
        """
        The HTTP DELETE request method deletes the specified resource.
        Request has body	May
        Successful response has body	May
        """
        self.method = NehushtanHTTPConstant.METHOD_DELETE
        self.process_request()

    def do_OPTIONS(self):
        """
        The HTTP OPTIONS method requests permitted communication options for a given URL or server.
        A client can specify a URL with this method, or an asterisk (*) to refer to the entire server.

        Request has body	No
        Successful response has body	Yes
        """
        self.method = NehushtanHTTPConstant.METHOD_OPTIONS
        self.process_request()

    def do_PATCH(self):
        """
        The HTTP PATCH request method applies partial modifications to a resource.

        PATCH is somewhat analogous to the "update" concept found in CRUD
            (in general, HTTP is different than CRUD, and the two should not be confused).

        A PATCH request is considered a set of instructions on how to modify a resource.
        Contrast this with PUT; which is a complete representation of a resource.

        A PATCH is not necessarily idempotent, although it can be. Contrast this with PUT;
            which is always idempotent.
        The word "idempotent" means that any number of repeated,
            identical requests will leave the resource in the same state.
        For example if an auto-incrementing counter field is an integral part of the resource,
            then a PUT will naturally overwrite it (since it overwrites everything),
            but not necessarily so for PATCH.

        PATCH (like POST) may have side-effects on other resources.

        To find out whether a server supports PATCH,
            a server can advertise its support by adding it to the list
            in the Allow or Access-Control-Allow-Methods (for CORS) response headers.

        Another (implicit) indication that PATCH is allowed,
            is the presence of the Accept-Patch header,
            which specifies the patch document formats accepted by the server.

        Request has body	Yes
        Successful response has body	Yes
        """
        self.method = NehushtanHTTPConstant.METHOD_PATCH
        self.process_request()

    def process_request(self):
        try:
            self.prepare_path_and_queries()
            self.prepare_cookie()

            filters, controller_and_method = self.seek_route_for_process_chains(self.method, self.parsed_path)

            methods_contains_body = (
                NehushtanHTTPConstant.METHOD_POST,
                NehushtanHTTPConstant.METHOD_PUT,
                NehushtanHTTPConstant.METHOD_DELETE,
                NehushtanHTTPConstant.METHOD_PATCH,
            )
            if methods_contains_body.__contains__(self.method):
                self.prepare_body()

            filter_data_dict = {}
            for filter_item in filters:
                c = filter_item
                if type(c) is str:
                    c = CommonHelper.class_with_class_path(c)
                if not issubclass(c, self.__filter_base_class):
                    raise NehushtanRequestProcessTargetError(
                        http_error_message=f'Filter Class Error: {filter_item}',
                        http_code=500
                    )
                filter_instance = c(self, filter_data_dict)
                if not filter_instance.should_accept_request():
                    raise NehushtanRequestDeniedByFilterError(
                        filter_item,
                        filter_instance.message_for_denial,
                        filter_instance.http_code_for_denial
                    )

            controller_item = controller_and_method[0]
            method_item = controller_and_method[1]

            c = controller_item
            if type(c) is str:
                c = CommonHelper.class_with_class_path(c)
            if not issubclass(c, self.__controller_base_class):
                raise NehushtanRequestProcessTargetError(
                    http_error_message=f'Controller Class Error for {controller_item}',
                    http_code=500
                )
            controller_instance = c(self)
            controller_instance_target_method = getattr(controller_instance, method_item)

            args = self.matched_arguments
            kwargs = self.matched_keyed_arguments
            controller_instance_target_method(*args, **kwargs)

        except NehushtanHTTPError as http_error:
            self.send_error(http_error.get_http_code(), http_error.http_error_message)
            self.wfile.write(http_error.get_http_error_message().encode())

    @abstractmethod
    def seek_route_for_process_chains(self, method: str, path: str) \
            -> Tuple[Sequence[Union[type, str]], Tuple[Union[type, str], str]]:
        """
        You may need to update `self.matched_arguments` or `self.matched_keyed_arguments` here.
        It would return the filter list and the controller-method pair.
        """
        pass

    def send_response_with_buffer(self, buffer: NehushtanHTTPResponseBuffer):
        if buffer.http_code < 200 or buffer.http_code >= 400:
            self.send_error(buffer.http_code, buffer.http_code_message)
            return self

        self.send_response(buffer.http_code, buffer.http_code_message)

        text = buffer.get_body_as_string()

        if buffer.encoding is not None:
            s = text.encode(buffer.encoding)
        else:
            s = text.encode()

        buffer.set_header('Content-Length', '%i' % len(s))

        for k, v in buffer.headers.items():
            self.send_header(k, v)
        self.end_headers()

        self.wfile.write(s)
