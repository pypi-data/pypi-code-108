"""Connectivity to a MongoDB database for HEA resources.

A MongoDB collection name may only be used by one microservice in a database instance. In addition, for microservices
with content, the collections <collection_name>.files and <collection_name>.chunks will be used for storing the
content. The following collection names are used by existing HEA microservices and are reserved:

folders
folder_items
data_adapters
components
properties
volumes
organizations
"""

from motor import motor_asyncio
from aiohttp import web
from .mongoexpr import mongo_expr, sub_filter_expr, GETTER_PERMS
from ..aiohttp import AioHTTPFileLikeObjectWrapper
import bson
import pymongo
from bson.codec_options import CodecOptions
import logging
import configparser
from typing import Optional, List, Dict, Any, IO
from heaobject import user, root
from pymongo.results import UpdateResult, DeleteResult
from .database import Database
from yarl import URL
from motor.motor_asyncio import AsyncIOMotorGridFSBucket
from ..response import SupportsAsyncRead
from gridfs.errors import NoFile
from bson import ObjectId

_codec_options = CodecOptions(tz_aware=True)


class Mongo(Database):
    """
    Connectivity to a MongoDB database for HEA resources.
    """
    def __init__(self, app: web.Application, config: Optional[configparser.ConfigParser],
                 connection_string: Optional[str] = None,
                 username: Optional[str] = None,
                 password: Optional[str] = None,
                 database_name: Optional[str] = None) -> None:
        """
        Performs initialization.

        :param app: the aiohttp app object (required).
        :param config: a configparser.ConfigParser object, which should have a MongoDB section with two properties:

                ConnectionString = the MongoDB connection string, default is http://localhost:5432
                Name = the database name, default is heaserver

                If the MongoDB section is missing or config argument is None, the default database name will be heaserver, and
                the default connection string will be http://localhost:27017.
        :param connection_string: an optional MongoDB connection string that will override any database connection
        string in a provided config file.
        :param username: an optional user name that will override any user name in the connection string.
        :param password: an optional password that will override any password in the connection string.
        :param database_name: an optional database name that will override any database name in a provided config file.
        """
        super().__init__(app, config)
        logger = logging.getLogger(__name__)
        logger.debug('Initializing mongo module')

        default_connection_string = 'mongodb://heauser:heauser@localhost:27017/hea'

        if config and 'MongoDB' in config:
            logger.debug('Parsing MongoDB section of config file')
            database_section = config['MongoDB']
            if connection_string is not None:
                conn_url = URL(connection_string)
            else:
                connection_string = database_section.get('ConnectionString', default_connection_string)
                conn_url = URL(connection_string)
            if username is not None:
                conn_url = conn_url.with_user(username)
            if password is not None:
                conn_url = conn_url.with_password(password)
            logger.debug('\tUsing connection string %s', conn_url.with_password('xxxxxxxx'))
            if database_name is not None:
                name = database_name
            else:
                name = database_section.get('Name')
            client = motor_asyncio.AsyncIOMotorClient(str(conn_url))
            logger.debug('\tUsing database %s', name or 'default from connection string')
            self.__connection_pool = client.get_database(name=name)
        else:
            if connection_string is not None:
                conn_url = URL(connection_string)
            else:
                conn_url = URL(default_connection_string)
            if username is not None:
                conn_url = conn_url.with_user(username)
            if password is not None:
                conn_url = conn_url.with_password(password)
            logger.debug('\tUsing connection string %s',
                         str(conn_url.with_password('xxxxxxxx')) if conn_url.password is None else str(conn_url))
            client = motor_asyncio.AsyncIOMotorClient(str(conn_url))
            if database_name is not None:
                self.__connection_pool = client.get_database(name=database_name)
            else:
                self.__connection_pool = client.get_database()

    async def get(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None, sub: str = None) -> Optional[Dict[str, Any]]:
        """
        Gets an object from the database.

        :param request: the aiohttp Request object (required).
        :param collection: the mockmongo collection (required).
        :param var_parts: the names of the dynamic resource's variable parts (required).
        :param mongoattributes: the attribute to query by. The default value is None. If None, the var_parts will be
        used as the attributes to query by.
        :param sub: the user to filter by.
        :return: a HEA name-value pair dict, or None if not found.
        """
        logger = logging.getLogger(__name__)
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        try:
            extra_ = sub_filter_expr(sub or user.NONE_USER, permissions=GETTER_PERMS)
            q = Mongo.__filter_by(mongo_expr(request,
                                             var_parts,
                                             mongoattributes,
                                             extra_))
            logger.debug('Query is %s', q)
            result = await coll.find_one(q)
            if result is not None:
                result['id'] = str(result['_id'])
                del result['_id']
            logger.debug('Got from mongo: %s', result)
            return result
        except bson.errors.InvalidId as e:
            logger.debug('Skipped mongo query: %s', e)
            return None

    async def get_content(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None, sub: str = None) -> Optional[SupportsAsyncRead]:
        """
        Handles getting a HEA object's associated content.

        :param request: the HTTP request. Required.
        :param collection: the Mongo collection name. Required.
        :return: a Response with the requested HEA object or Not Found.
        """
        obj = await self.get(request, collection, var_parts, mongoattributes, sub)
        if obj is None:
            return None
        fs = self.__new_gridfs_bucket(collection)
        try:
            return await fs.open_download_stream(ObjectId(request.match_info['id']))
        except NoFile:
            return None

    async def get_all(self, request: web.Request, collection: str, var_parts=None, mongoattributes=None,
                      sub: str = None) -> List[root.HEAObjectDict]:
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
        logger = logging.getLogger(__name__)
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        if var_parts is not None or mongoattributes is not None:
            q = Mongo.__filter_by(mongo_expr(request,
                                             var_parts,
                                             mongoattributes,
                                             sub_filter_expr(sub or user.NONE_USER, permissions=GETTER_PERMS))
                                  )
            logger.debug('Query is %s', q)
            results = await coll.find(q).to_list(10)
        else:
            q = sub_filter_expr(sub or user.NONE_USER, permissions=GETTER_PERMS)
            logger.debug('Query is %s', q)
            results = await coll.find(q).to_list(10)
        for result in results:
            result['id'] = str(result['_id'])
            del result['_id']
        logger.debug('Got from mongo: %s', results)
        return results

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
        logger = logging.getLogger(__name__)
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        if var_parts is not None or mongoattributes is not None:
            q = Mongo.__filter_by(mongo_expr(request,
                                             var_parts,
                                             mongoattributes,
                                             sub_filter_expr(sub or user.NONE_USER, permissions=GETTER_PERMS))
                                  )
            logger.debug('Query is %s', q)
            result = await coll.find_one(q) is None
        else:
            q = sub_filter_expr(sub or user.NONE_USER, permissions=GETTER_PERMS)
            logger.debug('Query is %s', q)
            result = await coll.find_one(q) is None
        logger.debug('Got from mongo: %s', result)
        return result

    async def post(self, request: web.Request, obj: root.DesktopObject, collection: str, default_content: Optional[IO] = None) -> Optional[str]:
        """
        Handle a post request.

        :param request: the HTTP request (required).
        :param obj: the HEAObject instance to post.
        :param collection: the MongoDB collection containing the requested object (required).
        :return: the generated id of the created object, or None if the object could not be inserted or was None.
        """
        if obj is None:
            return None
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        try:
            result = await coll.insert_one(document=obj.to_dict())
            if result and default_content is not None:
                fs = self.__new_gridfs_bucket(collection)
                await fs.upload_from_stream_with_id(ObjectId(obj.id), obj.display_name, default_content)
            return str(result.inserted_id)
        except (pymongo.errors.DuplicateKeyError, NoFile):
            return None

    async def put(self, request: web.Request, obj: root.HEAObject, collection: str) -> Optional[UpdateResult]:
        """
        Handle a put request.

        :param request: the HTTP request (required).
        :param obj: the HEAObject instance to put.
        :param collection: the MongoDB collection containing the requested object (required).
        :return: an instance of pymongo.results.UpdateResult.
        TODO: check that the user has the needed permissions to replace the object.
        """
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        try:
            return await coll.replace_one(Mongo.__filter_by_id(request), replace_id_with_object_id(obj.to_dict()))
        except bson.errors.InvalidId:
            return None

    async def put_content(self, request: web.Request, collection: str) -> bool:
        """
        Handle a put request of an HEA object's content.

        :param request: the HTTP request (required).
        :param collection: the MongoDB collection containing the requested object (required).
        :return: Whether or not it was successful.
        TODO: check that the user has the permissions needed to update the content.
        """
        obj = await self.get(request, collection, var_parts=['id'])
        if obj is None:
            return False
        try:
            fs = self.__new_gridfs_bucket(collection)
            await fs.upload_from_stream_with_id(obj['id'], str(obj), AioHTTPFileLikeObjectWrapper(request.content))
            return True
        except NoFile:
            # Delete orphaned chunks from gridfs if an error occurred
            return False

    async def delete(self, request: web.Request, collection: str) -> Optional[DeleteResult]:
        """
        Handle a delete request.

        :param request: the HTTP request.
        :param collection: the MongoDB collection containing the requested object (required).
        :return: an instance of pymongo.results.DeleteResult.
        TODO: check that the user has the permissions needed to delete the item.
        """
        coll = self.__connection_pool.get_collection(collection, codec_options=_codec_options)
        try:
            result = await coll.delete_many(Mongo.__filter_by_id(request))
            if result:
                fs = self.__new_gridfs_bucket(collection)
                try:
                    await fs.delete(ObjectId(request.match_info['id']))
                except NoFile:
                    pass
                finally:
                    return result
        except bson.errors.InvalidId:
            pass
        return None

    @staticmethod
    def __filter_by(filter_criteria) -> Dict[str, Any]:
        """
        Returns a filter for objects with an attribute value of interest.

        :param filter_criteria: the and'ed attribute-value pairs to filter by.
        :return: a filter dict.
        :raises bson.errors.InvalidId: if any id fields are not a 12-byte input or a 24-character hex string.
        """
        return {
            ('_id' if nm == 'id' else nm): (bson.objectid.ObjectId(val) if nm == 'id' else val)
            for nm, val in filter_criteria.items()}

    @staticmethod
    def __filter_by_id(request) -> Dict[str, Any]:
        """
        Returns a filter by the id variable in the request.

        :param request: a HTTP request.
        :return: a filter dict.
        """
        return Mongo.__filter_by({'id': request.match_info['id']})

    def __new_gridfs_bucket(self, bucket: str) -> AsyncIOMotorGridFSBucket:
        return AsyncIOMotorGridFSBucket(self.__connection_pool, bucket)


def replace_id_with_object_id(obj: Dict[str, Any]):
    """
    Returns a shallow copy of the provided dict with any id key replaced by an _id key with an ObjectId value.
    :param obj: a HEA object as a dict.
    :return: a newly created dict.
    """
    if 'id' in obj:
        f_ = dict(obj)
        f_['_id'] = bson.ObjectId(f_.pop('id', None))
        return f_
    else:
        return dict(obj)
