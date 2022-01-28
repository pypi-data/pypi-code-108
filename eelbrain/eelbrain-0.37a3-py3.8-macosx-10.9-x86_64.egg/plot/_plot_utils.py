#  Utilities working with (and needing to import) plots
import os

import numpy as np

from .._utils import ui
from ._base import TimeSlicer


def save_movie(figures, filename=None, time_dilation=4, tstart=None, tstop=None, size=None, **kwargs):
    """Save a movie combining multiple figures with moving time axes

    Parameters
    ----------
    figures : dict
        ``{(xpos, ypos): figure}`` dictionary indicating placement of figures.
    filename : str
        Filename for the movie (omit to use a GUI).
    time_dilation : float
        Factor by which to stretch time (default 4). Time dilation is
        controlled through the frame-rate; if the ``fps`` keyword argument
        is specified, ``time_dilation`` is ignored.
    tstart : float
        Time axis start (default is earliest time in ``figures``).
    tstop : float
        Time axis stop (default includes latest time in ``figures``).
    ...
        :func:`imageio.mimwrite` parmeters.
    """
    import imageio
    from PIL import Image

    if filename is None:
        filename = ui.ask_saveas("Save movie...", None, [('Movie (*.mov)', '*.mov')])
        if not filename:
            return
    else:
        filename = os.path.expanduser(filename)

    time_dims = list(filter(None, (getattr(f, '_time_dim', None) for f in figures.values())))
    if tstart is None:
        tstart = min(dim.tmin for dim in time_dims)
    if tstop is None:
        tstop = max(dim.tstop for dim in time_dims)
    if 'fps' in kwargs:
        tstep = time_dilation / kwargs['fps']
    else:
        tstep = min(dim.tstep for dim in time_dims)
        kwargs['fps'] = 1. / tstep / time_dilation

    times = np.arange(tstart, tstop, tstep)

    ims = []
    x_max = y_max = None
    for t in times:
        t_ims = []
        for (x, y), fig in figures.items():
            fig.set_time(t)
            f_im = Image.fromarray(fig._im_array(), 'RGBA')
            t_ims.append((x, y, f_im))

        if x_max is None:
            x_max = max(x + im.size[0] for x, y, im in t_ims)
            y_max = max(y + im.size[1] for x, y, im in t_ims)
        im_buf = Image.new('RGBA', (x_max, y_max), (1, 1, 1, 0))

        for x, y, im in t_ims:
            im_buf.paste(im, (x, y))

        ims.append(np.array(im_buf))
    imageio.mimwrite(filename, ims, **kwargs)
