"""
HTML helper file.
"""
from .uhtml import to_html
import html.entities as _h
import string as _s
import types as _types
from .css import css
from ..text import u8


_map = map

# pylint: disable=W0232,R0903,C0111

raw_string_encodings = ('utf-8', 'iso-8859-1')


class color(object):
    black = '"#000000"'
    silver = '"#COCOCO"'
    gray = '"#808080"'
    white = '"#FFFFFF"'
    maroon = '"#800000"'
    red = '"#FF0000"'
    purple = '"#800080"'
    fuchsia = '"#FF00FF"'
    green = '"#008000"'
    lime = '"#00FF00"'
    olive = '"#808000"'
    yellow = '"#FFFF00"'
    navy = '"#000080"'
    blue = '"#0000FF"'
    teal = '"#008080"'
    aqua = '"#00FFFF"'


INLINE_ELEMENTS = '''
   a abbr acronym b basefont bdo big br cite code dfn em figure figcaption font i img input
   kbd label q s samp select small span strike strong sub sup textarea tt
   u var applet button del iframe ins map object script'''.split()

BLOCKLEVEL_ELEMENTS = '''
   address blockquote center dir div dl fieldset form h1 h2 h3 h4 h5 h6
   hr isindex menu noframes noscript ol p pre table ul dd dt frameset
   li tbody td tfoot th thead tr applet button del iframe ins map object
   script main section article nav header footer
   '''.split()


def escape_char(unichar):
    if len(unichar) > 1 and (unichar[0] == '&' and unichar[-1] == ';'):
        return str(unichar)

    o = ord(unichar)
    t = _h.codepoint2name.get(o, o)
    if t == o:
        if 0 < t < 128:
            return str(unichar)
        else:
            return ''
    else:
        return '&' + t + ';'


def escaped_array(strval):
    """Convert unicode string to list of ascii characters or
       entitydefs like &oslash; etc.
    """
    return [escape_char(ch) for ch in strval]


def escape(strval, enc=None):
    """Convert string s (potentially unicode) to a ascii string
       with entitydefs like &oslash; &aelig; etc.
    """
    if strval is None:
        return ''
    if not isinstance(strval, str):
        if enc is not None:
            strval = strval.decode(enc)
    return ''.join(escape_char(c) for c in strval)


def unescape(txt):
    """Convert text containing entitydefs into Unicode.
    """
    try:  # pragma: nocover
        from html.parser import HTMLParser
    except ImportError:  # pragma: nocover
        from HTMLParser import HTMLParser
    h = HTMLParser()
    if isinstance(txt, bytes):
        txt = txt.decode('u8')
    # this one is undocumented...
    return h.unescape(txt)


def u8escape(strval):
    return escape(strval, 'u8')


def rawstr2unicode(strval):
    for enc in raw_string_encodings:
        try:
            return strval.decode(enc)
        except UnicodeDecodeError:
            pass
    raise UnicodeError("Could not decode raw string.")


def normalize(v):
    """returns a stringified unicode version of v
    """
    if not isinstance(v, str) and not isinstance(v, bytes):
        # all 'other' objects: call their __str__ method
        v = str(v)
    elif isinstance(v, bytes):
        # str objects: try to find encoding
        v = rawstr2unicode(v)
    return v


def quote_xhtml(v):
    if '"' in v:
        v = v.replace('"', '&quot;')
    return '"%s"' % v


def quote_smart(strval):
    dq = '"' in strval
    sq = "'" in strval
    if dq and sq:
        return "'%s'" % strval.replace('"', '&quot;')
    elif dq:
        return "'%s'" % strval
    else:
        return '"%s"' % strval


def plain_attribute(strval, legal=_s.ascii_letters + _s.digits + '-._:'):
    # html 4: 3.2.2 p4 some attributes may be unquoted
    for c in strval:
        if c not in legal:
            return False
    return True


def quote_if_needed(strval):
    if plain_attribute(strval):
        return strval
    else:
        return quote_smart(strval)


