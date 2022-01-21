import itertools
import os
import sys
import textwrap
from typing import Any, Callable, Generator, List, Optional, Type

from prototools.config import (
    BORDER,
    BORDER_TYPE,
    HEIGHT,
    MARGIN,
    PADDING,
    WIDTH,
)
from prototools.utils import strip_ansi_width
from prototools.colorize import *

class Screen:
    """Representation of a console screen.

    Attributes:
        width (int): Screen width in columns.
        height (int): Screen height in rows.
    
    Example:

        >>> screen = Screen()
    """

    def __init__(self) -> None:
        self.width = WIDTH
        self.height = HEIGHT

    @staticmethod
    def clear() -> None:
        """Clear the screen."""
        os.system("cls" if os.name == "nt" else "clear")

    @staticmethod
    def flush() -> None:
        """Flush any buffered standard output to screen."""
        sys.stdout.flush()

    def input(self, prompt: str = "") -> str:
        """
        Prompt the user for input.
        
        Args:
            prompt (str): Message to display as the prompt.

        Returns:
            User's input.
        """
        return input(prompt)

    @staticmethod
    def printf(*args: Any) -> None:
        """Print the arguments to the screen.

        Args:
            *args: Variable length argument list.
        """
        print(*args, end="")

    @staticmethod
    def println(*args: Any) -> None:
        """Print the arguments to the screen, including an appended
        newline character.

        Args:
            *args: Variable length argument list.
        """
        print(*args)


