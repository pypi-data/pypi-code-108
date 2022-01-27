from __future__ import unicode_literals


def get_http_bt_name(naming, request, base_name, custom=False):
    """Create a BT name based on naming properties and HTTP request data.

    Parameters
    ----------
    naming : mapping
        A naming scheme as specified as a set of key-value properties,
        retrieved from :py:class:`appdynamics.agent.core.registries.NamingSchemeRegistry`
    request : Request-like
        An object representing an incoming HTTP request, containing the
        attributes `method`, `headers`, `url` (the full URL with scheme),
        `cookies`, `path` (the path part of the URL), and `args` (query
        parameters). A Werkzeug `BaseRequest` is compatible, as are instances
        of :py:class:`appdynamics.lib.LazyWsgiRequest`
    base_name : str or None
        The base name for this BT, if any. If None or empty, then a base name
        will be generated from the request's `path` property according to the
        rules in the provided naming scheme
    custom : boolean
        True if bt name is constructed from custom rule matching

    Returns
    -------
    name : str
        The generated BT name

    """
    path = [s for s in request.path.split('/') if s]

    strategy_to_input = {
        'header-value': 'headers',
        'cookie-value': 'cookies',
        'param-value': 'args',
    }

    def name(strategy, param, delim='.'):
        name_string = ''
        if strategy == 'method':
            name_string = request.method
        elif strategy == 'first-n-segments':
            name_string = '/%s' % '/'.join(path[:int(param)])
        elif strategy == 'last-n-segments':
            name_string = '/%s' % '/'.join(path[-int(param):])
        elif strategy == 'uri-segment-number':
            data_len = len(path)
            indices = sorted(int(i) - 1 for i in param.replace(' ', '').split(','))
            name_string = delim.join(path[i] for i in indices if 0 <= i < data_len)
        elif strategy in strategy_to_input:
            data = getattr(request, strategy_to_input[strategy])
            keys = param.replace(' ', '').split(',')
            name_string = delim.join(data[k] for k in keys if data.get(k, None))

        return name_string

    base_strategy = naming.get('uri-length') or 'first-n-segments'
    base_name = base_name or name(base_strategy, naming.get('segment-length') or 2, '')

    base_delimiter = ' - ' if custom else '.'

    if 'uri-suffix-scheme' in naming:
        suffix = name(naming['uri-suffix-scheme'], naming.get('suffix-key', '0'))
    else:
        return base_name

    return base_delimiter.join(p for p in (base_name, suffix) if p)
