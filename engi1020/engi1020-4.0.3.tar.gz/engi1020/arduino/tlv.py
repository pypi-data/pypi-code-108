def encode(v):
    """Generate TLV encoding of a Python value."""

    if type(v) == bool:
        ty = b"B"
        raw = int(v).to_bytes(1, byteorder="little")
    elif type(v) == int:
        ty = b"I"
        raw = v.to_bytes(2, byteorder="little")
    elif type(v) == str:
        ty = b"S"
        raw = v.encode("UTF-8")

    encoded = bytearray(ty)
    encoded.append(len(raw))
    encoded.extend(raw)

    return encoded


def decode(ty, raw_bytes):
    """Parse TLV-encoded bytes."""

    if ty == "B":
        if raw_bytes[0] == 0:
            return False
        elif raw_bytes[0] == 1:
            return True
        else:
            from . import ProtocolError
            raise ProtocolError(f"Invalid byte value: {raw_bytes}")

    elif ty == "E":
        from . import DeviceError
        raise DeviceError(raw_bytes.decode("ascii", "backslashreplace"))

    elif ty == "I":
        return int.from_bytes(raw_bytes, byteorder="little")

    elif ty == "S":
        return raw_bytes.decode("ascii")

    assert False and "unreachable"