class Border:
    """Menu border.

    Args:
        type (str): Type of border (ascii, light, heavy, double),
            defaults to light.

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
    
    Example:

        >>> border = Border()
        >>> border.top_left
        ┌
        >>> border = Border("ascii")
        >>> border.top_left
        +
        >>> border = Border("double")
        >>> border.set_style("heavy")
        >>> border.type
        heavy
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
        
        Example:

            >>> border = Border()
            >>> border.set_style("ascii")
            >>> border.type
            ascii
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


class Margin:
    """Menu margin.

    Attributes:
        top (int): Top margin.
        left (int): Left margin.
        bottom (int): Bottom margin.
        right (int): Right margin.

    Examples:

        >>> margin = Margin()
        >>> margin.right
        2
        >>> margin.top
        1
    """
    __slots__ = tuple(MARGIN.keys())

    def __init__(self) -> None:
        self.left = None
        self.top = None
        self.right = None
        self.bottom = None
        self.set_defaults()

    def set_defaults(self) -> None:
        for attr, value in MARGIN.items():
            setattr(self, attr, value)


class Padding:
    """Menu padding.

    Attributes:
        top (int): Top padding.
        left (int): Left padding.
        bottom (int): Bottom padding.
        right (int): Right padding.

    Examples:

        >>> padding = Padding()
        >>> padding.left
        2
        >>> padding.bottom
        1
    """
    __slots__ = tuple(PADDING.keys())

    def __init__(self) -> None:
        self.left = None
        self.right = None
        self.top = None
        self.bottom = None
        self.set_defaults()
        
    def set_defaults(self) -> None:
        for attr, value in PADDING.items():
            setattr(self, attr, value)


class Style:
    """Specify all menu styling (margins, paddings and borders).

    Args:
        margin (Margin, optional): Menu margin.
        padding (Padding, optional): Menu padding.
        border_type (str, optional): Type of menu border.

    Example:

        >>> style = Style()
        >>> style.margin.left
        2
        >>> style.border.type
        light
        >>> style.paddin.bottom
        1
    """

    def __init__(
        self, 
        margin: Optional[Margin] = None,
        padding: Optional[Padding] = None,
        border_type: Optional[str] = None,
    ) -> None:
        if margin is None:
            margin = Margin()
        if padding is None:
            padding = Padding()
        if border_type is None:
            border = Border()
        else:
            border = Border(border_type)
        self.border = border
        self.margin = margin
        self.padding = padding


class Dimension:
    """Width and height of a component.

    Args:
        width (int): Width of the component, in columns.
        height (int): Height of the component, in rows.
        dimension (Dimension, optional): An existing Dimension from
            which to duplicate the height and width.
    
    Example:

        >>> dimension = Dimension(40, 20)
        >>> dimension.width
        40
        >>> dimension.height
        20
        >>> other_dimension = Dimension()
        >>> other_dimension
        0x0
        >>> new_dimension = Dimension(dimension=dimension)
        >>> new_dimension
        40x20
    """

    def __init__(
        self, 
        width: int = 0,
        height: int = 0,
        dimension: Optional[Type["Dimension"]] = None,
    ) -> None:
        self.width = width
        self.height = height
        if dimension is not None:
            self.width = dimension.width
            self.height = dimension.height

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


class Component:
    """Base class for menu components.

    Args:
        style (Style, optional): Style for the component.
        max_dimension (Dimension, optional): Maximum dimension
            (width x height) for the menu. Defaults to width=80
            and height=40.
        color (Callable, optional): Color function for the component.

    Raises:
        TypeError: If style is not an instance of Style.

    Example:

        >>> component = Component()
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
    ) -> None:
        if style is None:
            style = Style()
        if not isinstance(style, Style):
            raise TypeError("style must be of type Style")
        if max_dimension is None:
            max_dimension = Dimension(width=WIDTH, height=HEIGHT)
        self._style = style
        self._max_dimension = max_dimension
        self._color = color if color is not None else None

    @property
    def max_dimension(self) -> Dimension:
        """Max dimension of this component."""
        return self._max_dimension
    
    @property
    def style(self) -> Style:
        """Style of this component."""
        return self._style

    @property
    def margin(self) -> int:
        """Margin of this component."""
        return self._style.margin

    @property
    def padding(self) ->  int:
        """Padding of this component."""
        return self._style.padding

    @property
    def border(self) -> str:
        """Border of this component."""
        return self._style.border

    def _calculate_border_width(self) -> int:
        """Calculate the width of the menu border.

        This will be the width of the maximum allowable dimensions
        (screen size), minus the left and right margins and the new
        character.
        If the maximum width is 80, with left and right margins set
        to 1, the border width would be 77 (80 - 1 - 1 - 1 = 70).

        Returns:
            int: Border width in columns.

        Example:

            >>> margin = Margin()
            >>> margin.left = 1
            >>> margin.right = 1
            >>> component = Component(Style(margin=margin))
            >>> component._calculate_border_width()
            77
        """
        return (self.max_dimension.width
                - self.margin.left
                - self.margin.right - 1)

    def _calculate_content_width(self) -> int:
        """Calculate the width of inner content of the border.

        This will be the width of the menu borders, minus the left and
        right padding, and minus the two vertical borders characters.
        If the border width is 77, with left and right margins set to
        2, the content width would be 71 (71 - 2 - 2 - 2 = 71).
        
        Returns:
            int: Content width in columns.

        Example:

            >>> margin = Margin()
            >>> margin.left = 1
            >>> margin.right = 1
            >>> component = Component(Style(margin=margin)) 
            >>> component.padding.left
            2
            >>> component.padding.right
            2
            >>> component._calculate_border_width()
            77
            >>> component._calculate_content_width()
            71
        """
        return (self._calculate_border_width()
                - self.padding.left
                - self.padding.right - 2)

    def generate(self) -> Generator[str, str, None]:
        """Generate the component.

        Yields:
            str: Next string of characters for drawing this component.

        Note:
            Each subclass implements `generate()`::

                Subclass_A.generate()
                Subclass_B.generate()
                Subclass_C.generate()
        """
        raise NotImplemented()

    def _c(self, border):
        if self._color is not None:
            return self._color(border)
        return border

    def _inner_horizontals(self) -> str:
        """String of inner horizontal border characters.

        Returns:
            str: Inner horizontal characters.
        """
        return u"{}".format(
            self._c(self.border.horizontal) * (self._calculate_border_width() - 2)
        )

    def _outer_horizontals(self) -> str:
        """String of outer horizontal border characters.
        """
        return u"{}".format(
            self._c(self.border.horizontal) * (self._calculate_border_width() - 2)
        )

    def _inner_horizontal_border(self) -> str:
        """Complete inner horizontal border section.

        Returns:
            str: Complete inner horizontal border.
        """
        return u"{ml}{vl}{h}{vr}".format(
            ml=" " * self.margin.left,
            vl=self._c(self.border.vertical_left),
            vr=self._c(self.border.vertical_right),
            h=self._inner_horizontals(),
        )

    def _outer_horizontal_border_bottom(self) -> str:
        """Complete outer bottom horizontal border section.

        Returns:
            str: Complete bottom menu border.
        """
        return u"{ml}{vl}{h}{vr}".format(
            ml=" " * self.margin.left,
            vl=self._c(self.border.bottom_left),
            vr=self._c(self.border.bottom_right),
            h=self._inner_horizontals(),
        )

    def _outer_horizontal_border_top(self) -> str:
        """Complete outer top horizontal border section.

        Returns:
            str: Complete top menu border.
        """
        return u"{ml}{vl}{h}{vr}".format(
            ml=" " * self.margin.left,
            vl=self._c(self.border.top_left),
            vr=self._c(self.border.top_right),
            h=self._outer_horizontals(),
        )

    def _row(self, content: str = "", align: str = "left") -> str:
        """Row of the menu.

        Args:
            content (str): Content.
            align (str): Alignment (left, center, right)

        Returns:
            str: A row of this component with the content.
        """
        return u"{ml}{v}{content}{v}".format(
            ml= " " * self.margin.left,
            v=self._c(self.border.vertical),
            content=self._content(content, align)
        )

    @staticmethod
    def _alignment(align: str) -> str:
        """Alignment of the content.

        Args:
            align (str): Alignment (left, center, right)

        Returns:
            str: A character (<: left, ^: center, >: right)
        """
        if str(align).strip() == "center":
            return "^"
        elif str(align).strip() == "right":
            return ">"
        else:
            return "<"

    def _content(self, content: str = "", align: str = "left") -> str:
        """Content of the component.

        Args:
            content (str): Content, defaults to "".
            align (str): Alignment of the content, defaults to left.

        Returns:
            str: Content.
        """
        extra = strip_ansi_width(content)
        return u"{pl}{text:{al}{width}}{pr}".format(
            pl=" " * self.padding.left,
            pr=" " * self.padding.right,
            text=content,
            al=self._alignment(align),
            width=(self._calculate_border_width()
                    - self.padding.left
                    - self.padding.right - 2 + extra),
        )


