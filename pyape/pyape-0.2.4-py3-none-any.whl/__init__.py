__version__ = '0.2.4'

from functools import wraps

import sys
import flask
# 这里的导入目的是为了初始化，导入顺序是按照依赖顺序排列的，不可修改
import pyape.uwsgiproxy
from pyape.config import GlobalConfig


gconfig: GlobalConfig = None


def init(gconfig: GlobalConfig, init_app_method=None, cls_config=None):
    """ 初始化 APP
    :param gconfig: pyape.config.GlobalConfig 的实例
    :param init_app: 外部初始化方法
    :param cls_config: 一个包含自定义 Class 的 dict
        形如: {'FlaskClass': PyapeFlask, 'ResponseClass': PyapeResponse, 'ConfigClass': FlaskConfig}
        不需要同时包含 3 个 Class
    """
    sys.modules[__name__].__dict__['gconfig'] = gconfig

    flask.cli.load_dotenv()

    # pyape.app 需要导入 gconfig，因此在 gconfig 创建之后再导入
    import pyape.app

    if isinstance(cls_config, dict):
        pyape_app = pyape.app.create_app(**cls_config)
    else:
        pyape_app = pyape.app.create_app()

    pyape.app.init_db(pyape_app)
    pyape.app.init_redis(pyape_app)
    # logger 可能会使用 redis，因此顺序在 redis 初始化之后
    pyape.app.init_logger(pyape_app)
    # cache 可能会使用 redis，因此顺序在 redis 初始化之后
    pyape.app.init_cache(pyape_app)
    # 这个方法必须在注册蓝图前调用
    if init_app_method is not None:
        init_app_method(pyape_app, pyape.app.gdb)

    # blueprint 要 import gdb，因此要在 gdb 之后注册
    appmodules = gconfig.getcfg('PATH', 'modules')
    pyape.app.register_blueprint(pyape_app, 'app', appmodules)
    return pyape_app


def init_decorator(gconfig: GlobalConfig, cls_config=None):
    """ 初始化 APP 的装饰器版本
    :param gconfig: pyape.config.GlobalConfig 的实例
    :param init_app: 外部初始化方法
    :param cls_config: 一个包含自定义 Class 的 dict
        形如: {'FlaskClass': PyapeFlask, 'ResponseClass': PyapeResponse, 'ConfigClass': FlaskConfig}
        不需要同时包含 3 个 Class
    """
    sys.modules[__name__]['gconfig'] = gconfig

    flask.cli.load_dotenv()

    # pyape.app 需要导入 gconfig，因此在 gconfig 创建之后再导入
    import pyape.app

    if isinstance(cls_config, dict):
        pyape_app = pyape.app.create_app(**cls_config)
    else:
        pyape_app = pyape.app.create_app()

    pyape.app.init_db(pyape_app)
    pyape.app.init_redis(pyape_app)
    # logger 可能会使用 redis，因此顺序在 redis 初始化之后
    pyape.app.init_logger(pyape_app)
    # cache 可能会使用 redis，因此顺序在 redis 初始化之后
    pyape.app.init_cache(pyape_app)

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            kwargs['pyape_app'] = pyape_app
            kwargs['gdb'] = pyape.app.gdb
            # 在外部调用中需要做：
            # 1. 导入外部的 models
            # 2. 创建数据库
            # 这里不传递 *args 这个参数，因为在 uwsgi 中这个参数有不少来自于服务器的值，
            # 这会导致 f 调用失败，f 仅接受 gdb 和 pyape_app 两个参数
            decorated_return = f(**kwargs)

            # blueprint 要 import gdb，因此要在 gdb 之后注册
            appmodules = gconfig.getcfg('PATH', 'modules')
            pyape.app.register_blueprint(pyape_app, 'app', appmodules)
            return decorated_return

        return decorated_fun

    return decorator
