"""
The HEA Registry Service provides a table of all currently active HEA microservices. Microservices each have an unique
component name field, and the name may be used to get other information about the microservice including its base URL
to make REST API calls.
"""

from heaserver.service import response, appproperty
from heaserver.service.runner import init_cmd_line, routes, start, web
from heaserver.service.db import mongo, mongoservicelib
from heaserver.service.wstl import builder_factory, action
from heaobject.registry import Component, Property
from heaobject.volume import DEFAULT_FILE_SYSTEM

MONGODB_COMPONENT_COLLECTION = 'components'

MONGODB_PROPERTIES_COLLECTION = 'properties'


@routes.get('/components/{id}')
@action('heaserver-registry-component-get-properties', rel='properties')
@action('heaserver-registry-component-duplicate', rel='duplicator', path='/components/{id}/duplicator')
async def get_component(request: web.Request) -> web.Response:
    """
    Gets the component with the specified id.
    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by id.
    tags:
        - heaserver-registry-get-component
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/byname/{name}')
async def get_component_by_name(request: web.Request) -> web.Response:
    """
    Gets the component with the specified id.
    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by name.
    tags:
        - heaserver-registry-get-component-by-name
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/bytype/{type}')
@routes.get('/components/bytype/{type}/byfilesystemname/{filesystemname}')
async def get_component_by_type(request: web.Request) -> web.Response:
    """
    Gets the component that serves resources of the specified HEA object type.
    :param request: the HTTP request.
    :return: the requested component or Not Found.
    ---
    summary: A specific component, by type and file system.
    tags:
        - heaserver-registry-get-component-by-type-and-file-system
    parameters:
        - name: type
          in: path
          required: true
          description: The type of the component to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A component type
              value: heaobject.folder.Folder
        - name: filesystemname
          in: path
          required: true
          description: The file system of the component to retrieve.
          schema:
            type: string
          examples:
            example:
              summary: A component type
              value: DEFAULT_FILE_SYSTEM
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    if 'filesystemname' in request.match_info:
        file_system_name = request.match_info['filesystemname']
    else:
        file_system_name = DEFAULT_FILE_SYSTEM
    result = await request.app[appproperty.HEA_DB].get(request,
                                                       MONGODB_COMPONENT_COLLECTION,
                                                       mongoattributes={'resources': {
                                                           '$elemMatch': {
                                                               'resource_type_name': {'$eq': request.match_info['type']},
                                                               'file_system_name': {'$eq': file_system_name}
                                                           }}})
    return await response.get(request, result)


@routes.get('/components')
@routes.get('/components/')
@action('heaserver-registry-component-get-properties', rel='properties')
@action('heaserver-registry-component-duplicate', rel='duplicator', path='/components/{id}/duplicator')
async def get_all_components(request: web.Request) -> web.Response:
    """
    Gets all components.
    :param request: the HTTP request.
    :return: all components.
    ---
    summary: All components.
    tags:
        - heaserver-registry-get-all-components
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/components/{id}/duplicator')
@action(name='heaserver-registry-component-duplicate-form')
async def get_component_duplicator(request: web.Request) -> web.Response:
    """
    Gets a form template for duplicating the requested component.

    :param request: the HTTP request. Required.
    :return: the requested form, or Not Found if the requested component was not found.
    """
    return await mongoservicelib.get(request, MONGODB_COMPONENT_COLLECTION)


