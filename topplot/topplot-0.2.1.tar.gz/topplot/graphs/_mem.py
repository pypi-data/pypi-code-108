from ..toptype import TopType

# -------------------------------------------------------------------------


def graph_mem(
    self,
    figman,
    df,
    ax1,
    title,
    overview: bool = False,  # pylint: disable=unused-argument
):
    """Draw the memory summary graph."""
    ax1.set_title(title)

    mem_colours = []

    # Draw 'mem free' lowest in z-order, unless 'mem availble' is needed there
    lowest_mem = (
        "mem free"
        if self.mem_cached_or_available == "mem cached"
        else "mem available"
    )

    items = [lowest_mem, "mem used", "mem buffers"]
    for item in items:
        mem_colours.append(self.colours[item])
    df.filter(items=items).plot.area(ax=ax1, color=mem_colours)

    # Inform the user if it looks like top's scale was set too high
    if df.iloc[[0, -1]].sum(axis=1).sum() == 0.0:
        msg = (
            "The memory and swap values for the first and last cycles are all zero."
            " Was top's scale set too high?\nWhen configuring top, toggle through"
            " the available scales by pressing uppercase 'E' in top's Interactive"
            " mode's main page.\nThen save the config by press uppercase 'W'."
        )
        figman.display_msg(msg, 5)
        print(f"WARNING: {msg}")

    # 'mem used' includes 'mem cached' which is pants, since that memory is
    # available to use immediately, although if the VFS is asked for its old
    # contents and they're still valid, it will (immediately) be put back to use
    # as that data instead.  ('mem available' handles this better.)
    #
    # Indicate this state of affairs by colouring cached memory using the colours
    # for 'mem free' hatched with 'mem used'

    if self.mem_cached_or_available == "mem cached":
        # Overwrite the overlapping part of 'mem used' with 'mem cached'
        df.filter(items=["mem free", "mem cached"]).plot.area(
            ax=ax1, color=self.colours["mem free"]
        )
        chatch = ax1.collections[-1]

        # Knock out confusing repeat 'mem free' legend
        c = ax1.collections[-2]
        c.set_label("")
    else:
        # Overwrite the overlapping part of 'mem available' with 'mem free'
        df.filter(items=["mem free"]).plot.area(
            ax=ax1, color=self.colours["mem free"]
        )
        chatch = ax1.collections[0]
        chatch.set_label("mem cached")

    chatch.set_facecolor(self.colours["mem free"])
    chatch.set_edgecolor(self.colours["mem used"])
    # hatches = [".", "/", "\\", None, "\\\\", "*"]
    chatch.set_hatch("//")

    if self.config.toptype == TopType.PROCPS:
        df.filter(items=["swap free"]).plot(
            ax=ax1, color=self.colours["swap free"], lw=3
        )

    self.common_ax1(figman, ax1)

    l1 = ax1.legend(loc="upper right", title="memory")
    l1.set_draggable(True)
    ax1.set_ylabel(f"mem ({self.mem_unit})")

# -------------------------------------------------------------------------
