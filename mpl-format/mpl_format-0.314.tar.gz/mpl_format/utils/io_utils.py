from matplotlib.axes import Axes, SubplotBase
from matplotlib.figure import Figure
from pathlib import Path
from seaborn import JointGrid, PairGrid
from typing import Union, Optional

from mpl_format.compound_types import PlotObject


FILE_TYPES = [
    'eps',
    'jpg',
    'jpeg',
    'pdf',
    'pgf',
    'png',
    'ps',
    'raw',
    'rgba',
    'svg',
    'svgz',
    'tif',
    'tiff',
]


def save_plot(
        plot_object: PlotObject,
        file_path: Union[str, Path],
        file_type: Optional[str] = None
):
    """
    Save a plot object to disk.

    :param plot_object: The plot object to save to disk,
    :param file_path: The file path to save the plot object to.
    :param file_type: The type of file to save.
                      Detects from filename if possible.
                      Defaults to png if not given.
    """
    if file_type is None:
        str_fp = str(file_path)
        if '.' in str_fp and any(
            str_fp.endswith(f'.{ft}') for ft in FILE_TYPES
        ):
            file_type = str_fp.split('.')[-1]
        else:
            file_type = 'png'
    if isinstance(file_path, Path):
        file_path = str(file_path)
    kwargs = {}
    plot_obj_type = type(plot_object)
    if (
            plot_obj_type is Axes or
            issubclass(plot_obj_type, Axes) or
            issubclass(plot_obj_type, SubplotBase)
    ):
        fig = plot_object.figure
        kwargs['dpi'] = fig.dpi
    elif plot_obj_type is Figure:
        fig = plot_object
        kwargs['dpi'] = fig.dpi
    elif plot_obj_type in (JointGrid, PairGrid):
        fig = plot_object
    else:
        raise ValueError(
            'plot_object must be one of Axes, Figure, JointGrid, PairGrid. '
            'Type passed was %s'
            % type(plot_object)
        )
    fig.savefig(
        '%s%s' % (
            file_path,
            ('.' + file_type if not file_path.endswith('.' + file_type) else '')
        ),
        **kwargs
    )
