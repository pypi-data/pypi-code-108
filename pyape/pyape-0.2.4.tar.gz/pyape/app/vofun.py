"""
pyape.app.vofun
~~~~~~~~~~~~~~~~~~~

对 ValueObject 的操作封装
"""

import time

from pyape.util.func import parse_int
from pyape import gconfig
from pyape.app import gdb, gcache, logger
from pyape.app.models.valueobject import ValueObject, get_vo_query
from pyape.app.re2fun import get_request_values, responseto, get_page_response
from pyape.app.queryfun import commit_and_response_error


# @checker.request_checker('votype', 'status', 'merge', defaultvalue={'merge': 1, 'status': 1}, request_key='args', parse_int_params=['merge', 'status', 'votype'])
def valueobject_get_more(r, page, per_page, votype, status, merge, return_dict=False):
    """ 分页获取指定 votype 下的 ValueObject 信息
    """
    if merge > 0:
        return_method = lambda vos: [vo.merge() for vo in vos] 
    else:
        return_method = 'model'
    qry = get_vo_query(r, votype, status)
    rdata = get_page_response(qry, page, per_page, 'vos', return_method)
    return responseto(data=rdata, return_dict=return_dict)


# @checker.request_checker('votype', 'status', 'merge', defaultvalue={'merge': 0, 'status': 1}, request_key='args', parse_int_params=['merge', 'status', 'votype'])
def valueobject_get_all(r, votype, status, merge, return_dict=False):
    """ 获取指定 votype 下所有 ValueObject 信息
    """
    vos = get_vo_query(r, votype, status).all()
    if merge > 0:
        return responseto(vos=[vo.merge() for vo in vos], return_dict=return_dict)
    return responseto(vos=vos, return_dict=return_dict)


def _get_vo_by_cache(r, name):
    """ 从缓存中查询 vo 的 value
    若缓存中不存在，则从数据库中查询并将其写入缓存
    """
    valueobj = gcache.getg(name, r)
    if valueobj is None:
        vo = ValueObject.query.filter_by(name=name).first()
        if vo is not None:
            valueobj = vo.get_value()
            gcache.setg(name, valueobj, r)
    return valueobj


def valueobject_check_value(value, valuetype):
    """ 检查要写入 valueobject 的字符串或者对象
    字符串要检查是否合法，对象要将其转换成字符串并返回
    :@param value: list/dict/str
    :@param valuetype: json/toml
    """
    value_string = None
    if isinstance(value, str):
        # 检测字符串是否正常解析
        vobj = ValueObject.load_value(value, valuetype)
        if vobj is None:
            raise ValueError('value must be a {} string!'.format(valuetype))
        value_string = value
    elif isinstance(value, dict) or isinstance(value, list):
        value_string = ValueObject.dump_value(value, valuetype)
    if value_string is None:
        raise ValueError('value check error!')
    return value_string


# @checker.request_checker('vid', 'name', 'merge', defaultvalue={'merge': 1, 'withcache': 0}, request_key='args', parse_int_params=['merge', 'withcache'])
def valueobject_get(r, vid, name, merge, withcache, return_dict=False):
    """ 获取单个 ValueObject 信息，支持通过  vid 和 name
    """
    if withcache > 0:
        # 如果使用 withcache，必须提供 name
        if name is None:
            return responseto('请提供 name!', code=401, return_dict=return_dict)
        value_in_cache = _get_vo_by_cache(r, name)
        if value_in_cache is None:
            return responseto('no vo like this.', code=404, return_dict=return_dict)
        return responseto(vo=value_in_cache, return_dict=return_dict)

    # 从数据库中查询
    vo = None
    if vid is not None:
        vo = ValueObject.query.get(vid)
    elif name is not None:
        vo = ValueObject.query.filter_by(name=name).first()
    else:
        return responseto('vid or name please!', code=401, return_dict=return_dict)
    if vo is None:
        return responseto('no vo like this.', code=404, return_dict=return_dict)
    if merge > 0:
        vo = vo.merge()
    return responseto(vo=vo, return_dict=return_dict)


