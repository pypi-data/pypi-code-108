"""
WiP.

Soon.
"""

# region [Imports]

# * Standard Library Imports ---------------------------------------------------------------------------->
from abc import ABC, abstractmethod
from typing import Any, Union, Iterable, Optional
from pathlib import Path
from colorsys import hls_to_rgb, hsv_to_rgb, rgb_to_hls, rgb_to_hsv
from functools import cached_property

# * Third Party Imports --------------------------------------------------------------------------------->
import attr

# * Gid Imports ----------------------------------------------------------------------------------------->
from gidapptools.general_helper.color.preset_colors.web_colors import get_webcolors_data

try:
    from PySide6.QtGui import QColor
    PYSIDE6_AVAILABLE = True
except ImportError:
    PYSIDE6_AVAILABLE = False

# endregion[Imports]

# region [TODO]


# endregion [TODO]

# region [Logging]


# endregion[Logging]

# region [Constants]

THIS_FILE_DIR = Path(__file__).parent.absolute()

# endregion[Constants]

INT_OR_FLOAT = Union[int, float]

COLOR_FLOAT_TYPE = Union[tuple[float, float, float], tuple[float, float, float, float]]

COLOR_INT_TYPE = Union[tuple[int, int, int], tuple[int, int, int, float]]


def _validate_color_float(instance: object, attribute: attr.Attribute, value: Optional[float]) -> None:

    if 0.0 > value > 1.0:

        raise ValueError(f"{attribute.name!r}-value can only be between 0 and 1, not {value!r}.")


def _alpha_converter(alpha: Union[int, float] = None) -> float:
    if alpha is None:
        return 1.0

    return float(alpha)


