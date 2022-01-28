from ..figman import FigManager

# -------------------------------------------------------------------------


def graph_overview(self, use_progress_window: bool = False):
    """Draw the four overview graphs on a single Fig."""
    figman_name = "overview"
    fig_title = "overview"

    def setup(figman):
        graph_index = 1
        for (x, y, title) in zip([0, 0, 1, 1], [0, 1, 0, 1], self.graph_map.keys()):
            ax = figman.plots[x][y]
            self.graph_map[title].fn(
                figman,
                self.graph_map[title].data,
                ax,
                f"({str(graph_index)}) {title}",
                overview=True,
            )
            graph_index += 1

    def generate_figman():
        return FigManager(
            figman_name,
            self,
            self.title(fig_title),
            self.window_size,
            2,
            2,
        )

    self.dispense_graph(
        fig_title,
        figman_name,
        setup,
        generate_figman,
        use_progress_window,
    )

# -------------------------------------------------------------------------


def graph_by_overview_ordinal(self, n, use_progress_window: bool = False):
    """"Draw the requested graph from the Big Four overview graphs in its own Fig."""
    figman_name = f"overview_{n}"

    title = self.ordinal_to_title(n)

    def setup(figman):
        ax = (
            figman.plots
        )  # Note necessary absence of cartesian indexing for single subplot
        self.graph_map[title].fn(
            figman,
            self.graph_map[title].data,
            ax,
            figman.subtitle,
            overview=False,
        )

    def generate_figman():
        return FigManager(
            figman_name,
            self,
            self.title(title),
            self.window_size,
            1,
            1,
        )

    self.dispense_graph(
        title.partition("\n")[0],
        figman_name,
        setup,
        generate_figman,
        use_progress_window,
    )

# -------------------------------------------------------------------------
