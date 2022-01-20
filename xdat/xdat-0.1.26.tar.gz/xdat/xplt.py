import pandas as pd
import matplotlib.pyplot as plt
import seaborn._core
import seaborn.relational

from . import xsettings


def set_long_column_names(df):
    df = df.copy()

    renames = dict()
    for col in df.columns:
        new_name = xsettings.x_get_desc(col)
        renames[col] = new_name

    df.rename(columns=renames, inplace=True)
    return df


def match_key_value(values, hard_coded=None):
    hard_coded = hard_coded or dict()
    seen = dict()

    def get_value(key):
        key = str(key)

        if key in hard_coded:
            return hard_coded[key]

        if key in seen:
            return seen[key]

        seen[key] = values[len(seen) % len(values)]
        return seen[key]

    get_value.seen = seen
    get_value.values = values
    get_value.hard_coded = hard_coded

    return get_value


def match_colors(default_colors=None, hard_coded_colors=None):
    default_colors = xsettings.get_default(xsettings.DEFAULT_COLORS, default_colors)
    hard_coded_colors = xsettings.get_default(xsettings.HARD_CODED_COLORS, hard_coded_colors)

    return match_key_value(default_colors, hard_coded=hard_coded_colors)


def match_markers(default_markers=None, hard_coded_markers=None):
    default_markers = xsettings.get_default(xsettings.DEFAULT_MARKERS, default_markers)
    hard_coded_markers = xsettings.get_default(xsettings.HARD_CODED_MARKERS, hard_coded_markers)

    return match_key_value(default_markers, hard_coded=hard_coded_markers)


def update_axes(x=None, y=None):
    if isinstance(x, pd.Series):
        x = x.name

    if isinstance(y, pd.Series):
        y = y.name

    try:
        x = xsettings.x_get_desc(x)
        y = xsettings.x_get_desc(y)
    except TypeError:
        return

    if x:
        plt.xlabel(x)

    if y:
        plt.ylabel(y)


def decorate(x=None, y=None, xlim=None, ylim=None, title=None, show=False):
    update_axes(x=x, y=y)

    if xlim:
        plt.xlim(xlim)

    if ylim:
        plt.ylim(ylim)

    if title:
        plt.title(title)

    # plt.legend()
    plt.tight_layout()

    if show:
        plt.show()


def _sns_vp__init__(self, *args, **kwargs):
    """
    Fails for categorical that are actually numeric... need to fix
    """
    if 'data' in kwargs and isinstance(kwargs['data'], pd.DataFrame) and kwargs.get('variables', dict()).get('hue'):
        kwargs['data'] = kwargs['data'].sort_values(kwargs['variables']['hue']).reset_index(drop=True)

    return self._orig__init__(*args, **kwargs)


def _sns_add_axis_labels(self, ax, default_x="", default_y=""):
    """Add axis labels if not present, set visibility to match ticklabels."""
    # TODO ax could default to None and use attached axes if present
    # but what to do about the case of facets? Currently using FacetGrid's
    # set_axis_labels method, which doesn't add labels to the interior even
    # when the axes are not shared. Maybe that makes sense?
    if not ax.get_xlabel():
        x_visible = any(t.get_visible() for t in ax.get_xticklabels())
        label = self.variables.get("x", default_x)
        label = xsettings.x_get_desc(label)
        ax.set_xlabel(label, visible=x_visible)
    if not ax.get_ylabel():
        y_visible = any(t.get_visible() for t in ax.get_yticklabels())
        label = self.variables.get("y", default_y)
        label = xsettings.x_get_desc(label)
        ax.set_ylabel(label, visible=y_visible)


def _sns_rp_add_legend_data(self, *args, **kwargs):
    res = self._orig_add_legend_data(*args, **kwargs)
    self.legend_title = xsettings.x_get_desc(self.legend_title)
    return res


def monkey_patch_sns():
    seaborn._core.VectorPlotter._add_axis_labels = _sns_add_axis_labels

    # seaborn._core.VectorPlotter._orig__init__ = seaborn._core.VectorPlotter.__init__
    # seaborn._core.VectorPlotter.__init__ = _sns_vp__init__

    seaborn.relational._RelationalPlotter._orig_add_legend_data = seaborn.relational._RelationalPlotter.add_legend_data
    seaborn.relational._RelationalPlotter.add_legend_data = _sns_rp_add_legend_data


def monkey_patch_x_y(package, fname):
    f = getattr(package, fname)

    def f_new(x, y, *args, **kwargs):
        ret = f(x, y, *args, **kwargs)
        update_axes(x, y)
        return ret

    setattr(package, f"_{fname}_orig", f)
    setattr(package, fname, f_new)


def monkey_patch_x(package, fname):
    f = getattr(package, fname)

    def f_new(x, *args, **kwargs):
        ret = f(x, *args, **kwargs)
        update_axes(x)
        return ret

    setattr(package, f"_{fname}_orig", f)
    setattr(package, fname, f_new)


def monkey_patch():
    for fname in ['scatter', 'plot']:
        monkey_patch_x_y(plt, fname)

    for fname in ['hist']:
        monkey_patch_x(plt, fname)

    monkey_patch_sns()

