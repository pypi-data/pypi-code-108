from pprint import pformat


def pf_echo(object, *args, **kwargs):
    # return str
    t1 = ', '.join(pformat(x) for x in args)
    t2 = ''
    if kwargs:
        t2 = ', ' + ', '.join('{}={}'.format(k, v) for k, v in kwargs.items())
    if callable(object):
        name = getattr(object, "__name__")
        text = '{}({}{})'.format(name, t1, t2)
        return text
    else:
        return '[{}]: {}{}'.format(object, t1, t2)


def pf_response(response):
    """
    :param response: Flask.Response , requests.Response
    :return: str
    """
    url = response.url
    status_code = response.status_code
    content = response.content
    info = dict(
        url=url,
        status_code=status_code,
        content=content,
    )
    request = response.request
    if request:
        info['request_body'] = request.body
        info['request_method'] = request.method
        info['request_headers'] = request.headers
    msg = '[Response]' + '\n' + pformat(info, indent=4) + '\n'
    return msg


def sort_rows(rows, key):
    """
    # python3, cmp is deprecated, but in python2, cmp
    >>> func = lambda a, b: cmp(a.get(key), b.get(key))
    >>> ds = sort(rows, cmp=func)
    :param rows: array of dict, eg : mysql.proxy rows
    :param key:  sorted_key
    :return: new array
    """
    func = lambda x: x.get(key)
    ds = sorted(rows, key=func)
    return ds


def str2list(text, line_sep='\n', strip_chars=None, filter_func=None):
    paras = [x.strip(strip_chars) for x in text.split(line_sep)]
    data = list(filter(filter_func, paras))
    return data


def list2dict(lines, sep=':', strip_chars=None):
    result = {}
    for i, line in enumerate(lines):
        paras = line.split(sep)
        k = paras[0].strip(strip_chars)
        v = ':'.join(paras[1:]).strip(strip_chars)
        result[k] = v
    return result


def str2dict(text, line_sep='\n', dict_sep=':'):
    ls = str2list(text, line_sep)
    ds = list2dict(ls, dict_sep)
    return ds


def mirror_dict(form):
    '''dict(
        a=dict(x=0,y=1),     ==>   x=dict(a=0, b=0),
        b=dict(x=0,y=1),     ==>   y=dict(a=1, b=1),
    )
    '''
    result = {}
    if bool(form) and isinstance(form, dict):
        from_keys = form.keys()
        items = form.values()
        to_keys = items[0].keys()
        result = {tk: dict(map(lambda fk, item: (fk, item.get(tk)), from_keys, items)) for tk in to_keys}
        return result
    return result
