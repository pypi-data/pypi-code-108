# This file is part of Sympathy for Data.
# Copyright (c) 2016, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import sys
import copy
import numbers
from collections import defaultdict, OrderedDict, Iterable

import numpy as np
import matplotlib
import matplotlib.cm as cm
from matplotlib import collections as mpl_collections
from matplotlib import container as mpl_container
from matplotlib import dates as mpl_dates
from matplotlib import image as mpl_image
from matplotlib import lines as mpl_lines
from matplotlib import patches as mpl_patches
from matplotlib.text import Text
from matplotlib.ticker import FixedLocator
from matplotlib.transforms import IdentityTransform

from sylib.figure import colors, models, mpl_utils
from sympathy.platform.exceptions import sywarn
from sympathy.platform.exceptions import SyConfigurationError
from sympathy.platform.exceptions import SyDataError
from sympathy.typeutils import figure
from sympathy.typeutils.figure import SyAxes


def make_iterable(X, N):
    """
    If object X is not an array or list, then create a list containing N copies
    of X. If X is already iterable then keep it.
    """

    if X is None:
        return [None]*N
    if not (isinstance(X, np.ndarray) or isinstance(X, list)):
        return [X]*N
    else:
        return X


def make_iterable_or_none(X, N):
    """If X is None then return None, otherwise if object X is not an
    array or list, then create a list containing N copies of X. If X
    is already iterable then keep it."""

    if X is None:
        return None
    if not (isinstance(X, np.ndarray) or isinstance(X, list)):
        return [X]*N
    else:
        return X


def reconstruct_twin_axes(start_axes, axes):
    """Reconstruct the relationship between overlaying twin axes."""
    sibling_axes = {start_axes: (1, 1)}
    shared_ax = {ax: (ax._sharex, ax._sharey) for ax in axes}

    for ax in axes:
        if ax in sibling_axes.keys():
            continue
        has_shared = shared_ax.get(ax)
        if has_shared is not None and has_shared != (None, None):
            sharex, sharey = has_shared
            if sharex is not None and sharey is None:
                x_parent_pos = sibling_axes.get(sharex)
                pos = x_parent_pos[0], x_parent_pos[1] + 1
            elif sharex is None and sharey is not None:
                y_parent_pos = sibling_axes.get(sharey)
                pos = y_parent_pos[0] + 1, y_parent_pos[1]
            else:
                raise ValueError('Unknown axes configuration')
            sibling_axes[ax] = pos
    return sibling_axes


def create_axes(figure, positions):
    """
    Return the twin axes given by `xaxis`, `yaxis`.

    Parameters
    ----------
    figure : matplotlib Figure
        The figure that will get new axes.
    positions : list of tuples
        Each tuple contains the name of an xaxis position ('botton' or 'top')
        and a yaxis position ('left' or 'right').

    Returns
    -------
    axes_dict : dict
        A dictionary containing the requested axes.
    """
    bottom_left = ('bottom', 'left')
    bottom_right = ('bottom', 'right')
    top_left = ('top', 'left')
    top_right = ('top', 'right')
    axes_dict = {}
    default_ax = figure.first_subplot().get_mpl_axes()
    axes_dict[bottom_left] = default_ax

    if bottom_right in positions:
        axes_dict[bottom_right] = default_ax.twinx()
        if bottom_left not in positions and top_left not in positions:
            # twinx() will already hide the xaxis of the default_ax
            default_ax.yaxis.set_visible(False)

    if top_left in positions:
        axes_dict[top_left] = default_ax.twiny()
        if bottom_left not in positions and bottom_right not in positions:
            # twiny() will already hide the yaxis of the default_ax
            default_ax.xaxis.set_visible(False)

    if top_right in positions:
        if top_left in positions:
            axes_dict[top_right] = axes_dict[top_left].twinx()
            if bottom_left not in positions and bottom_right not in positions:
                # twinx() will hide the xaxis of the top-left axes
                axes_dict[top_left].yaxis.set_visible(False)
        elif bottom_right in positions:
            axes_dict[top_right] = axes_dict[bottom_right].twiny()
            if bottom_left not in positions and bottom_right not in positions:
                # twiny() will hide the yaxis of the bottom-right axes
                axes_dict[bottom_right].xaxis.set_visible(False)
        else:
            axes_dict[bottom_right] = default_ax.twinx()
            if bottom_left not in positions and top_left not in positions:
                # twinx() will already hide the xaxis of the default_ax
                default_ax.yaxis.set_visible(False)

            axes_dict[top_right] = axes_dict[bottom_right].twiny()
            if bottom_left not in positions and bottom_right not in positions:
                # twiny() will hide the yaxis of the bottom-right axes
                default_ax.xaxis.set_visible(False)
                axes_dict[bottom_right].xaxis.set_visible(False)

    return axes_dict


def get_twin_axes(axes_dict, xaxis, yaxis):
    """
    Return the twin axes given by `xaxis`, `yaxis`.

    Parameters
    ----------
    axes_dict : dict
        A dictionary containing at least the default axes
        with xaxis='bottom' and yaxis='left'.
    xaxis : unicode
        The name of the xaxis. Supported values are 'bottom' and 'top'.
    yaxis : unicode
        The name of the yaxis. Supported values are 'left' and 'right'.

    Returns
    -------
    ax : matplotlib.axes._subplots.AxesSubplot
    """
    ax = axes_dict.get((xaxis, yaxis), None)
    default_axes = axes_dict[('bottom', 'left')]
    if isinstance(default_axes, figure.SyAxes):
        default_axes = default_axes.get_mpl_axes()
    if ax is None:
        if xaxis == 'bottom' and yaxis == 'right':
            ax = default_axes.twinx()
        elif xaxis == 'top' and yaxis == 'left':
            ax = default_axes.twiny()
        elif xaxis == 'top' and yaxis == 'right':
            x1y2axes = get_twin_axes(axes_dict, 'bottom', 'right')
            ax = x1y2axes.twiny()
        else:
            raise ValueError('The axes type "{}, {}" is not '
                             'supported.'.format(xaxis, yaxis))
        axes_dict[(xaxis, yaxis)] = ax
    return ax


def classify_axes(axes):
    """
    Classify the axes in the scheme ('bottom', 'left').

    The axes get stored with a (x,y) key in a dictionary
    depending on their shared x or y axes. The first axes
    will always be set as ('bottom', 'left').
    """
    if len(axes):
        classed_axes = reconstruct_twin_axes(axes[0], axes)
        xaxis_options = ['bottom', 'top']
        yaxis_options = ['left', 'right']
        return {(xaxis_options[v[0]-1], yaxis_options[v[1]-1]): k
                for k, v in classed_axes.items()}
    return {}


def get_sorted_axes(axes_dict):
    """Sort axes dictionary."""
    order = [('bottom', 'left'),
             ('bottom', 'right'),
             ('top', 'left'),
             ('top', 'right')]
    return OrderedDict([(ax_id, axes_dict.get(ax_id))
                        for ax_id in order
                        if axes_dict.get(ax_id) is not None])


def _get_mpl_axes(source, target):
    if isinstance(target, figure.SyAxes):
        target = target.get_mpl_axes()
    if isinstance(source, figure.SyAxes):
        source = source.get_mpl_axes()
    return source, target


def _get_colorbar_axes(axes):
    """
    Helper function which returns all axes of colorbars linked to artists.

    Parameters
    ----------
    axes : list
        A list of matplotlib Axes.

    Returns
    -------
    cb_axes : set
    """
    cb_axes = []
    for ax in axes:
        for artist_type in ['images', 'collections']:
            for artist in getattr(ax, artist_type):
                if artist.colorbar is not None:
                    cb_axes.append(artist.colorbar.ax)
    return cb_axes


def _copy_axis_visibility(source, target):
    """
    Copies visibility and color properties from each X/Y axis in the source
    axes object to the target axes object.
    """
    if not source.get_xaxis().get_visible():
        target.get_xaxis().set_visible(False)
    if not source.get_yaxis().get_visible():
        target.get_yaxis().set_visible(False)
    target.set_facecolor(source.get_facecolor())


def _move_artists(source, target, existing_colors,
                  auto_recolor=True, clear_labels=False):
    """
    Move all supported artists from a source to a target axes.
    """
    colorbars = {}
    handles_labels = []

    handles_labels.extend(_move_lines_to(
        source, target, existing_colors, auto_recolor=auto_recolor,
        clear_labels=clear_labels))
    handles_labels.extend(_copy_patches_to(
        source, target, clear_labels=clear_labels))
    _copy_spines_to(source, target)
    cbs, collection_handles_labels = _move_collections_to(
        source, target, existing_colors, auto_recolor=auto_recolor,
        clear_labels=clear_labels)
    if cbs:
        colorbars['collections'] = cbs
    handles_labels.extend(collection_handles_labels)
    handles_labels.extend(_move_containers_to(
        source, target, clear_labels=clear_labels))
    _move_text_to(source, target)
    cbs, image_handles_labels = _move_images_to(
        source, target, clear_labels=clear_labels)
    if cbs:
        colorbars['images'] = cbs
    handles_labels.extend(image_handles_labels)

    total_handles = []
    total_labels = []
    for handle, label in handles_labels:
        if not label or label.startswith('_'):
            continue
        total_labels.append(label)
        total_handles.append(handle)
    return colorbars, total_handles, total_labels


def _move_lines_to(source, target, existing_colors,
                   auto_recolor=True, clear_labels=False):
    """
    Move a line artist from a source to a target axes.

    Remove the line artist from the source mpl.axes and
    add it to the target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []
    for i, line in enumerate(source.lines):
        # create new Line2D object
        x, y = line.get_data()
        new_line = mpl_lines.Line2D(x, y)
        new_line.update_from(line)
        if clear_labels:
            new_line.set_label(None)
        # this is a bit of a hack to remove axes specific properties
        new_line.set_transform(IdentityTransform())
        new_line._transformed_path = None
        new_line._transformSet = False
        new_line._xy = None
        new_line._x = None
        new_line._y = None
        handles_labels.append((new_line, new_line.get_label()))

        # auto assign new color from mpl color_cycle
        if auto_recolor:
            count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
                existing_colors)
            current_color = colors.color2hex(new_line.get_color())
            if current_color in unique_cols:
                # assign a new color
                if len(unused_cols):
                    new_color = unused_cols[0]
                else:
                    least_occuring_color = unique_cols[
                        np.argsort(count_cols)[0]]
                    if len(least_occuring_color):
                        new_color = least_occuring_color
                    else:
                        new_color = mpl_utils.color_cycle[0]()
            else:
                new_color = current_color
            new_line.set_color(new_color)
        target.add_line(new_line)
        existing_colors.append(new_line.get_color())
    return handles_labels


def _move_images_to(source, target, clear_labels=False):
    """
    Move image artists from a source to a target axes.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.
    clear_labels : bool, optional
        Set True if artist labels should be removed.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    handles_labels = []
    for i, image in enumerate(source.images):
        im = mpl_image.AxesImage(target,
                                 image.get_cmap(),
                                 image.norm,
                                 image.get_interpolation(),
                                 image.origin,
                                 image.get_extent(),
                                 filternorm=image.get_filternorm(),
                                 filterrad=image.get_filterrad(),
                                 resample=image.get_resample())
        im.set_data(image.get_array())
        im.set_alpha(image.get_alpha())
        if clear_labels:
            im.set_label(None)
        handles_labels.append((im, im.get_label()))

        if im.get_clip_path() is None:
            im.set_clip_path(target.patch)
        vmin, vmax = image.get_clim()
        if vmin is not None or vmax is not None:
            im.set_clim(vmin, vmax)
        else:
            im.autoscale_None()
        im.set_url(image.get_url())

        extent = im.get_extent()
        im.set_extent(extent)
        target.add_image(im)
        colorbar_params = _get_colorbar_properties(image)
        cbs.append((im, colorbar_params))
    return cbs, handles_labels