class Box(Component):
    """Optional box section.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        color (Color, optional): Color of the component.
        title (str, optional): Title of the header.
        subtitle (str, optional): Subtitle of the header.
        subtitle_align (str, optional): Subtitle alignment.
        text (str, optional): Text to be displayed.
        text_align (str, optional): Text alignment.
        textnl (str, optional): Text displayed in newlines.
        textnl_align (str, optional): Text in newlines alignment.

    Example:

        >>> t = "Prototools"
        >>> s = "... faster development"
        >>> box = Box(title=t, subtitle=s, subtitle_align="right")
        >>> render(box)
        ┌─────────────────────────────────────────────────┐
        │                                                 │
        │  Prototools                                     │
        │                                                 │
        │                         ... faster development  │
        │                                                 │
        └─────────────────────────────────────────────────┘
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
        title: Optional[str] = None,
        title_align: Optional[str] = None,
        subtitle: Optional[str] = None,
        subtitle_align: Optional[str] = None,
        text: Optional[str] = None,
        text_align: str = "left",
        textnl: Optional[str] = None,
        textnl_align: str = "left",
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)
        self.title = title
        self.title_align = title_align
        self.subtitle = subtitle
        self.subtitle_align = subtitle_align
        self.text = text
        self.text_align = text_align
        self.textnl = textnl
        self.textnl_align = textnl_align

    def generate(self) -> Generator[str, str, None]:
        """Generate the component."""
        for _ in range(self.margin.top):
            yield ""
        yield self._outer_horizontal_border_top()
        for _ in range(self.padding.top):
            yield self._row()
        if self.title is not None and self.title != "":
            yield self._row(
                content=self.title,
                align=self.title_align,
            )
        if self.subtitle is not None and self.subtitle != "":
            yield self._row()
            yield self._row(
                content=self.subtitle,
                align=self.subtitle_align,
            )
        if self.text is not None and self.text != "":
            for line in textwrap.wrap(
                self.text, 
                width=self._calculate_content_width(),
            ):
                yield self._row(content=line, align=self.text_align)
        if self.textnl is not None and self.textnl != "":
            self.textnl = textwrap.dedent(self.textnl)
            wt = textwrap.TextWrapper(width=self._calculate_content_width())
            textout = [wt.wrap(s) for s in self.textnl.split("\n") if s != ""]
            textout = list(itertools.chain.from_iterable(textout))
            for line in textout:
                yield self._row(
                    content=line,
                    align=self.textnl_align,
                )
        for _ in range(self.padding.bottom):
            yield self._row()
        yield self._outer_horizontal_border_bottom()


class Header(Component):
    """Menu header section.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        color (Color, optional): Color of the component.
        title (str, optional): Title of the header.
        subtitle (str, optional): Subtitle of the header.
        subtitle_align (str, optional): Subtitle alignment.
        show_bottom (bool): If True shows the bottom border, defaults
            to False.

    Example:

        >>> header = Header(title='Prototools')
        >>> render(header)
        ┌─────────────────────────────────────────────────┐
        │                                                 │
        │  ProtoTools                                     │
        │                                                 │
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
        title: Optional[str] = None,
        title_align: Optional[str] = None,
        subtitle: Optional[str] = None,
        subtitle_align: Optional[str] = None,
        show_bottom: bool = False,
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)
        self.title = title
        self.title_align = "center" if title_align is None else title_align
        self.subtitle = subtitle
        self.subtitle_align = subtitle_align
        self.show_bottom = show_bottom

    def generate(self) -> Generator[str, str, None]:
        """Generate the component."""
        for _ in range(self.margin.top):
            yield ""
        yield self._outer_horizontal_border_top()
        for _ in range(self.padding.top):
            yield self._row()
        if self.title is not None and self.title != "":
            yield self._row(
                content=self.title,
                align=self.title_align,
            )
        if self.subtitle is not None and self.subtitle != "":
            yield self._row()
            yield self._row(
                content=self.subtitle,
                align=self.subtitle_align,
            )
        for _ in range(self.padding.bottom):
            yield self._row()
        if self.show_bottom:
            yield self._inner_horizontal_border()


