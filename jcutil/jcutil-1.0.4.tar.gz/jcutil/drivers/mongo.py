from collections import namedtuple
from decimal import Decimal
from enum import Enum
from typing import Union, Optional, List, Dict
from uuid import uuid4
from functools import partial
import pymongo
import pytz
from bson import ObjectId, CodecOptions, Decimal128
from bson.codec_options import TypeRegistry
from bson.json_util import loads, dumps
from gridfs import GridFS, GridFSBucket, GridOut
from pymongo import MongoClient
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.results import InsertOneResult, UpdateResult
from jcramda import when, is_a, compose, attr, obj, has_attr, first, if_else, not_, popitem, \
    getitem, in_, _, bind, enum_name, curry, locnow


def fallback_encoder(value):
    return when(
        (is_a(Decimal), Decimal128),
        # (is_a(NDFrame), df_to_dict),
        (is_a(InsertOneResult), compose(obj('insertedId'), attr('inserted_id'))),
        (is_a(UpdateResult), compose(obj('upsertedId'), attr('upserted_id'))),
        (has_attr('get'), lambda o: o.get()),
        (has_attr('result'), lambda o: o.result()),
        else_=str
    )(value)


# class NDFrameCodec(TypeCodec):
#     python_type = pd.Series
#     bson_type = dict
#
#     def transform_bson(self, value):
#         return pd.Series(value)
#
#     def transform_python(self, value):
#         return df_to_dict(value)


_type_registry = TypeRegistry(
    # type_codecs=[NDFrameCodec()],
    fallback_encoder=fallback_encoder
)


class UniqFileGridFSBucket(GridFSBucket):
    def _find_one(self, filename):
        return [*self.find({'filename': filename}).sort('uploadDate', -1).limit(1)]

    def _create_proxy(self, out: GridOut, opened=False):
        fid: ObjectId = getattr(out, '_id')
        self.delete(fid)
        create_method = self.open_upload_stream_with_id if opened \
            else self.upload_from_stream_with_id
        return partial(create_method, fid)

    def open_save_file(self, filename, **kwargs):
        open_by_id = compose(
            lambda grid_out: self._create_proxy(
                grid_out, True)(filename, **kwargs),
            first,
        )
        return compose(
            if_else(not_,
                    lambda _: self.open_upload_stream(filename, **kwargs),
                    open_by_id),
            self._find_one,
        )(filename)

    def save_file(self, filename, **kwargs):
        upload_by_id = compose(
            lambda grid_out: self._create_proxy(grid_out)(filename, **kwargs),
            first,
        )

        return compose(
            if_else(not_,
                    lambda _: self.upload_from_stream(filename, **kwargs),
                    upload_by_id),
            self._find_one,
        )(filename)


class BaseModel(object):
    __collection: Optional[Collection] = None

    def __init__(self, db: Database, collection_name):
        self.__collection = db.get_collection(collection_name)

    def find_by_id(self, _id: Union[str, ObjectId]):
        query_id = _id if _id is ObjectId else ObjectId(_id)
        return self.__collection.find_one(filter={'_id': query_id})

    def find_in_ids(self, ids: List[str], *args):
        query = {'_id': {'$in': [ObjectId(n) for n in ids if n is not None]}}
        return list(self.__collection.find(query, *args))

    def _save(self, sepc_field: str = None, **kwargs):
        assert '_id' in kwargs or not not_(sepc_field) and sepc_field in kwargs, \
            f'must had [_id] field or [{sepc_field}] field'
        query = if_else(
            in_(_, '_id'),
            compose(obj('_id'), popitem('_id')),
            compose(obj(sepc_field), getitem(sepc_field))
        )
        return self.__collection.find_one_and_update(filter=query(kwargs),
                                                     update={'$set': kwargs},
                                                     upsert=True,
                                                     return_document=ReturnDocument.AFTER)


__clients: Dict[str, MongoClient] = dict()


def exists(name: str):
    return name in __clients


def new_client(uri: str, alias: str = None):
    db_name = alias if alias is not None else uuid4().hex
    __clients[db_name] = MongoClient(uri)
    return __clients[db_name]


db_getter = compose(bind('get_default_database'), getitem(_, __clients))


def conn(key=None):
    if key is None:
        key = first(list(__clients.keys()))
    return __clients[key]