def valueobject_add(r, withcache, name, value, votype, status=None, index=None, note=None, valuetype=None, return_dict=False):
    """ 增加一个 VO
    """
    if name is None or value is None or votype is None:
        return responseto(message='必须提供 name/value/votype!', code=401, error=True, return_dict=return_dict)
    if status is not None:
        status = parse_int(status)
        if status is None:
            return responseto(message='status 必须是整数!', code=401, error=True, return_dict=return_dict)
    if index is not None:
        index = parse_int(index)
    try:
        value = valueobject_check_value(value, valuetype)
    except ValueError as e:
        logger.error('valueobject_add %s', str(e))
        return responseto(message='value 无法正常解析！请检查。', code=401, error=True, return_dict=return_dict)

    votype = parse_int(votype)
    if votype is None:
        return responseto(message='请提供 votype!', code=401, error=True, return_dict=return_dict)

    now = int(time.time())
    voitem = ValueObject(name=name,
        value=value,
        status=status if status is not None else 1,
        index=index if index is not None else 0,
        r=r,
        votype=votype,
        createtime=now,
        updatetime=now,
        note=note)

    resp = commit_and_response_error(voitem, refresh=True, return_dict=True)
    if resp is not None:
        return resp

    if withcache > 0:
        valueobj = ValueObject.load_value(value)
        gcache.setg(name, valueobj, r)
    return responseto(vo=voitem, error=False, code=200, return_dict=return_dict)


def valueobject_edit(r, withcache, vid=None, name=None, value=None, votype=None, status=None, index=None, note=None, valuetype=None, return_dict=False):
    """ 更新一个 VO
    """
    if vid is not None:
        vid = parse_int(vid)
        if vid is None:
            return responseto(message='vid 必须是整数!', code=401, error=True, return_dict=return_dict)

    if status is not None:
        status = parse_int(status)
        if status is None:
            return responseto(message='status 必须是整数!', code=401, error=True, return_dict=return_dict)

    if index is not None:
        index = parse_int(index)

    try:
        value = valueobject_check_value(value, valuetype)
    except ValueError as e:
        logger.error('valueobject_edit %s', str(e))
        return responseto(message='value 无法正常解析！请检查。', code=401, error=True, return_dict=return_dict)

    voitem = None
    if vid is not None:
        # 提供 vid 代表是修改 vo
        voitem = ValueObject.query.get(vid)
    elif name is not None:
        # 没有提供 vid 但提供了 name 也代表是修改 vo
        voitem = ValueObject.query.filter_by(name=name).first()

    if voitem is None:
        return responseto(message='找不到 vo!', code=404, error=True, return_dict=return_dict)

    voitem.updatetime = int(time.time())

    # 只有明确提供了 status 才设置它
    # 不处理 votype/r ，因为已经创建了的 VO 不允许修改这些关键分类的值
    if name is not None:
        voitem.name = name
    if value is not None:
        voitem.value = value
    if status is not None:
        voitem.status = status
    if note is not None:
        voitem.note = note
    if index is not None:
        voitem.index = index
    if votype is not None:
        voitem.votype = votype

    resp = commit_and_response_error(voitem, refresh=True, return_dict=True)
    if resp is not None:
        return resp

    if withcache > 0:
        valueobj = ValueObject.load_value(value)
        gcache.setg(name, valueobj, r)
    return responseto(vo=voitem, error=False, code=200, return_dict=return_dict)


def valueobject_del(vid, name, return_dict=False):
    """ 删除一个 vo，优先使用 vid，然后考虑 name
    """
    vo = None

    if vid is not None:
        vo = ValueObject.query.get(vid)
    elif name is not None:
        vo = ValueObject.query.filter_by(name=name).first()

    if vo is None:
        return responseto('no vo like this.', code=404, return_dict=return_dict)

    r = vo.r
    name = vo.name

    resp = commit_and_response_error(vo, delete=True)
    if resp is not None:
        return resp
    gcache.delg(name, r)

    return responseto(return_dict=return_dict)


def update_cache(votype, r):
    """ 从数据库中获取 vo 数据，将其写入缓存中
    这个配置需要被客户端频繁调用，因此不应该去查询数据库
    每次增加或者修改服务器配置的时候，必须调用一次更新内存
    """
    allcache = {}
    for vo in get_vo_query(r, votype, 1).all():
        if vo.value is not None:
            # logger.info('vofun.update_cache %s', vo.get_value())
            allcache[vo.name] = vo.get_value()
    gcache.mset(allcache, r)
