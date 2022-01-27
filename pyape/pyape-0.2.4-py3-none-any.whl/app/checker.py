"""
pyape.app.checker
~~~~~~~~~~~~~~~~~~~

装饰器集合
"""
from functools import wraps

from flask import request, abort

from pyape import gconfig
from pyape.app import logger, gcache
from pyape.app.re2fun import get_request_values
from pyape.util.func import parse_int

from pyape.app.models.regional import check_regional


def page():
    """ @装饰器。检测 per_page 和 page，在被装饰方法中加入可用的 page 和 per_page 参数 """

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            page, per_page = get_request_values('page', 'per_page',
                                                defaultvalue={'page': 1, 'per_page': 10}, request_key='args')
            page = parse_int(page, 1)
            per_page = parse_int(per_page, 10)
            kwargs['page'] = page
            kwargs['per_page'] = per_page
            return f(*args, **kwargs)

        return decorated_fun

    return decorator


def request_values(*request_params, defaultvalue={}, request_key='args', parse_int_params=[]):
    """ 检测 vo 的请求值，做一些转换
    :param request_params: 请求的键名列表
    :param defaultvalue: 要替换的默认值，必须保证默认值是存在的
    :param parse_int_params: 需要做 int 转换的键名列表
    """

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            rdict = get_request_values(defaultvalue=defaultvalue, request_key=request_key)
            # kwargs2 = {}
            try:
                for k in request_params:
                    if k in parse_int_params:
                        kwargs[k] = parse_int(rdict.get(k))
                    else:
                        kwargs[k] = rdict.get(k)
            except Exception as e:
                logger.error('checker.request_values request_params(%s) defaultvalue:(%s) request_key(%s) error: %s',
                    request_params, defaultvalue, request_key, e)
                abort(401)
            return f(*args, **kwargs)

        return decorated_fun

    return decorator


def regional_gconfig(add_r=False, ignore_zero=False):
    """ @装饰器。 检测配置文件中是否包含需要的 regional 信息
    :param add_r: 是否传递 r 参数给被包装的方法
    :param ignore_zero: 值为真，则允许 r 值为 0。0 是一个特殊的 r 值，代表全局 r
    :return:
    """

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            if gconfig.regional is None:
                logger.error('@regional_checker_gconfig NO RegionalConfig')
                abort(403)
            r = request.args.get('r')
            r, robj = gconfig.regional.check_regional(r, ignore_zero)
            if r is None:
                logger.regional('@regional_checker_gconfig CAN NOT find regional {}.'.format(r))
                abort(403)
            if add_r:
                kwargs['r'] = r
            return f(*args, **kwargs)

        return decorated_fun

    return decorator


def regional_gdb(add_r=False, ignore_zero=False, add_robj=False):
    """ @装饰器。检查数据库中失败包含需要的 regional

    :param add_r: 是否传递 r 参数给被包装的方法
    :param ignore_zero: 值为真，则允许 r 值为 0。0 是一个特殊的 r 值，代表全局 r
    :param get_r: 值为真，则填充一个 robj 参数，其为 r 的对象值
    :return:
    """

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            regional = request.args.get('r')
            r, robj = check_regional(regional, ignore_zero)
            if r is None:
                logger.error('@regional_checker_gdb CAN NOT find regional %s.', regional)
                abort(403)
            if add_r:
                kwargs['r'] = r
            if add_robj:
                kwargs['robj'] = robj
            return f(*args, **kwargs)

        return decorated_fun

    return decorator


def ip_gconfig():
    """ 检测访问 IP 是否处于IP 地址列表中
    IPS 地址列表在配置中定义，定义到具体的 REGIONAL 中
    """

    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            if gconfig.regional is None:
                logger.error('@ip_checker_gconfig NO RegionalConfig')
                abort(403)
            r = request.args.get('r')
            r, robj = gconfig.regional.check_regional(r, False)
            if r is None:
                logger.error('@ip_checker_gconfig CAN NOT find regional %s.', r)
                abort(403)
            ip = request.remote_addr
            ips = robj.get('ips')
            # logger.info('@ip_checker_gconfig ip: %s, ips: %s', ip, ips)
            if isinstance(ips, list) and not ip in ips:
                logger.error('@ip_checker_gconfig IP %s is not in %s.', ip, ips)
                abort(403)
            return f(*args, **kwargs)

        return decorated_fun

    return decorator


def ip_gdb(use_global=False):
    """ 检测访问 IP 是否处于IP 地址列表中，从数据库中查找配置的 ips 列表

    :param use_global: 如果值为 True，则使用 regional 0 的 ips 配置
    """
    def decorator(f):
        @wraps(f)
        def decorated_fun(*args, **kwargs):
            if use_global:
                regional = 0
            else:
                regional = request.args.get('r', 0)

            r, robj = check_regional(regional, True)
            if r is None:
                logger.error('@ip_checker_gdb CAN NOT find regional %s.', r)
                abort(403)

            ip = request.remote_addr
            ips = robj.merge().get('ips')
            # logger.info('@ip_checker_gdb ip: %s, ips: %s', ip, ips)
            if isinstance(ips, list) and not ip in ips:
                logger.error('@ip_checker_gdb IP %s is not in %s.', ip, ips)
                abort(403)
            return f(*args, **kwargs)

        return decorated_fun

    return decorator