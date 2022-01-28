import os

__all__ = ["list_styles", "use", "context"]

# Get style directory and available styles
style_dir = os.path.split(os.path.realpath(__file__))[0]


def list_styles():
    """Lists all the styles (``.mplstyle`` files) available
    to use.

    Returns
    -------
    list
        A list containing the names of all available styles.
    """
    return [
        os.path.splitext(f)[0] for f in os.listdir(style_dir) if f.endswith(".mplstyle")
    ]


def get_style_path(style):
    """Returns the path to each style passed as an argument.

    Parameters
    ----------
    style : str or list of str
        The style(s) to get the paths of

    Returns
    -------
    list of str
        A list containing the paths of all requested styles.
    """
    if isinstance(style, str) or hasattr(style, "keys"):
        # If name is a single str or dict, make it a single element list.
        styles = [style]
    else:
        styles = style
    styles = list(map((lambda s: os.path.join(style_dir, s + ".mplstyle")), styles))
    return styles


def use(style):
    """Sets :mod:`matplotlib.pyplot` parameters to use the given style type.

    See :func:`.list_styles` for a list of all available styles.

    Parameters
    ----------
    style : str
        Name of the style to use.

    Examples
    --------
    To set-up your plots to use the ``default.mplstyle`` style-sheet, simply
    write::

        import finesse.plotting as fplt
        fplt.use('default')
    """
    import matplotlib.pyplot as plt

    plt.style.use(get_style_path(style))


def context(style, after_reset=False):
    """Sets :mod:`matplotlib.pyplot` parameters to use the given style type
    within the current context.

    See :func:`.list_styles` for a list of all available styles.

    Parameters
    ----------
    style : str
        Name of the style to use.

    after_reset : bool
        If True, apply style after resetting settings to their defaults;
        otherwise, apply style on top of the current settings.

    Examples
    --------
    To use the ``default.mplstyle`` style-sheet temporarily, use the `with`
    statement as so::

        import finesse.plotting as fplt
        with fplt.context('default'):
            ...
    """
    import matplotlib.pyplot as plt

    return plt.style.context(get_style_path(style), after_reset)
