from cgi import escape
from xml.dom import minidom


class BLESS_TERM:
    """Erradication the blessterm dependency which only did some ansi colors"""

    @staticmethod
    def color(color, s):
        return '\x1b[38;5;%sm%s\x1b(B\x1b[m' % (color, s)

    @staticmethod
    def nofmt(s):
        return s


#  term -> tag -> 8 means: format a tag to terminal color nummer 8.
# ax_xml __main__ prints colors all out:
TR069_STYLE = {
    'client': 'tr069_client',
    'markup': {
        'term': {
            'tag': 8,
            'text': 2,
            'attr': 0,
            'noxml': 12,
            'attr_val': 8,
            'tr_node': 8,
            'tr_leaf': 5,
            'tr_serial': 1,
        },
        'html': {
            'tag': 'rgb(142, 162, 162)',
            'text': '#00F',
            'attr': '#aaa',
            'text_bold': 1,
            'tr_leaf_bold': 1,
            'noxml': 'rgb(92, 124, 132)',
            'attr_val': '#aaa',
            'tr_node': 'rgb(104, 107, 200)',
            'tr_leaf': '#rgb(240, 232, 211)',
            'tr_serial': 'rgb(228, 50, 0)',
        },
    },
}


DEF_STYLES = {
    'client': '',
    'markup': {
        'term': {'noxml': 0, 'tag': 8, 'text': 2, 'attr': 0, 'noxml': 0, 'attr_val': 8},
        'html': {
            'indent': 2,
            'tag': '#8bd124',
            'text': '#000',
            'attr': '#555',
            'noxml': '#999',
            'attr_val': '#355',
        },
    },
}


def get_tag_val(tag, xml_str, match=None):
    """ quick access to tag values via string splitting
    FIXME: use regex...
    """

    def get_tag_content(stri):
        # string starts within a tag def, like ab='23' c='2'>foo</tag>
        # we return 'foo'
        return stri.split('</', 1)[0].split('>', 1)[1]

    if not match:
        return get_tag_content(xml_str.split('<%s' % tag, 1)[1])
    for tag_line in xml_str.split('<%s' % tag):
        tag_line = tag_line.split('</%s' % tag)[0]
        if match in tag_line:
            return get_tag_content(tag_line)


def pretty_print(xmlstr, style_overlay={}):
    """
    Called from outside, with a xml string given.

    Formats it to formats, like html or term.

    mode destines the formatting, we just search for
    control statements within it, like indent or compress
    """
    style = {}
    style.update(DEF_STYLES)
    style.update(style_overlay)
    # 1 or nothing:
    col = style.get('col')
    # 1 or nothing:
    do_indent = style.get('indent', 0)
    # semi or full or nothing:
    compress = style.get('compress')
    # html or term:
    format = style.get('format')
    if col:
        style['col_format'] = format

    try:
        el = minidom.parseString(xmlstr)
    except:
        # we should return sth - so...make it xml(text):
        xmlstr = str(xmlstr)
        if not col:
            return xmlstr
        res = col_format(xmlstr, '-', 'noxml', style)
        return escape_and_repl_html(res, style)

    if format == 'term':
        indent = int(do_indent) * ' '
        nl = '\n'
        if compress == 'full':
            nl = ''

    elif format == 'html':
        indent = int(do_indent) * '_AX_SP_'
        nl = '_AX_NL_'
        if compress == 'full':
            nl = ''
    else:
        return xmlstr

    if compress == 'semi':
        # need to pass this to the writexml
        # so that it makes a newline only at tag starts:
        style['semicompress'] = nl
        nl = ''

    myel = MyElement(el.firstChild, (col_format, style))
    # this is in minidom a function calling def writexml, which we overwrote below:
    res = myel.toprettyxml(indent=indent, newl=nl)

    # stupid html backreplacements:
    if format == 'html':
        res = escape_and_repl_html(res, style)
    return res


def escape_and_repl_html(res, style):
    # the stupid tag rewriting is to not have the writer replace it while doing toprettyxml :-/
    # replace is 2x faster then re.sub:
    res = escape(res)
    res = (
        res.replace('_AXO_', '<font color="')
        .replace('_AXC_', '">')
        .replace('_AXCC_', '</font>')
    )
    res = res.replace('_AX_SP_', '&nbsp;').replace('_AX_NL_', '<br>\n')
    res = res.replace('_AX_B_', '<b>').replace('_AX_BC_', '</b>')
    return res


def col_format(s, el, mode='tag', style={}):
    # either html or term:
    format = style.get('col_format', '')
    markup = style['markup'].get(format)
    if not markup:
        return s
    col = markup[mode]
    if mode == 'text' or mode == 'noxml':
        # keep newlines:
        if format == 'html':
            s = s.replace('\n', '_AX_NL_')
    try:
        res = check_special_clients(s, el, mode, style)
        if res:
            return res
    except:
        pass

    if format == 'html':
        if markup.get(mode + '_bold'):
            s = '%s%s%s' % ('_AX_B_', s, '_AX_BC_')
        return '_AXO_%s_AXC_%s_AXCC_' % (col, s)

    elif format == 'term':
        return BLESS_TERM.color(col, s)


