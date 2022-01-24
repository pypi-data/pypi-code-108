"""
  python module to Down Translate XML

Synopsis
========

# Description

"""
import pprint

from lxml.etree import XMLParser, parse, fromstring, Comment, HTMLParser
from xmldt.element import Element, toxml
import sys

__version__ = "0.0.5"
__docformat__ = 'markdown'


class XmlDt:

    @classmethod
    def tag(cls, name):
        def decorator(func):
            def tmp(*args, **kwargs):
                return func(*args, **kwargs)

            tmp.has_alias = name
            return tmp
        return decorator

    def __init__(self, strip=False, empty=False, html=False):
        self._parser = XMLParser(recover=True) if not html else HTMLParser(recover=True)
        self._path = []
        self._hooks = []
        self._strip = strip
        self._empty = empty
        self._types = getattr(self, "_types", {})
        self._alias = {
            method.has_alias: method for method in {
                getattr(self, name) for name in dir(self)
                if callable(getattr(self, name)) and hasattr(getattr(self, name), "has_alias")}}

    def __new__(cls, xml=None, filename=None, strip=False, empty=False, html=False):
        # nao gosto, mas funciona
        self = super(XmlDt, cls).__new__(cls)
        self.__init__(strip=strip, empty=empty, html=html)

        if filename is not None or xml is not None:
            return self(xml, filename)
        else:
            return self

    def __call__(self, xml=None, filename=None):
        if filename is not None:
            self.tree = parse(filename, parser=self._parser)
            self.root = self.tree.getroot()
        elif xml is not None:
            self.tree = fromstring(xml, parser=self._parser)
            self.root = self.tree
        else:
            raise Exception("DT called without arguments")
        return self.__end__(self._recurse_node(self.root))

    def __pcdata__(self, text):
        """Method called to process text nodes. If you override it, call its superclass method to
           guarantee empty and strip options to be honored"""
        if not self._empty and str.isspace(text):
            return None
        if self._strip:
            text = text.strip()
        return text

    def __default__(self, element):
        """Default handler for XML elements, when no specific handler is defined"""
        return element.xml

    def __end__(self, result):
        """Handler called after DT process, so it can be used for final processing tasks"""
        return result

    def __comment__(self, text):
        """Handles comment texts. Returns None by default"""
        return None

    def _recurse_node(self, element):
        # copy attributes, so we can store whatever object we want
        if element.tag is Comment:
            comment = self.__comment__(element.text)
            return comment
        else:
            tag_type = self._types.get(element.tag, "string")

            if tag_type == "zero":  # ignore and skip children
                return ""

            # add to path only if required
            self._path.append(Element(element.tag, {**element.attrib}, None, self))

            tag_handler = None
            for hook in self._hooks:
                tag_handler = hook(self._path[-1])
                if tag_handler is not None:
                    break

            if tag_handler is None:
                if element.tag in self._alias:
                    tag_handler = self._alias[element.tag]
                else:
                    tag_handler = getattr(self, element.tag, self.__default__)
                    if not callable(tag_handler):
                        tag_handler = self.__default__

            # given an element, process children, returning a list of pairs
            contents = self._dt(element)      # not zero:
            elem = self._path.pop()

            if tag_type == "string":
                c_list = [ele for t, ele in contents if ele]   # FIXME?? Caso do 0 ???
                elem.c = self.__join__(c_list)

            elif tag_type == "list":
                elem.c = [e for t, e in contents]

            elif tag_type == "map":
                elem.c = {t: e for t, e in contents}

            elif tag_type == "mmap":
                raux = {}
                for t, e in contents:
                    if t in raux:
                        raux[t].append(e)
                    else:
                        raux[t] = [e]
                elem.c = raux

            else:
                raise Exception(f"Element type not recognized: {tag_type}")

            return tag_handler(elem)

    def _dt(self, tree):
        children = []    # agora retorna lista de pares (tag, conte)*
        if tree.text:
            r = self.__pcdata__(tree.text)
            if r:  # should we check for None or "" ?
                children.append(("-pcdata", r))

        for child in tree:
            children.append((child.tag, self._recurse_node(child)))
            if child.tail:
                r = self.__pcdata__(child.tail)
                if r:  # should we check for None or "" ?
                    children.append(("-pcdata", r))
        return children

    def __join__(self, child):
        return str.join("", [str(x) for x in child])

    def __getitem__(self, item):
        dt = {
            "path": lambda: self._path,
            "father": self._father,
            "gfather": self._gfather,
            "root": self._root,
            "in_context": lambda: lambda x: self._in_context(x)  # lovely!
        }
        if item in dt:
            return dt[item]()
        else:
            return None

    def _in_context(self, tag):
        return len([e for e in self._path if e.tag == tag]) > 0

    def _father(self):
        return None if len(self._path) < 1 else self._path[-1]

    def _gfather(self):
        return None if len(self._path) < 2 else self._path[-2]

    def _root(self):
        return None if len(self._path) < 1 else self._path[0]
