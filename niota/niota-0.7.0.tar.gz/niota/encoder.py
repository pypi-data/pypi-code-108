from niota.models import hexstr


def str_to_hexstr(data: str) -> hexstr:
    return data.encode('utf-8').hex()


def hexstr_to_str(data: hexstr):
    return bytes.fromhex(data).decode('utf-8')