@routes.post('/components/duplicator')
async def post_component_duplicator(request: web.Request) -> web.Response:
    """
    Posts the provided component for duplication.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the
    """
    return await mongoservicelib.post(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.post('/components')
@routes.post('/components/')
async def post_component(request: web.Request) -> web.Response:
    """
    Posts the provided component.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Component creation
    tags:
        - heaserver-registry-post-component
    requestBody:
      description: A new component object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Joe"
                  },
                  {
                    "name": "invited",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "joe"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "base_url",
                    "value": "http://localhost/foo"
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "resource_type_name",
                    "value": "heaobject.folder.Folder",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "type",
                    "value": "heaobject.registry.Resource",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "base_path",
                    "value": "/folders"
                  },
                  {
                   "section": "resources",
                    "index": 0,
                    "name": "file_system_name",
                    "value": "DEFAULT_MONGODB"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Joe",
                "invited": [],
                "modified": null,
                "name": "joe",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.registry.Component",
                "version": null,
                "base_url": "http://localhost/foo",
                "resources": [{
                    "type": "heaobject.registry.Resource",
                    "resource_type_name": "heaobject.folder.Folder",
                    "base_path": "/folders",
                    "file_system_name": "DEFAULT_MONGODB"
                }]
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.put('/components/{id}')
async def put_component(request: web.Request) -> web.Response:
    """
    Updates the component with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Component updates
    tags:
        - heaserver-registry-put-component
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated component object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "template": {
                  "data": [{
                    "name": "created",
                    "value": null
                  },
                  {
                    "name": "derived_by",
                    "value": null
                  },
                  {
                    "name": "derived_from",
                    "value": []
                  },
                  {
                    "name": "description",
                    "value": null
                  },
                  {
                    "name": "display_name",
                    "value": "Reximus Max"
                  },
                  {
                    "name": "invited",
                    "value": []
                  },
                  {
                    "name": "modified",
                    "value": null
                  },
                  {
                    "name": "name",
                    "value": "reximus"
                  },
                  {
                    "name": "owner",
                    "value": "system|none"
                  },
                  {
                    "name": "shared_with",
                    "value": []
                  },
                  {
                    "name": "source",
                    "value": null
                  },
                  {
                    "name": "version",
                    "value": null
                  },
                  {
                    "name": "base_url",
                    "value": "http://localhost/foo"
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "resource_type_name",
                    "value": "heaobject.folder.Folder",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "type",
                    "value": "heaobject.registry.Resource",
                  },
                  {
                    "section": "resources",
                    "index": 0,
                    "name": "base_path",
                    "value": "/folders"
                  },
                  {
                   "section": "resources",
                    "index": 0,
                    "name": "file_system_name",
                    "value": "DEFAULT_MONGODB"
                  },
                  {
                  "name": "id",
                  "value": "666f6f2d6261722d71757578"
                  }]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Component example
              value: {
                "id": "666f6f2d6261722d71757578",
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Reximus Max",
                "invited": [],
                "modified": null,
                "name": "reximus",
                "owner": "system|none",
                "shared_with": [],
                "source": null,
                "type": "heaobject.registry.Component",
                "version": null,
                "base_url": "http://localhost/foo",
                "resources": [{
                    "type": "heaobject.registry.Resource",
                    "resource_type_name": "heaobject.folder.Folder",
                    "base_path": "/folders",
                    "file_system_name": "DEFAULT_MONGODB"
                }]
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_COMPONENT_COLLECTION, Component)


@routes.delete('/components/{id}')
async def delete_component(request: web.Request) -> web.Response:
    """
    Deletes the component with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Component deletion
    tags:
        - heaserver-registry-delete-component
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_COMPONENT_COLLECTION)


@routes.get('/properties/{id}')
async def get_property(request: web.Request) -> web.Response:
    """
    Gets the property with the specified id.
    :param request: the HTTP request.
    :return: the requested property or Not Found.
    ---
    summary: A specific property, by id.
    tags:
        - heaserver-registry-get-property
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get(request, MONGODB_PROPERTIES_COLLECTION)


@routes.get('/properties/byname/{name}')
async def get_property_by_name(request: web.Request) -> web.Response:
    """
    Gets the property with the specified id.
    :param request: the HTTP request.
    :return: the requested property or Not Found.
    ---
    summary: A specific property, by name.
    tags:
        - heaserver-registry-get-property-by-name
    parameters:
        - $ref: '#/components/parameters/name'
    responses:
      '200':
        $ref: '#/components/responses/200'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.get_by_name(request, MONGODB_PROPERTIES_COLLECTION)


@routes.get('/properties')
@routes.get('/properties/')
async def get_all_properties(request: web.Request) -> web.Response:
    """
    Gets all properties.
    :param request: the HTTP request.
    :return: all properties.
    ---
    summary: All properties.
    tags:
        - heaserver-registry-get-all-properties
    responses:
      '200':
        $ref: '#/components/responses/200'
    """
    return await mongoservicelib.get_all(request, MONGODB_PROPERTIES_COLLECTION)


@routes.post('/properties')
@routes.post('/properties/')
async def post_property(request: web.Request) -> web.Response:
    """
    Posts the provided property.
    :param request: the HTTP request.
    :return: a Response object with a status of Created and the object's URI in the Location header.
    ---
    summary: Property creation
    tags:
        - heaserver-registry-post-property
    requestBody:
      description: A new property object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: Property example
              value: {
                "template": {
                  "data": [
                    {"name": "name", "value": "HEA"}
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: Property example
              value: {
                "name": "applicationName",
                "value": "HEA"
              }
    responses:
      '201':
        $ref: '#/components/responses/201'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.post(request, MONGODB_PROPERTIES_COLLECTION, Property)


@routes.put('/properties/{id}')
async def put_property(request: web.Request) -> web.Response:
    """
    Updates the property with the specified id.
    :param request: the HTTP request.
    :return: a Response object with a status of No Content or Not Found.
    ---
    summary: Property updates
    tags:
        - heaserver-registry-put-property
    parameters:
        - $ref: '#/components/parameters/id'
    requestBody:
      description: An updated property object.
      required: true
      content:
        application/vnd.collection+json:
          schema:
            type: object
          examples:
            example:
              summary: A property example
              value: {
                "template": {
                  "data": [
                    {
                      "name": "name",
                      "value": "HEA"
                    },
                    {
                      "name": "created",
                      "value": null
                    },
                    {
                      "name": "derived_by",
                      "value": null
                    },
                    {
                      "name": "derived_from",
                      "value": []
                    },
                    {
                      "name": "description",
                      "value": null
                    },
                    {
                      "name": "display_name",
                      "value": "Reximus"
                    },
                    {
                      "name": "invited",
                      "value": []
                    },
                    {
                      "name": "modified",
                      "value": null
                    },
                    {
                      "name": "owner",
                      "value": "system|none"
                    },
                    {
                      "name": "shared_with",
                      "value": []
                    },
                    {
                      "name": "source",
                      "value": null
                    },
                    {
                      "name": "version",
                      "value": null
                    },
                    {
                      "name": "base_url",
                      "value": "http://localhost/foo"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "resource_type_name",
                      "value": "heaobject.folder.Folder"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "base_path",
                      "value": "/folders"
                    },
                    {
                      "section": "resources",
                      "index": 0,
                      "name": "file_system_name",
                      "value": "DEFAULT_MONGODB"
                    },
                    {
                      "name": "id",
                      "value": "666f6f2d6261722d71757578"
                    }
                  ]
                }
              }
        application/json:
          schema:
            type: object
          examples:
            example:
              summary: A property example
              value: {
                "created": null,
                "derived_by": null,
                "derived_from": [],
                "description": null,
                "display_name": "Untitled Property",
                "id": "618da15104811d77ca7221fd",
                "invites": [],
                "modified": null,
                "name": "applicationName",
                "owner": "system|none",
                "shares": [],
                "source": null,
                "type": "heaobject.registry.Property",
                "value": "HEA",
                "version": null
              }
    responses:
      '204':
        $ref: '#/components/responses/204'
      '400':
        $ref: '#/components/responses/400'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.put(request, MONGODB_PROPERTIES_COLLECTION, Property)


@routes.delete('/properties/{id}')
async def delete_property(request: web.Request) -> web.Response:
    """
    Deletes the property with the specified id.
    :param request: the HTTP request.
    :return: No Content or Not Found.
    ---
    summary: Property deletion
    tags:
        - heaserver-registry-delete-property
    parameters:
        - $ref: '#/components/parameters/id'
    responses:
      '204':
        $ref: '#/components/responses/204'
      '404':
        $ref: '#/components/responses/404'
    """
    return await mongoservicelib.delete(request, MONGODB_PROPERTIES_COLLECTION)


def main() -> None:
    config = init_cmd_line(description='Registry of HEA services, HEA web clients, and other web sites of interest',
                           default_port=8080)
    start(db=mongo.Mongo, wstl_builder_factory=builder_factory(__package__), config=config)