def _move_collections_to(source, target, existing_colors,
                         auto_recolor=True, clear_labels=False):
    """
    Move collection artists from a source to a target axes.

    Only some types of collections are supported.

    Parameters
    ----------
    source : SyAxes or matplotlib.axes.Axes
        The source axes from which artists are copied.
    target : SyAxes or matplotlib.axes.Axes
        The target axes into which artists are pasted.
    existing_colors : list
        A list of colors used by artists of the target axes. New used colors
        get appended to the list to be available to other '_move__to' helper
        functions.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored.
    clear_labels : bool, optional
        Set True if artist labels should be removed.

    Returns
    -------
    cbs : list
        A list of tuples (artist, colorbar properties dict).
    """
    source, target = _get_mpl_axes(source, target)
    cbs = []
    handles_labels = []
    for i, collection in enumerate(source.collections):
        kwargs = {}
        if isinstance(collection, mpl_collections.PathCollection):
            new_collection, kwargs = _move_path_collection(collection, target)
        elif isinstance(collection, mpl_collections.PolyCollection):
            new_collection, kwargs = _move_poly_collection(collection, target)
        elif isinstance(collection, mpl_collections.LineCollection):
            new_collection = mpl_collections.LineCollection(
                collection.get_segments())
            new_collection.update_from(collection)
            new_collection.set_transform(target.transData)
        elif isinstance(collection, mpl_collections.QuadMesh):
            new_collection = mpl_collections.QuadMesh(
                collection._meshWidth,
                collection._meshHeight,
                collection._coordinates,
                shading=collection._shading)
            new_collection.update_from(collection)
            new_collection.set_transform(target.transData)
            new_collection.set_cmap(collection.get_cmap())
        else:
            # Unsupported collection type. Skipping!
            continue
        if clear_labels:
            new_collection.set_label(None)
        handles_labels.append((new_collection, new_collection.get_label()))

        # auto assign new color from mpl color_cycle
        if auto_recolor:
            _set_unique_collection_color(new_collection, existing_colors)
        target.add_collection(new_collection, **kwargs)
        colorbar_params = _get_colorbar_properties(collection)
        cbs.append((new_collection, colorbar_params))
        target.autoscale_view()
    return cbs, handles_labels


def _move_poly_collection(collection, target):
    """Move a single PolyCollection to target axes."""

    verts = [p.vertices for p in collection.get_paths()]
    sizes = collection.get_sizes()

    new_collection = mpl_collections.PolyCollection(verts, sizes)
    new_collection.update_from(collection)
    new_collection._transformSet = False

    # now update the datalim and autoscale
    for path in collection.get_paths():
        target.dataLim.update_from_path(
            path, ignore=target.ignore_existing_data_limits,
            updatex=True, updatey=True)

    return new_collection, {'autolim': False}


def _move_path_collection(collection, target):
    """Move a single PathCollection to target axes."""
    x, y = collection.get_offsets().T
    # create a new Collection object
    new_collection = mpl_collections.PathCollection(
        collection.get_paths(),
        collection.get_sizes(),
        offsets=collection.get_offsets(),
        transOffset=target.transData,
        alpha=collection.get_alpha())

    new_collection.update_from(collection)
    new_collection.set_cmap(collection.get_cmap())
    if target._xmargin < 0.05 and x.size > 0:
        target.set_xmargin(0.05)
    if target._ymargin < 0.05 and y.size > 0:
        target.set_ymargin(0.05)
    return new_collection, {}


def _set_unique_collection_color(collection, existing_colors):
    count_cols, unique_cols, unused_cols = _get_unique_n_unused_colors(
        existing_colors)
    if isinstance(collection, mpl_collections.LineCollection):
        current_colors = collection.get_color()
    else:
        current_colors = collection.get_facecolor()
    if not len(current_colors):
        return
    current_color = colors.color2hex(current_colors[0])
    if current_color in unique_cols:
        # assign a new color
        if len(unused_cols):
            new_color = unused_cols[0]
        else:
            least_occuring_color = unique_cols[
                np.argsort(count_cols)[0]]
            if len(least_occuring_color):
                new_color = least_occuring_color
            else:
                new_color = mpl_utils.color_cycle[0]()
    else:
        new_color = current_color
    if isinstance(collection, mpl_collections.LineCollection):
        collection.set_color(new_color)
    else:
        collection.set_facecolor(new_color)
    existing_colors.append(new_color)


def _move_containers_to(source, target, clear_labels=False):
    """
    Move a bar containers artist from a source to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []
    for container in source.containers:
        if isinstance(container, mpl_container.BarContainer):
            patches = []
            for patch in container.patches:
                r = mpl_patches.Rectangle(
                    xy=patch.get_xy(),
                    width=patch.get_width(),
                    height=patch.get_height(),
                    facecolor=patch.get_facecolor(),
                    edgecolor=patch.get_edgecolor(),
                    linewidth=patch.get_linewidth(),
                    linestyle=patch.get_linestyle(),
                    fill=patch.get_fill(),
                    hatch=patch.get_hatch(),
                    alpha=patch.get_alpha())
                patches.append(r)

            if clear_labels:
                new_label = None
            else:
                new_label = container.get_label()

            container = mpl_container.BarContainer(
                patches, None, label=new_label)

        elif isinstance(container, mpl_container.ErrorbarContainer):
            lines, has_xerr, has_yerr = container
            if lines is None:
                continue
            data_line, caplines, barlinecols = lines
            capline0, capline1 = caplines
            new_data_line = mpl_lines.Line2D(data_line.x(), data_line.y())
            new_data_line.update_from(data_line)
            new_capline0 = mpl_lines.Line2D(capline0.x(), capline0.y())
            new_capline0.update_from(capline0)
            new_capline1 = mpl_lines.Line2D(capline1.x(), capline1.y())
            new_capline1.update_from(capline1)
            new_barlinecols = mpl_collections.LineCollection(
                barlinecols.get_segments())
            new_barlinecols.update_from(barlinecols)
            if clear_labels:
                container.set_label(None)

            container = mpl_container.ErrorbarContainer((
                (new_data_line, (new_capline0, new_capline1), new_barlinecols),
                container.has_xerr,
                container.has_yerr))

        else:
            continue

        target.add_container(container)
        handles_labels.append(
            (container, container.get_label()))

    return handles_labels


def _move_text_to(source, target):
    """
    Move text artist from a source to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    for text in source.texts:
        # get the text properties

        args = {}
        fancy_bbox = text.get_bbox_patch()
        if fancy_bbox:
            fbargs = {}
            fbargs['facecolor'] = fancy_bbox.get_facecolor()
            fbargs['edgecolor'] = fancy_bbox.get_edgecolor()
            fbargs['boxstyle'] = fancy_bbox.get_boxstyle()
            args['bbox'] = fbargs
        args['rotation'] = text.get_rotation()

        if isinstance(text, matplotlib.text.Annotation):
            new_text = matplotlib.text.Annotation(
                text.get_text(), text.xy, xytext=text.xyann,
                arrowprops=text.arrowprops, **args)
            target.add_artist(new_text)
            pass
        else:
            x, y = text.get_unitless_position()
            t = text.get_text()
            c = text.get_color()
            va = text.get_verticalalignment()
            ha = text.get_horizontalalignment()
            rot = text.get_rotation()
            rot_mode = text.get_rotation_mode()
            new_text = target.text(x, y, t, color=c, va=va, ha=ha, **args)

            # copy font properties
            new_text.set_fontproperties(text.get_font_properties())
            # apply rotation
            new_text.set_rotation_mode(rot_mode)
            new_text.set_rotation(rot)


def _copy_patches_to(source, target, clear_labels=False):
    """
    Copy patch artists from a soruce to a target axes.
    """
    source, target = _get_mpl_axes(source, target)
    handles_labels = []

    # We can't be sure that Axes.patches actually contains all patch artists.
    # For example box plot patches seem to end up in Axes.artists in
    # mpl==3.0.3.
    for patch in source.patches + source.artists:
        if isinstance(patch, matplotlib.patches.PathPatch):
            new_patch = matplotlib.patches.PathPatch(
                patch.get_path())
        elif isinstance(patch, matplotlib.patches.Wedge):
            new_patch = matplotlib.patches.Wedge(
                patch.center, patch.r, patch.theta1, patch.theta2)
        elif isinstance(patch, matplotlib.patches.Rectangle):
            new_patch = matplotlib.patches.Rectangle(
                patch.get_xy(), patch.get_width(), patch.get_height(),
                angle=patch.angle)
        elif isinstance(patch, matplotlib.patches.Ellipse):
            new_patch = matplotlib.patches.Ellipse(
                patch.get_center(), patch.width, patch.height,
                angle=patch.angle)
        else:
            # Ignore unknown Patch objects
            continue
        new_patch.update_from(patch)
        target.add_patch(new_patch)
        new_patch.set_transform(target.transData)
        if clear_labels:
            patch.set_label(None)
        handles_labels.append((patch, patch.get_label()))
    target.relim()
    target.autoscale_view()
    return handles_labels


def _copy_spines_to(source, target):
    """
    Positions the left/bottom spines in the target axes the same as in
    the source object. Also hides the top/right spines if they are
    hidden in the source axes.
    """
    source, target = _get_mpl_axes(source, target)

    left_pos = source.spines['left'].get_position()
    bottom_pos = source.spines['bottom'].get_position()
    if isinstance(left_pos, tuple) and left_pos[0] == 'outward':
        # Default spines (not manually set) always have "outward" as their pos
        pass
    else:
        target.spines['left'].set_position(
            source.spines['left'].get_position())
        target.spines['right'].set_color('none')
    if isinstance(bottom_pos, tuple) and bottom_pos[0] == 'outward':
        pass
    else:
        target.spines['bottom'].set_position(
            source.spines['bottom'].get_position())
        target.spines['top'].set_color('none')


def _get_unique_n_unused_colors(existing_colors):
    unique_colors = np.unique(existing_colors)
    # workaround for numpy version < 1.9
    # we could use return_count in np.unique in the future
    color_count = [(np.array(existing_colors) == item).sum()
                   for item in unique_colors]
    unique_colors = list(unique_colors)  # otherwise FutureWarning
    hex_color_cycle = [colors.color2hex(c) for c in mpl_utils.color_cycle()]
    unused_colors = [c for c in hex_color_cycle if
                     c not in unique_colors]
    return color_count, unique_colors, unused_colors


