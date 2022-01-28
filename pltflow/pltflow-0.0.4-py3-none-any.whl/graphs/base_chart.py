from __future__ import annotations

from typing import List, Union

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

from pltflow.utils.styling import load_style


class chart:
    def __init__(  # pylint: disable=dangerous-default-value
        self,
        data: pd.DataFrame,
        x: Union[str, list],
        y: str,
        style: str = "base",
        markers: bool = True,
        markers_kwargs: dict = {},
        **kwargs: dict,
    ) -> None:

        """
                The initializer of the chart class is intended for line and scatterplots.

                1) It takes an pandas datafrane as main input.
        `       2) It can plot by two different modes:
                    a) Tabular: by specifiying a list of colums in the dataframe to plot and y colum to plot
                    b) Single: by specifying a column in the dataframe to plot and y colum to plot
                3) Styles are defined in the plt,flow/ styles module. They are specified as a st
                4) Markers are only used for the line plot. in case markers are needed for the plot
                5) markers paramteres can be specified as a dictionary on markers_kwargs
                6) kwargs can modify scatter/line plot parameters accoriding to matplotlib inputs

        """

        self.markers = markers
        self.markers_kwargs = markers_kwargs

        self.mode = self.__class__.__name__.split("_")[0]  # name of the class

        # This function includes initialization common for all the clases
        self.initialize_plot_parameters(style, kwargs)

        # Initialize the plot for the specific class
        self.prepare_data(data, x, y)

    def prepare_data(
        self,
        data: Union[pd.DataFrame, list, np.ndarray, pd.Series],
        x: Union[str, list],
        y: str,
    ) -> None:
        """
        This parameters are set for the case of scatterplots.
        In this mode the only valid input is a dataframe
        """

        if isinstance(data, pd.DataFrame) and isinstance(x, str):
            self.df = data
            if x in self.df.columns:
                self.x = x
                self.set_xlabel(x)
            else:
                raise ValueError("X should be a valid column name")

        elif isinstance(data, pd.DataFrame) and isinstance(x, list):
            self.df = data.loc[:, x].melt(var_name="_key", value_name="_value")

            self.x = "_value"
            self.color_by("_key")
            self.set_xlabel("")

        else:
            raise ValueError(
                """
            data must have the following types combinations:
            * data = pd.DataFrame, x = str
            * data = pd.DataFrame, x = list
            """
            )

        self.y = y
        self.set_ylabel(self.y)

    def initialize_plot_parameters(self, style: str, kwargs: dict) -> None:
        plt.rcParams.update(plt.rcParamsDefault)

        self.rcParams, self.styleParams, self.colors = load_style(style)

        self.set_figsize()

        self.caps = False

        self.z = ""  # type: str
        self.main_categories = []  # type: list

        self.set_title("")
        self.set_subtitle("")

        self.set_kwargs(**kwargs)

    def set_kwargs(self, **kwargs: dict) -> None:

        instance = self.__class__.__name__.split("_")[0]
        self.styleParams[instance] = {**self.styleParams[instance], **kwargs}

    def upper(self, caps: bool = True) -> chart:
        """
        Set the title and the subtitle to upper case.
        """
        self.caps = caps

        return self

    def set_palette(self, palette: list) -> chart:

        """
        If one color is given, it will be used for all the categories.
        If two:
            * The first will be the main color
            * The first will be also used as additional colors
            * The second will be the grayed color
        if 3 or more:
            *the first will be the main color,
            *The first to -1 will be replicated until there are at least 10 category colores
            *The last will be the grayed color
        """

        if len(palette) == 0:
            raise ValueError("Palette must have at least one color")

        if len(palette) == 1:
            palette = palette * 12

        if len(palette) == 2:
            palette = [palette[0]] * 11 + [palette[1]]

        if (len(palette) > 2) and (len(palette) < 12):
            palette = palette[0:-1] * 4 + [palette[-1]]

        self.colors[self.mode] = palette
        return self

    def set_yticks(self, positions: list, **kwargs: dict) -> chart:
        self.styleParams["yticks"] = {**self.styleParams["yticks"], **{"ticks": positions}, **kwargs}
        return self

    def set_xticks(self, positions: list, **kwargs: dict) -> chart:
        self.styleParams["xticks"] = {**self.styleParams["xticks"], **{"ticks": positions}, **kwargs}
        return self

    def set_ylabel(self, label: str, **kwargs: dict) -> chart:

        self.styleParams["ylabel"] = {
            **self.styleParams["ylabel"],
            **{"ylabel": label},
            **kwargs,
        }
        return self

    def set_xlabel(self, label: str, **kwargs: dict) -> chart:

        self.styleParams["xlabel"] = {**self.styleParams["xlabel"], **{"xlabel": label}, **kwargs}

        return self

    def set_title(self, title: str, **kwargs: dict) -> chart:

        self.styleParams["title"] = {**self.styleParams["title"], **{"text": title}, **kwargs}

        return self

    def set_subtitle(self, subtitle: str) -> chart:
        self.styleParams["subtitle"]["text"] = subtitle

        return self

    def set_figsize(self, w: int = 9, h: int = 4) -> chart:
        if w > 0 and h > 0:
            self.rcParams["figure.figsize"] = (w, h)
        else:
            raise ValueError("w and h must be greater than 0")
        return self

    def color_by(self, column_name: str) -> chart:
        """
        Set the color for the plot.
        """

        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("color_by() can only be used with a dataframe as data source")

        if column_name not in self.df.columns:
            raise ValueError(f"{column_name} not in dataframe")

        self.z = column_name

        self.styleParams["color_by"] = column_name

        if self.main_categories == []:
            self.main_categories = list(self.df[column_name].unique())

        available_values = list(
            self.df.loc[self.df[self.z].isin(self.main_categories), self.z].value_counts().index
        )

        if len(self.main_categories) > 20:
            print(
                f"Posible categories to .focus_on()  {available_values[:20]} and {len(self.main_categories) - 20} more"
            )
        else:
            print(f"Possible categories to .focus_on() {available_values}")

        return self

    def focus_on(self, category: Union[str, list]) -> chart:
        """
        Set the main category for the plot.

        """
        if not isinstance(self.df, pd.DataFrame):
            raise ValueError("color_by() can only be used with a dataframe as data source")

        all_cats_available = list(self.df[self.z].unique())

        if self.main_categories == all_cats_available:
            self.main_categories = []

        if isinstance(category, str):

            if category not in all_cats_available:
                raise ValueError(
                    f"{category} is not included on the main categories avalable in the {self.z} column"
                )
            self.main_categories.append(category)

        elif isinstance(category, list):

            invalid_categories = []
            for requested_cat in category:
                if requested_cat not in all_cats_available:
                    invalid_categories.append(requested_cat)

            if len(invalid_categories) > 0:
                raise ValueError(
                    f"{invalid_categories} does not form part of the available categories of  the column {self.x}"
                )

            self.main_categories.append(category)

        self.main_categories = list(pd.Series(self.main_categories).unique())

        return self

    def display_chart_annotations(self) -> None:
        """
        Add a title and a subtitle to the plot.
        """

        if self.caps:
            self.styleParams["xlabel"]["xlabel"] = self.styleParams["xlabel"]["xlabel"].upper()
            self.styleParams["ylabel"]["ylabel"] = self.styleParams["ylabel"]["ylabel"].upper()
            self.styleParams["title"]["text"] = self.styleParams["title"]["text"].upper()
            self.styleParams["subtitle"]["text"] = self.styleParams["subtitle"]["text"].upper()

        if "text" in self.styleParams["title"]:
            plt.annotate(**self.styleParams["title"])

        if "text" in self.styleParams["subtitle"]:
            plt.annotate(**self.styleParams["subtitle"])

        plt.xlabel(**self.styleParams["xlabel"])
        plt.ylabel(**self.styleParams["ylabel"])

        plt.xticks(**self.styleParams["xticks"])
        plt.yticks(**self.styleParams["yticks"])

    def get_hue_categories(self) -> List[str]:

        if self.z != "":
            categories = self.df[self.z].unique().tolist()
            if len(categories) == 0:
                raise ValueError("No categories found: The column is empty")
            if len(categories) > 15:
                raise ValueError(
                    """
                        Too many categories: The column has more than 15 categories
                        Which will yield in an unclear graph.
                        """
                )
        else:
            categories = []

        return categories

    def plot_padding(self, up: tuple = (1, 1), down: tuple = (0, 0)) -> None:
        """
        This is a Dirty Trick to extend the plot to the right in Jupyter notebooks
        """
        plt.text(
            *up,
            "t",
            transform=plt.gcf().transFigure,
            color=self.rcParams["figure.facecolor"],
        )
        plt.text(
            *down,
            "t",
            transform=plt.gcf().transFigure,
            color=self.rcParams["figure.facecolor"],
        )

    def create_palette(self, categories: list) -> dict:

        colors = self.colors[self.mode]

        i = 0
        color_assigment = []

        for category in categories:
            if category in self.main_categories:
                color_assigment += [colors[:-1][i % len(colors)]]
                i += 1
            else:
                color_assigment += [colors[-1]]

        palette = dict(zip(categories, color_assigment))

        return palette

    def set_xlim(self, left: float, right: float) -> chart:
        self.styleParams["xlim"] = (left, right)
        return self

    def set_ylim(self, bottom: float, top: float) -> chart:
        self.styleParams["ylim"] = (bottom, top)
        return self

    def set_xylim(self) -> None:
        if "xlim" in self.styleParams:
            plt.xlim(self.styleParams["xlim"])
        if "ylim" in self.styleParams:
            plt.ylim(self.styleParams["ylim"])
