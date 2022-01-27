#!/usr/bin/env python3
# coding: utf-8

_closing_of_known_tags = {
    'a': 2,
    'img': 0,
    'script': 2,
    'link': 0,
    'source': 0,
    'audio': 0,
    'video': 0,
}

_url_attrname_of_known_tags = {
    'a': 'href',
    'link': 'href',
    'img': 'src',
    'script': 'src',
    'source': 'src',
    'audio': 'src',
    'video': 'src',
}

_default_props_of_known_tags = {
    'img': {
        'alt': '',
    },
    'script': {
        'type': "text/javascript",
    },
    'link': {
        'rel': "stylesheet",
        'type': "text/css",
    }
}

_templates = {
    0: '<{tagname} {props}>',
    1: '<{tagname} {props} />',
    2: '<{tagname} {props}>{content}</{tagname}>',
}


def fmttag(name, content, props=None, closing=None):
    props_parts = []
    for k, v in (props or {}).items():
        p = '{}="{}"'.format(k, v)
        props_parts.append(p)
    props_string = ' '.join(props_parts)
    ctx = {'tagname': name, 'props': props_string}
    if closing is None:
        closing = _closing_of_known_tags.get(name, 2)
    if closing == 2:
        ctx['content'] = content
    return _templates[closing].format(**ctx)


def wrap(content, *names):
    """
    :param content: string
    :param names: e.g. ('html', 'body')
    :return: string
    """
    parts = []
    names = list(names)
    for x in names:
        parts.append('<{}>'.format(x))

    parts.append(content)
    names.reverse()
    for x in names:
        parts.append('</{}>'.format(x))
    return ''.join(parts)


def wrap_url(url, tagname):
    props = _default_props_of_known_tags.get(tagname, {})
    props[_url_attrname_of_known_tags.get(tagname, 'href')] = url
    return fmttag(tagname, '', props=props)


def run_wrap_url(_, args):
    import sys
    tagname = args[0] if args else 'a'
    for line in sys.stdin:
        print(wrap_url(line.strip(), tagname))


def wrap_default(content):
    return wrap(content, 'html', 'body')


def table(rows, props=None):
    trs = []
    for row in rows:
        tr = ''.join("<td>" + c + "</td>" for c in row)
        tr = '<tr>' + tr + '</tr>'
        trs.append(tr)
    return fmttag('table', '\n'.join(trs), props)
