"""
The representor package contains modules that transform data between WeSTL and a RESTful API output format, and a
factory for getting an object that outputs in the format with a specified mime type. Each representor module implements
a different output format and implements the following:

(required) MIME_TYPE: the format's mime type.

(optional) async def formats(wstl_obj, coll_url, dumps=json.dumps): formats a run-time WeSTL document into the output
format. This function may not be implemented for input formats that do not support data output.

(optional) async def parses(request): parses an HTTP request into a dict with NVP (name-value
 pair JSON. This function may not be implemented for output formats that do not support data input.

The representor concept comes from:
Amundsen, Mike. RESTful Web Clients. Sebastopol, CA: O'Reilly Media, Inc., 2017.

Use the package as follows:
>>> from heaserver.service.representor import factory
>>> factory.get_representor('application/json')
"""
