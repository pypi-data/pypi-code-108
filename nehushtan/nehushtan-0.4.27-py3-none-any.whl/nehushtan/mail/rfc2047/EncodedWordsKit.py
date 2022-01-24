import quopri
import re
from base64 import b64decode, b64encode


class EncodedWordsKit:
    """
    Since 0.4.6
    """

    @staticmethod
    def decode_string_following_rfc2047(raw_string: str):
        """
        See https://datatracker.ietf.org/doc/html/rfc2047
        See https://tools.ietf.org/html/rfc2045
        Simply See https://dmorgan.info/posts/encoded-word-syntax/

        Encoded-word Syntax
        encoded-word = "=?" charset "?" encoding "?" encoded-text "?="

        `charset` is one of the character sets registered with IANA for use
            with the MIME text/plain content-type
        `encoding` is either the character Q or B,
            where B represents base64 encoding
            and Q represents an encoding similar to the “quoted-printable” content transfer encoding defined in RFC 2045
        `encoded-text` is the text encoded according to the defined `encoding`

        Sample:
        "=?UTF-8?B?5oqW5bqX?=" or =?UTF-8?B?5oqW5bqX?=
        Pared to 抖店
        """
        matched = re.match(r'"?=\?([A-Za-z0-9_-]+)\?([QB])\?(.+)\?="?', raw_string)
        if matched:
            charset = matched[1]
            encoding = matched[2]  # Q or B
            raw = matched[3]
            if encoding == 'B':
                return b64decode(raw).decode(charset)
            if encoding == 'Q':
                return quopri.decodestring(raw).decode(charset)
        return raw_string

    @staticmethod
    def encode_string_following_rfc2047(string: str, charset: str, encoding: str):
        """
        `charset` might be `UTF-8`
        `encoding` might be `Q` or `B`
        """
        byte_array = string.encode(charset)
        if encoding == 'B':
            x = b64encode(byte_array).decode()
        elif encoding == 'Q':
            x = quopri.encodestring(byte_array).decode()
        else:
            return string
        return f'=?{charset}?{encoding}?{x}?='
