# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).

# NOTE: This file is NOT cythonized!

import ipywidgets as widgets

from bamboolib.edaviz.__modules__ import _column_summary, get_loading_widget, compare

from bamboolib.helper import TabViewable, execute_asynchronously


class ColumnSummary(TabViewable):
    """
    Display a univariate column summary as a separate tab in the UI.
    """

    def __init__(self, column="", **kwargs):
        """
        :param column: string name of the column for which the univariate summary is to be displayed.
        """

        super().__init__(**kwargs)
        self.column = column

    def render(self):
        """Create tab and load its content asynchronously."""

        self.set_title(f"{self.column}")

        self.set_content(
            widgets.VBox(
                [
                    get_loading_widget(),
                    widgets.HTML("<br><br><br><br><br><br><br><br><br><br><br>"),
                ]
            )
        )

        # Render the rest asynchronously
        def full_render():
            df = self.df_manager.get_current_df()
            self.set_content(
                _column_summary(
                    df,
                    self.column,
                    df_manager=self.df_manager,
                    parent_tabs=self.parent_tabs,
                )
            )

        execute_asynchronously(full_render)


class RelateColumns(TabViewable):
    """
    Create a bunch of plots describing the univariate distribution and bivariate relationship
    for two columns x and y, in a new tab.
    """

    def __init__(self, x="", y="", **kwargs):
        super().__init__(**kwargs)
        self.x = x
        self.y = y

    def render(self):
        self.set_title(f"{self.x} predicts {self.y}")

        self.set_content(
            widgets.VBox(
                [
                    get_loading_widget(),
                    widgets.HTML("<br><br><br><br><br><br><br><br><br><br><br>"),
                ]
            )
        )

        def full_render():
            df = self.df_manager.get_current_df()
            self.set_content(
                compare(
                    df,
                    self.x,
                    self.y,
                    df_manager=self.df_manager,
                    parent_tabs=self.parent_tabs,
                )
            )

        execute_asynchronously(full_render)


class EmbeddableToTabviewable(TabViewable):
    def __init__(self, title, embeddable, **kwargs):
        super().__init__(**kwargs)
        self.title = title
        self.embeddable = embeddable

    def render(self):
        self.set_title(self.title)
        self.set_content(self.embeddable)
