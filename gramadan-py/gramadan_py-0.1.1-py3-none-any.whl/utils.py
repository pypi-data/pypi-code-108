from typing import Union


class Utils:
    @staticmethod
    def LowerInit(s: str) -> str:
        if len(s) > 1:
            s = s[0:1].lower() + s[1:]

        return s

    @staticmethod
    def UpperInit(s: str) -> str:
        if len(s) > 1:
            s = s[0:1].upper() + s[1:]

        return s


def to_bool(val: Union[str, int, bool]):
    if isinstance(val, str):
        if val.lower() in ("t", "true", "1"):
            return True
        if val.lower() in ("f", "false", "0"):
            return False
        raise RuntimeError(f"Unrecognised string for bool {val}")
    return bool(val)
