import numpy as np

def to_byt(str_or_byt):
    """
    Converts a plain string to a byte string (python2/3 compatibility)
    """

    str_out = str_or_byt.encode('utf8') if not isinstance(str_or_byt, bytes) else str_or_byt

    return str_out


def to_str(str_or_byt, strip=True):
    """
    Converts a byte string to a plain string (python2/3 compatibility)
    """

    str_out = str_or_byt.decode('utf8') if isinstance(str_or_byt, bytes) else str_or_byt

    if strip:
        return str_out.strip()
    else:
        return str_out


def to_small_endian(var):

    var = np.array(var)
    if var.dtype.byteorder == '>':
        var = var.newbyteorder().byteswap(inplace=True)
    return var