class Text(Component):
    """Menu text block section.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        color (Color, optional): Color of the component.
        text (str, optional): Text to be displayed.
        text_align (str, optional): Text alignment.
        show_top (bool): If True shows the top border, defaults
            to False.
        show_bottom (bool): If True shows the bottom border, defaults
            to False.

    Example:

        >>> message = 'This is a text section...'
        >>> text = Text(text=message)
        >>> render(text)
        │                                                 │
        │  This is a text section...                      │
        │                                                 │
    """

    def __init__(
        self, 
        style: Optional[Style] = None, 
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
        text: Optional[str] = None,
        text_align: str = "left",
        show_top: bool = False,
        show_bottom: bool = False,
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)
        self.text = text
        self.text_align = text_align
        self.show_top = show_top
        self.show_bottom = show_bottom

    def generate(self) -> Generator[str, str, None]:
        """Generate the component."""
        if self.show_top:
            yield self._inner_horizontal_border()
        for _ in range(self.padding.top):
            yield self._row()
        if self.text is not None and self.text != "":
            for line in textwrap.wrap(
                self.text, 
                width=self._calculate_content_width(),
            ):
                yield self._row(content=line, align=self.text_align)
        for _ in range(self.padding.bottom):
            yield self._row()
        if self.show_bottom:
            yield self._inner_horizontal_border()


