import sys


def toxml(tag, v, *cs):
    tag = tag 
    ats = str.join("", [f' {a}="{b}"' for a, b in v.items()])
    res = f"<{tag}{ats}"
    miolo = ""

    if len(cs) == 1 and isinstance(cs[0], (list, set, tuple)):
        for ele in cs[0]:
            miolo += toxml(tag, v, ele)
        return miolo

    for c in cs:
        if isinstance(c, (list, set, tuple)):
            for ele in c:
                miolo += toxml("item", {}, ele)

        elif isinstance(c, dict):
            for key, ele in c.items():
                miolo += toxml(key, {}, ele)
            # miolo = toxml(tag, v, miolo)

        else:
            miolo = f"{miolo} {c}" if miolo else c

    if miolo is not None and len(miolo) > 0:
        res += f">{miolo}</{tag}>"
    else:
        res += "/>"
    return res


class Element:
    def __init__(self, tag, attributes, content, dt=None):
        self._tag = tag
        self._attributes = attributes
        self._content = content
        self._dt = dt

    @property
    def tag(self):
        return self._tag

    @tag.setter
    def tag(self, value):
        self._tag = value

    @property
    def q(self):
        return self._tag

    @q.setter
    def q(self, value):
        self._tag = value

    @property
    def contents(self):
        return self._content

    @contents.setter
    def contents(self, value):
        self._content = value

    @property
    def c(self):
        return self._content

    @c.setter
    def c(self, value):
        self._content = value

    @property
    def attrs(self):
        return self._attributes

    @property
    def v(self):
        return self._attributes

    def __contains__(self, item):
        return item in self._attributes

    def __getitem__(self, item):
        return self._attributes[item] if item in self._attributes else None

    def __setitem__(self, key, value):
        self._attributes[key] = value

    def toxml(self, *, tag=None, v=None, c=None):
        tag = tag or self.tag
        if v is None:
            v = self._attributes
        ats = str.join("", [f' {a}="{b}"' for a, b in v.items()])
        res = f"<{tag}{ats}"

        if c is not None and len(c) > 0:
            res += f">{c}</{tag}>"
        elif c == "":      # allow to force an empty element. None can't be used, else following code is never called
            res += "/>"
        elif self.c is not None and len(self.c) > 0:
            res += f">{self.c}</{tag}>"
        else:
            res += "/>"

        return res

    @property
    def xml(self):
        return self.toxml()

    @property
    def father(self):
        return None if self._dt is None else self._dt["father"]

    @property
    def gfather(self):
        return None if self._dt is None else self._dt["gfather"]

    @property
    def root(self):
        return None if self._dt is None else self._dt["root"]

    @property
    def path(self):
        return None if self._dt is None else self._dt["path"]

    def in_context(self, tag):
        return None if self._dt is None else self._dt["in_context"](tag)