quote = quote_smart


def norm_attr_name(attr):
    """``_foo_bar => _foo_bar``,  ``class_ => class``,
       ``max_height => max-height``

           >>> norm_attr_name('class_')
           'class'
           >>> norm_attr_name('z_index')
           'z-index'
    """
    if attr[0] == '_':
        return attr
    if attr[-1] == '_':
        attr = attr[:-1]
    return attr.replace('_', '-')


class EmptyString(object):
    pass


def make_unicode(obj):
    """Return obj as a unicode string. If obj is a (non-)unicode string, then
       first try to decode it as utf-8, then as iso-8859-1.
    """
    if obj is EmptyString:
        return obj

    if isinstance(obj, str):
        return obj

    if isinstance(obj, bytes):
        try:
            return obj.decode('u8')
        except:  # noqa
            return obj.decode('l1')

    return str(obj)


class xtag(object):
    """x(ml-style)tag: a tag without content or a closing tag.

       E.g. <br/> would be xtag('br')

       [2009-03-11]
           w3 validator complains that 4.01 loose should not use
           <foo />  but <foo>.
    """
    def __init__(self, tag_name, **kw):
        self._attr = {}
        self._name = tag_name
        self._nlafter = ''

        for k, v in kw.items():
            self._attr[norm_attr_name(k)] = v

    def __getattr__(self, name):
        try:
            return self._attr[norm_attr_name(name)]
        except KeyError:
            raise AttributeError

    def __setattr__(self, name, value):
        name = norm_attr_name(name)
        if name.startswith('_'):
            object.__setattr__(self, name, value)
        elif name in self._attr:
            self._attr[name] = value
        elif hasattr(self, name):
            object.__setattr__(self, name, value)
        else:
            self._attr[name] = value

    def attributes(self):
        """return a string like key="val". """
        res = []
        for k, v in sorted(list(self._attr.items())):
            if isinstance(v, css):
                v = str(v)

            if isinstance(v, bool):
                if v:
                    res.append(' %s' % k)
            elif v is EmptyString:
                res.append(' %s=""' % k)
            else:
                v = normalize(v)
                if v:
                    res.append(' %s=%s' % (k, quote(escape(v))))
        return ''.join(res)

    def _flatten(self):
        yield self

    def flatten(self):
        yield self

    def __str__(self):
        return u'<' + self._name + self.attributes() + u'>'

    def __html__(self):
        return str(self)

    def __eq__(self, other):
        if isinstance(other, bytes):
            return self.__html__() == other.decode('u8')
        if isinstance(other, str):
            return self.__html__() == other
        # if sys.version_info.major >= 3 and isinstance(other, str):
        #     pass
        return False

    __repr__ = __str__


class stag(xtag):
    """s(ingle)tag
    """
    def __str__(self):
        return '<' + self._name + self.attributes() + '>'


class tag(xtag):
    """Regular tag: outputs an open tag with attributes, followed by its
       contents, followed by a closing tag.

       Attributes can be set either as keyword arguments in the constructor
       or by assigning to attributes of the object.

       Content can be any combination of items, iterables, and generators::

         >>> table(tr(td(i) for i in range(5)), tr(td(i**i) for i in range(5)))
         <table><tr><td>0</td><td>1</td><td>2</td><td>3</td><td>4</td></tr>
         <tr><td>1</td><td>1</td><td>4</td><td>27</td><td>256</td></tr>
         </table>
         <BLANKLINE>

       NB: Attributes that conflict with Python keywords have an underline
       appended, e.g.:  ``mytag.class_ = ...``
    """
    def __init__(self, tag_name, *content, **kw):
        xtag.__init__(self, tag_name, **kw)
        if len(content) == 1 and type(content[0]) == _types.GeneratorType:
            self._content = list(content[0])
        else:
            self._content = content

    def xcontent():  # pylint: disable=E0211
        # pylint: disable=W0612
        def fget(self):
            return self._content

        def fset(self, v):
            self._content = v

        return locals()
    xcontent = property(**xcontent())

    def _flatten(self, lst=None):
        if not lst:
            return
        for item in lst:
            if isinstance(item, (str, int, float)):
                yield item
            elif isinstance(item, xtag):
                for subitem in item.flatten():
                    yield subitem
            else:
                try:
                    for subitem in self._flatten(iter(item)):
                        yield subitem
                except TypeError:
                    yield item

    def flatten(self, lst=None):
        if lst is None:
            lst = self._content
        yield self.open_tag()
        for item in self._flatten(lst):
            yield item
        yield self.close_tag()
        return

    def open_tag(self):
        return '<' + self._name + self.attributes() + '>'

    def close_tag(self):
        return '</' + self._name + '>' + self._nlafter

    def __str__(self):
        res = []
        for item in self.flatten():
            try:
                res.append(to_html(item))
            except TypeError:
                # generator found for some reason
                print(type(item), dir(item))
                raise
        return u''.join(res)


