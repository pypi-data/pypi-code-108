import enum


class Alignment(enum.Enum):
    @classmethod
    def convert(cls, method):
        """
        Converts inputs into a
        """
        try:
            return cls(method)
        except ValueError:
            if isinstance(method, str):
                value = __conversionDict.get(method)
                if value:
                    return value
            raise

    TOP_LEFT = 0
    TOP_CENTER = 1
    TOP_RIGHT = 2
    RIGHT_CENTER = 3
    BOTTOM_RIGHT = 4
    BOTTOM_CENTER = 5
    BOTTOM_LEFT = 6
    LEFT_CENTER = 7
    CENTER_CENTER = 8


__conversionDict = {
    Alignment.TOP_LEFT: ('top left', 'tl', 'top_left', 'upper left', 'ul', 'upper_left'),
    Alignment.TOP_CENTER: ('top', 'tc', 'top_center', 'top center'),
    Alignment.TOP_RIGHT: ('top right', 'tr', 'top_right', 'upper right', 'ur', 'upper_right'),
    Alignment.RIGHT_CENTER: ('right', 'right center', 'right_center', 'rc', 'r'),
    Alignment.BOTTOM_RIGHT: ('bottom right', 'br', 'bottom_right', 'lower right', 'lr', 'lower_left'),
    Alignment.BOTTOM_CENTER: ('bottom', 'bc', 'bottom_center', 'bottom center'),
    Alignment.BOTTOM_LEFT: ('bottom left', 'bl', 'bottom_left', 'lower left', 'll', 'lower_left'),
    Alignment.LEFT_CENTER: ('left', 'left center', 'left_center', 'lc', 'l'),
    Alignment.CENTER_CENTER: ('center', 'cc', 'c', 'center center', 'center_center'),
}
