
def encode_id_as_hex_string(id: int) -> str:
    return id.to_bytes(length=16, byteorder="big", signed=False).hex()
