import enum
import warnings
from typing import List, Dict, Optional, Union, Any
from dataclasses import dataclass, field
from .common import ColorsNormalExt


class Style(enum.Enum):
    """
    CSS-like styles used by `Table Styler`
    """
    # Text styles
    BOLD = {'fontWeight': 'bold'}
    ITALIC = {'fontStyle': 'italic'}
    # Text colours
    WHITE = {'color': ColorsNormalExt.WHITE}
    SHADE = {'color': ColorsNormalExt.SHADE}
    RED = {'color': ColorsNormalExt.RED}
    BLUE = {'color': ColorsNormalExt.BLUE}
    GREEN = {'color': ColorsNormalExt.GREEN}
    PURPLE = {'color': ColorsNormalExt.PURPLE}
    ORANGE = {'color': ColorsNormalExt.ORANGE}
    NAVY = {'color': ColorsNormalExt.NAVY}
    GREY1 = {'color': '#F4F4F4'}   # light
    GREY2 = {'color': '#848484'}   # medium
    GREY3 = {'color': '#474747'}   # dark
    BLACK = {'color': '#000000'}
    # Text background colours
    BG_SHADE = {'backgroundColor': ColorsNormalExt.SHADE}
    BG_GREY = {'backgroundColor': '#848484'}
    BG_DARK = {'backgroundColor': '#474747'}
    BG_BLACK = {'backgroundColor': ColorsNormalExt.BLACK}
    BG_GREEN = {'backgroundColor': ColorsNormalExt.GREEN}
    BG_RED = {'backgroundColor': ColorsNormalExt.RED}
    # Text alignment
    LEFT = {'textAlign': 'left'}
    CENTER = {'textAlign': 'center'}
    RIGHT = {'textAlign': 'right'}
    # Font family
    FACE_ROMAN = {'fontFamily': '"Times New Roman", "Times", "serif"'}
    FACE_SANS = {'fontFamily': '"Arial", "Helvetica", "sans-serif"'}
    FACE_MONO = {'fontFamily': '"Lucida Console", "Courier New", "monospace"'}
    FACE_CURSIVE = {'fontFamily': '"Brush Script MT", "cursive"'}
    FACE_COMIC = {'fontFamily': '"Comic Sans MS", "Comic Sans"'}
    # Font size
    SIZE_12 = {'fontSize': '12px'}
    SIZE_14 = {'fontSize': '14px'}
    SIZE_16 = {'fontSize': '16px'}
    SIZE_18 = {'fontSize': '18px'}
    SIZE_20 = {'fontSize': '20px'}
    SIZE_22 = {'fontSize': '22px'}
    SIZE_24 = {'fontSize': '24px'}


@dataclass
class TableStyler:
    """
    Creates style and formatting CSS-like classes, used for Table Visualisations.

    Args:
        rows: list of row positions or slice values, can be mixed.
        columns: list of column positions or slice values, can be mixed.
        styles: list of `Style` enums or dictionaries with style properties to be applied for the instance
        context: row background tint ("light" | "dark")
        type: formating type ("date" | "number" | "currency" | "string")
        format: format for the type ("long date" | "full date" | "yyyy-MM-dd" | "<currency: USD|GBP|EUR|JPY>" | "percent" | "decimal")
        is_global: flag for applying the style to _all_ of the table (not just rows/columns).

    Notes:
        - `.rows` must always be set, unless using `.is_global=True` flag
        - When setting `.columns`, must always have `.rows` set as well.

    Examples:
        **Use of `slice`**
        `slice(0, None)` - all entries
        `slice(1, None)` - all but except first entry
        `slice(0, -1)` - all but except last entry
        `slice(2, None, 2)` - all even entries, beginning from second entry

        **Full example of setting an instance**
        ```
        new_style = TableStyler(
            rows=[slice(1, None)],  # will apply to all but 1st row
            columns=[3, 6],  # will apply to 4th and 7th columns
            styles=[Style.BLUE, Style.BOLD],  # make text blue and bold
            type='date',  # tream as date data type
            format='full date'  # apply formatting to the date
        )
        ```

    """
    rows: List[Union[slice, int]] = field(default_factory=list)
    columns: List[Union[slice, int]] = field(default_factory=list)
    styles: List[Union[Style, Dict[str, Any]]] = field(default_factory=list)
    context: Optional[str] = None
    type: Optional[str] = None
    format: Optional[str] = None
    is_global: bool = False

    def __post_init__(self):
        # Validate the inputs
        if self.is_global is False and not self.rows:
            raise ValueError('Must specify `rows`, or use `is_global`')
        if self.is_global is True and self.rows:
            warnings.warn('Warning, `is_global` is set to True, `rows` will be ignored.', UserWarning)

    def get_style(self) -> dict:
        style = {}
        for s in self.styles:
            if isinstance(s, enum.Enum):
                s = s.value
            style.update(s)
        return style

    def get_format(self) -> dict:
        if self.type and self.format:
            return dict(type=self.type, format=self.format)
        return dict()
