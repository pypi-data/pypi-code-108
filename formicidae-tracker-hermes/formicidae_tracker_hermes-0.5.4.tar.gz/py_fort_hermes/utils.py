def _decodeVaruint32(stream):
    v = 0
    b = None
    for i in range(5):
        b = stream.read(1)
        if not len(b):
            raise RuntimeError("EOF")
        v += (b[0] & 0x7f) << (7 * i)
        if b[0] & 0x80 == 0:
            break

    if b[0] & 0x80 != 0:
        raise RuntimeError("Varuint is too large")
    return v


def _encodeVaruint32(v: int):
    if (v < 0):
        raise ValueError("%d must be positive" % v)
    if (v > 2**32 - 1):
        raise ValueError("%d is too large (max is 2^32-1)" % v)
    res = bytearray()
    while (v > 127):
        res += ((v & 0x7f) | 0x80).to_bytes(1, byteorder='big')
        v = v >> 7
    res += (v & 0x7f).to_bytes(1, byteorder='big')
    return res


def _encodeMessageToStream(stream, message):
    encodedMessageSize = _encodeVaruint32(message.ByteSize())
    stream.write(encodedMessageSize)
    stream.write(message.SerializeToString())
