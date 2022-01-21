from typing_extensions import Literal   # can't use typing.Literal for Python < 3.8

H_ALIGN = Literal['left', 'center', 'right']
V_ALIGN = Literal['top', 'center', 'bottom']
TEXT_V_ALIGN = Literal['top', 'center', 'bottom', 'baseline', 'center_baseline']
ROTATION_MODE = Literal['absolute', 'relative']
WHICH_TICKS = Literal['major', 'minor', 'both']
WHICH_AXIS = Literal['x', 'y', 'both']
SHARE_AXES = Literal['none', 'all', 'row', 'col']
FIGURE_UNITS = Literal['inches', 'pixels']
AXIS_SCALE = Literal['log', 'linear', 'symlog', 'logit']
LINE_STYLE_STR = ['solid', 'dashed', 'dashdot', 'dotted']
