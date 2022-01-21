from typing import Any, Generator, List, Optional, Sequence, Tuple, Callable

from prototools.config import BORDER, BORDER_TYPE
from prototools.utils import strip_ansi_width


class _Border:
    """Representation of the border.

    Args:
        type (str): Type of border (ascii, light, heavy, double),
            defaults to 'light'.

    Attributes:
        type (str): Type of border.
        top_left (str): Top left corner of the menu.
        top_right (str): Top right corner of the menu.
        bottom_left (str): Bottom left corner of the menu.
        bottom_right (str): Bottom right corner of the menu.
        vertical (str): Vertical line (VL).
        vertical_left (str): VL with a protruding inner line to the R.
        vertical_right (str): VL with a protruding inner line to the L.
        horizontal (str): Horizontal line (HL).
        horizontal_bottom (str): HL with an upward inner line.
        horizontal_top (str): HL with an downward inner line.
        intersection (str): Intersection border.
    """

    def __init__(self, type: str = "light") -> None:
        self.type = type
        self.top_left = None
        self.top_right = None
        self.bottom_left = None
        self.bottom_right = None
        self.vertical = None
        self.vertical_left = None
        self.vertical_right = None
        self.horizontal = None
        self.horizontal_top = None
        self.horizontal_bottom = None
        self.intersection = None
        self.set_style(self.type)

    def set_style(self, type: str) -> None:
        """Set the type of the border.

        Args:
            type (str): Type of border (ascii, light, heavy, double).
        """
        if type in BORDER_TYPE.values():
            self.type = type
            for attr, value in BORDER.items():
                setattr(self, attr, value[type])
        else:
            raise TypeError(
                f"'type' must be 'str' and be one of the following options: "
                f"{', '.join(list(BORDER_TYPE.values()))}"
            )


class _Style:
    """Paddings and Margins for the table.

    Args:
        ml (int): Margin left.
        pl (int): Padding left.
        pr (int): Padding right.
        mr (int): Margin right.
    """

    def __init__(self, ml: int, pl: int, pr: int, mr: int) -> None:
        self.margin_left = ml
        self.padding_left = pl
        self.padding_right = pr
        self.margin_right = mr

    def paddings(self) -> int:
        """Return the paddings size."""
        return self.padding_left + self.padding_right

    def margins(self) -> int:
        """Return the margins size."""
        return self.margin_left + self.margin_right
    
    def witdh(self) -> int:
        """Return paddins and margins size."""
        return self.paddings() + self.margins()


