import logging

from aiohttp import web, TCPConnector, ClientSession
from heaserver.service import appproperty, requestproperty
from heaobject.root import json_dumps
from typing import AsyncGenerator
from aiohttp_remotes import XForwardedRelaxed


@web.middleware
async def new_wstl_builder(request: web.Request, handler) -> web.Response:
    wstl_builder_factory = request.app[appproperty.HEA_WSTL_BUILDER_FACTORY]
    request[requestproperty.HEA_WSTL_BUILDER] = wstl_builder_factory()
    response = await handler(request)
    return response


def new_app(testing=False) -> web.Application:
    """
    Creates and returns an aiohttp Application object. Installs middleware that sets the HEA_WSTL_BUILDER request
    property. Assumes that the HEA_WSTL_BUILDER_FACTORY app property has already been set. Unless testing is True, it
    it sets up a global HTTP client and assigns it to the HEA_CLIENT_SESSION application property. If running
    test cases, the HEAAioHTTPTestCase class handles creating and destroying HTTP clients instead.

    :param testing: whether this function was called by a test case implemented with HEAAioHTTPTestCase. Default is
    False.
    :return: the Application property.
    """
    app = web.Application(middlewares=[new_wstl_builder, XForwardedRelaxed().middleware])
    if not testing:
        app.cleanup_ctx.append(_client_session)
    return app


async def _client_session(app: web.Application) -> AsyncGenerator:
    """
    Manages global HTTP client session.
    :param app: the AioHTTP Application object.
    :return: an AsyncGenerator.
    """
    _logger = logging.getLogger(__name__)
    _logger.debug('Starting client session')
    app[appproperty.HEA_CLIENT_SESSION] = ClientSession(connector=TCPConnector(), connector_owner=True,
                                                        json_serialize=json_dumps,
                                                        raise_for_status=True)
    _logger.debug('Client session started')
    yield
    _logger.debug('Closing client session')
    await app[appproperty.HEA_CLIENT_SESSION].close()
