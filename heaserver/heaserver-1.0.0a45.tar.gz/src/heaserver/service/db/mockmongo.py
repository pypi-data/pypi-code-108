"""Connectivity to a MongoDB database for HEA resources.
"""
import io
import logging
from .mongoexpr import mongo_expr, sub_filter_expr, GETTER_PERMS
from mongoquery import Query
from aiohttp import web
from pymongo.results import UpdateResult, DeleteResult
from motor.motor_asyncio import AsyncIOMotorGridOut
from heaobject.root import DesktopObject
from typing import Dict, Any, Optional, List, IO
from unittest.mock import MagicMock
from copy import deepcopy
from .database import Database
from ..aiohttp import AioHTTPFileLikeObjectWrapper, AsyncReader
import configparser


class MockMongo(Database):

    def __init__(self, app: web.Application, config: configparser.ConfigParser,
                 fixtures: Optional[Dict[str, List[Dict[str, Any]]]] = None,
                 content:  Dict[str, Dict[str, bytes]] = None) -> None:
        """
        Sets the db property of the app context with a motor MongoDB client instance.

        :param app: the aiohttp app object (required).
        :param config: a configparser.ConfigParser object, which should have a MongoDB section with two properties:

                ConnectionString = the MongoDB connection string, default is http://localhost:5432
                Name = the database name, default is heaserver

                If the MongoDB section is missing or config argument is None, the default database name will be heaserver, and
                the default connection string will be http://localhost:27017.
        :param fixtures: data to insert into the mongo database before running each test. Should be a dict of
        collection -> list of objects. Optional.
        :param content: data to insert into GridFS (optional).
        """
        super().__init__(app, config)
        logger = logging.getLogger(__name__)

        self.__fixtures = deepcopy(fixtures) if fixtures else {}
        self.__content = deepcopy(content) if content else {}
        logger.debug('Initialized mockmongo')

    async def get(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None, sub: Optional[str] = None) -> Optional[dict]:
        """
        Gets an object from the database.

        :param request: the aiohttp Request object (required).
        :param collection: the Mongo DB collection (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attribute to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: a HEA name-value pair dict, or None if not found.
        """
        query = Query(mongo_expr(request,
                                 var_parts=var_parts,
                                 mongoattributes=mongoattributes,
                                 extra=sub_filter_expr(sub, permissions=GETTER_PERMS)))
        return deepcopy(next((d for d in self.__fixtures.get(collection, []) if query.match(d)), None))

    async def get_content(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None, sub: str = None) -> Optional[AsyncReader]:
        """
        Handles getting a HEA object's associated content.

        :param request: the HTTP request. Required.
        :param collection: the Mongo collection name. Required.
        :return: a Response with the requested HEA object or Not Found.
        """
        obj = await self.get(request, collection, var_parts, mongoattributes, sub)
        if obj is None:
            return None
        return AsyncReader(deepcopy(self.__content[collection][obj['id']]))

    async def get_all(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None, sub: str = None) -> List[dict]:
        """
        Handle a get request.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attributes to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: an iterator of HEA name-value pair dicts with the results of the mockmongo query.
        """
        query = Query(mongo_expr(request,
                                 var_parts=var_parts,
                                 mongoattributes=mongoattributes,
                                 extra=sub_filter_expr(sub, permissions=GETTER_PERMS)))
        return [deepcopy(d) for d in self.__fixtures.get(collection, []) if query.match(d)]

    async def empty(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                      sub: str = None) -> bool:
        """
        Returns whether there are no results returned from the query.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attributes to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: True or False.
        """
        query = Query(mongo_expr(request,
                                 var_parts=var_parts,
                                 mongoattributes=mongoattributes,
                                 extra=sub_filter_expr(sub, permissions=GETTER_PERMS)))
        return not any(deepcopy(d) for d in self.__fixtures.get(collection, []) if query.match(d))

    async def post(self, request: web.Request, obj: DesktopObject, collection: str, default_content: Optional[IO] = None) -> Optional[str]:
        """
        Handle a post request.

        :param request: the HTTP request (required).
        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :param default_content: the default content to store.
        :return: the generated id of the created object.
        """
        obj.id = '3'  # type: ignore[misc]
        f = self.__fixtures.get(collection, [])
        if obj is None or next((o for o in f if o['id'] == obj.id), None) is not None:
            return None
        else:
            return obj.id

    async def put(self, request: web.Request, obj: DesktopObject, collection: str) -> UpdateResult:
        """
        Handle a put request.

        :param request: the HTTP request (required).
        :param obj: the HEAObject instance to put.
        :param collection: the MongoDB collection containing the requested object (required).
        :return: an object with a matched_count attribute that contains the number of records updated.
        """
        result = MagicMock(type=UpdateResult)
        result.raw_result = None
        result.acknowledged = True
        f = self.__fixtures.get(collection, [])
        result.matched_count = len([o for o in f if request.match_info['id'] == o['id']])
        result.modified_count = len([o for o in f if request.match_info['id'] == o['id']])
        return result

    async def put_content(self, request: web.Request, collection: str) -> Optional[AsyncIOMotorGridOut]:
        """
        Handle a put request of an HEA object's content.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :return: Whether or not it was successful.
        """
        obj = await self.get(request, collection, var_parts=['id'])
        if obj is None:
            return None
        buffer = io.BytesIO()
        input_ = AioHTTPFileLikeObjectWrapper(request.content)
        while chunk := input_.read(1024):
            buffer.write(chunk)
        if buffer.getvalue() != b'The quick brown fox jumps over the lazy dog':
            return None
        return buffer

    async def delete(self, request: web.Request, collection: str) -> DeleteResult:
        """
        Handle a delete request.

        :param request: the HTTP request.
        :param collection: the MongoDB collection containing the requested object (required).
        :return: an object with a deleted_count attribute that contains the number of records deleted.
        """
        f = self.__fixtures.get(collection, [])
        result = MagicMock(type=DeleteResult)
        result.raw_result = None
        result.acknowledged = True
        result.deleted_count = len([o for o in f if request.match_info['id'] == o['id']])
        return result
