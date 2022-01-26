# Copyright (c) 2021 Mark Crowe <https://github.com/markcrowe-com>. All rights reserved.

from altair.vegalite.v4.api import ConcatChart
from IPython.core.display import display, HTML
from pandas import DataFrame
import altair
import matplotlib.pyplot as pyplot
import numpy as numpy
import seaborn as seaborn


def caption(title: str, css_class: str = "Caption") -> str:
    """
    Create Caption HTML.
    :param title: The title of the Caption.
    :param css_class: The CSS class of the Caption.
    :return: The Caption html.
    """
    return f'<p class="{css_class}">{title}</p>'


def build_interactive_population_pyramid_chart(population_dataframe: DataFrame, age_field: str = "Age", population_field: str = "Population",
                                               sex_field: str = "Sex", time_field: str = "Year",
                                               male_value: str = "Male", female_value: str = "Female", male_color: str = "darkblue", female_color: str = "darkgreen",
                                               year_min: int = 1950, year_max: int = 2021, year_init: int = 2020) -> ConcatChart:
    """
    Build a interactive population pyramid chart.
    :param population_dataframe: The population dataframe to display.
    :param age_field: The age field label.
    :param population_field: The population field label.
    :param sex_field: The sex field label.
    :param time_field: The time field label.
    :param male_value: The male value defined in the sex field.
    :param female_value: The female value defined in the sex field.
    :param male_color: The male color.
    :param female_color: The female color.
    :param year_min: The min year.
    :param year_max: The max year.
    :param year_init: The initial year to start the chart with.
    :return: The interactive population pyramid Chart.
    """

    year_bind_range = altair.binding_range(
        min=year_min, max=year_max, step=1, name="Select Year")
    year_selection = altair.selection_single(bind=year_bind_range,
                                             fields=[time_field],
                                             init={time_field: year_init},
                                             name="Irish Population")
    trunk = altair.Chart(population_dataframe, title="Age"
                         ).add_selection(year_selection
                                         ).transform_filter(year_selection
                                                            ).transform_calculate(Sex=altair.datum[sex_field]
                                                                                  ).properties(width=300)

    tree_color_scale = altair.Scale(domain=[male_value, female_value], range=[
                                    male_color, female_color])

    color = altair.Color(f"{sex_field}:N", scale=tree_color_scale)
    scale = altair.Scale(domain=[0, 300.0])
    sort_order = altair.SortOrder("descending")

    x_male = altair.X(f"sum({population_field}):Q", scale=scale,
                      sort=sort_order, title="Male Population (1000)")
    x_female = altair.X(f"sum({population_field}):Q",
                        scale=scale, title="Female Population (1000)")
    y = altair.Y(f"{age_field}:O", axis=None, sort=sort_order)

    def sex_tree_lambda(value, title, x_axis): return trunk.transform_filter(altair.datum[sex_field] == value
                                                                             ).encode(color=color, x=x_axis, y=y
                                                                                      ).mark_bar().properties(title=title)

    female_tree = sex_tree_lambda("Female", "female", x_female)
    male_tree = sex_tree_lambda("Male", "male", x_male)

    y_trunk = trunk.encode(text=altair.Text(
        f"{age_field}:O"), y=y).mark_text().properties(width=20)

    return altair.concat(male_tree, y_trunk, female_tree, spacing=2)


def display_caption(title: str, css_class: str = "Caption") -> None:
    """
    Display Caption HTML.
    :param title: The title of the Caption.
    :param css_class: The CSS class of the Caption.
    :return: The Caption html.
    """
    display(HTML(caption(title, css_class)))


def display_correlation_matrix_pyramid_heatmap(correlated_dataframe: DataFrame, figure_size: tuple = (11, 9), is_drawing_duplicates: bool = False) -> tuple:
    """
    Display a correlation matrix pyramid heatmap.
    :param correlated_dataframe: The correlated dataframe to display.
    :param figure_size: The size of the figure.
    :param is_drawing_duplicates: Whether or not to draw duplicates.
    :return: The correlation matrix pyramid heatmap Figure and Axes.
    """
    figure, axes = pyplot.subplots(figsize=figure_size)

    color_map = "BrBG"  # Add diverging colormap from red to blue
    cbar_kws = {"shrink": .5}

    if is_drawing_duplicates:
        seaborn.heatmap(correlated_dataframe, annot=True, ax=axes, cmap=color_map,
                        cbar_kws=cbar_kws, linewidth=.5, square=True)
    else:
        # Exclude duplicate correlations by masking upper right values
        mask = numpy.zeros_like(correlated_dataframe, dtype=bool)
        mask[numpy.triu_indices_from(mask)] = True

        seaborn.heatmap(correlated_dataframe, annot=True, ax=axes, cmap=color_map,
                        cbar_kws=cbar_kws, linewidth=.5, square=True,
                        mask=mask)
    return figure, axes


def plot_lines(dataframe: DataFrame, x_axis: str, y_line_configurations: list, size: list, x_axis_label: str, y_axis_label: str) -> None:
    pyplot.subplots(figsize=size)

    for column, color in y_line_configurations:
        pyplot.plot(dataframe[x_axis], dataframe[column],
                    color, label=column, marker='.')

    pyplot.xlabel(x_axis_label)
    pyplot.ylabel(y_axis_label)
    pyplot.legend()
    pyplot.show()


def plot_dataframes_lines(dataframes_configurations: list, x_axis: str, y_axis: str, size: list, x_axis_label: str, y_axis_label: str) -> None:
    pyplot.subplots(figsize=size)

    for dataframe, color, line_label in dataframes_configurations:
        pyplot.plot(dataframe[x_axis], dataframe[y_axis],
                    color, label=line_label, marker='.')

    pyplot.xlabel(x_axis_label)
    pyplot.ylabel(y_axis_label)
    pyplot.legend()
    pyplot.show()