class opentag(tag):
    def flatten(self, lst=None):
        yield self.open_tag()


class closetag(tag):
    def flatten(self, lst=None):
        yield self.close_tag()


class text_grouping(tag):
    """text tag: outputs its contents without any tags around it. Useful
       for grouping at the top level.
    """
    def __init__(self, *content):
        super(text_grouping, self).__init__('text', *content)

    def flatten(self):
        return self._flatten(self._content)


class lines(text_grouping):
    """like text, except each item in content is separated with a <br> tag.
    """
    def flatten(self):
        content = []
        for c in self._content[:-1]:
            content.append(c)
            content.append('<br>')
        content.append(self._content[-1])
        return self._flatten(content)


class dtag(tag):
    """d(issappearing)tag: if the content is empty, i.e. self.content == ('',)
       this tag doesn't output anything at all. Useful for legends, table
       captions, etc.
    """
    def __str__(self):
        if self._content:
            if len(self._content) == 1 and self._content[0] == '':
                return ''
            return super(dtag, self).__str__()
        else:
            return ''

    def flatten(self, lst=None):
        if not self._content:
            return
        for item in super(dtag, self).flatten(lst):
            yield item


def _add(left, right):
    t = {}
    t.update(left)
    t.update(right)
    return t


def mktag(name, _parent=tag, _nlafter=False, **attrs):
    class _tmp(_parent):
        def __init__(self, *content, **kw):
            _parent.__init__(self, name, *content, **_add(attrs, kw))
            self._nlafter = _nlafter and '\n' or ''
    _tmp.__name__ = name
    return _tmp


def mkxtag(name, **attrs):
    class _tmp(xtag):
        def __init__(self, **kw):
            xtag.__init__(self, name, **_add(attrs, kw))
    _tmp.__name__ = name
    return _tmp


def mkdtag(name, **attrs):
    return mktag(name, _parent=dtag, **attrs)


def mkstag(name):
    return mktag(name, _parent=stag)


doctype401strict = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"\n'
    '    "http://www.w3.org/TR/html4/strict.dtd"')
doctype401transitional = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN"\n'
    '    "http://www.w3.org/TR/html4/loose.dtd"')
doctype401frameset = mkstag(
    '!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Frameset//EN"\n'
    '    "http://www.w3.org/TR/html4/frameset.dtd"')

doctype = doctype401strict


xtags = "br hr img input link col meta".split()

# for t in xtags:
#    print '%s = mkxtag("%s")' % (t,t)
#    globals()[t] = mkxtag(t)

# these are created by the forloop above.
br = mkxtag("br")
hr = mkxtag("hr")
img = mkxtag("img")
input = mkxtag("input")   # ouch!
link = mkxtag("link")
col = mkxtag("col")
meta = mkxtag("meta")


