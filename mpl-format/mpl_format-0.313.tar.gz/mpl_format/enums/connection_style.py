from enum import Enum
from typing import Union


class CONNECTION_STYLE(Enum):

    angle = 1
    angle_3 = 2
    arc = 3
    arc_3 = 4
    bar = 5

    def get_name(self) -> str:

        return {
            'angle': 'angle',
            'angle_3': 'angle3',
            'arc': 'arc',
            'arc_3': 'arc3',
            'bar': 'bar'
        }[self.name]

    @staticmethod
    def get_connection_style(
            connection_style: Union[str, 'CONNECTION_STYLE']
    ) -> str:
        if connection_style and isinstance(connection_style, CONNECTION_STYLE):
            connection_style = connection_style.get_name()
        return connection_style
