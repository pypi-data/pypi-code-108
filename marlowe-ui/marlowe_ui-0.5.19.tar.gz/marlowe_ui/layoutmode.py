"""
layout modes
"""

modes = [
    (0, 'Full'),
    (1, 'Simple')]

mode_default = 1
mode_example = 0


class LayoutModeImplement(object):
    """Implementation of layout selector

    mode is layout mode, it is usually one of modes
    """
    def layout(self, mode=0):
        pass
