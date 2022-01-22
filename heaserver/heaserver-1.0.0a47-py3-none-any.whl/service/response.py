"""
This module defines functions that create HTTP responses.
"""
from aiohttp import web, hdrs
from aiohttp.client_exceptions import ClientResponseError
from heaserver.service import requestproperty, appproperty
from heaserver.service.representor import factory as representor_factory
from heaserver.service.representor.representor import Link
from yarl import URL
import logging
from typing import Union, List, Optional, Dict, Any
from .aiohttp import SupportsAsyncRead
from .wstl import RuntimeWeSTLDocumentBuilder


def status_not_found(body: bytes = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 404 and an optional body.
    :param body: the body of the message, typically an explanation of what was not found.
    :return: aiohttp.web.Response with a 404 status code.
    """
    return web.HTTPNotFound(body=body)


def status_multiple_choices(default_url: Union[URL, str], body: bytes = None, content_type: str = 'application/json') -> web.Response:
    """
    Returns a newly created HTTP response object with status code 300. This is for implementing client-side content
    negotiation, described at https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation.
    :param default_url: the URL of the default choice. Required.
    :param body: content with link choices.
    :param content_type: optional content_type (defaults to 'application/json'). Cannot be None.
    :return: aiohttp.web.Response object with a 300 status code.
    """
    return web.HTTPMultipleChoices(str(default_url),
                                   body=body,
                                   headers={hdrs.CONTENT_TYPE: content_type, hdrs.LOCATION: str(default_url if default_url else '#')})


def status_bad_request(body: bytes = None) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 400 and an optional body.
    :param body: the body of the message, typically an explanation of why the request is bad.
    :return: aiohttp.web.Response with a 400 status code.
    """
    return web.HTTPBadRequest(body=body)


def status_created(base_url: Union[URL, str], resource_base: str, inserted_id: str) -> web.Response:
    """
    Returns a newly created HTTP response object with status code 201 and the Location header set.

    :param base_url: the service's base URL (required).
    :param resource_base: the common base path fragment for all resources of this type (required).
    :param inserted_id: the id of the newly created object (required).

    :return: aiohttp.web.Response with a 201 status code and the Location header set to the URL of the created object.
    """
    if inserted_id is None:
        raise ValueError('inserted_id cannot be None')
    return web.HTTPCreated(headers={hdrs.LOCATION: str(URL(base_url) / resource_base / str(inserted_id))})


def status_ok(body: bytes, content_type: str = 'application/json') -> web.Response:
    """
    Returns a newly created HTTP response object with status code 201, the provided Content-Type header, and the
    provided body.
    :param body: the body of the response.
    :param content_type: the content type of the response (default is application/json).
    :return: aiohttp.web.Response object with a 200 status code.
    """
    if content_type is not None:
        return web.HTTPOk(headers={hdrs.CONTENT_TYPE: content_type}, body=body)
    else:
        return web.HTTPOk(body=body)


def status_no_content() -> web.Response:
    """
    Returns a newly created HTTP response object with status code 204.
    :return: aiohttp.web.Response object with a 204 status code.
    """
    return web.HTTPNoContent()


def status_not_acceptable() -> web.Response:
    """
    Returns a newly created HTTP response object with status code 406.
    :return: aiohttp.web.Response object with a 406 status code.
    """
    return web.HTTPNotAcceptable()


def status_internal_error() -> web.Response:
    """
    Returns a newly created HTTP response object with status code 500.
    :return: aiohttp.web.Response object with a 500 status code.
    """
    return web.HTTPInternalServerError()


def status_from_exception(e: ClientResponseError) -> web.Response:
    return web.Response(status=e.status, reason=e.message)


async def get(request: web.Request, data: Optional[Dict[str, Any]]) -> web.Response:
    """
    Create and return a HTTP response object in response to a GET request for one or more HEA desktop object resources.

    :param request: the HTTP request (required).
    :param data: a HEA desktop object dict. May be None if you want no data to be included in the response.
    :return: aiohttp.web.Response object, with status code 200, containing a body with the HEA desktop object, or
    status code 404 if the data argument is None.
    """
    if data:
        return await _handle_get_result(request, data)
    else:
        return web.HTTPNotFound()


async def get_multiple_choices(request: web.Request, result: Union[Dict[str, Any], List[Dict[str, Any]]]) -> web.Response:
    """
    Create and return a HTTP response object in response to a GET request with information about different
    representations that are available for opening the requested HEA desktop object. Unlike the get function, this
    function sets the response's status code to 300 to indicate that is for the purpose of client-side content
    negotiation. More information about content negotiation is available from
    https://developer.mozilla.org/en-US/docs/Web/HTTP/Content_negotiation.

    :param request: the HTTP request (required). If an Accepts header is provided, MIME types that do not support
    links will be ignored.
    :param result: a HEA desktop object dict.
    :return: aiohttp.web.Response object with status code 300, and a body containing the HEA desktop object and links
    representing possible choices for opening the HEA desktop object; status code 404 if no HEA desktop object dict
    was provided; or status code 406 if content negotiation failed to determine an acceptable content type.
    """
    _logger = logging.getLogger(__name__)
    if result is not None:
        wstl_builder: RuntimeWeSTLDocumentBuilder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = result if isinstance(result, list) else [result]
        wstl_builder.href = str(request.url)
        run_time_doc = wstl_builder()
        _logger.debug('Run-time WeSTL document is %s', run_time_doc)

        representor = representor_factory.from_accept_header(request.headers[hdrs.ACCEPT])
        _logger.debug('Using %s output format', representor)
        if representor is None:
            return status_not_acceptable()

        default_url: Optional[Union[URL, str]] = None

        def link_callback(action_index: int, link: Link):
            nonlocal default_url
            if default_url is None or 'default' in link.rel:
                default_url = link.href
        body = await representor.formats(request, run_time_doc, link_callback=link_callback)
        _logger.debug('Response body is %s', body)
        return status_multiple_choices(default_url=default_url if default_url else '#',
                                       body=body,
                                       content_type=representor.MIME_TYPE)
    else:
        return web.HTTPNotFound()


async def get_from_wstl(request: web.Request, run_time_doc: Dict[str, Any]) -> web.Response:
    """
    Handle a get request that returns a run-time WeSTL document. Any actions in the document are added to the
    request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL. The actions
    in the provided run-time document are expected to have a relative href.

    :param request: the HTTP request (required).
    :param run_time_doc: a run-time WeSTL document containing data.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result_from_wstl(request, run_time_doc)


async def get_all_from_wstl(request: web.Request, run_time_docs: List[Dict[str, Any]]) -> web.Response:
    """
    Handle a get all request that returns one or more run-time WeSTL documents. Any actions in the documents are added
    to the request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL. The
    actions in the provided run-time document are expected to have a relative href.

    :param request: the HTTP request (required).
    :param run_time_docs: a list of run-time WeSTL documents containing data.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result_from_wstl(request, run_time_docs)


async def get_all(request: web.Request, data: List[Dict[str, Any]]) -> web.Response:
    """
    Create and return a Response object in response to a GET request for all HEA desktop object resources in a
    collection.

    :param request: the HTTP request (required).
    :param data: a list of HEA desktop object dicts.
    :return: aiohttp.web.Response object with a body containing the object in a JSON array of objects.
    """
    return await _handle_get_result(request, data)


async def get_streaming(request: web.Request, out: SupportsAsyncRead, content_type: str = 'application/json') -> web.StreamResponse:
    """
    Create and return a StreamResponse object in response to a GET request for the content associated with a HEA desktop
    object.

    :param request: the HTTP request (required).
    :param out: a file-like object with an asynchronous read() method (required).
    :param content_type: optional content type.
    :return: aiohttp.web.StreamResponse object with status code 200.
    """
    logger = logging.getLogger(__name__)
    logger.debug('Getting content with content type %s', content_type)
    if content_type is not None:
        response = web.StreamResponse(status=200, reason='OK', headers={hdrs.CONTENT_TYPE: content_type})
    else:
        response = web.StreamResponse(status=200, reason='OK')
    await response.prepare(request)
    flag = True
    try:
        while chunk := await out.read(1024):
            await response.write(chunk)
        out.close()
        flag = False
    finally:
        if flag:
            try:
                out.close()
            except OSError:
                pass

    await response.write_eof()
    return response


async def post(request: web.Request, result: Optional[str], resource_base: str) -> web.Response:
    """
    Create and return a Response object in response to a POST request to create a new HEA desktop object resource.

    :param request: the HTTP request (required).
    :param result: the id of the POST'ed HEA object, or None if the POST failed due to a bad request.
    :param resource_base: the common base path fragment for all resources of this type (required).
    :return: aiohttp.web.Response with Created status code and the URL of the created object, or a Response with a Bad
    Request status code if the result is None.
    """
    if result is not None:
        return await _handle_post_result(request, resource_base, result)
    else:
        return web.HTTPBadRequest()


async def put(result: bool) -> web.Response:
    """
    Handle the result from a put request.

    :param result: whether any objects were updated.
    :return: aiohttp.web.Response object with status code 203 (No Content) or 404 (Not Found).
    """
    if result:
        return web.HTTPNoContent()
    else:
        return web.HTTPNotFound()


async def delete(result: bool) -> web.Response:
    """
    Handle the result from a delete request.

    :param result: whether any objects were deleted.
    :return: aiohttp.web.Response object with status code 203 (No Content) or 404 (Not Found).
    """
    if result:
        return web.HTTPNoContent()
    else:
        return web.HTTPNotFound()


async def _handle_get_result(request: web.Request, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> web.Response:
    """
    Handle the result from a get request. Returns a Response object, the body of which will always contain a list of
    JSON objects.

    :param request: the HTTP request object. Cannot be None.
    :param data: the retrieved HEAObject(s) as a dict or a list of dicts, with each dict representing a
    HEAObject with its attributes as name-value pairs.
    :return: aiohttp.web.Response object, either a 200 status code and the requested JSON object in the body, or status
    code 404 (Not Found).
    """
    if data is not None:
        wstl_builder = request[requestproperty.HEA_WSTL_BUILDER]
        wstl_builder.data = data if isinstance(data, list) else [data]
        wstl_builder.href = str(request.url)
        return await _handle_get_result_from_wstl(request, wstl_builder())
    else:
        return web.HTTPNotFound()


async def _handle_get_result_from_wstl(request: web.Request,
                                       run_time_docs: Union[Dict[str, Any], List[Dict[str, Any]]]) -> web.Response:
    """
    Handle a get or get all request that returns one or more run-time WeSTL documents. Any actions in the documents are
    added to the request's run-time WeSTL documents, and the href of the action is prepended by the service's base URL.
    The actions in the provided run-time documents are expected to have a relative href.

    :param request: the HTTP request object. Cannot be None.
    :param run_time_docs: a list of run-time WeSTL documents containing data
    :return: aiohttp.web.Response object, with a 200 status code and the requested JSON objects in the body,
    status code 406 (Not Acceptable) if content negotiation failed to determine an acceptable content type, or status
    code 404 (Not Found).
    """
    _logger = logging.getLogger(__name__)
    _logger.debug('Run-time WeSTL document is %s', run_time_docs)
    if run_time_docs is not None:
        representor = representor_factory.from_accept_header(request.headers.get(hdrs.ACCEPT, None))
        _logger.debug('Using %s output format', representor)
        if representor is None:
            return status_not_acceptable()
        body = await representor.formats(request, run_time_docs)
        _logger.debug('Response body is %s', body)
        return status_ok(body=body, content_type=representor.MIME_TYPE)
    else:
        return status_not_found()


async def _handle_post_result(request: web.Request, resource_base: str, inserted_id: str) -> web.Response:
    """
    Handle the result from a post request.

    :param request: the HTTP request object (required).
    :param resource_base: the common base path fragment for all resources of this type (required).
    :param inserted_id: the id of the newly created object (required).
    :return: aiohttp.web.Response object with status code 201 (Created).
    """
    return status_created(request.app[appproperty.HEA_COMPONENT], resource_base, inserted_id)
