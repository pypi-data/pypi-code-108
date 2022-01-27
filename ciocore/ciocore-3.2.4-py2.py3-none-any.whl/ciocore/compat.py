import sys
if sys.version_info < (3,):
    import codecs
    def u(x):
        return codecs.unicode_escape_decode(x)[0]

    text_type = unicode
    binary_type = str
else:
    def u(x):
        return str(x)

    text_type = str
    binary_type = bytes

