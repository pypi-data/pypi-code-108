import sys

_version = sys.version_info
PY2 = _version[0] == 2

if not PY2:
    string_types = (str,)
    from urllib.parse import (
        urlencode,
        quote,
        quote_plus,
        unquote,
        unquote_plus,
    )

    from base64 import decodebytes, encodebytes
    from urllib.request import urlopen


    # `b"" != ""`
    def u(s):
        # bytes => unicode/str
        if isinstance(s, bytes):
            return s.decode("utf-8")
        return s


    def b(s):
        # str/unicode => bytes
        if isinstance(s, str):
            return s.encode("utf-8")
        return s

else:
    string_types = (str, unicode)
    from urllib import (
        urlencode,
        quote,
        quote_plus,
        unquote,
        unquote_plus,
    )
    from base64 import decodestring as decodebytes
    from base64 import encodestring as encodebytes
    from urllib2 import urlopen


    # `b"" == "" == u""`
    def u(s):
        # str/bytes => unicode
        if not isinstance(s, unicode):
            return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
        return s


    def b(s):
        # str/unicode => bytes
        if isinstance(s, unicode):
            return s.encode()
        return s
