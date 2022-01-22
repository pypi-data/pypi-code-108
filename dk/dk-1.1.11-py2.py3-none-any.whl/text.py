try:
    unicode
except NameError:
    unicode = str


# XXX: this is fubar
def unicode_repr(obj):
    """Return obj as a unicode string. If obj is a (non-)unicode string, then
       first try to decode it as utf-8, then as iso-8859-1.
    """
    if isinstance(obj, unicode):
        return obj

    if isinstance(obj, str):
        try:
            return obj.decode('u8')
        except:  # noqa
            return obj.decode('l1')

    return unicode(obj)


u = unicode_repr


def utf8(obj):
    "Return a utf-8 representation of ``obj``."
    return unicode_repr(obj).encode('u8')


u8 = utf8
