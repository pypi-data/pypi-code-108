"""
New version of html.py module that works on/with Unicode.

"""
from __future__ import print_function

from typing import List, Any, Union
from dk.text import unicode_repr
import types as _types
import warnings
import html.entities as _h
from html import unescape as _unescape
import string as _s
from .css import css
_map = map

raw_string_encodings = ('utf-8', 'iso-8859-1')


def to_html(obj):
    if hasattr(obj, '__html__'):
        res = obj.__html__()
        if isinstance(res, bytes):
            warnings.warn("obj.__html__() returned bytes!: {}".format(
                obj.__class__.__name__
            ))
        return res
    if hasattr(obj, '_as_unicode'):
        return obj._as_unicode()
    if isinstance(obj, list):
        return u''.join([to_html(item) for item in obj])
    if isinstance(obj, bytes):
        return obj.decode('u8')
    if isinstance(obj, str):
        return obj

    return str(obj)


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


INLINE_ELEMENTS = u'''
   a abbr acronym b basefont bdo big br cite code dfn em figure figcaption font i img input
   kbd label q s samp select small span strike strong sub sup textarea tt
   u var applet button del iframe ins map object script'''.split()

BLOCKLEVEL_ELEMENTS = u'''
   address blockquote center dir div dl fieldset form h1 h2 h3 h4 h5 h6
   hr isindex menu noframes noscript ol p pre table ul dd dt frameset
   li tbody td tfoot th thead tr applet button del iframe ins map object
   script main section article nav header footer
   '''.split()


BOOLEAN_ATTRIBUTES = set(u'''
    allowfullscreen allowpaymentrequest async autofocus autoplay checked
    controls default disabled formnovalidate hidden ismap itemscope loop
    multiple muted nomodule novalidate open playsinline readonly required
    reversed selected truespeed
'''.split())


class EscapedString(str):
    pass


def escape_char(unichar):  # type: (str) -> str
    # if not isinstance(unichar, str):
    #     print("NOT UNICODE:", type(unichar), repr(unichar), unichar)
    #     1/0
    if isinstance(unichar, bytes):
        unichar = unichar.decode('u8')
    assert isinstance(unichar, str)
    if len(unichar) > 1 and (unichar[0] == u'&' and unichar[-1] == u';'):
        return str(unichar)

    ordch = ord(unichar)
    name = _h.codepoint2name.get(ordch, ordch)
    if name == ordch:
        if 0 < name < 128:
            return unichar
        else:
            return ''
    else:
        return u'&' + name + u';'


def escaped_array(s: str) -> List[str]:
    """Convert unicode string to list of ascii characters or
       entitydefs like &oslash; etc.
    """
    return [escape_char(ch) for ch in s]


def escape(s: Union[str, bytes], enc=None) -> str:
    """Convert string s (potentially unicode) to a unicode string
       with ascii representation, i.e.
       with entitydefs like &oslash; &aelig; etc.
    """
    if s is None:
        return u''
    if isinstance(s, bytes):
        if enc is not None:
            s = s.decode(enc)
    return u''.join(escape_char(c) for c in s)


def unescape(txt):
    """Convert text containing entitydefs into Unicode.
    """
    # from html.parser import HTMLParser
    # h = HTMLParser()
    if isinstance(txt, bytes):
        txt = txt.decode('u8')
    # this one is undocumented...
    return _unescape(txt)


def u8escape(s):
    return escape(s, 'u8')


def rawstr2unicode(s):  # type: (bytes) -> str
    # only used from normalize (below)
    for enc in raw_string_encodings:
        try:
            return s.decode(enc)
        except UnicodeDecodeError:
            pass
    raise UnicodeError("Could not decode raw string.")  # pragma: nocover


def normalize(v):   # type: (Any) -> str
    """returns a stringified unicode version of v
    """
    if isinstance(v, bytes):
        return rawstr2unicode(v)
    return str(v)


def quote_xhtml(v):  # type: (str) -> str
    if u'"' in v:
        v = v.replace(u'"', u'&quot;')
    return u'"%s"' % v


def quote_smart(strval):
    dq = u'"' in strval
    sq = u"'" in strval
    if dq and sq:
        return u"'%s'" % strval.replace(u'"', u'&quot;')
    elif dq:
        return u"'%s'" % strval
    else:
        return u'"%s"' % strval


def plain_attribute(strval, legal=_s.ascii_letters + _s.digits + '-._:'):  # type: (str, str) -> bool
    # html 4: 3.2.2 p4 some attributes may be unquoted
    for c in strval:
        if c not in legal:
            return False
    return True


def quote_if_needed(strval):  # type: (str) -> str
    if plain_attribute(strval):
        return strval
    else:
        return quote_smart(strval)


quote = quote_smart


def norm_attr_name(a):
    """``_foo_bar => _foo_bar``,  ``class_ => class``,
       ``max_height => max-height``

           >>> norm_attr_name(u'class_')
           u'class'
           >>> norm_attr_name(u'z_index')
           u'z-index'
    """
    if a[0] == u'_':
        return a
    if a[-1] == u'_':
        a = a[:-1]
    return a.replace(u'_', u'-')


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
        except UnicodeDecodeError:  # pragma: nocover
            raise
            return obj.decode('l1')

    return str(obj)


