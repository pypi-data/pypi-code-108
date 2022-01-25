"""
Incoming REST calls can be sent here to be converted back into dslibrary calls.
"""
import json
import typing
import urllib.parse

from dslibrary import DSLibrary


class RequestInfo(object):
    """
    Use this class to describe the incoming request.
    """
    def __init__(self, method: str, path: str, post_data: (bytes, bytearray)=None, headers: dict=None):
        self.method = method.lower()
        if not path.startswith("/"):
            path = "/" + path
        if "?" in path:
            path, query = path.split("?", maxsplit=1)
        else:
            query = ""
        self.path = path
        query_args = urllib.parse.parse_qs(query, keep_blank_values=True, encoding="utf-8", errors="ignore")
        self.query_args = {k: "" if len(v) == 0 else v[0] for k, v in query_args.items()}
        self.post_data = post_data
        self.headers = {k.lower(): v for k, v in (headers or {}).items()}


class ResponseInfo(object):
    """
    An instance of this class describes a response.
    """
    def __init__(self, content: (bytes, bytearray, str, typing.IO, dict, list, tuple), headers: dict=None, status_code: int=200):
        self.content = content
        self.headers = headers or {}
        self.status_code = status_code

    def close(self):
        if hasattr(self.content, "close"):
            self.content.close()


class HttpToDsl(object):
    """
    An instance of this class translates requests into actions against 'target', and returns responses.

    Structure of a REST service:
      * receive all requests to a particular path
      * do authentication, i.e. by checking HTTP headers for a token or credentials
      * do any other needed processing of the HTTP headers, which might supply other important context
      * turn the inbound request into a RequestInfo() object
      * call the translate() method
      * send a response based on the returnedResponseInfo() object
      * call the close() method of the response object
    """
    def __init__(self, target: DSLibrary, base_path: str=""):
        self.target = target
        self.base_path = "/" + base_path.strip("/")
        if not self.base_path.endswith("/"):
            self.base_path += "/"

    @staticmethod
    def err_400(message: str):
        return ResponseInfo(f"bad request: {message}", status_code=404)

    @staticmethod
    def err_404():
        return ResponseInfo("not found", status_code=404)

    @staticmethod
    def ok():
        return ResponseInfo({})

    def translate(self, request: RequestInfo) -> ResponseInfo:
        """
        Main entry point for translation of HTTP requests.
        """
        if not request.path.startswith(self.base_path):
            return self.err_404()
        path = request.path[len(self.base_path):]
        path_parts = path.strip("/").split("/")
        method_name = f"_{request.method}_{path_parts[0]}"
        if not hasattr(self, method_name):
            return self.err_404()
        return getattr(self, method_name)(request)

    def _get_context(self, request: RequestInfo) -> ResponseInfo:
        """
        Get all the constant elements of our target: parameters, metadata, etc..
        """
        ctx = {
            "uri": self.target.get_uri(),
            "metadata": self.target.get_metadata().to_json(),
            "parameters": self.target.get_parameters()
        }
        return ResponseInfo(content=ctx, headers={"Content-Type": "application/json"})

    def _read_resources(self, request: RequestInfo, open_method: typing.Callable, name: str) -> ResponseInfo:
        # TODO use headers instead of arg for byte range
        byte_range = json.loads(request.query_args.get("byte_range") or 'null')
        with open_method(name, mode='rb') as f_r:
            if byte_range:
                f_r.seek(byte_range[0])
                content = f_r.read(byte_range[1] - byte_range[0])
            else:
                content = f_r.read()
        return ResponseInfo(content, {"Content-Type": "application/octet-stream"})

    def _write_resources(self, request: RequestInfo, open_method: typing.Callable, name: str) -> ResponseInfo:
        append = request.query_args.get("append")
        with open_method(name, mode='ab' if append else 'wb') as f_w:
            f_w.write(request.post_data)
        return self.ok()

    def _get_resources(self, request: RequestInfo) -> ResponseInfo:
        """
        Read part of a resource.
        """
        resource_name = request.query_args.get("resource_name")
        if not resource_name:
            return self.err_400("missing 'resource_name'")
        return self._read_resources(request, open_method=self.target.open_resource, name=resource_name)

    def _put_resources(self, request: RequestInfo) -> ResponseInfo:
        """
        Write or append to a resource.
        """
        resource_name = request.query_args.get("resource_name")
        if not resource_name:
            return self.err_400("missing 'resource_name'")
        return self._write_resources(request, open_method=self.target.open_resource, name=resource_name)

    def _get_run_data(self, request: RequestInfo) -> ResponseInfo:
        """
        Read run data.
        """
        resource_name = request.query_args.get("resource_name")
        if not resource_name:
            return self.err_400("missing 'resource_name'")
        return self._read_resources(request, open_method=self.target.open_run_data, name=resource_name)

    def _put_run_data(self, request: RequestInfo) -> ResponseInfo:
        """
        Write run data.
        """
        resource_name = request.query_args.get("resource_name")
        if not resource_name:
            return self.err_400("missing 'resource_name'")
        return self._write_resources(request, open_method=self.target.open_run_data, name=resource_name)

    def _get_model_binary(self, request: RequestInfo) -> ResponseInfo:
        """
        Read model binary file(s).
        """
        part = request.query_args.get("part")
        return self._read_resources(request, open_method=self.target.open_model_binary, name=part)

    def _put_model_binary(self, request: RequestInfo) -> ResponseInfo:
        """
        Write mode binary data.
        """
        part = request.query_args.get("part")
        return self._write_resources(request, open_method=self.target.open_model_binary, name=part)

    def _get_db(self, request: RequestInfo) -> ResponseInfo:
        """
        Read chunk of SQL results.
        """
        # TODO see data_access code

    def _post_db(self, request: RequestInfo) -> ResponseInfo:
        """
        Execute SQL.
        """
        # TODO see data_access code


    # TODO scoring-requests
    # TODO score
    # TODO filesystem functions

    # TODO Not implemented yet in to_rest:
    #   - nosql, filesystem


