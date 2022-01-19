from typing import Dict, Callable

from mpl_format.enums import \
    FONT_SIZE, FONT_STRETCH, FONT_STYLE, FONT_VARIANT, FONT_WEIGHT, \
    BOX_STYLE, CAP_STYLE, JOIN_STYLE, LINE_STYLE


kwarg_mappings: Dict[str, Callable] = {
    'boxstyle': BOX_STYLE.get_box_style,
    'capstyle': CAP_STYLE.get_cap_style,
    'fontsize': FONT_SIZE.get_font_size,
    'fontstretch': FONT_STRETCH.get_font_stretch,
    'fontstyle': FONT_STYLE.get_font_style,
    'fontvariant': FONT_VARIANT.get_font_variant,
    'fontweight': FONT_WEIGHT.get_font_weight,
    'joinstyle': JOIN_STYLE.get_join_style,
    'linestyle': LINE_STYLE.get_line_style
}
