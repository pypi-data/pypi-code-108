from fractions import Fraction
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from poisson_approval.meta_analysis.colors import *
from poisson_approval.meta_analysis.binary_condorcet import draw_condorcet_intervals
from poisson_approval.utils.Util import my_range


def binary_figure(xscale, yscale, size_inches='auto'):
    """Create a binary plot.

    Parameters
    ----------
    xscale : Number
        The x-scale of the figure. The higher it is, the higher the resolution of the heatmap on x-axis.
    yscale : Number
        The y-scale of the figure. The higher it is, the higher the resolution of the heatmap on y-axis.
    size_inches : tuple or str
        The horizontal and vertical sizes of the figure, in inches. If ``'auto'``, we will try to do our best.

    Returns
    -------
    figure : matplotlib.figure.Figure
    binary_ax : :class:`BinaryAxesSubplotPoisson`
    """
    binary_ax = BinaryAxesSubplotPoisson(xscale=xscale, yscale=yscale, size_inches=size_inches)
    figure = plt.gcf()
    if size_inches == 'auto':
        figure.set_size_inches(4, 4)
    else:
        figure.set_size_inches(*size_inches)
    return figure, binary_ax


class BinaryAxesSubplotPoisson:
    """Wrapper for binary plots.

    For some examples, cf. the tutorial on binary plots.
    """
    def __init__(self, xscale=None, yscale=None, size_inches='auto'):
        self.xscale = xscale
        self.yscale = yscale
        self.size_inches = size_inches

    @staticmethod
    def set_title(title, **kwargs):
        """Title of the plot.

        Notes
        -----
        For the parameters, cf. ``set_title`` in `matplotlib`.
        """
        plt.gca().set_title(title, **kwargs)

    def heatmap_intensity(self, func, x_left_label, x_right_label, y_left_label, y_right_label, reverse_right=False,
                          cmap='plasma', **kwargs):
        """Intensity heatmap.

        Parameters
        ----------
        func : callable
            The function to plot. Input: coordinates `x`, `y1`, `y2`, each in [0, 1]. Output: a number.
        x_left_label : str
            Label on the left of the x-axis.
        x_right_label : str
            Label on the right of the x-axis.
        y_left_label : str
            Label of the left y-axis.
        y_right_label : str
            Label of the right y-axis.
        reverse_right : bool
            If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
            increasing from 0 to 1).
        cmap : str
            Colormap. Default: ``'plasma'``.
        kwargs
            All other keywords arguments are passed to method ``imshow`` of `matplotlib`.

        Examples
        --------
            >>> def f(x, y1, y2):
            ...     return (x**2 + y1) / (y2 + 1)
            >>> figure, tax = binary_figure(xscale=5, yscale=5)
            >>> tax.heatmap_intensity(f,
            ...                       x_left_label='x-left',
            ...                       x_right_label='x-right',
            ...                       y_left_label='y-left',
            ...                       y_right_label='y-right')
            >>> tax.set_title('An intensity heat map')
        """
        if reverse_right:
            m = np.array([
                [func(x, y, 1 - y) for x in np.arange(.5 / self.xscale, 1., 1 / self.xscale)]
                for y in np.arange(.5 / self.yscale, 1., 1 / self.yscale)
            ])
        else:
            m = np.array([
                [func(x, y, y) for x in np.arange(.5 / self.xscale, 1., 1 / self.xscale)]
                for y in np.arange(.5 / self.yscale, 1., 1 / self.yscale)
            ])
        plt.imshow(m, origin='lower', extent=([0, 1, 0, 1]), aspect='auto', cmap=cmap, **kwargs)
        plt.annotate(x_left_label, (0, -0.025), verticalalignment='top', horizontalalignment='left',
                     annotation_clip=False)
        plt.annotate(x_right_label, (1, -0.025), verticalalignment='top', horizontalalignment='right',
                     annotation_clip=False)
        plt.tick_params(axis='x', labelbottom=False)

        ax1 = plt.gca()
        ax1.set_xlim(0, 1)
        ax1.set_ylabel(y_left_label)
        ax1.set_ylim(0, 1)
        ax1.set_yticks(np.arange(0, 1.2, .2))
        ax1.set_yticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        ax2 = ax1.twinx()
        ax2.set_ylabel(y_right_label)
        ax2.set_ylim(0, 1)
        ax2.set_yticks(np.arange(0, 1.2, .2))
        if reverse_right:
            ax2.set_yticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
        else:
            ax2.set_yticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        plt.colorbar(pad=0.15)
        if self.size_inches == 'auto':
            plt.gcf().set_size_inches(5.75, 4)

    def heatmap_candidates(self, func, x_left_label, x_right_label, y_left_label, y_right_label, reverse_right=False,
                           legend_title='', legend_style='palette', **kwargs):
        """Heatmap of a function from a 3D vector (x, y1, y2) to a 3D vector.

        Parameters
        ----------
        func : callable
            The function to plot. Input: coordinates `x`, `y1`, `y2`, each in [0, 1]. Output: a list of 3 numbers
            between 0 and 1.
        x_left_label : str
            Label on the left of the x-axis.
        x_right_label : str
            Label on the right of the x-axis.
        y_left_label : str
            Label of the left y-axis.
        y_right_label : str
            Label of the right y-axis.
        reverse_right : bool
            If True, then the y-axis on the right goes decreasing from 1 to 0 (whereas the y-axis on the left goes
            increasing from 0 to 1).
        legend_title : str
            Title of the legend.
        legend_style : str
            The style of the legend. The two available options are ``'palette'`` and ``'color_patches'``.
            Cf. :meth:`legend_palette` and :meth:`legend_color_patches`.
        kwargs
            All other keywords arguments are passed to method ``imshow`` of `matplotlib`.

        Examples
        --------
            >>> def g(x, y1, y2):
            ...     a = x**.5
            ...     b = y1**2
            ...     c = 1 - a - b
            ...     return [a, b, c]
            >>> figure, tax = binary_figure(xscale=5, yscale=5)
            >>> tax.heatmap_candidates(g,
            ...                        x_left_label='x-left',
            ...                        x_right_label='x-right',
            ...                        y_left_label='y-left',
            ...                        y_right_label='y-right',
            ...                        legend_title='Candidates',
            ...                        legend_style='palette')
            >>> tax.set_title('A candidate heat map')
        """
        if reverse_right:
            m = np.array([
                [abc_to_rgb(func(x, y, 1 - y))
                 for x in my_range(Fraction(1, 2 * self.xscale), 1, Fraction(1, self.xscale))]
                for y in my_range(Fraction(1, 2 * self.yscale), 1, Fraction(1, self.yscale))
            ], dtype=float)
        else:
            m = np.array([
                [abc_to_rgb(func(x, y, y))
                 for x in my_range(Fraction(1, 2 * self.xscale), 1, Fraction(1, self.xscale))]
                for y in my_range(Fraction(1, 2 * self.yscale), 1, Fraction(1, self.yscale))
            ], dtype=float)
        plt.imshow(m, origin='lower', extent=([0, 1, 0, 1]), aspect='auto', **kwargs)
        plt.annotate(x_left_label, (0, -0.025), verticalalignment='top', horizontalalignment='left',
                     annotation_clip=False)
        plt.annotate(x_right_label, (1, -0.025), verticalalignment='top', horizontalalignment='right',
                     annotation_clip=False)
        plt.tick_params(axis='x', labelbottom=False)

        ax1 = plt.gca()
        ax1.set_xlim(0, 1)
        ax1.set_ylabel(y_left_label)
        ax1.set_ylim(0, 1)
        ax1.set_yticks(np.arange(0, 1.2, .2))
        ax1.set_yticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        ax2 = ax1.twinx()
        ax2.set_ylabel(y_right_label)
        ax2.set_ylim(0, 1)
        ax2.set_yticks(np.arange(0, 1.2, .2))
        if reverse_right:
            ax2.set_yticklabels([1.0, 0.8, 0.6, 0.4, 0.2, 0.0])
        else:
            ax2.set_yticklabels([0.0, 0.2, 0.4, 0.6, 0.8, 1.0])

        if self.size_inches == 'auto':
            plt.gcf().set_size_inches(4, 4)
        if legend_style == 'palette':
            self.legend_palette(title=legend_title)
        else:
            self.legend_color_patches(title=legend_title, data=m)

    @staticmethod
    def annotate_condorcet(left_order, right_order, d_order_fixed_share=None):
        """Annotate who is the Condorcet winner depending on the region.

        We consider a setting where:

        * Fixed shares of voters have preference orders given by `d_order_fixed_share`.
        * The remaining voters are split between `left_order` and `right_order` in proportions that are given by the
          x coordinate.

        This method annotates the regions according to which candidate is the Condorcet winner, and indicates where no
        one is the Condorcet winner.

        Parameters
        ----------
        left_order : str
            The order whose share is maximal for x = 0.
        right_order : str
            The order whose share is maximal for x = 1.
        d_order_fixed_share : dict, optional
            Key: order. Value: a fixed share of voters in [0, 1].
        """
        draw_condorcet_intervals(plt.gca(), left_order, right_order, d_order_fixed_share)

    @staticmethod
    def legend_color_patches(title, all_mixes=False, data=None):
        """Add a "color patches" legend to the current figure (for candidates heat maps).

        Parameters
        ----------
        title : str
            Title of the legend.
        all_mixes : bool
            If True, then all mixes are indicated in the legend: `a + b`, `a + c`, `b + c` and `a + b + c`.
        data : numpy.ndarray, optional
            Array m * n * 3. This is used only if `all_mixes` is False.

        Notes
        -----
        * The color patches for single candidates `a`, `b`, `c` are in the legend anyway.
        * If `all_mixes` is True, then all mixes are indicated in the legend.
        * If `all_mixes` is False and `data` is given, then if at least a value is close to a perfect mix (like half
          of `a` and half of `b`), then this mix is added to the legend.
        """
        def _edge_color(color):
            return [max(x - .4, 0) for x in color]
        legend_elements = [Patch(facecolor=COLOR_A, edgecolor=_edge_color(COLOR_A), label='$a$'),
                           Patch(facecolor=COLOR_B, edgecolor=_edge_color(COLOR_B), label='$b$'),
                           Patch(facecolor=COLOR_C, edgecolor=_edge_color(COLOR_C), label='$c$')]
        if all_mixes or data is not None:
            def add_optional_patch(color, label, insertion=False):
                if all_mixes or (data is not None
                                 and any(np.all(np.isclose(data_col[0:3], color, atol=1E-1))
                                         for line in data for data_col in line)):
                    patch = Patch(facecolor=color, edgecolor=_edge_color(color), label=label)
                    if insertion:
                        legend_elements.insert(0, patch)
                    else:
                        legend_elements.append(patch)
            add_optional_patch(COLOR_NO_ONE, 'No one', insertion=True)
            add_optional_patch(COLOR_AB, 'a, b')
            add_optional_patch(COLOR_AC, 'a, c')
            add_optional_patch(COLOR_BC, 'b, c')
            add_optional_patch(COLOR_ABC, 'a, b, c')
        plt.gcf().legend(title=title, handles=legend_elements,
                         bbox_to_anchor=(1.1, 0.5), loc="center left")

    @staticmethod
    def legend_palette(title):
        """Add a "palette" legend to the current figure (for candidates heat maps).

        Parameters
        ----------
        title : str
            Title of the legend.

        Notes
        -----
        This is more a hack than a real `matplotlib` legend. Hence the usual commands to choose the position
        of the legend, for example, are not meant to work here.
        """
        old_ax = plt.gca()
        legend_ax = plt.gcf().add_axes([1.05, .63, .2, .2], facecolor='k')
        legend_ax.imshow(DATA_PALETTE, origin='lower', interpolation='gaussian')
        legend_ax.set_xticks([])
        legend_ax.set_yticks([])
        legend_ax.axis('off')
        legend_ax.annotate('a', (100, 169), horizontalalignment='center', verticalalignment='center')
        legend_ax.annotate('b', (35, 63), horizontalalignment='center', verticalalignment='center')
        legend_ax.annotate('c', (165, 63), horizontalalignment='center', verticalalignment='center')
        legend_ax.set_title(title)
        plt.sca(old_ax)