class BaseColor(ABC):
    float_round_n: int = 4

    def __iter__(self):
        return (getattr(self, field.name) for field in attr.fields(self.__class__) if field.metadata.get("is_core_color", False) is True)

    @abstractmethod
    def as_rgb_float(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        ...

    @abstractmethod
    def as_rgb_int(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_INT_TYPE:
        ...

    @abstractmethod
    def as_hls(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        ...

    @abstractmethod
    def as_hsv(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        ...

    @cached_property
    def qcolor(self) -> Optional["QColor"]:
        if PYSIDE6_AVAILABLE:
            return QColor(*self.as_rgb_int(True, True))

    def to_q_style_rgba_string(self,) -> str:
        values = (str(i) for i in self.as_rgb_int(alpha_as_int=True))
        return "rgba(" + ', '.join(values) + ')'

    def __repr__(self) -> str:
        class_name = self.__class__.__name__.removesuffix("Color")
        _out = f"{class_name}(" + ', '.join(repr(x) for x in self)
        if self.name is not None:
            _out += f', name={self.name!r}'

        if self.aliases:
            _out += f", aliases={tuple(self.aliases)!r}"
        return _out + ')'

    def with_alpha(self, alpha: Union[int, float]) -> "BaseColor":
        if isinstance(alpha, int) or alpha > 1:
            alpha = round(alpha / 255, self.float_round_n)
        return self.__class__(*list(self)[:-1], alpha)


@attr.s(auto_attribs=True, auto_detect=True, slots=True, weakref_slot=True, frozen=True, order=True, repr=False)
class RGBColor(BaseColor):
    red: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    green: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    blue: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})

    alpha: float = attr.ib(default=1.0, converter=_alpha_converter, validator=_validate_color_float, metadata={'is_core_color': True})

    name: str = attr.ib(default=None)
    aliases: Iterable[str] = attr.ib(factory=set, converter=attr.converters.default_if_none(factory=set))

    def as_rgb_float(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = list(self)[:-1]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_rgb_int(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_INT_TYPE:
        _out = [int(sub_col * 255) for sub_col in list(self)[:-1]]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_hls(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in rgb_to_hls(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return _out

    def as_hsv(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in rgb_to_hsv(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return _out


@attr.s(auto_attribs=True, auto_detect=True, slots=True, weakref_slot=True, frozen=True, order=True, repr=False)
class HLSColor(BaseColor):
    hue: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    saturation: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    lightness: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})

    alpha: float = attr.ib(default=1.0, converter=_alpha_converter, validator=_validate_color_float, metadata={'is_core_color': True})

    name: str = attr.ib(default=None)
    aliases: Iterable[str] = attr.ib(factory=set, converter=attr.converters.default_if_none(factory=set))

    def as_hls(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = list(self)[:-1]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_rgb_float(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in hls_to_rgb(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_rgb_int(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_INT_TYPE:
        _out = [int(sub_col * 255) for sub_col in hls_to_rgb(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_hsv(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in rgb_to_hsv(*hls_to_rgb(*list(self)[:-1]))]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return _out


@attr.s(auto_attribs=True, auto_detect=True, slots=True, weakref_slot=True, frozen=True, order=True, repr=False)
class HSVColor(BaseColor):
    hue: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    saturation: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})
    value: float = attr.ib(validator=_validate_color_float, metadata={'is_core_color': True})

    alpha: float = attr.ib(default=1.0, converter=_alpha_converter, validator=attr, metadata={'is_core_color': True})

    name: str = attr.ib(default=None)
    aliases: Iterable[str] = attr.ib(factory=set, converter=attr.converters.default_if_none(factory=set))

    def as_hsv(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = list(self)[:-1]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_hls(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in rgb_to_hls(*hsv_to_rgb(*list(self)[:-1]))]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return _out

    def as_rgb_float(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_FLOAT_TYPE:
        _out = [round(col, self.float_round_n) for col in hsv_to_rgb(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)

    def as_rgb_int(self, include_alpha: bool = True, alpha_as_int: bool = False) -> COLOR_INT_TYPE:
        _out = [int(sub_col * 255) for sub_col in hsv_to_rgb(*list(self)[:-1])]
        if include_alpha is True:
            if alpha_as_int is True:
                _out.append(int(self.alpha * 255))
            else:
                _out.append(self.alpha)
        return tuple(_out)


color_class_map: dict[str, type[BaseColor]] = {"rgb": RGBColor,
                                               "hls": HLSColor,
                                               "hsv": HSVColor}


class ColorRegistry:

    def __init__(self) -> None:
        self.colors_by_name: dict[str:RGBColor] = {}
        self.colors_by_rgba_value: dict[tuple[float, float, float, float]:RGBColor] = {}

    def _add_color(self, color: RGBColor) -> None:
        if color.name:
            self.colors_by_name[color.name.casefold()] = color
        for alias in color.aliases:
            self.colors_by_name[alias.casefold()] = color

        self.colors_by_rgba_value[color.as_rgb_float(True, False)] = color

    def get_color(self, r: float, g: float, b: float, alpha: float = 1.0, name: str = None, aliases: Iterable[str] = None) -> RGBColor:
        if name is not None:
            if color := self.colors_by_name.get(name.casefold()):
                return color
        if color := self.colors_by_rgba_value.get((r, g, b, alpha)):
            return color

        color = RGBColor(r, g, b, alpha, name, aliases)
        self._add_color(color)
        return color

    def color_factory(self, r: Union[int, float], g: Union[int, float], b: Union[int, float], alpha: float = 1.0, name: str = None, aliases: Iterable[str] = None):

        if any(sub_v > 1 for sub_v in (r, g, b)) or all(isinstance(sub_v, int) for sub_v in (r, g, b)):
            values = tuple(round(sub_v / 255, BaseColor.float_round_n) for sub_v in (r, g, b))

        if alpha is not None and alpha > 1:
            alpha = round(alpha / 255, BaseColor.float_round_n)
        return self.get_color(*values, alpha=alpha, name=name, aliases=aliases)

    def __call__(self, r: Union[int, float], g: Union[int, float], b: Union[int, float], alpha: float = 1.0, name: str = None, aliases: Iterable[str] = None) -> Any:
        return self.color_factory(r, g, b, alpha, name, aliases)

    def get_color_by_name(self, name: str) -> "RGBColor":
        return self.colors_by_name[name.casefold()]


Color = ColorRegistry()
for p_color in get_webcolors_data():
    Color(**p_color)

# region[Main_Exec]
if __name__ == '__main__':
    pass
# endregion[Main_Exec]