class xtag(object):
    """x(ml-style)tag: a tag without content or a closing tag.
       E.g. <br/> would be xtag('br')

       .. note:: [2009-03-11] w3 validator complains that 4.01 loose should not
                              use <foo />  but <foo>.
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
                v = str(v)  # str is correct here for both py2 and 3

            if k in BOOLEAN_ATTRIBUTES and v == '4242424242':
                res.append(u' %s ' % k)
            elif isinstance(v, bool) and k in BOOLEAN_ATTRIBUTES:
                if v:
                    res.append(u' %s' % k)
            elif v is EmptyString:
                res.append(' %s=""' % k)
            else:
                v = normalize(v)
                if v:
                    res.append(u' %s=%s' % (k, quote(escape(v))))
        return u''.join(res)

    def _flatten(self):
        yield self

    def flatten(self):
        yield self

    def __str__(self):
        return u'<' + self._name + self.attributes() + u'>'

    def __html__(self):  # type: () -> str
        return str(self)

    def __eq__(self, other):
        if isinstance(other, (bytes, str)):
            return self.__html__() == other
        return False

    __repr__ = __str__


class stag(xtag):
    """s(ingle)tag
    """
    def __str__(self):
        return u'<' + self._name + self.attributes() + u'>'


class tag(xtag):
    """Regular tag: outputs an open tag with attributes, followed by its
       contents, followed by a closing tag.

       Attributes can be set either as keyword arguments in the constructor
       or by assigning to attributes of the object.

       Content can be any combination of items, iterables, and generators:

         >> table(tr(td(i) for i in range(5)), tr(td(i**i) for i in range(5)))

       NB: Attributes that conflict with Python keywords have an underline
       appended, e.g.:  ``mytag.class_ = ...``
    """
    def __init__(self, tag_name, *content, **kw):
        super(tag, self).__init__(tag_name, **kw)
        if len(content) == 1 and type(content[0]) == _types.GeneratorType:
            self._content = list(content[0])
        else:
            self._content = content

    @property
    def xcontent(self):
        return self._content

    @xcontent.setter
    def xcontent(self, v):
        self._content = v

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
        return u'<' + self._name + self.attributes() + u'>'

    def close_tag(self):
        return u'</' + self._name + u'>' + self._nlafter

    def __str__(self):
        res = []
        for item in self.flatten():
            try:
                res.append(to_html(item))       # XXX: 12: unicode_repr
            except TypeError:  # pragma: nocover
                # generator found for some reason
                print(type(item), dir(item))
                raise
        return u''.join(res)


# unused?
class opentag(tag):  # pragma: nocover
    def flatten(self, lst=None):
        yield self.open_tag()


# unused?
class closetag(tag):  # pragma: nocover
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
            content.append(u'<br>')
        content.append(self._content[-1])
        return self._flatten(content)


class dtag(tag):
    """d(issappearing)tag: if the content is empty, i.e. self.content == ('',)
       this tag doesn't output anything at all. Useful for legends, table
       captions, etc.
    """
    def _as_unicode(self):
        if self._content:
            if len(self._content) == 1 and self._content[0] == u'':
                return u''
            return super(dtag, self)._as_unicode()
        else:
            return u''

    def flatten(self, lst=None):
        if not self._content:
            return
        for item in super(dtag, self).flatten(lst):
            yield item


def _add(a, b):
    t = {}
    t.update(a)
    t.update(b)
    return t


def mktag(name, _parent=tag, _nlafter=False, **attrs):
    class _tmp(_parent):
        def __init__(self, *content, **kw):
            super(_tmp, self).__init__(name, *content, **_add(attrs, kw))
            self._nlafter = _nlafter and '\n' or ''
    _tmp.__name__ = name
    return _tmp


def mkxtag(name, **attrs):
    class _tmp(xtag):
        def __init__(self, **kw):
            super(_tmp, self).__init__(name, **_add(attrs, kw))
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
#     globals()[t] = mkxtag(t)

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
#     globals()[t] = mktag(t, tag, t in _nlafter)


class a(tag):
    def __init__(self, *content, **kw):
        super(a, self).__init__('a', *content, **kw)
        self._nlafter = ''


# these are created by the forloop above.
# a = mktag("a", tag, False)
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
#     globals()[t] = mkdtag(t)

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
        if 'id' not in kw and 'name' in kw and kw['name']:
            kw['id'] = 'id_' + kw['name']
        super(select, self).__init__('select', **kw)
        self._options = None
        self.options = options
        if selected is not None:
            selected = str(selected)
        content = []
        for k, v in self.options:
            if str(k) == selected:
                opt = option(v, value=k, selected='selected')
            else:
                opt = option(v, value=k)
            content.append(opt)
        self._content = tuple(content)

    @property
    def options(self):
        return self._options

    @options.setter
    def options(self, options):
        if len(options) == 0:
            self._options = []
        else:
            first = options[0]

            if len(first) == 2 and not isinstance(first, str):
                self._options = [(unicode_repr(k), unicode_repr(v))
                                 for (k, v) in options]
            else:
                self._options = [(unicode_repr(o), unicode_repr(o))
                                 for o in options]

    @property
    def selected(self):
        return self._selected

    @selected.setter
    def selected(self, v):
        if v not in self.values:
            raise ValueError("Only valid options can be selected.")
        self._selected = v

    @property
    def values(self):
        return [k for (k, v) in self.options]


class tabledesc(object):
    def __init__(self, *cols):
        self.cols = cols
