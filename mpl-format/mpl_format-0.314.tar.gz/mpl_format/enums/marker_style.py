from enum import Enum
from typing import Union


class MARKER_STYLE(Enum):

    nothing = 0
    point = 1
    pixel = 2
    circle = 3
    triangle_down = 4
    triangle_up = 5
    triangle_left = 6
    triangle_right = 7
    octagon = 8
    square = 9
    pentagon = 10
    star = 11
    hexagon_1 = 12
    hexagon_2 = 13
    plus = 14
    cross = 15
    diamond = 16
    diamond_thin = 17
    v_line = 18
    h_line = 19
    plus_filled = 20
    cross_filled = 21
    tick_left = 22
    tick_right = 23
    tick_up = 24
    tick_down = 25
    caret_left = 26
    caret_right = 27
    caret_up = 28
    caret_down = 29
    caret_left_base = 30
    caret_right_base = 31
    caret_up_base = 32
    caret_down_base = 33

    def get_name(self) -> str:

        return {
            'nothing': 'nothing',
            'point': 'point',
            'pixel': 'pixel',
            'circle': 'circle',
            'triangle_down': 'triangle_down',
            'triangle_up': 'triangle_up',
            'triangle_left': 'triangle_left',
            'triangle_right': 'triangle_right',
            'octagon': 'octagon',
            'square': 'square',
            'pentagon': 'pentagon',
            'star': 'star',
            'hexagon_1': 'hexagon1',
            'hexagon_2': 'hexagon2',
            'plus': 'plus',
            'cross': 'x',
            'diamond': 'diamond',
            'diamond_thin': 'thin_diamond',
            'v_line': 'vline',
            'h_line': 'hline',
            'plus_filled': 'plus_filled',
            'cross_filled': 'x_filled',
            'tick_left': 'tickleft',
            'tick_right': 'tickright',
            'tick_up': 'tickup',
            'tick_down': 'tickdown',
            'caret_left': 'caretleft',
            'caret_right': 'caretright',
            'caret_up': 'caretup',
            'caret_down': 'caretdown',
            'caret_left_base': 'caretleftbase',
            'caret_right_base': 'caretrightbase',
            'caret_up_base': 'caretupbase',
            'caret_down_base': 'caretdownbase'
        }[self.name]

    @staticmethod
    def get_marker_style(
            marker_style: Union[int, float, 'MARKER_STYLE']
    ) -> Union[str, int, float]:
        if marker_style and isinstance(marker_style, MARKER_STYLE):
            marker_style = marker_style.get_name()
        return marker_style
