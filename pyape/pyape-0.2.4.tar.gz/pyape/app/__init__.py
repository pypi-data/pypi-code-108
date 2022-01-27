import importlib
import logging
from datetime import datetime
from functools import partial
from decimal import Decimal
from functools import wraps

from sqlalchemy.inspection import inspect
from flask_compress import Compress
from flask_sqlalchemy import SQLAlchemy

from pyape import uwsgiproxy
from pyape import gconfig, errors
from pyape.cache import GlobalCache
from pyape.logging import get_logging_handler, get_pyzog_handler
from pyape.flask_redis import FlaskRedis
from pyape.flask_extend import PyapeFlask, PyapeResponse, FlaskConfig


class PyapeDB(SQLAlchemy):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 保存根据 regional 进行分类的表定义
        self.__regional_tables = {}

    def build_regional_tables(self, name, build_table_method, rconfig):
        """ 根据 regionals 的配置创建多个表
        :param name: 表的名称前缀
        :param build_table_method: 创建表的方法，接受两个参数，动态创建一个 Table Class
        :param rconfig: RegionalConfig 的实例
        """
        tables = self.__regional_tables.get(name)
        if tables is None:
            tables = {}
            self.__regional_tables[name] = tables
        for regional in rconfig.rlist:
            r = regional.get('r')

            # 避免重复建立表
            if tables.get(r) is not None:
                continue

            # 默认使用键名 bind_key_db，若找不到则使用键名 bind_key。
            bind_key = regional.get('bind_key_db')
            Cls = build_table_method(name + str(r), bind_key=bind_key)
            tables[r] = Cls
        # logger.info('build_regional_tables %s', tables)

    def get_regional_table(self, name, r, build_table_method, rconfig):
        """ 根据 regionals 和表名称前缀获取一个动态创建的表
        :param name: 表的名称前缀
        :param r: regional
        :param rconfig: RegionalConfig 的实例
        """
        if not r in rconfig.rids:
            raise ValueError('get_regional_table: No regional %s' % r)
        tables = self.__regional_tables.get(name)
        Cls = None
        if isinstance(tables, dict):
            Cls = tables.get(r)
        if Cls is None:
            # 可能存在更新了 regional 之后，没有更新 tables 的情况，这里要更新一次。
            # 每个进程都需要更新，但每次调用可能仅发生在其中一个进程。因此必须在每次调用的时候都检测更新。
            self.build_regional_tables(name, build_table_method, gconfig)
            return self.__regional_tables.get(name)
        # logger.info('get_regional_table %s', Cls)
        return Cls

    def ismodel(self, instance):
        """ 判断一个实例是否是 gdb.Model 的实例
        """
        return isinstance(instance, self.Model)

    def result2dict(self, result, keys, replaceobj=None, replaceobj_key_only=False):
        """
        根据提供的 keys、replaceobj、replaceobj_key_only 转换 result 为 dict

        :param result: 要转换的对象
        :param keys: 要转换对象的key list
        :param replaceobj: 可替换的键
        :param replaceobj_key_only: 仅包含可替换的键
        :return dict: 转换成功的 dict
        """
        rst = {}
        for key in keys:
            value = getattr(result, key)
            if isinstance(value, datetime):
                value = value.isoformat()
            elif isinstance(value, Decimal):
                value = int(value)
            newkey = key
            if replaceobj:
                # 仅使用 replaceobj 中提供的键名，这样在找不到键名的时候，newkey 的值为 None
                if replaceobj_key_only:
                    newkey = replaceobj.get(key, None)
                # 找不到对应键名，就使用原始键名
                else:
                    newkey = replaceobj.get(key, key)
            if newkey:
                rst[newkey] = value
        return rst

    def to_response_data(self, result, replaceobj=None, replaceobj_key_only=False):
        # zrong 2017-08-31
        """ 把数据库查询出来的 ResultProxy 转换成 dict 或者 list
        仅支持 list 和 dict 类型，且不支持嵌套（dict 中的值不能包含 ResultProxy 对象）

        :param replaceobj: 替换键名
        :param replaceobj_key_only: 仅使用替换键名，丢掉非替换键名的键
        """
        if result is None:
            return {}
        if isinstance(result, list):
            return [self.to_response_data(item, replaceobj, replaceobj_key_only) for item in result]
        # 这里直接将 dict 类型返回，是避免下面对 keys 方法的检查。因为 dict 也有 keys 方法
        # dict 应该直接视为最终结果，不必再进行一次 key 的筛选
        if isinstance(result, dict):
            return result
        # 转换 Model 到 dict
        if self.ismodel(result):
            return self.result2dict(result, inspect(result).mapper.column_attrs.keys(), replaceobj, replaceobj_key_only)
        # zrong 2017-10-11
        # 若使用 gdb.session.query 的方式查询，返回的结果是 <class 'sqlalchemy.util._collections.result'>
        # 它是一个动态生成的 tuple 的子类，带有 keys() 方法
        if callable(getattr(result, 'keys', None)):
            return self.result2dict(result, result.keys(), replaceobj, replaceobj_key_only)
        return result


class PyapeRedis(FlaskRedis):
    """ 增加 根据 Regional 获取 redis client 的封装
    """
    def get_regional_client(self, r, force=True):
        """ 根据 r 获取到一个 py_redis_client
        :param r: regional
        :param force: 没有 redis 配置会抛出 ValueError 异常。若设置为 False 则返回 None（无异常）
        """
        if not r in gconfig.regional_ids:
            if force:
                raise ValueError('get_redis_client: no regional %s' % r)
            return None
        robj = gconfig.regional_dict.get(r)
        # bind_key_redis 如果没有定义，或者为 None，就会得到默认的 REDIS_URI
        return grc.get_client(robj.get('bind_key_redis'))

    def get_regional_clients(self):
        """ 获取到一个以 regional 为键名的 py_redis_client dict
        """
        clients = {}
        rc_clients = self.get_clients()
        for r, robj in gconfig.regional_dict.items():
            # bind_key_redis 如果没有定义，或者为 None，就会得到默认的 REDIS_URI
            bind_key_redis = robj.get('bind_key_redis')
            clients[r] = rc_clients[bind_key_redis]
        return clients


