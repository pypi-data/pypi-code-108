# -*- coding: utf-8 -*-
"""Micro tidy.

   Usage::

       >>> print utidy('''
       ... <form name="FirmaForm" id="FirmaForm" method="POST" autocomplete="off"
       ... action="." class="fForm"><input type="hidden" name="__cmd"
       ... value="FirmaForm"></form>hello
       ... ''')
       ...
       <form action="." autocomplete="off" class="fForm" id="FirmaForm" method="POST" name="FirmaForm">
           <input name="__cmd" type="hidden" value="FirmaForm">
       </form>
       hello

"""
from __future__ import print_function, unicode_literals
from builtins import str as text
import sys
import re

from .html.uhtml import to_html

self_closing_tags = """
    area
    base
    br
    col
    command
    embed
    hr
    img
    input
    keygen
    link
    meta
    param
    source
    track
    wbr
""".split()


class HtmlTag(object):
    attre = re.compile(r"""
        (?P<attr>[-\w]+)                            # attribute
        (?:                                         # either = followed by..
           (?: = (?P<quote>['"])(.*?)(?P=quote))    #  something in quotes
          |(?: = ([^\s]+))                          #  something without quotes
        )?                                          # or a plain attribute
        """, re.VERBOSE)  # "

    def __init__(self, txt):
        self.orig = txt
        # collapse multiple spaces
        self.text = re.subn(r'(\s+)', " ", txt)[0]
        m = re.match(r'<\s*(/)?\s*([-\w]+)(\s.*)?>', self.text)
        if not m:  # pragma:nocover
            print("NOT M:", txt)
        g = m.groups()
        self.closing = g[0] is not None
        self.name = g[1]
        self.attrtxt = g[2] or ""
        self.selfclosing = self.name in self_closing_tags
        if not self.closing and self.attrtxt.strip():
            self.attrs = self.normalize_attrs(
                HtmlTag.attre.findall(self.attrtxt)
            )
        else:
            self.attrs = []
        self.kind = 'tag'
        if self.closing:
            self.kind += '-end'
        if not self.closing and not self.selfclosing:
            self.kind += '-start'

    def normalize_class(self, val):
        return ' '.join(sorted(val.split()))

    def normalize_style(self, val):
        styles = [s.split(':', 1) for s in val.split(';') if s.strip()]
        return ';'.join('{}:{}'.format(k.strip(), v.strip())
                        for k, v in sorted(styles)) + ';'

    def normalize_attrs(self, attrs):
        res = []
        # attributes who should preserve empty string
        empty_is_empty = {'action'}
        for attrname, _quote, qval, noqval in sorted(attrs):
            if attrname in empty_is_empty:
                val = qval or noqval
            else:
                val = qval or noqval or attrname
            if attrname == 'class':
                res.append((attrname, self.normalize_class(val)))
            elif attrname == 'style':
                res.append((attrname, self.normalize_style(val)))
            else:
                res.append((attrname, val))
        return res

    def __str__(self):
        if self.closing:
            return "</%s>" % self.name
        res = "<%s" % self.name
        if self.attrtxt:
            res += ' '
        res += ' '.join(['%s="%s"' % (k, v) for k, v in self.attrs])
        res += ">"
        return res

    def __repr__(self):
        return "{{%s}}" % str(self)


def tokenize_html(html):
    tagre = re.compile(r'(<.*?>)', re.MULTILINE | re.DOTALL | re.UNICODE)
    tokens = []
    pos = 0
    while 1:
        m = tagre.search(html, pos)
        if not m:
            break

        txt = html[pos:m.start()]
        if txt.strip():
            tokens.append(('text', txt.strip()))

        tag = HtmlTag(html[m.start():m.end()])
        tokens.append((tag.kind, tag))

        pos = m.end()
    if pos < len(html):
        tokens.append(('text', html[pos:].strip()))
    return tokens


def simplify_simple_tags(html):
    """Put tags without any nested children on one line, i.e. turn::

           <h1>
               foo
           </h1>

       into::

           <h1>foo</h1>

    """
    def replacement(m):
        grps = m.groups()
        res = "<%s>%s</%s>" % (grps[0], grps[1].strip(), grps[0])
        # print "REPLS:", grps, res
        return res

    import time
    start = time.time()
    res = re.sub(
        r'<(\w+)>([^<]*)</\1>',
        replacement,
        html,
        flags=re.MULTILINE | re.DOTALL
    )
    sys.stderr.write('done: %.3f\n' % (time.time() - start))
    return res


def utidy(html, level=0, indent='    ', simplify=False):
    """micro-tidy

       Normalizes the html.
    """
    tokens = tokenize_html(to_html(html).strip())
    res = []

    def _indent(n):
        return indent * max(0, n)
    i = level
    for kind, token in tokens:
        if kind == 'text':
            res.append(_indent(i) + token)
        elif kind == 'tag-start':
            res.append(_indent(i) + str(token))
            i += 1
        elif kind == 'tag-end':
            i -= 1
            res.append(_indent(i) + str(token))
        elif kind == 'tag':
            res.append(_indent(i) + str(token))
    html = '\n'.join(res)
    if simplify:
        html = simplify_simple_tags(html)
    return html


class Utidy(object):
    def __init__(self, item, **kw):
        self.debug = kw.pop('debug', False)
        self.item = item
        self.kw = kw
        if not isinstance(item, text):
            item = to_html(item)
        self.html = utidy(item, **kw)

    def _as_unicode(self):
        return self.html

    def _as_bytes(self):
        return self._as_unicode().encode('u8')

    __unicode__ = _as_unicode
    __bytes__ = _as_bytes

    def __str__(self):
        if sys.version_info.major < 3:
            return self._as_bytes()
        else:
            return self._as_unicode()

    __repr__ = __str__

    def __html__(self):
        return self.html

    def __eq__(self, other):
        if not isinstance(other, text):
            other = to_html(other)
        other_html = utidy(other, **self.kw)
        res = self.html == other_html
        if not res and self.debug:
            print("LHS:\n", self.html)
            print("RHS:\n", other_html)
        return res


if __name__ == "__main__":  # pragma: nocover
    print(utidy(open(sys.argv[1]).read(), simplify=True))