def get_collection(tag, collection: Union[str, Enum], db_name=None):
    assert tag in __clients, f'not found mongo connection: {tag}'
    db = __clients[tag].get_default_database() if db_name is None \
        else __clients[tag].get_database(db_name)
    return db.get_collection(enum_name(collection),
                             codec_options=CodecOptions(tz_aware=True,
                                                        type_registry=_type_registry,
                                                        tzinfo=pytz.timezone('Asia/Shanghai')))


def fs_client(key=None) -> GridFS:
    if key is None:
        key = first(list(__clients.keys()))
    assert key in __clients
    return compose(GridFS, db_getter)(key)


def fs_bucket(db_name, bucket_name='fs') -> UniqFileGridFSBucket:
    assert db_name in __clients
    return compose(
        lambda db: UniqFileGridFSBucket(db, bucket_name),
        db_getter
    )(db_name)


def load(conf: dict):
    if conf and len(conf) > 0:
        for key in conf:
            new_client(conf[key], key)
            # print(f'mongodb: [{key}] connected')


def instances():
    return list(map(str, __clients.keys()))


@curry
def find(collection, query):
    assert is_a(Collection, collection)
    return tuple(collection.find(query))


def find_page(collection, query, page_size=10, page_no=1, sort=None):
    assert is_a(Collection, collection)
    skip = page_size * (page_no - 1)
    if sort is None:
        sort = [('createdTime', pymongo.DESCENDING)]
    query['logicDeleted'] = False
    c = collection.find(query).sort(sort).skip(skip).limit(page_size)
    return {'content': list(c), 'pageNo': page_no, 'pageSize': page_size, 'totalCount': c.count()}


@curry
def find_one(collection, query):
    assert is_a(Collection, collection)
    return collection.find_one(query)


@curry
def find_by(collection, key, value):
    """

    Parameters
    ----------
    collection  Collection
    key str
    value Any
    """
    return collection.find(filter={key: value})


@curry
def save(collection, data):
    """
    更新或新增数据
    如data中含有_id，则为update操作，如无则为insert操作

    Parameters
    ----------
    collection
    data

    Returns
    -------

    """
    r = if_else(
        in_(_, '_id'),
        lambda d: collection.update_one(
            {'_id': data['_id']}, {'$set': d}, upsert=True),
        collection.insert_one
    )(data)
    if hasattr(r, 'inserted_id'):
        data['_id'] = r.inserted_id
    return data


@curry
def replace_one(collection, data):
    """
    用于替换操作，查询条件为：

        {_id: data['_id']}

    先查找老稳定，然后修改或创建

    Parameters
    ----------
    collection: pymongo.collection.Collection
    data: dict
        要替换的完整文档，必须包含 _id

    Returns
    -------
    tuple
        (new_data, old_data)
    """
    assert '_id' in data, 'must include _id field in data.'
    query = {'_id': data['_id']}
    old = collection.find_one(query)
    collection.update_one(query, data, upsert=True)

    return data, old


to_json = dumps
from_json = loads


def mdb_proxy(tag, collection_name):

    proxy_obj = namedtuple(f'{tag}_{collection_name}',
                           'all,find,add,update,replace,delete')
    collection = get_collection(tag, collection_name)

    def find(query: dict, **kwargs):
        return [*collection.find(query, **kwargs)]

    def add(data):
        new_id = collection.insert_one(
            {**data, 'createTime': locnow()}).inserted_id
        return collection.find_one(new_id)

    def update(_id, data, **kwargs):
        result = collection.update_one({'_id': ObjectId(_id)}, {
                                       '$set': data, '$currentDate': {'updateTime': True}, '$inc': {'__v': 1}
                                       }, **kwargs)
        if result.modified_count:
            return collection.find_one(ObjectId(_id))
        return None

    def replace(_id, data, **kwargs):
        if _id == data.get('_id'):
            data.pop('_id')
            result = collection.replace_one({'_id': ObjectId(_id)}, {
                **data, '__v': data.get('__v', 0)+1, 'updateTime': locnow()})
            if result.modified_count:
                return collection.find_one(ObjectId(_id))
        return None

    def delete(_id):
        result = collection.delete_one({'_id': ObjectId(_id)})
        return result.deleted_count
    return proxy_obj(partial(find, {}), find, add, update, replace, delete)