# 全局的数据库引用，保存的是 PyapeDB 的实例
gdb: PyapeDB = None

# grc 就是 Global Redis Client 的缩写，pyape.flask_redis.FlaskRedis 的实例
grc: PyapeRedis = None

# 全局缓存实例，pyape.cache.GlobalCache 的实例
gcache: GlobalCache = None

# 就是 flas.app.logger 放在这里不必引用 current_app，参考：
# https://flask.palletsprojects.com/en/1.1.x/logging/
logger: logging.Logger = logging.getLogger(__name__)


def init_db(pyape_app):
    """ 初始化 SQLAlchemy
    """
    sql_uri = pyape_app.config.get('SQLALCHEMY_DATABASE_URI')
    if sql_uri is None:
        return
    global gdb
    if gdb is not None:
        raise ValueError('gdb 不能重复定义！')
    # db 初始化的时候带上 app 参数，这样就不必再次 init_app
    gdb = PyapeDB(app=pyape_app)


def init_redis(pyape_app):
    """ 初始化 REDIS ，配置文件中包含 REDIS_URI 才进行初始化
    """
    redis_uri = pyape_app.config.get('REDIS_URI')
    if redis_uri is None:
        return
    global grc
    if grc is not None:
        raise ValueError('redis client 不能重复定义！')
    grc = PyapeRedis(app=pyape_app)


def init_logger(pyape_app):
    """ 设置 Flask app 和 sqlalchemy 的logger
    """
    flasklogger = pyape_app.logger
    sqlalchemylogger = logging.getLogger('sqlalchemy')
    # 删除 Flask 的默认 Handler
    del flasklogger.handlers[:]
    handler = None
    level = logging.DEBUG

    if pyape_app.config.get('DEBUG'):
        handler = get_logging_handler('stream', 'text', level)
    else:
        name = gconfig.getcfg('NAME')
        if name is None:
            logger_name = 'app'
        else:
            logger_name = 'app.%s' % name
        level = logging.INFO
        handler = get_pyzog_handler(logger_name, gconfig.getcfg(), gconfig.getdir('logs'), level=level)

    flasklogger.setLevel(level)
    sqlalchemylogger.setLevel(logging.WARNING)
    for log in (flasklogger, sqlalchemylogger):
        log.addHandler(handler)


def init_cache(pyape_app):
    """ 初始化全局缓存对象
    """
    global gcache
    if gcache is not None:
        raise ValueError('global cache 不能重复定义！')
    ctype = None
    flask_redis_client = None
    if grc is None:
        if uwsgiproxy.in_uwsgi:
            ctype = 'uwsgi'
        else:
            ctype = 'dict'
    else:
        flask_redis_client = grc.get_client(bind_key='cache')
        if flask_redis_client is None:
            flask_redis_client = grc.get_client()
    gcache = GlobalCache.from_config(ctype, flask_redis_client=flask_redis_client)


def register_blueprint(pyape_app, rest_package, rest_package_names):
    """ 注册 Blueprint，必须在 db 的创建之后调用
    :param app: flask app 实例
    :param rest_package: 父包名
    :param rest_package_names: {name:url, name2:url2}
    :return:
    """
    if rest_package is None:
        return
    for name, url in rest_package_names.items():
        bp_module = importlib.import_module('.' + name, rest_package)
        # name 可能为 app.name 这样的复合包，这种情况下，Blueprint 实例的名称为 app_name
        bp_name = name.replace('.', '_')
        pyape_app.register_blueprint(getattr(bp_module, bp_name), url_prefix=url)


def _build_kwargs_for_app():
    """ 将本地所有路径转换为绝对路径，以保证其在任何环境下可用
    """
    kwargs = {
            'static_url_path': gconfig.getcfg('PATH', 'STATIC_URL_PATH', default_value=''),
            'static_folder': gconfig.getcfg('PATH', 'STATIC_FOLDER', default_value='static'),
            'template_folder': gconfig.getcfg('PATH', 'TEMPLATE_FOLDER', default_value='templates')
        }

    instance_path = gconfig.getcfg('PATH', 'INSTANCE_PATH')
    if instance_path:
        kwargs['instance_path'] = str(gconfig.getdir(instance_path).resolve())
    else:
        kwargs['instance_path'] = str(gconfig.getdir().resolve())

    kwargs['template_folder'] = str(gconfig.getdir(kwargs['template_folder']).resolve())
    kwargs['static_folder'] = str(gconfig.getdir(kwargs['static_folder']).resolve())
    return kwargs


def create_app(FlaskClass=PyapeFlask, ResponseClass=PyapeResponse, ConfigClass=FlaskConfig):
    """
    根据不同的配置创建 app
    :param config_name:
    :return:
    """
    kwargs = _build_kwargs_for_app()

    pyape_app = FlaskClass(__name__, **kwargs)
    pyape_app.response_class = ResponseClass
    pyape_app.config.from_object(ConfigClass(gconfig.getcfg('FLASK')))
    if pyape_app.config.get('COMPRESS_ON'):
        # 压缩 gzip
        compress = Compress()
        compress.init_app(pyape_app)
    # 处理全局错误
    errors.init_app(pyape_app)
    return pyape_app
