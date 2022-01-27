"""
pyape.app.re2fun
~~~~~~~~~~~~~~~~~~~

请求和响应的常用方法封装
re2 = request + response
"""

from pathlib import Path
from datetime import datetime

from flask import (request, jsonify, make_response, send_file)
from flask_sqlalchemy import BaseQuery

from pyape import gconfig
from pyape.app import gdb, logger
from pyape.util.func import parse_float, parse_date, daydt



def get_post_data():
    """ 优先作为 json 获取数据
    如果不是 json 则获取 form 数据
    """
    if request.is_json:
        try:
            logger.info('get_post_data request.data: %s', request.data)
            return request.get_json()
        except Exception as e:
            logger.error('get_post_data request.get_json error:%s', str(e))
            return None
    return request.form.to_dict()


def get_request_values(*args, replaceobj=None, defaultvalue={}, request_key='json'):
    """ 检测提供的 HTTP REQUEST 的值。包括 POST/PUT

    replaceobj 参数替换。
        例如 *args 中有个参数名称为 a1，但希望查询 json 中名为 a2 的键，
        则在 replaceobj 中设置 {"a1": "a2"}
    defaultvalue 默认值。
        若在参数中找不到值，则使用 defaultvalue 中的值替代。
        例如 *args 中有个参数名称为 a1，但 json 中没有 a1，希望 a1 有一个默认值，则可以提供 {"a1": 42}
    request_key 可用值为 
        args = request.args
        form = request.form
        values = request.values
        json = request.json
    """
    rinfo = getattr(request, request_key, {}) or {}
    # rinfo 可能是一个 dict，或者一个 werkzeug.datastructures.CombinedMultiDict/ImmutableMultiDict
    # 后者拥有 to_dict 方法
    if hasattr(rinfo, 'to_dict'):
        rinfo = rinfo.to_dict()
    rdata = {}
    values = []
    if args:
        for arg in args:
            # 替换 arg 的名称
            if replaceobj:
                arg = replaceobj.get(arg, arg)
            # 若 form 中没有，使用 data 的数据，data 中没用，使用 defaultvalue 的数据
            values.append(rinfo.get(arg, rdata.get(arg, defaultvalue.get(arg))))
        if values:
            if len(values) > 1:
                return tuple(values)
            return values[0]
        return None
    # 没有提供参数，返回 defaultvalue, form 和 data 合并后的 dict
    return dict(defaultvalue, **dict(rinfo, **rdata))


def responseto(message=None, error=None, code=None, data=None, replaceobj=None, replaceobj_key_only=False, return_dict=False, **kwargs):
    """ 封装 json 响应
    :param message: 错误消息，若提供则默认 error 为 True
    :param error: 是否包含错误
    :param code: 错误代码，若不提供则值可能为 200 error=False/444 error=True
    :param data: 若提供了 data，则 data 中应该包含 error/message/code
    :param replaceobj: 替换响应中的键名。 {'被替换': '替换值'}
    :param return_dict: 若值为 True，则返回 dict
    :param kwargs: 要加入响应的其他对象，可以是 model 也可以是 dict
    :return: 一个 Response 对象，或者一个 dict
    """

    # 如果提供了 data，那么不理任何其他参数，直接响应 data
    if not data:
        data = kwargs
        for k, v in kwargs.items():
            # 不处理空对象
            if not v:
                continue
            data[k] = gdb.to_response_data(v, replaceobj, replaceobj_key_only)
        data['error'] = error
        data['code'] = code
        if message:
            # 除非显示提供 error 的值，否则默认为 True
            # 意思是提供了 message 就代表有 error
            data['message'] = message
            if error is None:
                data['error'] = True
            if not data.get('code'):
                data['code'] = 444
        else:
            # 除非显示提供 error 的值，否则默认为 False
            # 意思是没有提供 message 就代表没有 error
            if error is None:
                data['error'] = False
            if not data.get('code'):
                data['code'] = 200
    if not isinstance(data, dict):
        # 444 为不合法操作
        data = {'error': True, 'code': 444, 'message': 'data 必须是一个 dict！'}
    if not data.get('code'):
        if data.get('error'):
            data['code'] = 444
        else:
            data['code'] = 200
    if return_dict:
        return data
    return jsonify(data)


