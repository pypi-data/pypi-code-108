# -*- coding: utf-8 -*-
import io
import sys

PY2, U8 = sys.version_info[0] < 3, 'UTF-8'
if PY2:

    def unic(s):
        return s if isinstance(s, unicode) else unicode(s, encoding=U8)

    def bytes_(s):
        return s if isinstance(s, str) else s.encode(U8)


else:

    def unic(s):
        return s if isinstance(s, str) else str(s, encoding=U8)

    def bytes_(s):
        return s if isinstance(s, bytes) else bytes(s, encoding=U8)


native = bytes_ if PY2 else unic


# http://jrgraphix.net/r/Unicode/2500-257F
# e.g.: [print(chr(i)) for i in box_drawing]
class blocks:
    """usage: e.g. term.py"""

    geometric_shapes = range(0x25A0, 0x25FF)
    box_drawing = range(0x2500, 0x257F)
    arrows = range(0x2190, 0x21FF)
    basic_latin = range(0x0020, 0x007F)


def read_uni_chars_off_str(s, chars, buffer=None):
    fd = io.BytesIO(bytes_(s))
    res = read_uni_chars(fd, chars)
    fd.close()
    return res


def read_uni_chars(fd, chars, buffer=None):
    """
    read as many bytes from an fd as required to get <chars> characters back -
    as str in 2, as unicode in3
    """
    if not PY2:
        # fd must be a textio wrapper, why would you open an fd with 'rb' in
        # py3 if you want the chars?
        return fd.read(chars)

    if not chars > 0:
        return fd.read(chars)

    # now the problem: Py2, user wants 10 chars:
    # could not get this to work with BytesIO/TextIO because its late but
    # there Must be a way -> remove this crap when fit:
    buffer = buffer or chars
    s = unicode('')

    s, last_chunk_bytes = unicode(''), ''

    while True:
        chunk = fd.read(buffer)
        if not chunk:
            break
        chunk, last_chunk_bytes = split_off_incompl(chunk, last_chunk_bytes)
        if not chunk and not last_chunk_bytes:
            break
        s += chunk
        if len(s) >= chars:
            break
    return s.encode('utf-8') if PY2 else s


def split_off_incompl(chunk, pre=None):
    """
    returns the decodable part of a chunk, plus the last bytes which
    are incomplete
    """

    def is_compl(b):
        try:
            return b.decode('utf-8')
        except:
            return False

    if pre is not None:
        chunk = pre + chunk

    last = bytes_('')
    while True:
        uni = is_compl(chunk)
        if uni is not False:
            return uni, last
        chunk, l = chunk[:-1], chunk[-1]
        last = l + last


# ---------------------------------------------------------- oldish stuff below
# remove when surely uneeded
class UCs:
    """ unicode characteres. type new ones in vi (insert mode) like:
        strg-v u 2500
    """

    # for table prettyfying:
    VU = '│'
    H = '─'
    JUNC = '┼'

    NOTE = '♩'
    NOTES = '♬'
    PIEK = '♠'
    MARK = '☀'
    SKULL = '☠'
    GOOD = '☺'
    BAD = '☹'
    # not curses complient, i. not in bpython:
    EMO_SMILE = '😀'


if __name__ == '__main__':
    print('─')
    for k in dir(UCs):
        print(getattr(UCs, k))
