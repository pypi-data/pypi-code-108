def refloatstr(name):
    return r'(?P<{0:s}>[-+]?(\d*(\.\d*)?|\.\d+)([Ee][+-]?\d+|))'.format(name)


def skip_to_nonblankline(enumstream, strip=True):
    """skip to non-blank line and returns it,

    enumstream yields (lineno, line)
    strip chooses wheter returned line is stripped (strip==True) or not

    (lineno, line) is retuned
    """
    while True:
        lineno, line = next(enumstream)
        strippedline = line.strip()
        if strippedline:
            if strip:
                return lineno, strippedline
            else:
                return lineno, line