tags = '''
  a abbr acronym address applet area b base bsefont bdo big blockquote
  body button center cite code colgroup dd dfn div dl dt em
  fieldset font form frame frameset h1 h2 h3 h4 h5 h6 head html i
  iframe ins kbd label li map menu nobr noframes noscript ol
  optgroup option p param pre q s samp small span strike strong sub
  sup table tbody td textarea tfoot th thead title tr tt u ul var
  '''.split()

_nlafter = '''
  blockquote body center div dl dt fieldset form frame h1 h2 h3 h4 h5 h6
  head html iframe legend li ol option p pre table tbody title tr ul
  col colgroup
  '''.split()


# for t in tags:
#    print '%s = mktag("%s", tag, %r)' % (t,t, t in _nlafter)
#    globals()[t] = mktag(t, tag, t in _nlafter)

# these are created by the forloop above.
a = mktag("a", tag, False)
abbr = mktag("abbr", tag, False)
acronym = mktag("acronym", tag, False)
address = mktag("address", tag, False)
applet = mktag("applet", tag, False)
area = mktag("area", tag, False)
b = mktag("b", tag, False)
base = mktag("base", tag, False)
bsefont = mktag("bsefont", tag, False)
bdo = mktag("bdo", tag, False)
big = mktag("big", tag, False)
blockquote = mktag("blockquote", tag, True)
body = mktag("body", tag, True)
button = mktag("button", tag, False)
center = mktag("center", tag, True)
cite = mktag("cite", tag, False)
code = mktag("code", tag, False)
colgroup = mktag("colgroup", tag, True)
dd = mktag("dd", tag, False)
dfn = mktag("dfn", tag, False)
div = mktag("div", tag, True)
dl = mktag("dl", tag, True)
dt = mktag("dt", tag, True)
em = mktag("em", tag, False)
fieldset = mktag("fieldset", tag, True)
figure = mktag("figure", tag, True)
font = mktag("font", tag, False)
form = mktag("form", tag, True)
frame = mktag("frame", tag, True)
frameset = mktag("frameset", tag, False)
h1 = mktag("h1", tag, True)
h2 = mktag("h2", tag, True)
h3 = mktag("h3", tag, True)
h4 = mktag("h4", tag, True)
h5 = mktag("h5", tag, True)
h6 = mktag("h6", tag, True)
head = mktag("head", tag, True)
html = mktag("html", tag, True)          # same name as module :-(
i = mktag("i", tag, False)
iframe = mktag("iframe", tag, True)
ins = mktag("ins", tag, False)
kbd = mktag("kbd", tag, False)
label = mktag("label", tag, False)
li = mktag("li", tag, True)
map = mktag("map", tag, False)           # ouch!
menu = mktag("menu", tag, False)
nobr = mktag("nobr", tag, False)
noframes = mktag("noframes", tag, False)
noscript = mktag("noscript", tag, False)
ol = mktag("ol", tag, True)
optgroup = mktag("optgroup", tag, False)
option = mktag("option", tag, True)
p = mktag("p", tag, True)
param = mktag("param", tag, False)
pre = mktag("pre", tag, True)
q = mktag("q", tag, False)
s = mktag("s", tag, False)
samp = mktag("samp", tag, False)
small = mktag("small", tag, False)
span = mktag("span", tag, False)
strike = mktag("strike", tag, False)
strong = mktag("strong", tag, False)
sub = mktag("sub", tag, False)
sup = mktag("sup", tag, False)
table = mktag("table", tag, True)
tbody = mktag("tbody", tag, True)
td = mktag("td", tag, False)
textarea = mktag("textarea", tag, False)
tfoot = mktag("tfoot", tag, False)
th = mktag("th", tag, False)
thead = mktag("thead", tag, False)
title = mktag("title", tag, True)
tr = mktag("tr", tag, True)
tt = mktag("tt", tag, False)
u = mktag("u", tag, False)
ul = mktag("ul", tag, True)
var = mktag("var", tag, False)      # ouch

dtags = "caption legend figcaption".split()