parameter_list_to_copy = [
    # 'title',  # doesn't work for whichever reason
    'xscale',
    'yscale',
    'xlabel',
    'ylabel',
    'xlim',
    'ylim',
    'aspect',
]


def copy_axes_parameter(source, target):
    """
    Copy axes parameters from a source to a target axes.

    Copy the parameters defined in the ``parameter_list_to_copy``
    from the ``source`` mpl axes to the ``target`` mpl axes.
    """
    source, target = _get_mpl_axes(source, target)
    for attr in parameter_list_to_copy:
        value = getattr(source, 'get_{}'.format(attr))()
        setter = getattr(target, 'set_{}'.format(attr))
        setter(value)

    for saxis, taxis in zip([source.xaxis, source.yaxis],
                            [target.xaxis, target.yaxis]):
        grid_params = {}
        try:
            # Matplotlib>=3.3.3
            # See https://github.com/matplotlib/matplotlib/pull/18769
            major_grid_on = saxis._major_tick_kw.get('gridOn', False)
            minor_grid_on = saxis._minor_tick_kw.get('gridOn', False)
        except KeyError:
            # Matplotlib<3.3.3
            major_grid_on = saxis._gridOnMajor
            minor_grid_on = saxis._gridOnMinor

        if major_grid_on and minor_grid_on:
            grid_params['which'] = 'both'
        elif major_grid_on:
            grid_params['which'] = 'major'
        elif minor_grid_on:
            grid_params['which'] = 'minor'

        grid_lines = saxis.get_gridlines()
        if grid_lines:
            line_properties = grid_lines[0].properties()
            for prop in ['color', 'linewidth', 'linestyle']:
                value = line_properties.get(prop, None)
                grid_params[prop] = value

        grid_params['zorder'] = 1
        if major_grid_on or minor_grid_on:
            taxis.grid(**grid_params)

        # Copy axis tick locators and formatters
        taxis.set_major_locator(saxis.get_major_locator())
        taxis.set_minor_locator(saxis.get_minor_locator())
        taxis.set_major_formatter(saxis.get_major_formatter())
        taxis.set_minor_formatter(saxis.get_minor_formatter())
        for stick, ttick in zip(saxis.get_ticklabels(),
                                taxis.get_ticklabels()):
            ttick.set_rotation(stick.get_rotation())
            ttick.set_horizontalalignment(stick.get_horizontalalignment())


def compress_axes(axes_of_figures, default_output_axes,
                  legends_join=False, legend_location='best',
                  copy_properties_from=0, auto_recolor=True,
                  auto_rescale=True, add_colorbars=True, add_legends=True):
    """
    Compress the plots and parameters from different axes into one.

    For legends, the handling should work for all figures from the figure node,
    but might break horribly for figures with custom legends.

    Parameters
    ----------
    axes_of_figures : array-like
        List of mpl axes
    default_output_axes : axes
        Mpl axes
    legends_join : bool, optional
        Set True if legends for different twin axes should be joined
        into one. Default False.
    legend_location : unicode or str or int, optional
        Location of the joined legend in mpl strings or int.
        Default 'best'., optional
    copy_properties_from : int, optional
        The set of twinaxes from which the axes properties should be
        copied to the resulting axes. Default 0.
    auto_recolor : bool, optional
        Set True if artists should be automatically recolored [Default: True].
    auto_rescale : bool or {'x', 'y'}, optional
        Automatically rescale selected axes to fit the visible data.
    add_colorbars : bool, optional
        If True colorbars are added to the output axes.
        Default True
    add_legends : bool, optional
        If True legends are added to the output axes.
        Default True

    Returns
    -------
    axes_colorbars : dict
    """
    output_axes_dict = {('bottom', 'left'): default_output_axes}
    if copy_properties_from >= len(axes_of_figures):
        copy_properties_from = 0
        sywarn('The figure specified as source for the new axes parameter '
               'does not exist. The first figure will be used!')

    axes_legend_props = {}
    axes_legend_labels = defaultdict(list)
    axes_legend_handles = defaultdict(list)
    axes_colorbars = {}

    figure_legend_ax_id = None
    last_axes_drawn_to = default_output_axes
    existing_colors = []

    title = ''
    for idx, axes in enumerate(axes_of_figures):
        cb_axes = _get_colorbar_axes(axes)
        axes = [a for a in axes if a not in cb_axes]
        axes_dict = classify_axes(axes)
        frame_on = any([_get_mpl_axes(source_ax, None)[0].get_frame_on()
                        for _, source_ax
                        in get_sorted_axes(axes_dict).items()])

        for ax_id, source_ax in get_sorted_axes(axes_dict).items():
            # save old ids, required to find last added axes
            old_axes_ids = list(output_axes_dict.keys())
            target_ax = get_twin_axes(output_axes_dict, ax_id[0], ax_id[1])
            source_ax, target_ax = _get_mpl_axes(source_ax, target_ax)

            # Copy visibility/frame_on and other properties
            target_ax.set_frame_on(frame_on)
            _copy_axis_visibility(source_ax, target_ax)

            # move supported artists
            colorbars, handles, labels = _move_artists(
                source_ax, target_ax, existing_colors,
                auto_recolor=auto_recolor, clear_labels=(
                    not legends_join and idx != copy_properties_from))

            # save the last added axes
            if ax_id not in old_axes_ids:
                last_axes_drawn_to = target_ax

            if len(title) == 0 or idx == copy_properties_from:
                title = source_ax.get_title()
                if len(title) > 0:
                    target_ax.set_title(title)

            if idx == copy_properties_from:
                copy_axes_parameter(source_ax, target_ax)

            # set converter from source axes to format and locate datetime
            # correctly in only scatter plots
            target_ax.xaxis.converter = source_ax.xaxis.converter
            # call _update_axisinfo to reformat date axis
            target_ax.xaxis._update_axisinfo()
            target_ax.yaxis._update_axisinfo()

            if auto_rescale in ['x', 'y']:
                target_ax.autoscale(axis=auto_rescale)
            elif auto_rescale:
                target_ax.autoscale()

            # Check if the axes has a legend and if it seems like a figure
            # legend
            labels_in_legend = set()
            legend = source_ax.get_legend()
            if legend is not None:
                labels_in_legend = {t.get_text() for t in legend.texts}
                if labels_in_legend != set(labels):
                    figure_legend_ax_id = ax_id

            if idx == copy_properties_from or legends_join:
                # Store labels/handles for recreating the legend
                axes_legend_labels[ax_id].extend(labels)
                axes_legend_handles[ax_id].extend(handles)

                # Attempt to recreate legend properties
                if legend is not None:
                    legend_props = {}
                    for prop in list(models.Legend.NODE_LEAFS.keys()):
                        value = None
                        if hasattr(legend, prop):
                            value = getattr(legend, prop)
                        elif hasattr(legend, 'get_{}'.format(prop)):
                            value = getattr(legend, 'get_{}'.format(prop))()
                        elif hasattr(legend, '_{}'.format(prop)):
                            value = getattr(legend, '_{}'.format(prop))
                        elif prop == 'frameon':
                            value = legend.get_frame_on()
                        if value is not None:
                            legend_props[prop] = value
                    if legends_join:
                        legend_props['loc'] = legend_location
                    elif legend._bbox_to_anchor is not None:
                        # Get bbox_to_anchor from old legend:
                        bbox = legend.get_bbox_to_anchor()
                        bbox_ax = bbox.transformed(source_ax.transAxes.inverted())
                        bbox_to_anchor = bbox_ax.bounds[:2]
                        legend_props['bbox_to_anchor'] = bbox_to_anchor
                    if legend_props:
                        legend_props['show'] = True
                    legend_props = _cleanup_legend_props(legend_props)
                    axes_legend_props[ax_id] = legend_props

            if colorbars:
                axes_colorbars[ax_id] = colorbars

    figure_legend_props = axes_legend_props.get(figure_legend_ax_id)

    if add_colorbars and axes_colorbars:
        for colorbars in axes_colorbars.values():
            axes_ = list(get_sorted_axes(output_axes_dict).values())
            for artist_type, artists in colorbars.items():
                for (artist, colorbar_params) in artists:
                    _add_colorbar(colorbar_params, artist, axes=axes_)

    if add_legends and figure_legend_props:
        figure_legend_props['loc'] = legend_location
        _draw_figure_legend(last_axes_drawn_to, figure_legend_props,
                            axes_legend_labels, axes_legend_handles)
    elif add_legends:
        _draw_axes_legends(output_axes_dict, axes_legend_props,
                           axes_legend_labels, axes_legend_handles)

    return axes_colorbars


def add_global_colorbar(axes_colorbars, figure):
    """
    Add a global colorbar to a figure.

    Parameters
    ----------
    axes_colorbars : dict
    figure : syfigure.Figure
    """
    for ax_id, colorbars in axes_colorbars.items():
        for artist_type, artists in colorbars.items():
            if artists:
                for (artist, colorbar_params) in artists:
                    if colorbar_params.pop('show', False):
                        figure.colorbar(artist, **colorbar_params)
                        break


def _cleanup_legend_props(props):
    title = props.pop('title', None)
    if title and title != 'None':
        if isinstance(title, Text):
            title = title.get_text()
        if title != 'None':
            props['title'] = title

    if 'loc' in props:
        location = props['loc']
        distance = props.pop('distance', 4.0)
        if isinstance(location, str) and location.startswith("outside "):
            if location.endswith("right"):
                props['loc'] = "center left"
                props['bbox_to_anchor'] = (1, 0.5)
            elif location.endswith("left"):
                props['loc'] = "center right"
                props['bbox_to_anchor'] = (0, 0.5)
            elif location.endswith("upper"):
                props['loc'] = "lower center"
                props['bbox_to_anchor'] = (0.5, 1)
            elif location.endswith("lower"):
                props['loc'] = "upper center"
                props['bbox_to_anchor'] = (0.5, 0)
            props['borderaxespad'] = distance
    return props


def _draw_figure_legend(ax, figure_legend, axes_labels, axes_handles):
    """
    Draw one joined legend for all axes in the figure.

    Adds arrows to labels to denote which axes the artist is part of.

    Parameters
    ----------
    ax: matplotlib Axes
        The Axes where the legend will be drawn.
    figure_legend: dict
        Properties dictionary for the figure legend.
    axes_labels: dict
        A dict mapping axes ids to lists of labels.
    axes_handles: dict
        A dict mapping axes ids to lists of handles.
    """
    lookup = {('bottom', 'left'): r'$\downarrow\leftarrow$',
              ('bottom', 'right'): r'$\downarrow\rightarrow$',
              ('top', 'left'): r'$\uparrow\leftarrow$',
              ('top', 'right'): r'$\uparrow\rightarrow$'}
    legend_handles = []
    legend_labels = []
    multiple_axes = len(set(axes_labels.keys())) > 1
    props = _cleanup_legend_props(figure_legend)

    # Combine the lists of labels and handles for all axes
    for ax_name in axes_labels.keys():
        legend_handles.extend(axes_handles[ax_name])
        if multiple_axes:
            labels = ['{} ({})'.format(l, lookup[ax_name])
                      for l in axes_labels[ax_name]]
        else:
            labels = axes_labels[ax_name]
        legend_labels.extend(labels)

    if not len(legend_labels) or not len(legend_handles):
        return
    if not props.pop('show', False):
        return
    ax.legend(legend_handles, legend_labels, **props)


