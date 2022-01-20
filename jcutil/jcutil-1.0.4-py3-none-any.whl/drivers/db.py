from importlib import import_module
from typing import Union
from jcramda import loc
import logging


__all__ = [
    'connect',
    'conn',
    'init_engine',
]

__engines = dict()


def init_engine(tag: str, *args, create_engine=None, **kwargs):
    """Init a oracle engine

    :param tag: a flag with connection engine
    :param create_engine: a function create a database connection engine
    :param kwargs: database connection config

    **Options**
     * schema: default is 'oracle', can use ['oracle', 'mysql', 'sqlite', 'postgres', etc...]
     * user: database connection username
     * password: database connection password
     * dsn: database host and port dsn string
     * url: database connection url, like that: "oracle://username:password@10.0.0.5:1521/sid?encoding=utf-8

    :return:
    """
    schema = kwargs.get('schema', 'oracle')
    if create_engine is None:
        sqlmodule = import_module('sqlalchemy')
        url = '{schema}://{user}:{password}@{dsn}?encoding=utf-8'\
            .format(schema=schema, user=kwargs['user'], password=kwargs['password'],
                    dsn=kwargs['dsn']) if 'url' not in kwargs else kwargs.pop('url')
        current_engine = sqlmodule.create_engine(
            url, pool_size=10, encoding='utf-8', **kwargs)
    else:
        current_engine = create_engine(*args, **kwargs)
    __engines[tag] = current_engine
    return current_engine


def new_client(tag, *args, create_engine=None, **kwargs):
    if create_engine is None:
        try:
            module = import_module('sqlalchemy')
            create_engine = getattr(module, 'create_engine')
        except ModuleNotFoundError as err:
            logging.error(err)

    __engines[tag] = create_engine(*args, **kwargs)
    return __engines[tag]


def get_client(name: Union[str, int] = 0):
    if len(__engines) > 0:
        return loc(name, __engines)
    raise RuntimeError('no any host can connect.')


def connect(n: Union[str, int] = 0):
    return get_client(n).connect()


def load(conf: dict):
    """
    一次性读取配置文件，生成数据库链接
    配置文件格式：dict(dbname="{dburl}")
    ```
    {
      "db1": "mysql://username:password@127.0.0.1:3306/dbname?encoding=utf8mb",
      "myoracle": "oracle://...",
    }
    ```
    @param conf: Dict[str, str]
    """
    if conf and len(conf) > 0:
        for key in conf:
            try:
                init_engine(key, url=conf[key])
            except Exception as err:
                logging.warning(f'load database [{key}] failed: {err}')
            # print(f'database [{key}] connected')


conn = connect


def instances():
    return [*__engines.keys()]
