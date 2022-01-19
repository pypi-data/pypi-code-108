from enum import Enum
from typing import Union


class ARROW_STYLE(Enum):

    Curve = 1
    CurveB = 2
    BracketB = 3
    CurveFilledB = 4
    CurveA = 5
    CurveAB = 6
    CurveFilledA = 7
    CurveFilledAB = 8
    BracketA = 9
    BracketAB = 10
    Fancy = 11
    Simple = 12
    Wedge = 13
    BarAB = 14

    def get_name(self) -> str:

        return {
            'Curve': '-',
            'CurveB': '->',
            'BracketB': '-[',
            'CurveFilledB': '-|>',
            'CurveA': '<-',
            'CurveAB': '<->',
            'CurveFilledA': '<|-',
            'CurveFilledAB': '<|-|>',
            'BracketA': ']-',
            'BracketAB': ']-[',
            'Fancy': 'fancy',
            'Simple': 'simple',
            'Wedge': 'wedge',
            'BarAB': '|-|',
        }[self.name]

    @staticmethod
    def get_arrow_style(
            arrow_style: Union[str, 'ARROW_STYLE']
    ) -> str:
        if arrow_style and isinstance(arrow_style, ARROW_STYLE):
            arrow_style = arrow_style.get_name()
        return arrow_style
