"""
pyape.app.rfun
~~~~~~~~~~~~~~~~~~~

对 Regional 的操作封装
"""

import time

import toml
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql.expression import or_

from pyape.app.re2fun import get_request_values, responseto, get_page_response
from pyape.app.queryfun import commit_and_response_error
from pyape.app import gdb, logger
from pyape.util.func import parse_int

from pyape.app.models.regional import Regional
from pyape.app.models.valueobject import ValueObject


def regional_get_more(page, per_page, kindtype, status, merge):
    """ 分页获取指定 votype 下的 ValueObject 信息
    """
    if merge > 0:
        return_method = lambda vos: [vo.merge() for vo in vos] 
    else:
        return_method = 'model'
    qry = Regional.get_qry(kindtype=kindtype, status=status)
    rdata = get_page_response(qry, page, per_page, 'regionals', return_method)
    return responseto(data=rdata)


def regional_get(r, merge):
    """ 获得一个 regional 项目
    :param merge: 若 merge 为 0，则直接返回原始数据；
                    若 merge 为 1，执行 Regional 中的 merge 方法
    """
    if r is None:
        return responseto('Param please!', code=401)
    robj = Regional.query.get(r)
    if robj is None:
        return responseto('No regional %s!' % r, code=404)

    if merge > 0:
        return responseto(regional=robj.merge(), code=200)
    return responseto(regional=robj, code=200)


def regional_get_all(kindtype, rtype, merge):
    """ 获得多个 regional 项目
    """
    rtype = parse_int(rtype)
    kindtype = parse_int(kindtype)

    if rtype is not None:
        if not rtype in Regional.REGIONAL_TYPES:
            return responseto('The rtype of regional %s is unavailable!' % rtype, code=401)

    regionals = Regional.get_qry(kindtype=kindtype, rtype=rtype).all()
    if merge > 0:
        regionals = [regional.merge() for regional in regionals] 
    return responseto(regionals=regionals, code=200)


def regional_get_all_trim(kindtype, rtype, rformat):
    """ 获得多个 regional 项目，仅包含 r 和 name

    :param kindtype:
    :param rtype: 1000/2000/5000
    :param rformat: 0 代表返回 json 格式的 list，1 代表仅仅返回 r 的 list
    """
    if rtype is not None and not rtype in Regional.REGIONAL_TYPES:
        return responseto('The rtype of regional %s is unavailable!' % rtype, code=401)
    qry = Regional.get_qry(kindtype=kindtype, rtype=rtype, status=1)
    regionals = qry.with_entities(Regional.r, Regional.name, Regional.createtime).all()
    if rformat == 1:
        regionals = [ritem.r for ritem in regionals]
    return responseto(regionals=regionals, code=200)


def regional_add(r, name, value, kindtype, status):
    """ 增加一个 regional
    """
    if r is None or name is None or value is None:
        return responseto('Param please!', code=401)
    kindtype = parse_int(kindtype, 0)
    try:
        toml.loads(value)
    except toml.TomlDecodeError as e:
        msg = 'value is not a TOML string: %s' % str(e)
        logger.error(msg)
        return responseto(msg, code=401)

    now = int(time.time())
    robj = Regional(r=r, name=name, value=value, status=status, kindtype=kindtype, createtime=now, updatetime=now)
    resp = commit_and_response_error(robj, refresh=True)
    if resp is not None:
        return resp
    return responseto(regional=robj, code=200)
    

def regional_edit(r, name, value, kindtype, status):
    """ 修改一个 regional
    """
    status = parse_int(status, 1)
    kindtype = parse_int(kindtype)
    if r is None:
        return responseto('Param please!', code=401)
    robj = Regional.query.get(r)
    if robj is None:
        return responseto('找不到 regional %s!' % r, code=404)
    if name is not None:
        robj.name = name
    if value is not None:
        try:
            toml.loads(value)
            robj.value = value
        except toml.TomlDecodeError as e:
            msg = 'value is not a TOML string: %s' % str(e)
            logger.error(msg)
            return responseto(msg, code=401)
    if kindtype is not None:
        robj.kindtype = kindtype
    if status is not None:
        robj.status = status
    robj.updatetime = int(time.time())
    resp = commit_and_response_error(robj, refresh=True)
    if resp is not None:
        return resp
    return responseto(regional=robj, code=200)
    

def regional_del(r):
    """  删除一个 regional
    """
    if r is None:
        return responseto('Param please!', code=401)
    # 必须先删除所有的与这个 Regional 相关的关系
    if ValueObject.query.filter_by(r=r).first() is not None:
        return responseto('Please delete valueobjet of %s first!' % r, code=403)
    try:
        Regional.query.filter_by(r=r).delete()
        gdb.session.commit()
    except SQLAlchemyError as e:
        msg = 'regional_del error: ' + str(e)
        logger.error(msg)
        return responseto(msg, code=500)
    return responseto(code=200)
    