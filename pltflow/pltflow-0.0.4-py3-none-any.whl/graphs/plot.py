from __future__ import annotations

import pandas as pd
from matplotlib import pyplot as plt

from pltflow.graphs.base_chart import chart
from pltflow.utils.styling import create_legend_patches


class lines(chart):

    """
    Generic class to genererate a plt graph
    """

    def show(self) -> None:

        plt.rcParams.update(self.rcParams)

        categories = self.get_hue_categories()

        palette = self.create_palette(categories)

        self.plot(self.df, self.mode, categories, palette)

        if self.mode == "lines" and self.markers:

            df = self.df if self.z == "" else self.df[self.df[self.z].isin(self.main_categories)]

            self.plot(df, "scatter", categories, palette, self.markers_kwargs)

        if len(categories) > 1:

            patches = create_legend_patches(palette, grayed_color=self.colors[self.mode][-1])

            plt.legend(handles=patches)

        self.display_chart_annotations()
        self.plot_padding((1.02, 1.2), (-0.07, -0.2))

        self.set_xylim()

        plt.show()

    def plot(  # pylint: disable=dangerous-default-value
        self, df: pd.DataFrame, mode: str, categories: list, palette: dict, markers_kwargs: dict = {}
    ) -> None:

        if len(categories) > 1:

            for category in categories:

                x_axis = df[self.x][df[self.z] == category]
                y_axis = df[self.y][df[self.z] == category]

                if mode == "lines":
                    plt.plot(x_axis, y_axis, color=palette[category], **self.styleParams[mode])
                elif mode == "scatter":
                    scatter_params = {**markers_kwargs, **self.styleParams[mode]}
                    plt.scatter(x_axis, y_axis, color=palette[category], **scatter_params)
        else:
            x_axis = df[self.x]
            y_axis = df[self.y]

            print(mode, self.styleParams[mode])

            if mode == "lines":
                plt.plot(x_axis, y_axis, color=self.colors[self.mode][0], **self.styleParams[mode])
            elif mode == "scatter":
                plt.scatter(x_axis, y_axis, color=self.colors[self.mode][0], **self.styleParams[mode])


class scatter(lines):
    ...