class Items(Component):
    """Menu section for displayin the menu items.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        color (Color, optional): Color of the component.
        items (list, optional): Items of the menu to be displayed.
        items_align (str, optional): Items alignment.

    Example:

        >>> options = [Item('Accounts'), Item('Transactions')]
        >>> items = Items(items=options)
        >>> render(items)
        │                                                 │
        │  1 - Accounts                                   │
        │  2 - Transactions                               │
        │                                                 │
    """

    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
        items: Optional[List] = None,
        items_align: str = "left",
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)
        self._items = items if items is not None else []
        self.items_align = items_align
        self._top = {}
        self._bottom = {}

    @property
    def items(self) -> str:
        return self._items

    @items.setter
    def items(self, items: list) -> None:
        self._items = items

    @property
    def items_bottom(self) -> str:
        """Return a list of the names of all items that should show a
        bottom border.
        """
        return self._bottom.keys()

    @property
    def items_top(self) -> str:
        """Return a list of the names of all items that should show a
        top border.
        """
        return self._top.keys()

    def show_item_bottom(self, text: str, flag: bool) -> None:
        """Set a flag that will show a bottom border for an item with
        the specified text.

        Args:
            text (str): Text property of the item.
            flag (bool): Boolean specifying if the border should be
                shown.
        """
        if flag:
            self._bottom[text] = True
        else:
            self._bottom.pop(text, None)

    def show_item_top(self, text: str, flag: bool) -> None:
        """Set a flag that will show a top border for an item with
        the specified text.

        Args:
            text (str): Text property of the item.
            flag (bool): Boolean specifying if the border should be
                shown.
        """
        if flag:
            self._top[text] = True
        else:
            self._top.pop(text, None)

    def generate(self) -> Generator[str, str, None]:
        """Generate the component."""
        for _ in range(self.padding.top):
            yield self._row()
        for index, item in enumerate(self.items):
            if item.text in self.items_top:
                yield self._inner_horizontal_border()
            yield self._row(content=item.show(index), align=self.items_align)
            if item.text in self.items_bottom:
                yield self._inner_horizontal_border()
        for _ in range(self.padding.bottom):
            yield self._row()


class Footer(Component):
    """Menu footer section.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        color (Color, optional): Color of the component.

    Example:

        >>> footer = Footer()
        >>> render(footer)
        │                                                 │
        └─────────────────────────────────────────────────┘
    """
    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)

    
    def generate(self) -> Generator[str, str, None]:
        for _ in range(self.padding.top):
            yield self._row()
        yield self._outer_horizontal_border_bottom()
        for _ in range(self.margin.bottom):
            yield ""


class Prompt(Component):
    """Menu prompt for user input.

    Args:
        style (Style, optional): Style of the component.
        max_dimension (Dimension, optional): Maximum dimension.
        prompt (str): Prompt, defaults to ">>>".
    
    Note:

        The prompt `>>>` is generated in a newline.

    Example:
        Script::

            prompt = Prompt()
            render(prompt)

        Output::

            
            >>>
    """
    
    def __init__(
        self,
        style: Optional[Style] = None,
        max_dimension: Optional[Dimension] = None,
        color: Optional[Callable] = None,
        prompt: str = "",
    ) -> None:
        super().__init__(style=style, max_dimension=max_dimension, color=color)
        self._prompt = prompt

    @property
    def prompt(self) -> str:
        return self._prompt

    @prompt.setter
    def prompt(self, prompt) -> None:
        self._prompt = prompt
    
    def generate(self) -> Generator[str, str, None]:
        """Generate the component."""
        for _ in range(self.padding.top):
            yield ""
        for line in self.prompt.split():
            yield u"{ml}{line}".format(
                ml=" " * self.margin.left,
                line=line,
            )


def render(component: Component) -> None:
    """Render a component.

    Args:
        component (Component): Component to be rendered.
    """
    content = "\n".join(component.generate())
    Screen.printf(content + "\n")


def to_str(component: Component) -> str:
    """Render a component to string.

    Args:
        component (Component): Component to be rendered.

    Returns:
        str: String version of the component.
    """
    return "\n".join(component.generate())