def _draw_axes_legends(axes_by_name, axes_legends, axes_labels, axes_handles):
    """
    Draw one axes legend for each specified axes legend in the figure.

    Parameters
    ----------
    axes_by_name: dict
        A dict mapping axes ids to matplotlib Axes objects.
    axes_legends: dict
        A dict mapping axes ids to properties dictionaries.
    axes_labels: dict
        A dict mapping axes ids to lists of labels.
    axes_handles: dict
        A dict mapping axes ids to lists of handles.
    """
    for ax_name, props in axes_legends.items():
        ax = axes_by_name[ax_name]
        props = _cleanup_legend_props(props)
        handles = axes_handles[ax_name]
        labels = axes_labels[ax_name]

        if not props.pop('show', False):
            continue
        if not len(labels) or not len(handles):
            continue
        ax.legend(handles, labels, **props)


def _draw_bar_labels(
        axes, x_coords, y0, values, bar_labels, bar_labels_valign,
        bar_labels_font=None, bar_orientation='Vertical'):
    """Draw bar labels onto axes."""
    if y0 is None:
        y0 = np.zeros_like(values)
    if bar_orientation == 'Vertical':
        y_min, y_max = axes.get_ylim()
        bottom_text_alignment = 'bottom'
        top_text_alignment = 'top'
    else:
        y_min, y_max = axes.get_xlim()
        bottom_text_alignment = 'left'
        top_text_alignment = 'right'
    inside = np.logical_not(np.logical_or(y0 > y_max, y0 + values < y_min))

    # Calculate positions based on y limits or bar edges, whichever is smaller.
    y_bot = np.minimum(y0, y_max)
    y_bot = np.maximum(y_bot, y_min)
    y_top = np.minimum(y0 + values, y_max)
    y_top = np.maximum(y_top, y_min)

    if bar_labels_valign == 'over':
        y_pos = y_top
        text_valign = bottom_text_alignment
    elif bar_labels_valign == 'top':
        y_pos = y_top
        text_valign = top_text_alignment
    elif bar_labels_valign == 'center':
        y_pos = np.mean([y_bot, y_top], axis=0)
        text_valign = 'center'
    elif bar_labels_valign == 'bottom':
        y_pos = y_bot
        text_valign = bottom_text_alignment
    elif bar_labels_valign == 'under':
        y_pos = y_bot
        text_valign = top_text_alignment
    else:
        raise ValueError('Unknown value for bar_labels_valign: '
                         '{}'.format(bar_labels_valign))

    if bar_labels_font is None:
        bar_labels_font = {}
    for x, y, s, i in zip(x_coords, y_pos, bar_labels, inside):
        if i:  # Ignore bars that are entirely outside of ylimits
            if bar_orientation == 'Vertical':
                axes.text(x, y, s, horizontalalignment='center',
                          verticalalignment=text_valign, **bar_labels_font)
            else:
                axes.text(y, x, s, horizontalalignment=text_valign,
                          verticalalignment='center', **bar_labels_font)


def get_fill_coords(bin_edges, values, y0=None):
    """
    Return coordinates suitable for building a histogram using fill_between.
    """
    if y0 is None:
        y0 = np.zeros_like(values)
    fill_x = np.zeros((2*(values.size + 1),), dtype=bin_edges.dtype)
    fill_x[::2] = bin_edges
    fill_x[1::2] = bin_edges
    fill_y = np.zeros_like(fill_x, dtype=values.dtype)
    fill_y[1:-2:2] = values + y0
    fill_y[2:-1:2] = values + y0
    fill_y0 = np.zeros_like(fill_x, dtype=values.dtype)
    fill_y0[1:-2:2] = y0
    fill_y0[2:-1:2] = y0
    return fill_x, fill_y, fill_y0


# TODO: This could be put either in figure API or in add_barcontainer.
def barcontainer_plot(axes, values_list, labels=None, grouping='grouped',
                      **kwargs):
    if grouping not in ('grouped', 'stacked'):
        raise ValueError("Invalid value for 'grouping': {}".format(grouping))

    group = None
    last_values = None
    for i, (values, label) in enumerate(zip(values_list, labels)):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        if grouping == 'grouped':
            group = i, len(values_list)
        bar_plot(axes, values, label, group=group, y0=last_values, **kwargs_)
        if grouping == 'stacked':
            if last_values is None:
                last_values = np.array(values)
            else:
                last_values += np.array(values)


