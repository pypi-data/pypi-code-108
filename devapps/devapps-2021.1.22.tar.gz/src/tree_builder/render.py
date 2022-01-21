"""
Renders for a Type / Class Tree
"""

import os
from collections import OrderedDict as OD

from . import (
    TypeMetaClass,
    full_id,
    has_parent,
    props,
    simple_props,
    simple_types,
    walk_tree,
)

try:
    from colour import Color
except ImportError:
    Color = None
    # print('colour package missing - no hsl html rendering')

exists = os.path.exists


def color(hir):
    # hue, sat, lum
    return (
        hir * 50,
        min(2 * hir * 10 / 100.0, 0.8),
        min(2 * hir * 10 / 100.0, 0.8),
    )


def to_primitives(root, **cfg):
    t = '''
     new primitives.orgdiagram.ItemConfig({
                    id: %(id)s,
                    parent: %(parentid)s,
                    title: '%(type)s %(name)s %(level)s',
                    description: "%(hir)s %(name)s",
                    itemTitleColor: tinycolor("%(color)s").toHexString()
                }),
    '''

    def pre(c, r, level, cfg, t=t):
        i = {}
        print(c)
        ics = cfg['id_by_cls']
        hir = c._hir
        i['id'] = id = c._id
        if hir == 0:
            c._color = getattr(c, '_color', '#8bd124')
        i['itemTitleColor'] = getattr(c, '_color', '%s' % Color(hsl=color(hir)).hex)
        i['hir'] = c._hir
        i['level'] = c._level
        h = [('_id', c._id)]
        for k, v in simple_props(c):
            h.append((k, v))
        i['html'] = ',&nbsp;'.join(
            ['<span title="%s">%s</span>' % (k, v) for k, v in h]
        )
        ics[c] = id
        i['parent'] = 'null'
        p = getattr(c, '_parent', None)
        if p:
            i['parent'] = p._id
        i['type'] = c.type
        i['name'] = c.name
        i['title'] = '%(type)s %(name)s' % i
        i['description'] = '%(hir)s %(name)s' % i
        i['image'] = 'images/letters/%s.png' % c.type[0].lower()
        if hir > 0:
            i['templateName'] = 'axc'
        r.append(i)

    cfg['id_by_cls'] = {}
    cfg['id'] = -1
    res = walk_tree(root, pre, None, has_parent, cfg=cfg)
    # res[-1] = res[-1].rsplit(',', 1)[0]
    return ['var items = %s;' % res]


def to_ctree(root, **cfg):
    cfg['props_ign'] = cfg.get('props_ign', ())

    def pre(c, r, level, cfg):
        r.append('%s<li><a href="#">%s %s</a><ul>' % (level * ' ', c.type, c.name))

    def post(c, r, level, cfg):
        r.append('%s</ul></li>' % (level * ' '))

    res = walk_tree(root, pre, post, has_parent, cfg=cfg)
    return [r for r in res if r.strip()]


def to_dict(root, res=None, **cfg):
    if res is None:
        res = OD()
    for k, v in reversed(props(root)):
        if not type(v) == TypeMetaClass:
            # if k in ('alias', 'type', 'descr'):
            res[k] = v
        else:
            res[k] = to_dict(v, **cfg)
    return res


def to_tuples(root, **cfg):
    def pre(c, r, level, cfg):
        key = '.'.join(full_id(c))
        va = []
        for k, v in props(c):
            if not type(v) == TypeMetaClass:
                va.append([k, v])
        r.append([key, va])

    res = []
    walk_tree(root, pre, None, match=has_parent, res=res, cfg=cfg)
    return res


def to_class_tree(root, **cfg):
    def pre(c, r, level, cfg):
        ind = '   '
        n, t = c._cls, c.type
        r.append('%sclass %s(%s):' % (ind * (level - 1), n, t))
        for k in dir(c):
            if k.startswith('_'):
                continue
            v = getattr(c, k)
            if isinstance(v, simple_types):
                apo = "'''" if isinstance(v, str) else ''
                r.append('%s%s = %s%s%s' % (ind * level, k, apo, v, apo))

    res = walk_tree(root, pre, None, match=has_parent, cfg=cfg)
    res = [r for r in res if not 'tree_builder' in r]
    cfg['into'] = ('build_type_hirarchy', 'build_tree')
    cfg['skip_line_with'] = 'tree_builder'
    cfg['replace'] = (('(T, ', '('),)
    return res


