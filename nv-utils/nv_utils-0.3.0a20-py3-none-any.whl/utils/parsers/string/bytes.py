from typing import Union

from nv.utils.decorators import requires
from nv.utils.encoding import decode_bytes, EncodingDetectionException
from nv.utils.typing import Raise


RAISE = Raise(EncodingDetectionException)


@requires('charset_normalizer')
def cast_bytes(obj: Union[bytes, bytearray], default: str | Raise | None = RAISE, **decoder_kwargs) -> str:
    try:
        return decode_bytes(obj, **decoder_kwargs)
    except EncodingDetectionException:
        pass

    if default is RAISE:
        default.raise_exception("unable to detect encoding of bytes object and no fallback provided via default")

    return obj.decode(encoding=default)