class _Tabulate:
    """Tabulate data.

    Args:
        data (Sequence): Data to be shown.
        header (List[str], optional): Optional header of the table.
        headless (bool, optional): If True, the data has no header. If
            False, the first row of the data becomes the header.
            Defaults False.
        inner (bool, optional): If True, the inner borders are drawn.
            Defaults False.
        style (Tuple[int, ...], optional): Tuple of int representing
            the padding left, padding right, margin left and margin
            right.
        border_type (str, optional): Type of the border.
        align (str, optional): Alignment.
        color (Callable, optional): Color function for the table.
    """
    
    def __init__(
        self,
        data: Sequence,
        headers: Optional[List[str]] = None,
        headless: Optional[bool] = False,
        inner: Optional[bool] = False,
        style: Tuple[int, ...] = None,
        border_type: Optional[str] = None,
        align: Optional[str] = "<",
        color: Optional[Callable] = None,
        title: Optional[str] = None,
    ) -> None:
        self.title = title if title is not None else None
        self._color = color if color is not None else None
        self._set_defaults(style, border_type)
        self._set_data(data, headers, headless)
        self.row = len(data)
        self.col = len(data[0])
        self.inner = inner
        self.align = align
        
    def _set_defaults(self, style: Tuple[int, ...], border_type: str) -> None:
        """Set defaults."""
        if style is None:
            style = (1, 1, 1, 1)
        self.style = _Style(*style)
        if border_type is None:
            border_type = "light"
        self.border = _Border(border_type)
    
    def _set_data(
        self,
        data: Sequence,
        headers: Optional[List[str]],
        headless: bool
    ) -> None:
        """Setup data."""
        if headers is not None:
            self.headers = headers
            self.data = data
        elif headers is None and headless:
            self.headers = None
            self.data = data
        elif headers is None and not headless:
            self.headers = data[0]
            self.data = data[1:]
        self.row = len(data)
        self.col = len(data[0])
        self._transpose()
        self._calculate_widths()
        self._calculate_total_width()
    
    def _transpose(self) -> None:
        """Transpose data"""
        self.data_transposed = list(map(list, zip(*self.data)))
        
    def _is_rotated(self, rotate, data) -> None:
        if rotate:
            self.data = list(map(list, zip(*data)))
        else:
            self.data = data

    def _calculate_widths(self) -> None:
        """Calculate columns width."""
        if self._color is not None:
            self.cols_list = [
                max([len(str(e))-strip_ansi_width(str(e)) for e in i]) for i in self.data_transposed
            ]
        else:
            self.cols_list = [
                max([len(str(e)) for e in i]) for i in self.data_transposed
            ]
        if self.headers is not None:
            self.h_list = [len(str(e))-strip_ansi_width(e) for e in self.headers]
            self.cols_list = list(
                map(max, zip(self.cols_list, self.h_list))
            )
        self.cols_width = max(self.cols_list)

    def _calculate_total_width(self) -> None:
        """Calculate total width."""
        self.total_width = self.style.witdh()*2 + sum(self.cols_list) + 3

    def _c(self, border):
        if self._color is not None:
            return self._color(border)
        return border

    def _cell(
        self,
        content: str,
        width: int,
        align: Optional[str] = "<",
    ) -> str:
        """Draw a row of the table.
        
        Args:
            content (str): Content of the table cell.
            width (int): Width of the table cell.
            Align (str): Alignment of the content.

        Returns:
            str: The entire row of the table.

        ml | pl ** content:align/width ** pr | mr
        """
        extra = strip_ansi_width(str(content))
        return u"{v}{pl}{content:{align}{width}}{pr}".format(
            ml=" "* self.style.margin_left,
            v=self._c(self.border.vertical),
            content=content,
            width=width + extra,
            align=self.align,
            pl=" " * self.style.padding_left,
            pr=" " * self.style.padding_right,
        )

    def _draw_line(self, pos: str) -> str:
        """Draw a line separation.

        Args:
            width (int): Width of the table cell.
            ncols (int): Number of columns.
            pos (str): Position of the line in the table.
        
        Returns:
            str: Entire separation line.
        """
        D = {
            "T": {
                "L": self.border.top_left,
                "C": self.border.horizontal_top,
                "R": self.border.top_right,
            },
            "B": {
                "L": self.border.bottom_left,
                "C": self.border.horizontal_bottom,
                "R": self.border.bottom_right,
            },
            "M": {
                "L": self.border.vertical_left,
                "C": self.border.intersection,
                "R": self.border.vertical_right,
            },
            "H": {
                "L": self.border.vertical_left,
                "C": self.border.horizontal_top,
                "R": self.border.vertical_right,
            },
        }
        line = " "*self.style.margin_left + self._c(D[pos]["L"])
        extra = 1 if self._color is None else 5
        for w in self.cols_list:
            line += u"{content}".format(
                content=(
                    self._c(self.border.horizontal) * (w+self.style.paddings()) +
                    self._c(D[pos]["C"])
                    ),
            )
        return line[:-(extra)] + self._c(D[pos]["R"])

    def _draw_inner(self):
        line = " "*self.style.margin_left + self._c(self.border.vertical_left)
        extra = 1 if self._color is None else 5
        for w in self.cols_list:
            line += u"{content}".format(
                content=(
                    self._c(self.border.horizontal) * (w+self.style.paddings()) +
                    self._c(self.border.intersection)
                    ),
            )
        return line[:-(extra)] + self._c(self.border.vertical_right)

    def _draw_title(self):
        extra = 1 if self._color is None else 5
        extra_title = strip_ansi_width(self.title)
        line = ""
        line += u"{right}{line}{left}".format(
            right=" "*self.style.margin_left + self._c(self.border.top_left),
            line= self._c(self.border.horizontal * (self.total_width)),
            left=self._c(self.border.top_right),
        )
        line += "\n"
        line += u"{right}{line:{al}{w}}{left}".format(
            right=" "*self.style.margin_left + self._c(self.border.vertical),
            line=self.title,
            al="^",
            w=self.total_width + extra_title,
            left=self._c(self.border.vertical),
        )
        return line

    def _draw_data(self) -> str:
        content = ""
        for row in self.data:
            content += " "*self.style.margin_left
            for i, col in enumerate(row):
                content += self._cell(col, self.cols_list[i])
            content += self._c(self.border.vertical)+"\n"
            if self.inner:
                if row != self.data[-1]:
                    content += self._draw_inner() + "\n"
        return content[:-1]

    def _draw_header(self) -> str:
        content = " "*self.style.margin_left
        for i, title in enumerate(self.headers):
            content += self._cell(title, self.cols_list[i])
        content += self._c(self.border.vertical)
        return content

    def _generate(self)  -> Generator:
        if self.title is not None and self.headers is not None:
            yield self._draw_title()
            yield self._draw_line("H")
            yield self._draw_header()
            yield self._draw_line("M")
            yield self._draw_data()
            yield self._draw_line("B")
        if self.headers is not None and self.title is None:
            yield self._draw_line("T")
            yield self._draw_header()
            yield self._draw_line("M")
            yield self._draw_data()
            yield self._draw_line("B")
        if self.headers is None and self.title is None:
            yield self._draw_line("T")
            yield self._draw_data()
            yield self._draw_line("B")

    def show(self) -> None:
        """Print the entire table."""
        print("\n".join(self._generate()))

    def retrieve_str(self) -> str:
        """Returns the data as string."""
        return "\n".join(self._generate())