def html_props(c, cfg):
    p = []
    if not cfg.get('no_props'):
        for k, v in props(c):
            if k in cfg['props_ign'] or not isinstance(v, simple_types):
                continue
            p += ['<tr><td>%s:</td><td><b>%s</b></td></tr>' % (k, v)]
    if p:
        p.insert(0, '<table>')
        p.append('</table>')
    return '\n'.join(p)


def to_html(root, **cfg):
    # ignored:
    hirarchy = root._hirarchy_list
    cfg['props_ign'] = cfg.get('props_ign', ())
    cc = cfg['css_clses'] = []

    def pre(c, r, level, cfg):
        cc = cfg['css_clses']
        if not c.type in cc:
            cc.append(c.type)
        classes = ()
        v = getattr(c, 'criticality', None)
        if v == 1:
            classes += ('critical',)
        if v == 2:
            classes += ('warning',)
        classes = ' '.join(classes)

        r.append('%s<%s class="%s">' % (level * '  ', c.type, classes))
        n = c._cls
        r.append('%s<b>%s</b> %s' % ((level + 1) * '  ', c._cls, c.descr))
        r.append(html_props(c, cfg))

    def post(c, r, level, cfg):
        r.append('%s</%s>' % (level * '  ', c.type))

    res = walk_tree(root, pre, post, has_parent, cfg=cfg)

    # setup css, using less:
    css = [
        ', '.join([f for f in [t.type for t in hirarchy]])
        + ''' {
        display:      inline-block;
        border-style: solid;
        border-width: 3px;
        padding:      5px; margin: 10px;
        }
    .critical {border-color: red}
    .warning {border-color: yellow}
    '''
    ]

    base = {'hue': 10, 'sat': 80, 'lum': 60, 'sat_bg': 30, 'lum_bg': 90}
    m = dict(base)
    hue_add = 70
    col = 'color: hsl(%(hue)s, %(sat)s%%, %(lum)s%%)'
    col_bg = 'color: hsl(%(hue)s, %(sat_bg)s%%, %(lum_bg)s%%)'

    for t in [t.type for t in hirarchy]:
        m['type'] = t
        m['col'] = col % m
        m['col_bg'] = col_bg % m

        css += ['%(type)s:before {content: "%(type)s:" attr(t);%(col)s}' % m]
        css += [
            ''.join(['%(type)s {background-%(col_bg)s; ' % m, 'border-%(col)s}' % m,])
        ]
        m['hue'] += hue_add

    res = '\n'.join([r for r in res if r.strip()])
    # res = res.replace('Service', 'service')
    res = [
        '<html>',
        '<body>',
        '<style>',
        '\n'.join(css),
        '</style>',
        '<div><table><tr><td>',
        '<div>',
        res,
        '</div>',
        '</td></tr></table></div>',
        '</body>',
    ]
    return res


def print_out(
    res, tmplfile=None, into='', outfile=None, skip_line_with=None, replace=(), **cfg
):
    """
    into: two seperators within a file where we put the result, keeping the seps,
          for a subsequent update (good for embedding e.g. into a md doc)
          string or tuple for same sep.
    """
    if tmplfile and not outfile:
        # -> tree_tmpl.html -> tree.html
        outfile = tmplfile.replace('_tmpl', '')
    out, tmpl = '\n'.join(res), ''
    if tmplfile:
        if not exists(tmplfile):
            raise Exception('template file not found', tmplfile)
        with open(tmplfile, 'r') as fd:
            tmpl = fd.read()

    pre, post = '', ''
    if into:
        if isinstance(into, str):
            into = (into, into)
        if not into[0] in tmpl or not into[1] in tmpl:
            # put at beginning then:
            tmpl = '\n%s\n%s\n%s' % (into[0], into[1], tmpl)
        pre, old = ('\n' + tmpl).split('\n' + into[0], 1)[:2]
        post = ''
        if '\n' in old:
            old = old.split('\n', 1)[1]
            old, post = old.split(into[1])[:2]
            post = post.split('\n', 1)[1]

    if skip_line_with:

        def sk(s):
            return '\n'.join([r for r in s.splitlines() if not skip_line_with in r])

        pre, post = sk(pre), sk(post)

    if pre or post:
        if outfile != file:
            # no seps in the target if target not the file
            into = ('', '')
        out = '\n'.join((pre, into[0], out, into[1], post)).strip()

    for k, v in replace:
        out = out.replace(k, v)

    if outfile:
        with open(outfile, 'w') as fd:
            fd.write(out)
    # print (out)
    return out
