"""
The HEA Keychain provides ...
"""

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.keychain import Credentials
import logging
import copy

_logger = logging.getLogger(__name__)
MONGODB_CREDENTIALS_COLLECTION = 'keychain'


@routes.get('/credentials/{id}')
@action('heaserver-keychain-credentials-get-properties', rel='properties')
@action('heaserver-keychain-credentials-open', rel='opener', path='/credentials/{id}/opener')
@action('heaserver-keychain-credentials-duplicate', rel='duplicator', path='/credentials/{id}/duplicator')
async def get_credentials(request: web.Request) -> web.Response:
    """
    Gets the credentials with the specified id.
    :param request: the HTTP request.
    :return: the requested credentials or Not Found.
    ---
    summary: A specific credentials.
    tags:
        - credentials
    parameters:
        - name: id
          in: path
          required: true
          description: The id of the credentials to retrieve.
          schema:
            type: string
    responses:
      '200':
        description: Expected response to a valid request.
        content:
            application/json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.collection+json:
                schema:
                    type: array
                    items:
                        type: object
            application/vnd.wstl+json:
                schema:
                    type: array
                    items:
                        type: object
      '404':
        $ref: '#/components/responses/404'
    """
    _logger.debug('Requested credentials by id %s' % request.match_info["id"])
    return await mongoservicelib.get(request, MONGODB_CREDENTIALS_COLLECTION)


@routes.get('/credentials/byname/{name}')
async def get_credentials_by_name(request: web.Request) -> web.Response:
    """
    Gets the credentials with the specified id.
    :param request: the HTTP request.
    :return: the requested credentials or Not Found.
    """
    return await mongoservicelib.get_by_name(request, MONGODB_CREDENTIALS_COLLECTION)


@routes.get('/credentials')
@routes.get('/credentials/')
@action('heaserver-keychain-credentials-get-properties', rel='properties')
@action('heaserver-keychain-credentials-open', rel='opener', path='/credentials/{id}/opener')
@action('heaserver-keychain-credentials-duplicate', rel='duplicator', path='/credentials/{id}/duplicator')
async def get_all_credentials(request: web.Request) -> web.Response:
    """
    Gets all credentials.
    :param request: the HTTP request.
    :return: all credentials.
    """
    return await mongoservicelib.get_all(request, MONGODB_CREDENTIALS_COLLECTION)


@routes.get('/credentials/{id}/duplicator')
@action(name='heaserver-keychain-credentials-duplicate-form')
async def get_credentials_duplicate_form(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested credentials.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested credentials was not found.
    """
    return await mongoservicelib.get(request, MONGODB_CREDENTIALS_COLLECTION)


@routes.post('/credentials/duplicator')
async def post_credentials_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided credentials for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_CREDENTIALS_COLLECTION, Credentials)


@routes.post('/credentials')
@routes.post('/credentials/')
async def post_credentials(request: web.Request) -> web.Response:
    """
    Posts the provided credentials.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_CREDENTIALS_COLLECTION, Credentials)


@routes.put('/credentials/{id}')
async def put_credentials(request: web.Request) -> web.Response:
    """
    Updates the credentials with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    """
    return await mongoservicelib.put(request, MONGODB_CREDENTIALS_COLLECTION, Credentials)


@routes.delete('/credentials/{id}')
async def delete_credentials(request: web.Request) -> web.Response:
    """
    Deletes the credentials with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    """
    return await mongoservicelib.delete(request, MONGODB_CREDENTIALS_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='a service for managing laboratory/user credentials',
                           default_port=8080)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
