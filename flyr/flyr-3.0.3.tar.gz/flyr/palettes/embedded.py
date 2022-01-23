from typing import Tuple


def ycc_to_rgb(y: int, cr: int, cb: int) -> Tuple[int, int, int]:
    r = y + 1.4075 * (cr - 128)
    g = y - 0.3455 * (cb - 128) - (0.7169 * (cr - 128))
    b = y + 1.7790 * (cb - 128)

    r = max(min(int(r), 255), 0)
    g = max(min(int(g), 255), 0)
    b = max(min(int(b), 255), 0)

    return (r, g, b)