def to_list(d: dict, return_head=False) -> List[Any]:
    """Convert a dictionary to a list.

    Args:
        d (Dict[Any]): Dictionary to convert.
    
    Returns:
        List[Any]: List of the dictionary.
    """
    if isinstance(d, dict):
        return [(k, v) for k, v in d.items()]
    if isinstance(d, list):
        t = []
        h = [k for k in d[0].keys()]
        for i in d:
            t.append([i[k] for k in h])
        if return_head:
            return t, h
        return t


def tabulate(
    data: Sequence,
    headers: Optional[List[str]] = None,
    headless: Optional[bool] = False,
    inner: Optional[bool] = False,
    style: Tuple[int, ...] = None,
    border_type: Optional[str] = None,
    align: Optional[str] = None,
    color: Optional[Callable[[str], str]] = None,
    title: Optional[str] = None,
) -> str:
    """Display data in a table.

    Args:
        data (Sequence): Data to be shown.
        headers (List[str], optional): Optional header of the table.
        headless (bool, optional): If True, the data has no header. If
            False, the first row of the data becomes the header.
            Defaults False.
        inner (bool, optional): If True, the inner border is shown.
            Defaults False.
        style (Tuple[int, ...], optional): Tuple of int representing
            the padding left, padding right, margin left and margin
            right.
        border_type (str, optional): Type of the border.
        align (str, optional): Alignment can be left, center or right.
    
    Returns:
        str: Data ready to be printed.

    TODO: add example
    """
    alignment = {"right": ">", "center": "^", "left": "<"}
    align = align if align is not None else "left"
    t = _Tabulate(
        data=data,
        headers=headers,
        headless=headless,
        inner=inner,
        style=style,
        border_type=border_type,
        align=alignment[align],
        color=color,
        title=title,
    )
    return t.retrieve_str()


def _generate_columns(
    data: List[float],
    c: str = u"\u2589",
    bg: Optional[Callable] = None,
) -> List[str]:
    """
    TODO: Implement to show percentage instead of numbers.
    """
    def _c(s):
        if bg is not None:
            return bg(s)
        return s
    
    t = []
    for value in data:
        tmp = []
        for _ in range(value):
            tmp.append(c)
        for _ in range(value, max(data)):
            tmp.append(_c(u"\u2591"))
        t.append(tmp)
    return t


def _show_columns(origin: List[float], data: List[str]) -> None:
    """
    TODO: add proper description.
    """
    s = " "
    for i in range(max(origin) -1, -1, -1):
        for m in data:
            s = s + m[i] + " "
        yield s
        s = " "


def show_cols(
    data: List[float],
    chars: Optional[str] = None,
    fg: Optional[Callable] = None,
    bg: Optional[Callable] = None,
) -> str:
    """Prints columns representing the data.

    Args:
        data (List[float]): Data to be shown.
        chars (str, optional): Character to be used. Defaults to
            'Full Block'
        fg (Callable, optional): Foreground color. Defaults to None.
        bg (Callable, optional): Background color. Defaults to None.

    >>> data = [4, 3, 0, 2, 1]
    >>> print(show_cols(data))
    █ ░ ░ ░ ░
    █ █ ░ ░ ░
    █ █ ░ █ ░
    █ █ ░ █ █
    """
    def _c(s):
        if fg is not None:
            return fg(s)
        return s
    if chars is None:
        chars = _c(u"\u2588")
    t = _show_columns(data, _generate_columns(data, chars, bg))
    return "\n".join(t)