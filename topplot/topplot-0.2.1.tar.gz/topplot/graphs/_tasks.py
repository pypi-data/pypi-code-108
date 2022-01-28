# -------------------------------------------------------------------------


def graph_procps_tasks(
    self,
    figman,
    df_in,
    ax_sleeping,
    title,
    overview: bool = False,  # pylint: disable=unused-argument
):
    """Draw the procps task summary graph."""

    ax_others = ax_sleeping.twinx()

    df = df_in.rename(columns=lambda x: x[5:] if x[:5] == "task " else x)
    df.filter(items=["sleeping"]).plot(
        ax=ax_sleeping, color=self.colours["task sleeping"], x_compat=True
    )

    task_colours = []
    items = ["running", "stopped", "zombie"]
    for item in items:
        task_colours.append(self.colours["task " + item])
    df.filter(items=items).plot(ax=ax_others, color=task_colours, x_compat=True)

    self.combined_legend(
        figman,
        title,
        "tasks",
        "sleeping tasks",
        "running, stopped, and zombie tasks",
        ax_sleeping,
        ax_others,
    )
    self.common_ax1(figman, ax_sleeping)
    self.common_ax2(figman, ax_others)
    ax_others.set_ybound(lower=0)
    ax_sleeping.set_ybound(lower=0, upper=df["sleeping"].max() * 105.0 / 100)

# -------------------------------------------------------------------------


def graph_busybox_tasks(
    self,
    figman,
    df_in,
    ax_in,
    title,
    overview: bool = False,  # pylint: disable=unused-argument
):
    """Draw the BusyBox task summary graph."""
    ax_in.set_title(title)
    df = df_in.rename(columns=lambda x: x[5:] if x[:5] == "task " else x)
    df.plot(ax=ax_in, color=self.colours["task running"], x_compat=True)
    self.single_legend(figman, title, "tasks", "count of running tasks", ax_in)
    self.common_ax1(figman, ax_in)

# -------------------------------------------------------------------------
