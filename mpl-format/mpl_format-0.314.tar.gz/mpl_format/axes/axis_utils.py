import matplotlib.pyplot as plt
from matplotlib.axes import Axes


def new_axes(width: int = None, height: int = None,
             constrained_layout: bool = False) -> Axes:
    """
    Return new matplotlib axes.
    """
    width = width or 16
    height = height or 9
    _, ax = plt.subplots(
        figsize=(width, height),
        constrained_layout=constrained_layout
    )
    return ax