def check_special_clients(s, el, mode, style):
    """ that's the main reason why we do this mess instead of
    usual xml formatting via xsl bla: """
    # special handling for some prominent clients:
    # those things are the reason y i don't use xslt:
    # the tr-069 command line client:
    if 'cwmp:ID' in str(el):
        pass
    if style.get('client', '') == 'tr069_client':
        if mode == 'tag' and s.startswith('<cwmp:'):
            begin, end = s.split(':', 1)
            if not end:
                return
            return '%s%s' % (
                col_format(begin + ':', el, mode, style),
                col_format(end, el, 'tr_leaf', style),
            )
        if not mode == 'text':
            return

        if el.tagName == 'Name':
            # coloring just the leafs of a tr-069 name:
            begin, end = s.rsplit('.', 1)
            return '%s.%s' % (
                col_format(begin, el, 'tr_node', style),
                col_format(end, el, 'tr_leaf', style),
            )
        elif el.tagName == 'SerialNumber':
            return col_format(s, el, 'tr_serial', style)


class MyElement(minidom.Element):
    """ pretty much the original, except the format calls """

    def __init__(self, el, fmt):
        self.tagName = getattr(el, 'tagName', None)
        self.nodeName = getattr(el, 'nodeName', None)
        self.prefix = el.prefix
        self.namespaceURI = el.namespaceURI
        self.childNodes = el.childNodes
        self._attrs = getattr(el, '_attrs', {})
        self._attrsNS = getattr(el, '_attrsNS', {})
        self.fmt, self.style = fmt

    def writexml(self, writer, indent='', addindent='', newl=''):
        """ this goes plain stupid through an xml tag with its attrs and text"""
        style = self.style
        close_tag = self.fmt('>', self, 'tag', style)
        # indent = current indentation
        # addindent = indentation to add to higher levels
        # newl = newline string
        writer.write(
            style.get('semicompress', '')
            + indent
            + self.fmt('<' + self.tagName, self, 'tag', style)
        )

        attrs = self._get_attributes()
        a_names = list(attrs.keys())
        a_names.sort()

        for a_name in a_names:
            # attribute names:
            writer.write(' %s' % self.fmt(' %s="' % a_name, self, 'attr', style))
            minidom._write_data(
                writer, self.fmt(attrs[a_name].value, self, 'attr_val', style)
            )
            writer.write(self.fmt('"', self, 'attr', style))

        if self.childNodes:
            if (
                not newl
                and len(self.childNodes) == 1
                and self.childNodes[0].nodeType == minidom.Node.TEXT_NODE
            ):
                writer.write(
                    '%s%s%s%s'
                    % (
                        close_tag,
                        self.fmt(self.childNodes[0].data, self, 'text', style),
                        self.fmt('</%s>' % self.tagName, self, 'tag', style),
                        newl,
                    )
                )
                return

            ind = ''
            if newl:
                ind = indent + addindent
            writer.write('%s%s' % (close_tag, newl))
            for node in self.childNodes:
                if node.nodeName == '#text':
                    if node.data.strip():
                        minidom._write_data(
                            writer,
                            '%s%s%s'
                            % (ind, self.fmt(node.data, self, 'text', style), newl),
                        )
                else:
                    MyElement(node, (self.fmt, self.style)).writexml(
                        writer, indent + addindent, addindent, newl
                    )
            writer.write(
                '%s%s%s%s'
                % (
                    style.get('semicompress', ''),
                    indent,
                    self.fmt('</%s>' % self.tagName, self, 'tag', style),
                    newl,
                )
            )
        else:
            writer.write('%s%s' % (self.fmt('/>', self, 'tag', style), newl))


if __name__ == '__main__':
    print('term colors')
    if BLESS_TERM:
        for i in range(0, 255):
            print(BLESS_TERM.color(i, str(i)))

    xml_str = "<doc><foo bar='1'>tag val</foo><foo class='err'><innerfoo>tag err</innerfoo></foo></doc>"

    print((get_tag_val('foo', xml_str)))
    print((get_tag_val('foo', xml_str, 'err')))
    print()
    print(('Pretty printing this: %s' % xml_str))
    print(('-' * 100))
    for style in [
        {'format': 'html', 'col': 1},
        {'format': 'html', 'compress': 'full', 'col': 1},
        {'format': 'term', 'col': 1, 'compress': 'full', 'indent': 1},
        {'format': 'term', 'col': 1, 'indent': 1, 'compress': 'semi'},
    ]:
        print(('.' * 100))
        print(('Style %s:' % style))
        print(('.' * 100))
        print((pretty_print(xml_str, style_overlay=style)))
        print((pretty_print('noxml', style_overlay=style)))