# for t in dtags:
#    print '%s = mkdtag("%s")' % (t,t)
#    globals()[t] = mkdtag(t)

# created from above for loop
caption = mkdtag("caption")
figcaption = mkdtag("figcaption")
legend = mkdtag("legend")

# special case (del is a keyword)
del_ = mktag('del')
dir_ = mktag('dir')
object_ = mktag('object')

start = mkxtag('link', rel='start')
prev = mkxtag('link', rel='prev')
next = mkxtag('link', rel='next')
stylesheet = mkxtag('link', rel='stylesheet', type='text/css', media='screen')
nynorsk = mkxtag('link', rel='alternate', hreflang='nn', lang='nn')
bokmaal = mkxtag('link', rel='alternate', hreflang='nb', lang='nb')
norsk = mkxtag('link', rel='alternate', hreflang='no', lang='no')
english = mkxtag('link', rel='alternate', hreflang='en', lang='en')
pdf = mkxtag('link', rel='alternate', type='application/pdf', media='print')

script = mktag('script', type='text/javascript')
style = mktag('style', type='text/css')

text_input = mkxtag('input', type='text')
hidden_input = mkxtag('input', type='hidden')
password_input = mkxtag('input', type='password')
checkbox_input = mkxtag('input', type='checkbox')
radio_input = mkxtag('input', type='radio')
submit_button = mkxtag('input', type='submit')


class select(tag):
    def __init__(self, options, selected=None, **kw):
        if 'id' not in kw:
            kw['id'] = 'id_' + kw['name']
        super(select, self).__init__('select', **kw)
        self._options = None
        self.options = options  # assigns to property
        if selected is not None:
            selected = u8(selected)
        content = []
        for k, v in self.options:
            if u8(k) == selected:
                opt = option(v, value=k, selected='selected')
            else:
                opt = option(v, value=k)
            content.append(opt)
        self._content = tuple(content)

    def options():  # pylint: disable=E0211
        # pylint: disable=W0612
        def fset(self, options):
            if len(options) == 0:
                self._options = []
            else:
                first = options[0]

                if len(first) == 2 and not isinstance(first, str):
                    self._options = [(make_unicode(k), make_unicode(v))
                                     for (k, v) in options]
                else:
                    self._options = [(make_unicode(o), make_unicode(o))
                                     for o in options]

        def fget(self):
            return self._options

        return locals()
    options = property(**options())

    def selected():  # pylint: disable=E0211
        # pylint: disable=W0612
        def fset(self, v):
            if v not in self.values:
                raise ValueError("Only valid options can be selected.")
            self._selected = v

        def fget(self):
            return self._selected
        return locals()
    selected = property(**selected())

    def values():  # pylint: disable=E0211
        # pylint: disable=W0612
        def fget(self):
            return [k for (k, v) in self.options]
        return locals()
    values = property(**values())


class tabledesc(object):
    def __init__(self, *cols):
        self.cols = cols


class sqlresult(tag):
    def __init__(self, res, desc=None, **kw):
        super(sqlresult, self).__init__('div', **kw)

        evenstyle = css(background='lightyellow')
        oddstyle = css(background='aqua')
        # _tablestyle = css(font='9pt/16pt Verdana')

        result = []
        if desc:
            heading = [d[0] for d in desc.cols]
            tdcell = [d[1] for d in desc.cols]
            result.append(map(th, heading))
        else:
            pass

        for j, item in enumerate(res):
            if desc:
                cells = [tdcell[n](cell) for (n, cell) in enumerate(item)]
            else:
                cells = [td(cell) for cell in item]

            if j % 2 == 0:
                row = tr(cells, style=evenstyle)
            else:
                row = tr(cells, style=oddstyle)
            result.append(row)
        tbl = table(result, style=css(font='10pt Verdana', margin_left='10%'))
        self.content = (tbl,)


def page(xtitle, abody):
    """Shortcut to get a page up quickly."""
    return html(head(title(xtitle)), body(h1(xtitle), abody))
