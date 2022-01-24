import matplotlib.colors
import matplotlib.pyplot as plt
from mpl_toolkits import axes_grid1


# Sea NRCS color map
cdict_sea = {
    "red": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.75, 0.0, 0.0),
        (1.0, 1.0, 1.0),
    ),
    "green": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.75, 0.5, 0.5),
        (1.0, 1.0, 1.0),
    ),
    "blue": (
        (0.0, 0.0, 0.0),
        (0.25, 0.5, 0.5),
        (0.75, 1.0, 1.0),
        (1.0, 1.0, 1.0),
    ),
}

sea_cmap = matplotlib.colors.LinearSegmentedColormap("sea_cmap", cdict_sea)

# Sea light NRCS color map
cdict_sealight = {
    "red": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.75, 0.0, 0.0),
        (1.0, 1.0, 1.0),
    ),
    "green": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.75, 0.0, 0.0),
        (1.0, 1.0, 1.0),
    ),
    "blue": (
        (0.0, 0.0, 0.0),
        (0.25, 0.0, 0.0),
        (0.75, 0.5, 0.5),
        (1.0, 1.0, 1.0),
    ),
}

sealight_cmap = matplotlib.colors.LinearSegmentedColormap(
    "sealight_cmap", cdict_sealight
)

# Blue-White-Red color map
cdict_bwr = {
    "red": ((0.0, 1.0, 1.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "green": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 0.0, 0.0)),
    "blue": ((0.0, 0.0, 0.0), (0.5, 1.0, 1.0), (1.0, 1.0, 1.0)),
}

bwr_cmap = matplotlib.colors.LinearSegmentedColormap("bwr_cmap", cdict_bwr)


def add_colorbar(im, aspect=20, pad_fraction=0.5, **kwargs):
    """Add a vertical color bar to an image plot.

    Parameters
    ----------
    im :

    aspect :
         (Default value = 20)
    pad_fraction :
         (Default value = 0.5)
    **kwargs :


    Returns
    -------

    """
    divider = axes_grid1.make_axes_locatable(im.axes)
    width = axes_grid1.axes_size.AxesY(im.axes, aspect=1 / aspect)
    pad = axes_grid1.axes_size.Fraction(pad_fraction, width)
    current_ax = plt.gca()
    cax = divider.append_axes("right", size=width, pad=pad)
    plt.sca(current_ax)
    return im.axes.figure.colorbar(im, cax=cax, **kwargs)