def get_from_to_date(from_date=None, to_date=None, default=True, strftime=False):
    """ 校验 from_date/to_date 并返回这两个值
    :param from_date:
    :param to_date:
    :param default: 若值为true，则保证 from_date 和 to_date 有值
    :return:
    """
    from_date = parse_date(from_date)
    to_date = parse_date(to_date, to_day_end=True)
    if default:
        # 如果必须提供默认值，from_date使用10月15日（开始开发日），to_date 使用今天（由于不是0点，不用加1）
        if from_date is None:
            from_date = daydt(default_initday=True)
        if to_date is None:
            to_date = datetime.today()
    if strftime:
        if from_date is not None:
            from_date = from_date.strftime('%Y-%m-%d')
        if to_date is not None:
            to_date = to_date.strftime('%Y-%m-%d')
    return from_date, to_date


def get_from_to_date_query(query, time_column, from_date=None, to_date=None):
    from_date = parse_date(from_date)
    to_date = parse_date(to_date, to_day_end=True)
    if from_date:
        query = query.filter(time_column >= from_date)
    if to_date:
        query = query.filter(time_column <= to_date)
    return query


def get_min_max_value_query(query, value_column, min_value=None, max_value=None):
    min_value = parse_float(min_value)
    max_value = parse_float(max_value)
    if min_value is not None:
        query = query.filter(value_column >= min_value*100)
    if max_value is not None:
        query = query.filter(value_column <= max_value*100)
    return query


def get_page_response(query, page, per_page, itemskey, return_method=None,
                      replaceobj=None, replaceobj_key_only=False, **kwargs):
    """ 获取一个多页响应对象
    :param query: 查询对象，或者直接返回的对象
    :param page: 当前页
    :param per_page: 每页项目数
    :param itemskey: 对应 items 的键名
    :param return_method: 若值不为 None 根据特定的方式转换 pages.items，返回 data 对象而非 Response 对象，同时会 ignore **kwargs 参数。
    :param replaceobj: 见 re2fun.responseto
    :param replaceobj_key_only:  见 re2fun.responseto
    :param kwargs: 见 re2fun.responseto
    :return: 一个多页响应对象
    """
    data = None
    if isinstance(query, BaseQuery):
        try:
            pages = query.paginate(int(page), int(per_page), False)
            data = dict(page=pages.page, prev_num=pages.prev_num, next_num=pages.next_num,
                        has_next=pages.has_next, has_prev=pages.has_prev, pages=pages.pages,
                        total=pages.total, per_page=pages.per_page, error=False, code=200)
            if callable(return_method):
                data[itemskey] = return_method(pages.items)
                return data
            elif return_method == 'model':
                data[itemskey] = gdb.to_response_data(pages.items, replaceobj, replaceobj_key_only)
                return data
            data[itemskey] = pages.items
        except Exception as e:
            logger.critical('re2fun.get_page_response error: %s', str(e))
            return responseto(message=str(e), error=True, code=500)
    else:
        data = dict(page=page, prev_num=1, next_num=1,
            has_next=False, has_prev=False, 
            pages=1, total=0, per_page=per_page, 
            error=False, code=200)
        data[itemskey] = query
    return responseto(**data, replaceobj=replaceobj, replaceobj_key_only=replaceobj_key_only, **kwargs)


def get_download_response(filepath, filename=None, content_type=None, inline=False):
    """
    获取一个下载文件的响应
    for jquery.fileDownload, see:
    http://johnculviner.com/jquery-file-download-plugin-for-ajax-like-feature-rich-file-downloads/

    :param filepath: 文件绝对路径
    :param filename: 文件名，若不提供，就使用原始文件名
    :param content_type: 文件的 content_type
    :return:
    """
    # 转换字符串路径为 Path 对象
    if isinstance(filepath, str):
        filepath = Path(filepath)
    if filename is None:
        filename = filepath.name

    filepath_string = str(filepath.resolve())
    logger.info('get_download_response. filepath_string:%s', filepath_string)

    response = make_response(send_file(filepath_string, as_attachment=True, attachment_filename=filename))
    response.headers['Set-Cookie'] = 'fileDownload=true; path=/'
    content_disposition =  'inline' if inline else 'attachment; filename=%s' % filename
    response.headers['Content-Disposition'] = content_disposition

    if content_type is not None:
        response.headers['Content-Type'] = content_type
    return response