def tornado_to_dslibrary(target: DSLibrary, verifier: typing.Callable=None):
    """
    Generate a Tornado app that proxies data requests to a DSLibrary instance.

    This shortens creation of a data service endpoint to the following:
        app = tornado_to_dslibrary(target)
        app.listen(port)
        tornado.ioloop.IOLoop.current().start()

    :param target:   Data handler.
    :param verifier: Checks every request for validity, i.e. ensuring it has a valid access token.  It is passed a
        RequestInfo instance, and can return a DSLibrary instance.  It should raise a tornado.web.* exception if
        the authorization is incorrect.
    :return:    Tornado app object.
    """
    import tornado.web
    to_dsl = HttpToDsl(target)
    class MainHandler(tornado.web.RequestHandler):
        def run(self, rqst: RequestInfo):
            to_dsl = None
            if verifier:
                alt_dsl = verifier(rqst)
                if alt_dsl:
                    to_dsl = HttpToDsl(alt_dsl)
            try:
                resp = to_dsl.translate(rqst)
                for k, v in resp.headers.items():
                    self.set_header(k, v)
                self.write(resp.content)
            except Exception as err:
                raise tornado.web.HTTPError(500, f"Internal error: {err}")

        def _common(self):
            path = self.request.path
            if self.request.query:
                path += "?" + self.request.query
            return {
                "path": path, "headers": self.request.headers
            }

        async def get(self):
            rqst = RequestInfo(
                method="get", **self._common()
            )
            return self.run(rqst)

        async def post(self):
            rqst = RequestInfo(
                method="post", **self._common(), post_data=self.request.body
            )
            return self.run(rqst)

        async def put(self):
            rqst = RequestInfo(
                method="put", **self._common(), post_data=self.request.body
            )
            return self.run(rqst)

        async def delete(self):
            rqst = RequestInfo(
                method="delete", **self._common()
            )
            return self.run(rqst)

    return tornado.web.Application([
        (r"/.*", MainHandler),
    ])
