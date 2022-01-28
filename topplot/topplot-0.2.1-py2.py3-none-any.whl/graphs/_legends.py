import re

import matplotlib as mpl
import matplotlib.pyplot as plt

# -------------------------------------------------------------------------


def pickable_legend_lines(figman, legend, ax1, ax2=None, len1=None):
    """Map legend lines to plotted lines.

       Note: An mpl API workaround is required.
    """
    leglines = legend.get_lines()
    legtexts = legend.get_texts()

    # WARNING: going off mpl API here to get the legend's handles
    leghandles = legend.legendHandles

    # WARNING: going off mpl API here to access the artist of the legend's title box
    title = legend._legend_title_box._text  # pylint: disable=protected-access

    if len1 is None:
        len1 = len(ax1.get_lines())

    if len1 > 0:
        figman.map_legend_lines(
            ax1,
            title,
            leglines=leglines[:len1],
            legtexts=legtexts[:len1],
            leghandles=leghandles[:len1],
        )

    if ax2 is not None:
        figman.map_legend_lines(
            ax2,
            title,
            leglines=leglines[len1:],
            legtexts=legtexts[len1:],
            leghandles=leghandles[len1:],
        )

# -------------------------------------------------------------------------


def single_legend(_, figman, title, legtitle, ax_ylabel, ax, *, cap=None):
    """Produce a legend for a single axis."""
    # Set furniture text
    ax.set_title(title)
    ax.set_ylabel(ax_ylabel)

    # Get legend lines ready
    handles, labels = ax.get_legend_handles_labels()

    if cap is not None:
        handles = handles[0:cap]
        labels = labels[0:cap]

    # Generate new legend
    legend = ax.legend(handles, labels, loc="upper right", title=legtitle)
    legend.set_draggable(True)

    pickable_legend_lines(figman, legend, ax)

# -------------------------------------------------------------------------


def otm_legend(
    _,
    figman,
    legtitle,
    prefix_regex,
    ax,
    src_legend,
    *,
    loc="upper right",
    copy_markers=True,
):
    """Produce an extra one-to-many (otm) legend to enable togging of a particular
       measurement in a single plot displaying all CPU cores.
    """
    re_prefix = re.compile(prefix_regex)
    re_trailing_digits = re.compile(r"\d+$")

    categories = {}

    # Sort out toggleable elements
    for (legline, handle, text) in zip(
        src_legend.get_lines(), src_legend.legendHandles, src_legend.texts
    ):
        label = text.get_text()
        match = re_prefix.match(label)
        if match is not None:
            category = match.group(1)
            legelts = [figman.legtexts[legline], figman.legmarkers[legline]]
            if category not in categories:
                marker = (
                    handle._marker.get_marker()  # pylint: disable=protected-access
                )
                marker = re_trailing_digits.sub("", marker, 1)
                categories[category] = {
                    "lines": [handle],
                    "legelts": legelts,
                    "colour": handle.get_color(),
                    "lw": handle.get_linewidth(),
                    "marker": marker,
                }
            else:
                categories[category]["lines"].append(handle)
                categories[category]["legelts"] += legelts

    # Create shiney new legend lines
    new_handles = []
    new_labels = []
    for category, cat_data in categories.items():
        extra_args = {"lw": cat_data["lw"]}
        if copy_markers:
            extra_args["marker"] = cat_data["marker"]
        line = mpl.lines.Line2D(
            [],
            [],
            color=cat_data["colour"],
            label=category,
            **extra_args,
        )
        new_handles.append(line)
        new_labels.append(category)

    # Generate new legend
    legend = plt.legend(new_handles, new_labels, loc=loc, title=legtitle)
    figman.register_legend(ax, legtitle, legend)
    legend.set_draggable(True)

    # WARNING: going off mpl API here to access the artist of the legend's title box
    title = legend._legend_title_box._text  # pylint: disable=protected-access
    title.set_picker(10)
    figman.legotmtitles[title] = []

    for (line, text) in zip(legend.get_lines(), legend.get_texts()):
        label = line.get_label()
        line.set_picker(5)
        text.set_picker(10)
        figman.legotm[line] = categories[label]["lines"]
        figman.legotm[text] = categories[label]["lines"]
        figman.legotmtitles[title].append(line)
        figman.legotmtexts[line] = text
        figman.legotmtexts[text] = line

    # Re-add src legend since it will have been detached by the
    # plt.legend([..]) call above
    ax.add_artist(src_legend)

    return legend

# -------------------------------------------------------------------------


def combined_legend(
    _,
    figman,
    title,
    legtitle,
    ax1_ylabel,
    ax2_ylabel,
    ax1,
    ax2,
    *,
    cap1=None,
    cap2=None,
    location="upper right",
):
    """Combine legends from both axes in to single axis."""
    # Set furniture text
    ax2.set_title(title)
    ax1.set_ylabel(ax1_ylabel)
    ax2.set_ylabel(ax2_ylabel)

    # Get legend lines ready
    handles1, labels1 = ax1.get_legend_handles_labels()
    handles2, labels2 = ax2.get_legend_handles_labels()

    if cap1 is not None:
        handles1 = handles1[0:cap1]
        labels1 = labels1[0:cap1]

    if cap2 is not None:
        handles2 = handles2[0:cap2]
        labels2 = labels2[0:cap2]

    # Remove original legends from drawing tree
    ax1.get_legend().remove()
    ax2.get_legend().remove()

    # Generate new legend
    legend = ax2.legend(
        handles1 + handles2, labels1 + labels2, loc=location, title=legtitle
    )
    legend.set_draggable(True)
    ax2.get_legend().set_draggable(True)

    pickable_legend_lines(figman, legend, ax1, ax2, len1=len(handles1))

    return legend

# -------------------------------------------------------------------------
