from typing import Tuple

from .math import round


class Color:
    """Color RGBA(0-1)"""

    def __init__(self, r: float = 1, g: float = 1, b: float = 1, a: float = 1):
        self.r: float = r
        self.g: float = g
        self.b: float = b
        self.a: float = a

    @property
    def rgba(self) -> Tuple[float, float, float, float]:
        return self.r, self.g, self.b, self.a

    @property
    def html_rgba(self) -> str:
        return self.color32.html_rgba

    @property
    def color32(self):
        return Color32(
            round(self.r * 255),
            round(self.g * 255),
            round(self.b * 255),
            round(self.a * 255),
        )

    def __str__(self) -> str:
        return r"{Color r: %f, g: %f, b: %f, a: %f}" % (self.r, self.g, self.b, self.a)


class Color32:
    """Color32 RGBA(0-255)"""

    def __init__(self, r: int = 255, g: int = 255, b: int = 255, a: int = 255):
        self.r: int = round(r)
        self.g: int = round(g)
        self.b: int = round(b)
        self.a: int = round(a)

    @property
    def rgba(self) -> Tuple[int, int, int, int]:
        return self.r, self.g, self.b, self.a

    @property
    def html_rgba(self) -> str:
        return "#%02X%02X%02X%02X" % (self.r, self.g, self.b, self.a)

    @property
    def color(self) -> Color:
        return Color(self.r / 255, self.g / 255, self.b / 255, self.a / 255)

    def __str__(self) -> str:
        return r"{Color32 r: %d, g: %d, b: %d, a: %d}" % (
            self.r,
            self.g,
            self.b,
            self.a,
        )


def _hex(s: str) -> int:
    if len(s) == 1:
        s *= 2
    return int(s, 16)


def _split3(s: str) -> Tuple[str, str, str]:
    per: int = len(s) // 3
    return s[0:per], s[per : per * 2], s[per * 2 :]


def _split4(s: str) -> Tuple[str, str, str, str]:
    per: int = len(s) // 4
    return s[0:per], s[per : per * 2], s[per * 2 : per * 3], s[per * 3 :]


def parse_hex_color(s: str) -> Tuple[int, int, int, int]:
    """ #RGBA #RGB RGBA RGB or dubule """

    str_color: str = s[1:] if s.startswith("#") else s

    length = len(str_color)
    sr, sg, sb, sa = "FF", "FF", "FF", "FF"
    if 6 == length or 3 == length:
        sr, sg, sb = _split3(str_color)
    elif 4 == length or 8 == length:
        sr, sg, sb, sa = _split4(str_color)
    else:
        assert False, "incorrect format for colr:%s" % str_color
    return _hex(sr), _hex(sg), _hex(sb), _hex(sa)


def parse_color32(str_color: str) -> Color32:
    """Parse hex color to Color32, the default alpha is FF
    format:
    RGB RRGGBB
    RGBA RRGGBBAA
    #RGB #RRGGBB
    #RGBA #RRGGBBAA
    """
    r, g, b, a = parse_hex_color(str_color)
    return Color32(r, g, b, a)


def parse_color(str_color: str) -> Color:
    """Parse hex color to Color, the default alpha is FF
    format:
    RGB RRGGBB
    RGBA RRGGBBAA
    #RGB #RRGGBB
    #RGBA #RRGGBBAA
    """
    return parse_color32(str_color).color
