# -*- coding: utf-8 -*-
""" simple conversion functions """
import html
import json
import string
import sys
from collections import OrderedDict
from os import linesep as LS

from theming.tablepretty import PrettyTable
from theming.unicode_chars import UCs

# from ax.utils.six import string_types
string_types = (str,)
ASCIDIGITS = string.ascii_letters + string.digits


def strfilter(s, f):
    # filter s for chars in str f:
    return [x for x in s if x in f]


def printables(s):
    return strfilter(s, string.printable)


def repl_unprintable(res):
    res = res.replace('//', '|_AX//_|')
    for r in (
        ('/r', '\r'),
        ('/n', '\n'),
        ('/t', '\t'),
        ('/COL', ':'),
        ('/COM', ','),
        ('/SPC', ' '),
    ):
        res = res.replace(r[0], r[1])
    res = res.replace('|_AX//_|', '\\')
    return res


def show_unprintable(res):
    """ show line ends and tabs:  \r \n \t \r\n """
    res = res.replace('\r\n', '\\r\\n|_AX_RN_|')
    res = res.replace('\t', '\\t\t')
    res = res.replace('\r', '\\r\r')
    res = res.replace('\n', '\\n\n')
    res = res.replace('|_AX_RN_|', '\r\n')
    return res


def printout(m, get=0):
    if isinstance(m, dict) or isinstance(m, (list, tuple)):
        m = dict_to_txt(m, fmt={'ax': 1})
    if hasattr(sys, 'AXFORMATTER'):
        r = sys.AXFORMATTER.fmt(m)
    else:
        r = m
    if get:
        return r
    print(r)


def mtrim(s, l):
    """ foobazbar -> 'fo..ar' if l=6 """
    s = str(s)
    if len(s) <= l - 2:
        # no need to trim:
        return s
    s = s[: l / 2] + '..' + s[-l / 2 :]
    return s


class PTable(PrettyTable):
    """ reformatting a prettytable with better borders.
    note: without calling print_fancy this class makes no sense """

    encoding = 'UTF-8'

    def __init__(self, *a, **kw):
        """
        set never occurring border chars, then replace back in print_fancy:
        directly replacing the default (|-+) is too risky regarding unwanted
        content replacements
        """
        kw['vertical_char'] = chr(4)
        kw['horizontal_char'] = chr(5)
        kw['junction_char'] = chr(6)
        super(PTable, self).__init__(*a, **kw)
        if not 'float_format' in kw:
            self.float_format = '6.2'
        self.int_format['Nr'] = '3'

    def print_fancy(self, get=0, fancy=1, title=None, dt=None):
        """ replace asci borders with unicode """
        r = str(self)
        v, h, j = '|', '-', '+'
        if fancy:
            v, h, j = UCs.VU, UCs.H, UCs.JUNC
        # insert the final borders, plain or unicode fancies, where also the
        # formatter can color on:
        r = r.replace(chr(4), v).replace(chr(5), h).replace(chr(6), j)
        if title:
            r = '\n\n%s\n\n' % fmt(title.upper(), 'important') + r
        post = ''
        if dt:
            post = fmt('\n%.2fs total runtime' % dt, 'debug')
        if get:
            return fmt(r) + post
        printout(r)
        # no printout (=fmt) for post, since already formatted, the reset codes
        # of formattings of contained chars would kill the main formatting:
        print(post)


def fmt(s, prio='info'):
    if hasattr(sys, 'AXFORMATTER'):
        # fmt(s, 'alarm') -> .fmt_alarm(s) on formatter:
        s = getattr(sys.AXFORMATTER, 'fmt_%s' % prio)(s)
    return s