# TODO: This could be put either in figure API or in add_histcontainer.
def histcontainer_plot(axes, values_list, bin_min_edges, bin_max_edges,
                       **kwargs):
    last_values = None
    for i, values in enumerate(values_list):
        kwargs_ = {}
        for k, v in kwargs.items():
            if v is None:
                continue
            elif isinstance(v, list):
                kwargs_[k] = v[i]
            else:
                kwargs_[k] = v

        hist_plot(axes, values, bin_min_edges, bin_max_edges, y0=last_values,
                  **kwargs_)
        if last_values is None:
            last_values = np.array(values)
        else:
            last_values += np.array(values)


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def bar_plot(axes, values, labels=None, rwidth=0.8, bar_labels=None,
             bar_labels_valign='center', bar_labels_font=None, color=None,
             group=None, y0=None, capsize=10, **kwargs):
    """Make a bar plot the way you want it."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if labels is None:
        labels = np.arange(len(values))
    if color is not None:
        kwargs['facecolor'] = color
    bar_orientation = kwargs.pop('orientation', 'Vertical')

    x_data = np.arange(len(values))
    left, width = x_data, rwidth

    # Assume unity bin width
    bin_width = 1
    padding = bin_width*(1 - rwidth)/2.0
    left = x_data - bin_width/2.0 + padding
    if group is not None:
        width *= bin_width/group[1]
        left += group[0]*width
    if bar_orientation == 'Vertical':
        bar = axes.bar
    else:
        bar = axes.barh
        err = kwargs.pop('yerr', None)
        if err is not None:
            kwargs['xerr'] = err
    patches = bar(
        left, values, width, y0, align='edge', capsize=capsize, **kwargs)

    # Draw bar labels
    if bar_labels is not None:
        x_coords = left + width/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font, bar_orientation)

    # Label the bins on the x axis.
    if bar_orientation == 'Vertical':
        axes.set_xticks(x_data)
        axes.set_xticklabels(labels)
    else:
        axes.set_yticks(x_data)
        axes.set_yticklabels(labels)
    return patches


# TODO: I would like to put this method into typeutils/figure.py but this
# module is only working with pure mpl objects.
def box_plot(axes, values, bin_labels=None,
             color=None, filled=True, alpha=None, marker=None, linewidth=None,
             markersize=None, flier_color=None, **kwargs):
    """Make a box plot."""
    if bin_labels is None:
        manage_ticks = False
        bin_labels = np.arange(len(values))
    else:
        manage_ticks = True
    labels = bin_labels

    kwargs['sym'] = mpl_utils.lookup_marker(marker)
    flierprops = {}
    if markersize is not None:
        flierprops['markersize'] = markersize
    if flier_color:
        flierprops['markerfacecolor'] = flier_color
    kwargs['flierprops'] = flierprops
    if filled or color is not None:
        kwargs['patch_artist'] = True
    box_orientation = kwargs.pop('orientation', 'Vertical')
    kwargs['vert'] = box_orientation == 'Vertical'

    kwargs['manage_ticks'] = manage_ticks

    patches = axes.boxplot(values, labels=labels, **kwargs)

    if color is not None:
        if not isinstance(color, list):
            color = [color]*len(patches['boxes'])
        for patch, col in zip(patches['boxes'], color):
            patch.set_facecolor(col)
    if alpha:
        for patch_category in patches.values():
            for patch in patch_category:
                patch.set_alpha(alpha)
    if linewidth:
        for name, vals in patches.items():
            for patch in vals:
                patch.set_linewidth(linewidth)

    if labels is not None:
        for patch, label in zip(patches['boxes'], bin_labels):
            patch.remove()
            patch.set_label(label)
            axes.add_artist(patch)

    return patches


def timeline(figure_object, axes, xdata, values,
             y_start=0, y_height=0.5, colormap_name='accent (qualitative 8)',
             edgecolor='black', linewidth=2, label=None, text_visible=True,
             add_to_legend=True, filled=True,
             fontsize=12, fontcolor='black', last_step=None,
             **kwargs):

    if len(xdata) != len(values):
        raise SyDataError('Length of X and values must be the same '
                          'in a timeline plot')
    if len(xdata) == 0:
        return
    if len(xdata) < 2:
        raise SyDataError('Dataset for timeline cannot have only one entry')

    all_values = sorted(list(set(values)))
    if colormap_name == 'auto':
        colormap_name = 'tab20  (qualitative 20)'
    try:
        colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])
    except KeyError:
        sywarn("Could not find colormap {}".format(colormap_name))
        colormap = cm.get_cmap(colors.COLORMAPS['tab20  (qualitative 20)'])

    vmin, vmax = colors.get_vmin_vmax(colormap_name)
    if vmax == 1:
        vmax = len(all_values)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    color_mapping = {key: colormap(norm(i))
                     for i, key in enumerate(all_values)}

    if add_to_legend:
        for i, value in enumerate(all_values):
            axes.scatter([], [], color=colormap(norm(i)), label=value)

    if np.issubdtype(xdata.dtype, np.datetime64):
        xaxis_as_dates = True
        xdata = mpl_dates.date2num(xdata)
    else:
        xaxis_as_dates = False

    if last_step is None:
        last_step = xdata[-1] - xdata[-2]

    x_starts = []
    x_start = xdata[0]
    labels = []
    cols = []
    prev = values[0]
    for i in range(1, len(xdata)):
        if values[i] != prev:
            if prev != '':
                labels.append(prev)
                x_starts.append((x_start, xdata[i] - x_start))
                cols.append(color_mapping[prev])
            prev = values[i]
            x_start = xdata[i]
    if prev != '':
        labels.append(prev)
        x_starts.append((x_start, xdata[-1] - x_start + last_step))
        cols.append(color_mapping[prev])

    if not filled:
        cols = '#00000000'

    axes.broken_barh(x_starts, (y_start, y_height),
                     facecolors=cols, edgecolor=edgecolor, linewidth=linewidth,
                     **kwargs)

    if xaxis_as_dates:
        axes.xaxis_date(tz=None)

    if label is not None:
        axes.text(x_starts[0][0], y_start+y_height, label+" ",
                  horizontalalignment='left', verticalalignment='bottom',
                  fontsize=12, color='black')

    if text_visible:
        for i, text in enumerate(labels):
            axes.text(x_starts[i][0]+x_starts[i][1]/2, y_start+y_height/2,
                      text, horizontalalignment='center',
                      verticalalignment='center',
                      fontsize=fontsize, color=fontcolor)


def draw_image(figure_object, axes, image, colormap_name='gray', origin=(0, 0),
               width=None, height=None, **kwargs):
    if len(image.shape) == 3 and image.shape[-1] == 1:
        image = image[:, :, 0]
    colormap = cm.get_cmap(colors.COLORMAPS[colormap_name])
    if width is None:
        width = image.shape[1]
    if height is None:
        height = image.shape[0]
    kwargs['extent'] = (origin[0], origin[0]+width,
                        origin[1]+height, origin[1])
    axes.imshow(image, cmap=colormap, **kwargs)


def draw_lines(figure_object, axes,
               startx=None, starty=None, endx=None, endy=None,
               label=None, linestyle='-', linewidth=None,
               color=None, alpha=None, zorder=None,
               marker='', markersize=None, markeredgewidth=None,
               markeredgecolor=None, markerfacecolor=None,
               **kwargs):

    # Promote xdata/ydata to lists or arrays.
    # Any non-scalar ones of them determine length.
    if isinstance(starty, np.ndarray) or isinstance(starty, list):
        N = len(starty)
    else:
        N = 1
    startx = make_iterable(startx, N)
    N = len(startx)
    starty = make_iterable(starty, N)
    endx = make_iterable(endx, N)
    endy = make_iterable(endy, N)

    if len(starty) != N:
        raise SyDataError('Length of starty does not match length of startx')
    if len(endx) != N:
        raise SyDataError('Length of endx does not match length of startx')
    if len(endy) != N:
        raise SyDataError('Length of endy does not match length of startx')

    if isinstance(label, np.ndarray) or isinstance(label, list):
        multi_labels = True
    else:
        multi_labels = False
    labels = make_iterable(label, N)
    linestyles = make_iterable(linestyle, N)
    linewidths = make_iterable(linewidth, N)
    colors = make_iterable(color, N)
    alphas = make_iterable(alpha, N)
    zorders = make_iterable(zorder, N)

    markers = make_iterable(marker, N)
    markersizes = make_iterable(markersize, N)
    markeredgewidths = make_iterable(markeredgewidth, N)
    markeredgecolors = make_iterable(markeredgecolor, N)
    markerfacecolors = make_iterable(markerfacecolor, N)

    if 'linestyle' in kwargs.keys() and kwargs['linestyle'] is None:
        kwargs['linestyle'] = 'none'
    if 'linestyle' not in kwargs.keys():
        kwargs['linestyle'] = '-'

    if 'marker' not in kwargs.keys():
        kwargs['marker'] = ''
    else:
        marker = kwargs.pop('marker')
        for key, value in mpl_utils.MARKERS.items():
            if marker == key:
                break
            elif marker == value:
                marker = key
                break
        kwargs['marker'] = marker

    for i, (x0, y0, x1, y1) in enumerate(zip(startx, starty, endx, endy)):
        label = labels[i]
        if multi_labels is False and i != 0:
            label = None
        linestyle = linestyles[i]
        linewidth = linewidths[i]
        color = colors[i]
        alpha = alphas[i]
        zorder = zorders[i]
        marker = markers[i]
        if marker is None:
            marker = ''
        else:
            for key, value in mpl_utils.MARKERS.items():
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break

        markersize = markersizes[i]
        markeredgewidth = markeredgewidths[i]
        markeredgecolor = markeredgecolors[i]
        markerfacecolor = markerfacecolors[i]

        artist = matplotlib.lines.Line2D(
            [x0, x1], [y0, y1],
            alpha=alpha,
            linewidth=linewidth, linestyle=linestyle,
            color=color, marker=marker, markersize=markersize,
            markeredgewidth=markeredgewidth,
            markeredgecolor=markeredgecolor,
            markerfacecolor=markerfacecolor,
            label=label
        )
        axes.add_line(artist)
        axes.relim()
        axes.autoscale_view(True, True, True)


def draw_box_like(figure_object, axes, artist_fn,
                  xdata=None, ydata=None, width=None, height=None,
                  rotation=None, angle=0.0,
                  label=None, linestyle='-', linewidth=None, fill=True,
                  facecolor=None, edgecolor=None, alpha=None, zorder=None,
                  **kwargs):
    """Draws rectangles, ellipses or other objects
    defined by an XY point and width/height/rotation"""

    # Promote xdata/ydata to lists or arrays.
    # Any non-scalar ones of them determine length.
    if isinstance(ydata, np.ndarray) or isinstance(ydata, list):
        N = len(ydata)
    else:
        N = 1
    xdata = make_iterable(xdata, N)
    N = len(xdata)
    ydata = make_iterable(ydata, N)
    if len(ydata) != N:
        raise SyDataError('Length of ydata does not match length of xdata')
    # Promote width/height to lists or arrays
    width = make_iterable(width, N)
    height = make_iterable(height, N)
    if len(width) != N:
        raise SyDataError('Length of width does not match length of xdata')
    if len(height) != N:
        raise SyDataError('Length of height does not match length of xdata')

    if isinstance(label, np.ndarray) or isinstance(label, list):
        multi_labels = True
    else:
        multi_labels = False
    rotations = make_iterable(rotation, N)
    labels = make_iterable(label, N)
    angles = make_iterable(angle, N)
    linestyles = make_iterable(linestyle, N)
    linewidths = make_iterable(linewidth, N)
    facecolors = make_iterable(facecolor, N)
    edgecolors = make_iterable(edgecolor, N)
    alphas = make_iterable(alpha, N)
    zorders = make_iterable(zorder, N)
    fills = make_iterable(fill, N)

    if 'linestyle' in kwargs.keys() and kwargs['linestyle'] is None:
        kwargs['linestyle'] = 'none'
    if 'linestyle' not in kwargs.keys():
        kwargs['linestyle'] = '-'

    if 'marker' not in kwargs.keys():
        kwargs['marker'] = ''
    else:
        marker = kwargs.pop('marker')
        for key, value in mpl_utils.MARKERS.items():
            if marker == key:
                break
            elif marker == value:
                marker = key
                break
        kwargs['marker'] = marker

    for i, (x0, y0, w, h) in enumerate(zip(xdata, ydata, width, height)):
        label = labels[i]
        if multi_labels is False and i != 0:
            label = None
        angle = angles[i]
        rotation = rotations[i]
        linestyle = linestyles[i]
        linewidth = linewidths[i]
        facecolor = facecolors[i]
        edgecolor = edgecolors[i]
        alpha = alphas[i]
        zorder = zorders[i]
        fill = fills[i]

        artist = artist_fn(
            x=x0, y=y0, width=w, height=h,
            angle=angle, alpha=alpha,
            linewidth=linewidth, linestyle=linestyle, fill=fill,
            facecolor=facecolor, edgecolor=edgecolor, label=label
        )
        axes.add_patch(artist)
        axes.relim()
        axes.autoscale_view(True, True, True)


def draw_rectangles(figure_object, axes, **kwargs):
    def artist_fn(x=None, y=None, width=None, height=None, **kwargs):
        return matplotlib.patches.Rectangle(
            [x, y], width, height, **kwargs)
    draw_box_like(figure_object, axes, artist_fn, **kwargs)


def draw_ellipses(figure_object, axes, **kwargs):
    def artist_fn(x=None, y=None, width=None, height=None, **kwargs):
        return matplotlib.patches.Ellipse(
            [x, y], width, height, **kwargs)
    draw_box_like(figure_object, axes, artist_fn, **kwargs)


def annotation(axes, text, textx, texty, background, arrow,
               annotate_x=None, annotate_y=None, fontsize=None, fontcolor=None,
               shrink=0.0, linewidth=None, alpha=None,
               horz_align=None, vert_align=None,
               textalpha=None, rotation=None,
               **kwargs):
    """Adds an annotation (text and arrow) to a graph.
    If no XY point is given for the annotation then only the text is drawn.
    """

    textx = make_iterable_or_none(textx, 1)
    texty = make_iterable_or_none(texty, len(textx))
    text = make_iterable_or_none(text, len(textx))
    fontcolor = make_iterable_or_none(fontcolor, len(textx))
    textalpha = make_iterable_or_none(textalpha, len(textx))
    rotation = make_iterable_or_none(rotation, len(textx))
    horz_align = make_iterable_or_none(horz_align, len(textx))
    vert_align = make_iterable_or_none(vert_align, len(textx))

    if arrow is not None:
        annotate_x = make_iterable_or_none(
            arrow.pop('annotate_x', None), len(textx))
        annotate_y = make_iterable_or_none(
            arrow.pop('annotate_y', None), len(textx))
        arrow_width = make_iterable_or_none(
            arrow.pop('arrow_width', None), len(textx))
        arrow_headwidth = make_iterable_or_none(
            arrow.pop('arrow_headwidth', None), len(textx))
        arrow_length = make_iterable_or_none(
            arrow.pop('arrow_length', None), len(textx))
        facecolor = make_iterable_or_none(
            arrow.pop('facecolor', 'black'), len(textx))
        edgecolor = make_iterable_or_none(
            arrow.pop('edgecolor', 'black'), len(textx))
        shrink = make_iterable_or_none(arrow.pop('shrink', None), len(textx))

    if background is not None:
        bg_color = make_iterable_or_none(
            background.pop('color', None), len(textx))
        bg_border = make_iterable_or_none(
            background.pop('border', None), len(textx))
        bg_style = background.pop('style', None)
        bg_hatch = background.pop('hatch', None)

    if annotate_x is not None and annotate_y is None:
        sywarn("Whenever annotate X is given you must also give annotate Y")
    if annotate_y is not None and annotate_x is None:
        sywarn("Whenever annotate Y is given you must also give annotate X")

    def calc_generic_args(i):
        args = {}
        if horz_align is not None:
            args['ha'] = horz_align[i]
        if vert_align is not None:
            args['va'] = vert_align[i]
        if rotation is not None:
            args['rotation'] = rotation[i]
        if background is not None:
            bbox = {}
            if bg_style is not None and bg_style != 'rounded':
                bbox['boxstyle'] = bg_style
            else:
                bbox['boxstyle'] = 'round'
            if bg_color is not None:
                bbox['facecolor'] = bg_color[i]
            if bg_border is not None:
                bbox['edgecolor'] = bg_border[i]
            # Note: hatch argument is currently ignored by matplotlib
            if bg_hatch is not None:
                bbox['hatch'] = bg_hatch
            args['bbox'] = bbox
        return args

    if arrow is None:
        for i, (t, x, y) in enumerate(zip(text, textx, texty)):
            args = calc_generic_args(i)
            if fontcolor is not None:
                args['color'] = fontcolor[i]
            patches = axes.text(x, y, t, fontsize=fontsize, **args)
            if textalpha is not None:
                patches.set_alpha(textalpha[i])
    else:
        arrowprops = {}
        for i, (t, x, y, ax, ay) in (
                enumerate(zip(text, textx, texty, annotate_x, annotate_y))):
            arrowprops['facecolor'] = facecolor[i]
            arrowprops['edgecolor'] = edgecolor[i]
            if shrink is not None:
                arrowprops['shrink'] = shrink[i]
            if arrow_width is not None:
                arrowprops['width'] = arrow_width[i]
            if arrow_headwidth is not None:
                arrowprops['headwidth'] = arrow_headwidth[i]
            if arrow_length is not None:
                arrowprops['headlength'] = arrow_length[i]
            args = calc_generic_args(i)
            patches = axes.annotate(
                t, xytext=(x, y), xy=(ax, ay),
                fontsize=fontsize,
                arrowprops=arrowprops,
                **args
            )
            if fontcolor is not None:
                patches.set_color(fontcolor[i])
            if textalpha is not None:
                patches.set_alpha(textalpha[i])


def piechart(axes, weights, fontsize=None, fontcolor=None, edgecolor=None,
             linewidth=None, alpha=None, labelhide=False, **kwargs):
    """Make a pie chart."""
    # Explicitly convert to array to avoid warning from matplotlib>=3.1
    weights = np.atleast_1d(weights)

    if 'colors' in kwargs:
        if not (isinstance(kwargs['colors'], list) or
                isinstance(kwargs['colors'], np.ndarray)):
            kwargs['colors'] = [kwargs['colors']] * len(weights)
    if 'explode' in kwargs and isinstance(kwargs['explode'], numbers.Number):
        kwargs['explode'] = [kwargs['explode']]*len(weights)
    if 'autopct' in kwargs and kwargs['autopct'] == 'Auto':
        kwargs['autopct'] = '%2d%%'
    wedgeprops = {}
    if linewidth is not None:
        wedgeprops['linewidth'] = linewidth
    if edgecolor is not None:
        wedgeprops['edgecolor'] = edgecolor

    artists = axes.pie(weights, wedgeprops=wedgeprops, frame=True, **kwargs)
    perc_labels = []
    if 'autopct' in kwargs:
        wedges, labels, perc_labels = artists
    else:
        wedges, labels = artists

    for artist in wedges + labels + perc_labels:
        if alpha:
            artist.set_alpha(alpha)
    for text in labels + perc_labels:
        if fontsize:
            text.set_size(fontsize)
        if fontcolor:
            text.set_color(fontcolor)
    for text in labels:
        if labelhide:
            text.set_text('')
    axes.autoscale()


def hist_plot(axes, values, bin_min_edges, bin_max_edges, bar_labels=None,
              bar_labels_valign='center', bar_labels_font=None,
              edges=False, color=None, y0=None, **kwargs):
    """Make a histogram plot."""
    if not isinstance(values, np.ndarray):
        values = np.array(values)
    if color is not None:
        kwargs['facecolor'] = color
    else:
        kwargs['facecolor'] = mpl_utils.next_color(axes)

    if edges:
        width = bin_max_edges - bin_min_edges
        patches = axes.bar(
            bin_min_edges, height=values, width=width, bottom=y0,
            align='edge', **kwargs)
    else:
        # Use fill_between() instead of hist() to get around bugs in matplotlib
        # histograms with 'step' histtype.
        bin_edges = np.append(bin_min_edges, bin_max_edges[-1])
        fill_x, fill_y, fill_y0 = get_fill_coords(bin_edges, values, y0)

        patches = axes.fill_between(fill_x, fill_y0, fill_y, **kwargs)

        try:
            sticky_edges = patches.sticky_edges
        except AttributeError:
            # sticky_edges don't exist prior to matplotlib 2.0
            pass
        else:
            sticky_edges.y[:] = (0,)
            axes.autoscale_view()

    # Draw bar labels
    if bar_labels is not None:
        # Workaround for datetime compatibility:
        # Use formula a + (a - b)/2 instead of (a + b)/2
        x_coords = bin_min_edges + (bin_max_edges - bin_min_edges)/2.0
        _draw_bar_labels(axes, x_coords, y0, values, bar_labels,
                         bar_labels_valign, bar_labels_font)

    return patches


def heatmap_plot(axes, xdata, ydata, zdata, colormap='auto',
                 normalization='linear', vmin=None, vmax=None,
                 zlabels=None):
    """Create a heatmap."""
    # TODO: Check integrity of xdata and ydata! There should be no reoccuring
    # and no missing indices (x,y).
    unique_x = np.unique(xdata)
    unique_y = np.unique(ydata)
    masked_z = np.ma.masked_all(zdata.shape, zdata.dtype)
    finite_mask = np.isfinite(zdata)
    if isinstance(zdata, np.ma.MaskedArray):
        finite_mask = finite_mask.filled(False)
    masked_z[finite_mask] = zdata[finite_mask]
    if normalization == 'log':
        non_positive_mask = (masked_z <= 0).filled(False)
        if np.any(non_positive_mask):
            sywarn("Ignoring non-positive z-values when using log scale.")
            masked_z.mask = np.logical_or(masked_z.mask, non_positive_mask)

    if len(unique_x) == 1:
        next_x = unique_x[0] + 1
    else:
        x_step = np.median(np.diff(unique_x))
        next_x = max(unique_x) + x_step
    if len(unique_y) == 1:
        next_y = unique_y[0] + 1
    else:
        y_step = np.median(np.diff(unique_y))
        next_y = max(unique_y) + y_step
    x_to_index = dict(zip(unique_x, range(len(unique_x))))
    y_to_index = dict(zip(unique_y, range(len(unique_y))))
    X = np.concatenate((unique_x, [next_x]))
    Y = np.concatenate((unique_y, [next_y]))
    Z = np.ma.masked_all((len(unique_y), len(unique_x)), dtype=float)
    for x, y, z in zip(xdata, ydata, masked_z):
        xi = x_to_index[x]
        yi = y_to_index[y]
        Z[yi, xi] = z

    # Set up colormap
    colormap = colors.COLORMAPS[colormap]
    if colormap is None:
        # Use sequential colormap by default
        colormap = 'viridis'
        try:
            if np.any(masked_z < 0) and np.any(masked_z > 0):
                # Use diverging colormap
                colormap = 'BrBG'
        except TypeError:
            pass

    if np.all(masked_z.mask):
        # There are no finite values in zdata. z-scale doesn't matter.
        if normalization == 'linear':
            vmin, vmax = 0, 1
        elif normalization == 'log':
            vmin, vmax = 1, 10
    else:
        if colormap in list(colors.DIVERGING_COLORMAPS.values()):
            zabsmax = max(np.abs(np.min(masked_z)), np.abs(np.max(masked_z)))
            if vmin is None:
                vmin = -zabsmax
            if vmax is None:
                vmax = zabsmax
        else:
            if vmin is None:
                vmin = np.min(masked_z)
            if vmax is None:
                vmax = np.max(masked_z)

    if normalization == 'linear':
        norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    elif normalization == 'log':
        norm = matplotlib.colors.LogNorm(vmin=vmin, vmax=vmax)
    heatmap = axes.pcolormesh(X, Y, Z, cmap=colormap, norm=norm)

    # Draw zlabels if selected
    if zlabels is not None:
        for x, y, zlabel in zip(xdata, ydata, zlabels):
            # Never print masked values
            if zlabel is np.ma.masked:
                continue

            # Position in center of bin
            xpos = x + x_step/2
            ypos = y + y_step/2

            # Find a good text color for this bin, choosing white if the
            # bin color is dark and black if the bin color is bright.
            c = heatmap.cmap
            n = heatmap.norm
            xi = x_to_index[x]
            yi = y_to_index[y]
            bg_color_tuple = c(n(Z[yi, xi]))
            bg_brightness = sum(bg_color_tuple[:3]) / 3.0
            if bg_brightness > 0.5:
                text_color = '#000000'
            else:
                text_color = '#FFFFFF'

            axes.text(xpos, ypos, str(zlabel),
                      horizontalalignment='center',
                      verticalalignment='center',
                      color=text_color, fontsize='small')

    return heatmap


def _add_colorbar(colorbar, artist, axes=None):
    """
    Add a colorbar for given artist to the figure.

    Parameters
    ----------
    colorbar : dict
        Dictionary of parameters.
    artist : matplotlib.artist.Artist
        The artist which should be linked to the colorbar.
    axes : matplotlib.axes.Axes or list, optional
        None | parent axes object(s) from which space for a new colorbar axes
        will be stolen. If a list of axes is given they will all be resized to
        make room for the colorbar axes.

    Returns
    -------
    cb : matplotlib.colorbar.Colorbar
    """
    figure = artist.get_figure()

    if colorbar is not None and colorbar.get('show', False):
        orientation = colorbar.get('orientation', 'vertical')
        ax = axes if axes is not None else figure.axes
        if isinstance(axes, Iterable):
            pad = 0.05
            for ax_ in ax:
                axis = ax_.yaxis if orientation == 'vertical' else ax_.xaxis
                if axis.get_ticks_position() in ('right', 'bottom'):
                    pad = 0.15
                    break

            cax, kw = matplotlib.colorbar.make_axes_gridspec(
                ax[0], orientation=orientation, pad=pad)

            for target_ax in ax[1:]:
                target_ax.set_subplotspec(ax[0].get_subplotspec())
                target_ax.set_anchor(ax[0].get_anchor())
            cb = figure.colorbar(artist, cax=cax, **kw)
        else:
            cb = figure.colorbar(artist, ax=ax, orientation=orientation)
        cb_label = colorbar.get('label')
        if cb_label:
            cb.set_label(cb_label)
        return cb
    return None


def _recreate_colorbar(old_artist, new_artist):
    colorbar_params = _get_colorbar_properties(old_artist)
    _add_colorbar(colorbar_params, new_artist)


def _get_colorbar_properties(old_artist):
    """
    Returns the parameters for recreating the colorbar.

    Parameters
    ----------
    old_artist : matplotlib.artist.Artist
        The artist whose colorbar to copy.

    Returns
    -------
    colorbar : dict
        Dictionary of parameters.
    """
    cb = getattr(old_artist, 'colorbar')
    if cb is not None:
        colorbar = {'show': True,
                    'orientation': cb.orientation}
        if cb.orientation == 'horizontal':
            label = cb.ax.get_xlabel()
        else:
            label = cb.ax.get_ylabel()
        colorbar['label'] = label
        return colorbar
    else:
        return {}


def is_numeric_ndarray(arr):
    return isinstance(arr, np.ndarray) and arr.dtype.kind in 'fuiMm'


class CreateFigure(object):
    """
    This :class:`CreateFigure` class is used to create and populate a
    ``matplotlib`` figure with data from `data_table` as defined in `param`.
    """
    def __init__(self, data_table, figure, params):
        self._workaround_pandas_unit_registrations()
        self.data_table = data_table
        self.figure = figure
        self.axes = {}

        root = models.Root(copy.deepcopy(params))
        root.set_data_table(data_table)
        self.parsed_param = root.export_config(eval=True)

        self.axes_legends = {}
        self.global_legend_properties = None
        self.last_axes_drawn_to = None
        self.xaxes_with_dates = {}
        self.yaxes_with_dates = {}

    def _workaround_pandas_unit_registrations(self):
        # Matplotlib >= 2.2 can handle datetime64 on its own, so we don't
        # want pandas to needlessly affect any global state.
        if 'pandas' in sys.modules:
            try:
                from pandas.plotting import (
                    deregister_matplotlib_converters)
            except ImportError:
                # Older pandas versions didn't have this function.
                pass
            else:
                deregister_matplotlib_converters()

    def create_figure(self):
        fig_param = self.parsed_param
        self.apply_figure_parameters(fig_param)
        ax_params = fig_param.get('axes', [])
        self._create_axes(ax_params)

        for axes_param in ax_params:
            xaxis = axes_param.get('xaxis', {})
            yaxis = axes_param.get('yaxis', {})
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')
            ax = self.axes[(xaxis_pos, yaxis_pos)]
            plots = axes_param.get('plots', [])
            # plots = parse_plots_container(
            #     axes_param.get('plots', []), self.data_table)
            self.apply_axes_color_cycle(ax, axes_param)
            for plot_param in plots:
                plot_type = plot_param.pop('type')
                if not plot_param.pop('show', True):
                    continue
                if plot_type == 'line':
                    self.add_lineplot(ax, plot_param)
                elif plot_type == 'scatter':
                    self.add_scatter(ax, plot_param)
                elif plot_type == 'bar':
                    self.add_bars(ax, plot_param)
                elif plot_type == 'barcontainer':
                    self.add_barcontainer(ax, plot_param)
                elif plot_type == 'hist':
                    self.add_hist(ax, plot_param)
                elif plot_type == 'histcontainer':
                    self.add_histcontainer(ax, plot_param)
                elif plot_type == 'heatmap':
                    self.add_heatmap(ax, plot_param)
                elif plot_type == 'box':
                    self.add_boxplot(ax, plot_param)
                elif plot_type == 'pie':
                    self.add_piechart(ax, plot_param)
                elif plot_type == 'annotation':
                    self.add_annotation(ax, plot_param)
                elif plot_type == 'timeline':
                    self.add_timeline(ax, plot_param)
                elif plot_type == 'image':
                    self.add_image(ax, plot_param)
                elif plot_type == 'lines':
                    self.add_lines(ax, plot_param)
                elif plot_type == 'rectangles':
                    self.add_rectangles(ax, plot_param)
                elif plot_type == 'ellipses':
                    self.add_ellipses(ax, plot_param)
            self.last_axes_drawn_to = ax

        self.apply_axes_parameters(ax_params)
        self.draw_legends()

        for axes, xlim in self.xaxes_with_dates.items():
            axes.set_xlim(xlim)
        for axes, ylim in self.yaxes_with_dates.items():
            axes.set_ylim(ylim)
        return self.figure

    def update_date_axes_xlimits(self, axes, xlim):
        old_xlim = self.xaxes_with_dates.get(axes)
        if old_xlim:
            xlim = (min(old_xlim[0], xlim[0]), max(old_xlim[1], xlim[1]))
        self.xaxes_with_dates[axes] = xlim

    def update_date_axes_ylimits(self, axes, ylim):
        old_ylim = self.yaxes_with_dates.get(axes)
        if old_ylim:
            ylim = (min(old_ylim[0], ylim[0]), max(old_ylim[1], ylim[1]))
        self.yaxes_with_dates[axes] = ylim

    def _create_axes(self, parameters):
        """Create all defined axes."""
        axes_positions = []
        for axes_params in parameters:
            xaxis_pos = axes_params.get('xaxis', {}).get('position', 'bottom')
            yaxis_pos = axes_params.get('yaxis', {}).get('position', 'left')
            axes_positions.append((xaxis_pos, yaxis_pos))
        self.axes = create_axes(self.figure, axes_positions)

    def apply_axes_color_cycle(self, ax, parameters):
        color_cycle_name = parameters.get('color_cycle', 'default')
        color_cycle = colors.COLOR_CYCLES.get(color_cycle_name, 'default')
        mpl_utils.set_color_cycle(ax, color_cycle)

    def apply_axes_parameters(self, parameters):
        for axes_params in parameters:
            axes_params = copy.deepcopy(axes_params)

            xaxis = axes_params.pop('xaxis', {})
            yaxis = axes_params.pop('yaxis', {})
            grid_params = axes_params.pop('grid', None)

            # add a grid if specified
            frameon = axes_params.pop('frameon', True)
            color = axes_params.pop('color', None)
            spinex = xaxis.pop('spinex', 'default')
            spiney = yaxis.pop('spiney', 'default')
            xlabel = xaxis.pop('label', None)
            ylabel = yaxis.pop('label', None)

            x_minor_ticks = xaxis.pop('minor_ticks', None)
            y_minor_ticks = yaxis.pop('minor_ticks', None)
            x_major_ticks = xaxis.pop('major_ticks', None)
            y_major_ticks = yaxis.pop('major_ticks', None)

            # create the defined axes
            xaxis_pos = xaxis.get('position', 'bottom')
            yaxis_pos = yaxis.get('position', 'left')

            for l, axis in zip('xy', [xaxis, yaxis]):
                value = axis.get('scale')
                if value is not None:
                    axes_params[l + 'scale'] = value

            # save legend parameters for later handling
            self.axes_legends[(xaxis_pos, yaxis_pos)] = axes_params.pop(
                'legend', {'show': False})

            ax = self.axes[(xaxis_pos, yaxis_pos)]
            if color is not None:
                # Set color on all axes:
                for ax_ in self.axes.values():
                    ax_.set_facecolor(color)

            if x_major_ticks is not None:
                if isinstance(ax.xaxis.get_major_locator(), FixedLocator):
                    # A FixedLocator means that bar/box plot has already set
                    # the ticks. We should try not to interfere with those.
                    old_ticks = ax.get_xticks()
                    new_ticks = [
                        t for t in x_major_ticks if t not in old_ticks]
                    # Place the old_ticks first to match up with tick labels
                    # from bar/box plot:
                    x_major_ticks = list(old_ticks) + new_ticks
                ax.set_xticks(x_major_ticks)
            if x_minor_ticks is not None:
                ax.set_xticks(x_minor_ticks, minor=True)
            if y_major_ticks is not None:
                if isinstance(ax.yaxis.get_major_locator(), FixedLocator):
                    # A FixedLocator means that bar/box plot has already set
                    # the ticks. We should try not to interfere with those.
                    old_ticks = ax.get_yticks()
                    new_ticks = [
                        t for t in y_major_ticks if t not in old_ticks]
                    # Place the old_ticks first to match up with tick labels
                    # from bar/box plot:
                    y_major_ticks = list(old_ticks) + new_ticks
                ax.set_yticks(y_major_ticks)
            if y_minor_ticks is not None:
                ax.set_yticks(y_minor_ticks, minor=True)

            rot_tick_labels = xaxis.get("rot_tick_labels")
            ha = 'center'
            rot = 0
            if rot_tick_labels == 'Clockwise':
                ha = 'left'
                rot = -30
            elif rot_tick_labels == 'Vertical':
                rot = -90
            elif rot_tick_labels == 'Counter clockwise':
                ha = 'right'
                rot = 30
            for tick in ax.get_xticklabels():
                tick.set_rotation(rot)
                tick.set_horizontalalignment(ha)

            xmin = xaxis.get('min')
            xmax = xaxis.get('max')
            if not (xmin is xmax is None):
                ax.set_xlim(xmin, xmax)
            ymin = yaxis.get('min')
            ymax = yaxis.get('max')
            if not (ymin is ymax is None):
                ax.set_ylim(ymin, ymax)

            x_invert = xaxis.get('inverted', False)
            y_invert = yaxis.get('inverted', False)

            ax.xaxis.set_inverted(x_invert)
            ax.yaxis.set_inverted(y_invert)

            # If an axis is shared between two axes its label needs to be set
            # on the original axes in order to be shown. This question
            # describes the problem/bug:
            # https://stackoverflow.com/q/23702364/1529178
            if xlabel is not None:
                if xaxis_pos == 'bottom':
                    label_axes = self.axes[('bottom', 'left')]
                else:
                    label_axes = ax
                label_axes.set_xlabel(xlabel)
            if ylabel is not None:
                if yaxis_pos == 'left':
                    label_axes = self.axes[('bottom', 'left')]
                elif xaxis_pos == 'top':
                    label_axes = self.axes[('bottom', 'right')]
                else:
                    label_axes = ax
                label_axes.set_ylabel(ylabel)

            if grid_params is not None:
                self.apply_axes_grid_parameters(ax, grid_params)

            # evaluate parameters
            axes_params.pop('plots', None)
            if isinstance(ax, SyAxes):
                ax = ax.get_mpl_axes()

            # Remove processed color_cycle
            axes_params.pop('color_cycle', None)
            # Always set aspect ratio, to override when it gets automatically
            # set by Axes.pie().
            axes_params.setdefault('aspect', 'auto')

            ax.set(**axes_params)

            if spinex != 'default':
                ax.spines['bottom'].set_position(spinex)
                ax.spines['top'].set_color('none')
            if spiney != 'default':
                ax.spines['left'].set_position(spiney)
                ax.spines['right'].set_color('none')

            ax.get_xaxis().set_visible(xaxis.get('visible', True))
            ax.get_yaxis().set_visible(yaxis.get('visible', True))
            ax.set_frame_on(frameon)

    def add_bars(self, axes, bar):
        ydata = bar.pop('ydata')

        if not is_numeric_ndarray(ydata):
            sywarn('The data for bar plot is not accessible and '
                   'will not be plotted!')
            return

        bin_labels = bar.pop('bin_labels', None)
        bar_plot(axes, ydata, bin_labels, **bar)

    def add_barcontainer(self, axes, barcontainer):
        """Add a list of bar plots (stacked or grouped)."""
        plots = barcontainer.pop('plots')

        bar_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very reasonable ones:
            'label', 'bar_labels', 'color', 'edgecolor', 'orientation',
            # Slightly less reasonable ones:
            'bar_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder',
            'bin_labels', 'bar_labels_font'
            # Not allowed:
            # 'axes'
        ]

        # Create lists of parameters
        for i, bar in enumerate(plots):
            for k in listable_params:
                value = bar.get(k, None)
                if k == 'color' and value is None:
                    value = mpl_utils.next_color(axes)
                elif k == 'ydata' and not is_numeric_ndarray(value):
                    sywarn('The data for Bar plot in the Bar Container '
                           'is not accessible and will not be plotted!')
                    value = None
                bar_list_params[k].append(value)

        # Remove lists with only None
        for k, v in list(bar_list_params.items()):
            if all(e is None for e in v):
                del bar_list_params[k]
        bar_list_params = {k: v for k, v in bar_list_params.items()
                           if any(e is not None for e in v)}

        barcontainer.update(bar_list_params)
        ydata = barcontainer.pop('ydata', None)
        bin_labels = barcontainer.pop('bin_labels', None)
        grouping = barcontainer.pop('grouping', None)
        if ydata is None:
            sywarn('No y-data specified. Please check the configuration.')
        else:
            barcontainer_plot(axes, ydata, bin_labels, grouping=grouping,
                              **barcontainer)

    def add_boxplot(self, axes, args):
        ydata_old = args.pop('ydata')

        if not isinstance(ydata_old, list):
            ydata_old = [ydata_old]

        ydata = []
        for yvalue in ydata_old:
            if isinstance(yvalue, list):
                yvalue = np.array(yvalue)
            if not is_numeric_ndarray(yvalue):
                sywarn('Some data for box plot is invalid and will '
                       'not be plotted!')
                ydata.append([])
            else:
                ydata.append(yvalue)

        positions = args.pop('positions', None)
        if positions is not None:
            if isinstance(positions, numbers.Number):
                positions = np.arange(len(ydata)) + positions

        box_plot(axes, ydata, positions=positions, **args)

    def add_piechart(self, axes, args):
        weights = args.pop('weights')
        piechart(axes, weights, **args)

    def add_annotation(self, axes, args):
        text = args.pop('text')
        textx = args.pop('textx')
        texty = args.pop('texty')
        box_background = args.pop('boxbackground', None)
        arrow = args.pop('arrow', None)

        annotation(axes, text, textx, texty, box_background, arrow, **args)

    def add_timeline(self, axes, args):
        xdata = args.pop('xdata')
        values = args.pop('values')

        timeline(self, axes, xdata, values, **args)

    def add_image(self, axes, args):
        im = args.pop('image')
        origin = args.pop('origo', (0, 0))
        draw_image(self, axes, im, origin=origin, **args)

    def add_lines(self, axes, args):
        draw_lines(self, axes, **args)

    def add_rectangles(self, axes, args):
        draw_rectangles(self, axes, **args)

    def add_ellipses(self, axes, args):
        draw_ellipses(self, axes, **args)

    def add_hist(self, axes, hist):
        bin_min_edges = hist.pop('bin_min_edges')
        bin_max_edges = hist.pop('bin_max_edges')
        ydata = hist.pop('ydata')

        if (not is_numeric_ndarray(bin_min_edges) or
                not is_numeric_ndarray(bin_max_edges) or
                not is_numeric_ndarray(ydata)):
            sywarn('The data for hist plot is not accessible and '
                   'will not be plotted!')
            return

        hist_plot(axes, ydata, bin_min_edges, bin_max_edges, **hist)

    def add_histcontainer(self, axes, histcontainer):
        """Add a list of hist stacked plots."""
        plots = histcontainer.pop('plots')

        # axes_desc = histcontainer.pop('axes', '_default_')
        # axes = self.axes.get(axes_desc)
        hist_list_params = defaultdict(list)
        listable_params = [
            # Mandatory:
            'ydata',
            # Very resonable ones:
            'label', 'bar_labels', 'color', 'edgecolor', 'bar_labels_font',
            'edges',
            # Slightly less resonable ones:
            'hist_labels_valign', 'linewidth', 'linestyle', 'alpha', 'zorder'
            # Not allowed:
            # 'bin_min_edges', 'bin_max_edges', 'axes', 'histtype'
        ]

        possible_glob_params = [
            'bin_min_edges', 'bin_max_edges',
        ]

        # Create lists of parameters
        for hist in plots:
            for k in listable_params:
                value = hist.get(k, histcontainer.get(k, None))
                if k == 'color' and value is None:
                    value = mpl_utils.next_color(axes)
                elif (k in ['bin_min_edges', 'bin_max_edges', 'ydata'] and
                      not is_numeric_ndarray(value)):
                    sywarn('The data for Histogram plot in the '
                           'Histogram Container is not '
                           'accessible and will not be plotted!')
                    value = None
                hist_list_params[k].append(value)

            for k in possible_glob_params:
                if k not in histcontainer:
                    value = hist.get(k, None)
                    if value is not None:
                        histcontainer[k] = value

        # Remove lists with only None
        for k, v in list(hist_list_params.items()):
            if all(e is None for e in v):
                del hist_list_params[k]
        hist_list_params = {k: v for k, v in hist_list_params.items()
                            if any(e is not None for e in v)}

        histcontainer.update(hist_list_params)
        bin_min_edges = histcontainer.pop('bin_min_edges', None)
        bin_max_edges = histcontainer.pop('bin_max_edges', None)
        ydata = histcontainer.pop('ydata', None)
        histcontainer_plot(axes, ydata, bin_min_edges, bin_max_edges,
                           **histcontainer)

    def add_lineplot(self, axes, line):
        xdata = line.pop('xdata')
        ydata = line.pop('ydata')

        if not is_numeric_ndarray(xdata) or not is_numeric_ndarray(ydata):
            sywarn('The data for line plot is not accessible and '
                   'will not be plotted!')
            return

        if 'marker' in line:
            marker = line.pop('marker')
            for key, value in mpl_utils.MARKERS.items():
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            line['marker'] = marker

        # cleanup parameters
        if 'linestyle' in line.keys() and line['linestyle'] is None:
            line['linestyle'] = 'none'
        # required to plot as lines and not as markers
        if 'linestyle' not in line.keys():
            line['linestyle'] = '-'
        if 'marker' not in line.keys():
            line['marker'] = ''
        # make sure color values are given in correct format
        for color_key in ['color', 'markeredgecolor', 'markerfacecolor']:
            if color_key in line:
                line[color_key] = colors.parse_to_mpl_color(line[color_key])

        axes.plot(xdata, ydata, **line)

    def add_scatter(self, axes, scatter):
        xdata = scatter.pop('xdata')
        ydata = scatter.pop('ydata')
        colorbar = scatter.pop('colorbar', None)
        errorbar = scatter.pop('errorbar', None)

        if not is_numeric_ndarray(xdata) or not is_numeric_ndarray(ydata):
            sywarn('The data for scatter plot is not accessible and '
                   'will not be plotted!')
            return

        # make sure color values are given in correct format
        vmin = scatter.get('vmin')
        vmax = scatter.get('vmax')

        if 'color' in scatter:
            color = scatter.pop('color')
            if isinstance(color, np.ndarray):
                # Set up colormap
                colormap = colors.COLORMAPS[scatter.get('cmap', 'auto')]
                if colormap is None:
                    # Use sequential colormap 'magma' by default
                    colormap = 'magma'
                    try:
                        if np.any(color < 0) and np.any(color > 0):
                            # Use diverging colormap
                            colormap = 'BrBG'
                    except TypeError:
                        pass

                if colormap in list(colors.DIVERGING_COLORMAPS.values()):
                    c_abs_max = max(abs(min(color)),
                                    abs(max(color)))
                    if vmin is None:
                        vmin = -c_abs_max
                    if vmax is None:
                        vmax = c_abs_max
                else:
                    if vmin is None:
                        vmin = min(color)
                    if vmax is None:
                        vmax = max(color)
                scatter['vmin'] = vmin
                scatter['vmax'] = vmax
                scatter['cmap'] = colormap
            scatter['c'] = color

        if 'marker' in scatter:
            marker = scatter.pop('marker', 'circle')
            for key, value in mpl_utils.MARKERS.items():
                if marker == key:
                    break
                elif marker == value:
                    marker = key
                    break
            scatter['marker'] = marker

        # plot error bars before scatter to appear below
        if errorbar is not None:
            alpha = errorbar.pop('alpha', None)
            res = axes.errorbar(xdata, ydata, fmt='none',
                                barsabove=False, **errorbar)
            artists = list(res[1]) + list(res[2])
            if alpha is not None:
                for artist in artists:
                    artist.set_alpha(alpha)

        # plot scatter
        artist = axes.scatter(xdata, ydata, **scatter)

        # Workaround for a bug in Matplotlib (in at least <= 3.0.2):
        # Automatically setting axis limits for datetime data doesn't work well
        # with scatter plots. See: https://stackoverflow.com/a/53454900/1529178
        # and https://github.com/matplotlib/matplotlib/issues/7413
        if xdata.dtype.kind == 'M':
            # fix autoscaling for scatter plots
            xmin = xdata.min()
            xmax = xdata.max()
            xr = xmax - xmin
            xlim = (xmin - xr * axes._xmargin, xmax + xr * axes._xmargin)
            self.update_date_axes_xlimits(axes, xlim)
        if ydata.dtype.kind == 'M':
            # fix autoscaling for scatter plots
            ymin = ydata.min()
            ymax = ydata.max()
            yr = ymax - ymin
            ylim = (ymin - yr * axes._ymargin, ymax + yr * axes._ymargin)
            self.update_date_axes_ylimits(axes, ylim)

        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes).values()))

    def add_heatmap(self, axes, heatmap):
        xdata = heatmap.pop('xdata')
        ydata = heatmap.pop('ydata')
        zdata = heatmap.pop('zdata')
        colorbar = heatmap.pop('colorbar', None)

        if (not is_numeric_ndarray(xdata) or
                not is_numeric_ndarray(ydata) or
                not is_numeric_ndarray(zdata)):
            sywarn('The data for heatmap plot is not accessible and '
                   'will not be plotted!')
            return

        diverging = heatmap.get('colormap') in list(
            colors.DIVERGING_COLORMAPS.keys())
        log_scale = heatmap.get('normalization') == 'log'
        if diverging and log_scale:
            raise SyConfigurationError(
                "Can't use diverging colormaps with logarithmic colormap "
                "scale.")

        artist = heatmap_plot(axes, xdata, ydata, zdata, **heatmap)
        _add_colorbar(colorbar, artist,
                      axes=list(get_sorted_axes(self.axes).values()))

        axes.autoscale_view()

    def draw_legends(self):
        axes_labels = {}
        axes_handles = {}
        for ax_name, ax in self.axes.items():
            handles, labels = ax.get_legend_handles_labels()
            axes_labels[ax_name] = labels
            axes_handles[ax_name] = handles
        if self.global_legend_properties is not None:
            ax = self.last_axes_drawn_to or self.axes.get(('bottom', 'left'))
            _draw_figure_legend(ax, self.global_legend_properties,
                                axes_labels, axes_handles)
        else:
            _draw_axes_legends(self.axes, self.axes_legends,
                               axes_labels, axes_handles)

    def apply_figure_parameters(self, parameters):
        for param, value in parameters.items():
            if param == 'title':
                self.figure.set_title(value)
                # set the default tight layout to false
                # if figure suptitle is set
                # self.figure.get_mpl_figure().set_tight_layout(False)
                # self.figure.subplots_adjust(top=0.85)
            elif param == 'legend':
                self.global_legend_properties = value

    def apply_axes_grid_parameters(self, axes, params):
        if params.pop('show', False):
            axes.grid(**params)

    def apply_axes_legend_parameters(self, axes, params):
        if params.pop('show', False):
            axes.legend(**params)