def dict_to_txt(dictObj, hir=0, fmt={}):
    """
    formats hierarchical lists and maps

    fmt map may contain keys for:
    block_sep<hir>: linebreak between keys at this hir level
    em_<hir>: underline the key at this level (em = emphasis)
    plus general format s (html, wiki currently)

    See supported formats below.
    the 'ax' format is reverse compatible with the parse_text
    module in ../parsing/'

    Features of the ax format:
    See the wiki.


    """
    # do trivial cases here, then client does not have to:
    if fmt == 'dict' or 'dict' in fmt:
        return dictObj
    elif fmt == 'json' or 'json' in fmt:
        return json.dumps(dictObj)

    list_marker = '-'
    assert isinstance(fmt, dict), 'Need the format as dictionary'
    prolog = epilog = ''
    if fmt.get('wiki'):
        nl = ' ||\n'
        ind = ' || '
        sep = ' || '
        start = ' || '

    elif fmt.get('html'):
        """ hirarchical html map of maps - see tests """

        def s(pref1, pref2, hir):
            """ flexible parametrization of styles """
            sm = fmt.get('styles')
            if sm == None or isinstance(sm, string_types):
                # must have a styles MAP:
                return ''
            # checking from most to least specific style settings:
            # fmt = {'html': 1, 'styles': {'td': 'report3'}}) would give all tds
            # report3:
            Style = sm.get(
                '%s%s%s' % (pref1, pref2, hir),
                sm.get(
                    '%s%s' % (pref1, pref2),
                    sm.get('%s' % pref1, '%s%s%s' % (pref1, pref2, hir)),
                ),
            )
            return 'class="%s"' % Style

        tind = '   ' * hir
        prolog = (
            '</td><td>' * min(hir, 1)
            + '\n'
            + tind * 2
            + '<table %s>\n' % s('table', '', hir)
        )

        nl = '</td><td colspan="100" %s></td></tr>\n' % s('td', '3', hir)

        epilog = tind * 2 + '</table>\n%s' % (tind * 2)

        if hir:
            epilog += nl
            nl = '</td><td colspan="100" %s></td></tr>\n' % s('td', '3', hir)
        ind = ''
        sep = '</td><td %s>' % s('td', '2', hir)
        start = '  ' + tind * 2
        start += '<tr %s><td %s>' % (s('tr', '', hir), s('td', '1', hir))

    elif fmt.get('ax'):
        nl = '\n'
        ind = '\t'
        sep = ':\t'
        start = ''

        if fmt.get('style') == 'DBG':
            """ this prints out which format markers are inserted """
            start = 'START' + start
            ind = 'IND' + ind
            sep = 'SEP' + sep
            nl = 'NL' + nl

    else:
        nl = '\n'
        ind = '  '
        sep = ':'
        start = ''

    def draw_str(k, hir):
        return start + ind * hir + '%s' % k + nl

    res = prolog
    block_sep = (nl + start) * fmt.get('block_sep_%s' % hir, 0)
    em = fmt.get('em_%s' % hir)

    if isinstance(dictObj, (list, tuple)):
        # is it a plain list or do we need to separate the structures?
        is_plain = 1
        for k in dictObj:
            if isinstance(k, (tuple, list, dict)):
                is_plain = 0
                break
        lcount = 0
        for k in dictObj:
            lcount += 1
            if not is_plain:
                res += dict_to_txt(k, hir, fmt)
                if lcount < len(dictObj) or len(dictObj) == 1:
                    # insert the separator:
                    res += draw_str(list_marker, hir)
            else:
                res += draw_str(k, hir)

    elif isinstance(dictObj, dict):
        it = list(dictObj.keys())
        if not isinstance(dictObj, OrderedDict):
            it.sort()
        for k in it:
            v = dictObj[k]
            if isinstance(v, (tuple, list, dict)):
                res += block_sep
                res += '%s%s%s%s%s' % (start, ind * hir, k, sep, nl)
                if em:
                    res += start + ind * hir + '-' * (len(str(k)) + 1) + nl
                if isinstance(v, dict):
                    res += start + dict_to_txt(v, hir + 1, fmt=fmt) + block_sep
                else:
                    res += dict_to_txt(v, hir + 1, fmt)
            else:
                res += draw_str('%s%s%s' % (k, sep, v), hir)
                if em:
                    res += start + ind * hir + '-' * (len(str(k)) + 1) + nl
            res += block_sep

    elif isinstance(dictObj, (string_types, bool, int, float)):
        res += draw_str(dictObj, hir)

    else:
        # no exception, just draw the repr:
        res += draw_str(dictObj.__repr__(), hir)
        # raise Exception ("type of %s not supported" % dictObj)
    # we need to stay reverse compatible with the synthesiser,
    # so we have to mark lists as such
    # if res is only a string but input was a list:
    if isinstance(dictObj, (tuple, list)):
        if ''.join(res.rsplit(nl)) == res.rsplit(nl, 1)[0]:
            res = res + draw_str(list_marker, hir)

    return res + epilog


def hstr(v):
    return html.escape(str(v)).replace('\n', '<br>\n')


def obj_to_html_list(iObj, hir=0):
    if isinstance(iObj, (list, tuple)):
        return list_to_html_list(iObj)
    elif isinstance(iObj, dict):
        return dict_to_html_list(iObj)
    else:
        return hstr(iObj)


def dict_to_html_list(dictObj, hir=0):
    pre = LS + '  ' * hir
    res = pre + '<ul>'
    for k, v in list(dictObj.items()):
        # keys must be native types, str, ints..:
        if not isinstance(v, (list, tuple, dict)):
            res += pre + '<li>%s: %s</li>' % (hstr(k), hstr(v))
        else:
            res += pre + '<li>%s:</li>' % hstr(k)
            res += pre + obj_to_html_list(v, hir + 1)
    res += pre + '</ul>' + LS
    return res


def list_to_html_list(listObj, hir=0):
    pre = LS + '  ' * hir
    ret = ''
    if isinstance(listObj, (list, tuple)):
        ret += pre + '<ul>'
        for v in listObj:
            v = obj_to_html_list(v, hir + 1)
            ret += pre + '<li>' + v + '</li>'
        ret += pre + '</ul>' + LS
    return ret


if __name__ == '__main__':
    z = {
        '1': 'v1',
        '2': {'21': 'v1', '222': {'deep': 23, 'deepsub': {'deeper': 33}}, '22': 'v2'},
        '3': 'foo',
    }
    ax = dict_to_txt(z, fmt={'html': 1, 'styles': {'td': 'report3'}})
    ax2 = dict_to_txt(z, fmt={'ax': 1})
    print(ax)
    print(('<pre>%s</pre>' % ax2))
    # other tests in unittests folder
    # see also tests in the parsers folder,
    # dict_to_txt is the reverse function of parse there
