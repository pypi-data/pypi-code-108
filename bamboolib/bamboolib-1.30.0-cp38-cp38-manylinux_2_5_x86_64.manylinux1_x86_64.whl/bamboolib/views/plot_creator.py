# Copyright (c) 8080 Labs GmbH.
# Distributed under the terms of our End-User License Agreement (see bamboolib.com/eula
# for more information).

import os
import time
import attr

from bamboolib.helper import (
    replace_code_placeholder,
    execute_asynchronously,
    notification,
    AuthorizedPlugin,
)

from bamboolib.widgets.block_manager import BlockManager
from bamboolib.widgets import Singleselect

from bamboolib.plugins import ViewPlugin, create_plugin_base_class

from bamboolib.views.plot_creator_configs import *


class Figure:
    """
    The base class for plot creator figures

    Instances should provide the following:
    - name: str, name of the figure e.g. Histogram
    - description: str, that is shown in search
    - get_final_code: method for providing the final code str

    Optional:
    - required_configs: list of Configurations that are required. Those configs will be added automatically when the figure gets created. Also, the figure will not render unless all of them are valid. Those configs can not be deleted by the user.
    - recommended_configs: list of Configurations that are recommended. Those configs will be added automatically when the figures gets created. However, the figure also renders when they are not all valid and they can be deleted by the user.
    - optional_configs: list of Configurations that the user can add manually to the figure and that can be deleted.
    - other_configs: list of Configurations that are deemed as supported which means that their code is requested and used if they are valid. There is no further behavior
    """

    name = None
    description = ""

    # Attention: those are class variables. They should never be set on an instance but only on the class
    # MAYBE: enforce this constraint via adding properties that set class variables instead of instance variables
    required_configs = []  # added at init and not deletable
    recommended_configs = []  # added at init and deletable
    optional_configs = []  # can be added and deleted
    other_configs = []  # are supported but do not have default behavior

    def get_final_code(self):
        """
        NEEDS TO BE OVERRIDEN

        Returns the code that should be executed for creating the figure.
        This is the code that the user would write in Jupyter to create the same output.

        :return str of code
        """
        raise NotImplementedError

    def can_be_rendered(self):
        """
        CAN be overriden

        Should return True when the figure can be rendered.
        Otherwise should return an Embeddable to explain the error

        :return True or embeddable
        """
        return True

    def get_exception_message(self, exception):
        """
        CAN be overriden

        :param exception: the exception that was thrown when trying to execute the final code
        :return None or embeddable that explains the error or gives some guidance
        """
        result = None
        return result

    def figure_got_selected(self):
        """
        CAN be overriden

        Lifecycle method that is called after the figure got selected
        """
        pass

    def init_figure(self):
        """
        CAN be overriden

        Lifecycle method that is called after the figure got initialized
        """
        pass

    def __init_subclass__(subclass):
        super().__init_subclass__()
        # Attention: copy all the mutable class attributes when creating a new subclass
        # otherwise, there are bugs with manipulating the configs of another Figure

        # we might also get the mutable class attributes dynamically in the future
        # e.g. via looking up the dir() and checking for mutable types like lists
        mutable_class_attributes = [
            "required_configs",
            "recommended_configs",
            "optional_configs",
            "other_configs",
        ]
        for attribute in mutable_class_attributes:
            # attribute not defined on the class (would be looked up from a baseclass)
            if attribute not in subclass.__dict__:
                setattr(subclass, attribute, getattr(subclass, attribute).copy())
                # we can validate that the copy worked via checking id() of the attributes

    def __init__(self, *args, plot_creator=None, **kwargs):
        super().__init__(*args, **kwargs)
        if plot_creator is None:
            raise ValueError
        self.plot_creator = plot_creator
        self.__class__._ensure_that_there_are_no_duplicate_similar_configs()
        self.init_figure()

    def __bam_figure_got_selected__(self):
        """
        This bamboolib dunder method is an internal lifecycle method that is called when the figure got selected

        Some more infos about bamboolib dunder methods:
        its usage communicates the following:
        this is like a public method for this class BUT
        the method shall only be called by bamboolib and not by the user
        the name is prefixed with bam in order to eliminate the chance of collision with Python dunder methods
        """
        # We are adding the required and recommended configs if they don't already exist

        # Attention: when adding those configs, we do not specify if the configs can be deleted or not
        # because this decision is derived decentrally by the config
        # because the decision depends on the figure, too, and the figure might change
        # although the config might stay
        previous_config = None
        for config_class in (
            self.__class__.required_configs + self.__class__.recommended_configs
        ):
            similar_config = self.plot_creator.maybe_get_similar_config(config_class)
            if similar_config is None:
                new_config = config_class(
                    plot_creator=self.plot_creator, focus_after_init=False
                )
                if previous_config is None:
                    self.plot_creator.add_config(new_config, after_figure_selector=True)
                else:
                    self.plot_creator.add_config(new_config, after=previous_config)
                previous_config = new_config
            else:
                previous_config = similar_config
        self.figure_got_selected()

    def get_all_supported_configs(self):
        """
        :return list of Configurations that are supported by this figure
        """
        return (
            self.__class__.required_configs
            + self.__class__.recommended_configs
            + self.__class__.optional_configs
            + self.__class__.other_configs
        )

    def supports_config(self, config):
        """
        :param config: Configuration
        :return bool, if the config is supported by the figure
        """
        return config.__class__ in self.get_all_supported_configs()

    def requires_config(self, config):
        """
        :param config: Configuration
        :return bool, if the config is required by the figure
        """
        return config.__class__ in self.__class__.required_configs

    def maybe_get_supported_config_class_from_same_family(self, config):
        """
        Tries to find a config that is supported by the figure and similar to the given one

        :param config: Configuration
        :return None or Configuration class. None if there is no supported config from the same family. Otherwise a Configuration class
        """
        for config_class in self.get_all_supported_configs():
            if config_classes_belong_to_same_family(config.__class__, config_class):
                return config_class
        return None

    def can_apply(self, config):
        """
        :param config: Configuration
        :return bool, if the config can be applied by the figure. That means that the config is supported and valid.
        """
        return config.is_valid() and self.supports_config(config)

    @classmethod
    def add_config(cls, config, config_type="optional"):
        """
        CLASSMETHOD

        Add a config to the figure as a given config_type

        :param config: Configuration class that should be added
        :param config_type: str, optional, default is "optional", one of ["required", "recommned", "optional", "other"]
        """
        # Attention: deleting similar configs has to happen before getting the reference to the list
        # because the implementation of the deletion process might override the lists
        cls._maybe_delete_similar_configs_from_config_lists(config)

        if config_type == "required":
            config_list = cls.required_configs
        elif config_type == "recommended":
            config_list = cls.recommended_configs
        elif config_type == "optional":
            config_list = cls.optional_configs
        elif config_type == "other":
            config_list = cls.other_configs
        else:
            raise KeyError(f"The config_type {config_type} is not supported")
        config_list.append(config)

    @classmethod
    def _maybe_delete_similar_configs_from_config_lists(cls, config):
        """
        CLASSMETHOD

        Makes sure that a config class (or a similar config) is deleted from the config lists

        :param config: Configuration class that should be removed
        """
        for config_list in [
            cls.required_configs,
            cls.recommended_configs,
            cls.optional_configs,
            cls.other_configs,
        ]:
            to_be_removed = []
            for old_config in config_list:
                if old_config.is_similar_to(config):
                    to_be_removed.append(old_config)
            for item in to_be_removed:
                config_list.remove(item)

    @classmethod
    def _ensure_that_there_are_no_duplicate_similar_configs(cls):
        """
        CLASSMETHOD

        This method makes sure that after it was run, there are no duplicate or similar configs in the config lists.
        If a config is duplicate, it will be removed in the precedence order that is specified below
        Thus, a config that is both optional and required, will be kept in required

        From higher precedence to lower precedence:
        - required
        - recommended
        - optional
        - other
        """

        old_other = cls.other_configs.copy()
        cls.other_configs = []
        old_optional = cls.optional_configs.copy()
        cls.optional_configs = []
        old_recommended = cls.recommended_configs.copy()
        cls.recommended_configs = []
        old_required = cls.required_configs.copy()
        cls.required_configs = []

        for config in old_other:
            cls._maybe_delete_similar_configs_from_config_lists(config)
            cls.other_configs.append(config)

        for config in old_optional:
            cls._maybe_delete_similar_configs_from_config_lists(config)
            cls.optional_configs.append(config)

        for config in old_recommended:
            cls._maybe_delete_similar_configs_from_config_lists(config)
            cls.recommended_configs.append(config)

        for config in old_required:
            cls._maybe_delete_similar_configs_from_config_lists(config)
            cls.required_configs.append(config)


class PlotlyFigure(Figure):
    """
    The figure base class for plotly express figures

    In addition to the normal figure attributes, it requires its instances to provide the following:
    figure_function: str, name of the plotly express function e.g. px.histogram

    This class offers the following code template that can be filled by the configs via the code objects:
    >>> {imports}
    >>> {figure_name} = {figure_function}({df_name}{df_adjustments}{kwargs})
    >>> {figure_adjustments}
    >>> {figure_name}

    The class adds sampling, makes sure that missing values are dropped, and provides error handling.
    """

    figure_function = "TO BE OVERRIDEN"

    other_configs = [Sampling]

    def get_code(self):
        """
        CAN BE OVERRIDEN

        The purpose of the method is to calculate code that needs to be derived centrally in the figure
        instead of decentrally in the configs.
        The resulting code object is processed together with all the other code objects.

        For PlotlyFigures, one example is making sure that missing values are dropped.

        :return PlotlyFigureCode object
        """
        # makes sure that columns with na values are dropped
        columns_with_missing_values = []
        df = self.plot_creator.df_manager.get_current_df()
        for column in self.plot_creator.get_columns():
            has_missing_values = df[column].isnull().sum() > 0
            if has_missing_values:
                columns_with_missing_values.append(column)
        if len(columns_with_missing_values) == 0:
            result = Code()
        else:
            result = Code(
                df_adjustments=f".dropna(subset={columns_with_missing_values})"
            )

        result.imports += ["import plotly.express as px"]
        return result

    def can_be_rendered(self):
        invalid_required_configs = []
        for config in self.required_configs:
            if self.plot_creator.has_similar_and_valid_config(config):
                pass
            else:
                invalid_required_configs.append(config)

        if len(invalid_required_configs) == 0:
            return True
        else:
            return notification(
                f"""
                The figure is missing input for the following required property(s):<br>
                {", ".join([config.name for config in invalid_required_configs])}<br>
                <br>
                Please provide the required input."""
            )

    def get_final_code(self):
        code_results = self._get_code_results_merged_by_key()
        imports = self._get_code_for_results_key(
            code_results, "imports", join_with="\n"
        )
        figure_name = self.plot_creator.get_figure_name()
        figure_code = self._get_figure_code(code_results)
        figure_adjustments = self._get_figure_adjustments(code_results)

        # Attention: do not use textwrap.dedent here to change the nesting level of the syntax
        # Using textwrap.dedent will fail when multiple figure_adjustments configs are added
        # Then, the second figure_adjustment will somehow add too much spacing
        code = f"""
{imports}
{figure_name} = {figure_code}
{figure_adjustments}
{figure_name}
        """
        code = code.strip()
        code = self._remove_empty_lines_from_string(code)
        code = replace_code_placeholder(
            code, old_df_name=self.plot_creator.df_manager.get_current_df_name()
        )
        return code

    def get_exception_message(self, exception):
        result = None

        if (
            "Plotly Express cannot process wide-form data with columns of different type."
            in str(exception)
        ):
            # if the plot_creator has any config from the y_axis family
            # maybe we can express that better via passing a YAxisFamily class or so?
            if self.plot_creator.has_similar_and_valid_config(YAxisWithMultipleColumns):
                result = notification(
                    """The columns on the y-Axis seem to have different data types e.g. numeric and categoric. However, it is only allowed that they all have the same type e.g. numeric<br>
                        <br>
                        Please adjust your column selection or adjust the data types of the columns.""",
                    type="info",
                )
            else:
                # most likely, there is no XAxis or YAxis - and if they exist, they do not have a valid value
                result = notification(
                    """The figure is missing a value for the x-Axis or y-Axis.<br>
                        <br>
                        Please add the x-Axis or y-Axis property""",
                    type="info",
                )
        elif isinstance(exception, KeyError) and (
            "('', '', nan, '')" in str(exception)
        ):
            # # eg facet_rows with embarked (has nans) in a histogram with x = survived
            # import pandas as pd
            # df = pd.read_csv(bam.titanic_csv)
            # import plotly.express as px
            # fig = px.histogram(df, x='Survived', facet_row='Embarked')
            # fig
            result = notification(
                f"""One of the columns has missing values which cannot be handled by Plotly.<br>
                    Most likely, this is the column in the last property<br>
                    <br>
                    Please review the column(s) and remove the missing values""",
                type="info",
            )
        elif isinstance(exception, ValueError) and (
            "Can't clean for JSON: <NA>" in str(exception)
        ):
            # # pd.NA bug that Harneet reported:
            # df = pd.DataFrame({'day':[1,2,3,4,5],
            #        'ox_conc': [10,20,30,40,pd.NA]},
            #      dtype='Int64')
            # px.scatter(df, x='day', y=['ox_conc'])
            result = notification(
                f"""One of the columns has missing values which cannot be handled by Plotly.<br>
                    <br>
                    Please review the column(s) and remove the missing values""",
                type="info",
            )
        elif isinstance(exception, ValueError) and (
            "Invalid value of type 'builtins.float' received for the 'domain[1]' property of layout."
            in str(exception)
        ):
            # import plotly.express as px
            # fig = px.histogram(df2, x='region', facet_row='country')
            # fig
            result = notification(
                f"""Plotly cannot draw the figure because your faceting variables have too many unique values.<br>
                <br>
                Please try some of the following solutions:
                <ul>
                    <li>Column wrap: Add a limit to the maximum number of facet columns</li>
                    <li>Adjust the width or height of the figure</li>
                    <li>Adjust the spacing between facet rows or facet columns</li>
                    <li>Filter your faceting column(s) so that they have less unique values</li>
                </ul>""",
                type="info",
            )

        return result

    def _get_code_results_merged_by_key(self):
        """
        This method gathers all code objects and then merges all the code objects
        into one large dict that contains a list of code strings for all keys e.g.
        >>> {
        >>>     "imports": [
        >>>         "import pandas as pd",
        >>>         "import plotly.express as px",
        >>>         ...
        >>>     ],
        >>>     "df_adjustments": [...],
        >>>     ...
        >>> }
        """
        code_list = [
            self._get_code_from_config(config)
            for config in self.plot_creator.get_all_configs()
            if self.can_apply(config)
        ]
        code_list = code_list + [self.get_code()]

        result_dict = {}
        for code in code_list:
            code_dict = attr.asdict(code)
            for key, value in code_dict.items():
                if result_dict.get(key, None) is None:
                    result_dict[key] = []
                result_dict[key] += value
        return result_dict  # dict with lists of str

    def _get_code_from_config(self, config):
        """
        Get the code from a config and make sure that it has the right format

        :param config: Configuration that provides code
        :return PlotlyFigureCode object
        """
        # Idea: if we want to override the code that a particular config provides for a certain
        # figure then we can add code_formatter classes that provide a different get_code method
        # and are registered e.g. in a dict like: {"XAxis": XAxisCodeFormatter} for a particular
        # figure only
        result = config.get_code()
        if isinstance(result, PlotlyFigureCode):
            pass
        elif isinstance(result, dict):
            result = PlotlyFigureCode(**result)
        else:
            # potentially raise error or warning later?
            result = PlotlyFigureCode()
        return result

    def _remove_empty_lines_from_string(self, string):
        """
        :param string: str that might contain empty lines e.g. "start\n\nsomething after an empty line"
        :return string that does not contain empty lines e.g. "start\nsomething after an empty line"
        """
        return os.linesep.join([line for line in string.splitlines() if line])

    def _get_code_for_results_key(
        self, code_results, key, join_with="", prefix="", suffix=""
    ):
        """
        :param code_results: dict with list of code str
        :param key: str with key name
        :param join_with: str to join with between strings
        :param prefix: str, optional, prefix str
        :param suffix: str, optional, suffix str
        :return str with code
        """
        items = code_results.get(key, None)
        if (items is None) or (len(items) == 0):
            return ""
        else:
            return f"{prefix}{join_with.join(items)}{suffix}"

    def _get_figure_code(self, code_results):
        """
        :param code_results: dict of list of code str
        :return str of code for creating the figure based on template {figure_function}({df_name}{df_adjustments}{kwargs})
        """
        figure_function = self.figure_function
        df_name = self.plot_creator.df_manager.get_current_df_name()
        df_adjustments = self._get_code_for_results_key(
            code_results, "df_adjustments", join_with=""
        )
        kwargs = self._get_code_for_results_key(
            code_results, "kwargs", join_with=", ", prefix=", "
        )  # e.g. ", x='region', color='region'"
        return "{figure_function}({df_name}{df_adjustments}{kwargs})".format(**locals())

    def _get_figure_adjustments(self, code_results):
        """
        Returns the code for the figure_adjustments placeholder
        Merges all the relevant code and replaces the FIGURE code placeholder with the figure name

        :param code_results: dict of list of code str
        :return str of code for the figure adjustments
        """
        code = self._get_code_for_results_key(
            code_results, "figure_adjustments", join_with="\n"
        )
        return code.replace(FIGURE, self.plot_creator.get_figure_name())


@create_plugin_base_class
class PlotlyFigurePlugin(PlotlyFigure):
    """
    The plugin base class for all plotly figures. This class should be used via inheritance
    """


class Histogram(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Histogram"
    figure_function = "px.histogram"

    recommended_configs = []
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        FigureMarginalDistribution,
        ColorOpacity,
        BarOrientation,
        BarDisplayMode,
        BarNormalizeValues,
        HistogramNormalization,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        HistogramAggregationFunction,
        CumulativeSumOfValues,
        FigureNumberOfBins,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class BarPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Bar plot"
    figure_function = "px.bar"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        MarkTextLabel,
        XAxisErrorBar,
        XAxisNegativeErrorBar,
        YAxisErrorBar,
        YAxisNegativeErrorBar,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorScaleType,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        ColorOpacity,
        BarOrientation,
        BarDisplayMode,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class LinePlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Line plot"
    figure_function = "px.line"
    optional_configs = [
        XAxisWithMaybeSortColumn,
        YAxisWithMultipleColumns,
        LineGroup,
        Color,
        LineType,
        FacetRow,
        FacetColumn,
        MarkTextLabel,
        HoverTitle,
        HoverInfoColumns,
        XAxisErrorBar,
        XAxisNegativeErrorBar,
        YAxisErrorBar,
        YAxisNegativeErrorBar,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        LineTypeTheme,
        LineTypeStyleForValue,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        LineShapeInterpolation,
        FigureRenderMode,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        LineAddMarkers,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
        # special
        XAxisRangeSlider,
        XAxisDefaultDateRangeSelectors,
    ]


class ScatterPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Scatter plot"
    figure_function = "px.scatter"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        MarkShape,
        MarkSize,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        MarkTextLabel,
        XAxisErrorBar,
        XAxisNegativeErrorBar,
        YAxisErrorBar,
        YAxisNegativeErrorBar,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorScaleType,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        MarkTheme,
        MarkStyleForValue,
        ColorOpacity,
        MarkMaxSize,
        XAxisMarginalDistribution,
        YAxisMarginalDistribution,
        Trendline,
        TrendlineColor,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        FigureRenderMode,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class PieChart(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Pie chart"
    figure_function = "px.pie"
    optional_configs = [
        PiechartSectorValue,
        PiechartSectorLabel,
        Color,
        HoverTitle,
        HoverInfoColumns,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        ColorOpacity,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class BoxPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Box plot"
    figure_function = "px.box"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        BarOrientation,
        BoxPlotColorGroupMode,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        FigureShowDataPoints,
        BoxNotchStyle,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class ViolinPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Violin plot"
    figure_function = "px.violin"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        BarOrientation,
        ViolinPlotColorGroupMode,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        FigureShowDataPoints,
        FigureAddBoxPlotToViolinPlot,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class StripPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Strip / Jitter plot"
    figure_function = "px.strip"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        BarOrientation,
        StripPlotColorGroupMode,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class DensityHeatmap(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Density heatmap"
    figure_function = "px.density_heatmap"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        ZAxis,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        XAxisMarginalDistribution,
        YAxisMarginalDistribution,
        ColorOpacity,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        HistogramAggregationFunction,
        HistogramNormalization,
        XAxisNumberOfBins,
        YAxisNumberOfBins,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # ZAxis
        ZAxisAxisTitle,
        ZAxisDistanceBetweenTicks,
        ZAxisLogScale,
        ZAxisLinearScale,
        ZAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class DensityContour(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Density contour"
    figure_function = "px.density_contour"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        ZAxis,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        XAxisMarginalDistribution,
        YAxisMarginalDistribution,
        Trendline,
        TrendlineColor,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        HistogramAggregationFunction,
        HistogramNormalization,
        XAxisNumberOfBins,
        YAxisNumberOfBins,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # ZAxis
        ZAxisAxisTitle,
        ZAxisDistanceBetweenTicks,
        ZAxisLogScale,
        ZAxisLinearScale,
        ZAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class AreaPlot(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Area plot"
    figure_function = "px.area"
    optional_configs = [
        XAxis,
        YAxisWithMultipleColumns,
        LineGroup,
        Color,
        FacetRow,
        FacetColumn,
        HoverTitle,
        HoverInfoColumns,
        MarkTextLabel,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        BarOrientation,
        FigureNormalizeGroups,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        LineShapeInterpolation,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FacetColumnWrap,
        FacetRowSpacing,
        FacetColumnSpacing,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class ScatterPlot3D(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Scatter plot 3D"
    figure_function = "px.scatter_3d"
    required_configs = [XAxis, YAxisWithSingleColumn, ZAxis]
    optional_configs = [
        Color,
        MarkShape,
        MarkSize,
        MarkTextLabel,
        HoverTitle,
        HoverInfoColumns,
        XAxisErrorBar,
        XAxisNegativeErrorBar,
        YAxisErrorBar,
        YAxisNegativeErrorBar,
        ZAxisErrorBar,
        ZAxisNegativeErrorBar,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorScaleType,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        MarkTheme,
        MarkStyleForValue,
        ColorOpacity,
        MarkMaxSize,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        ZAxisMinMaxRange,
        FigureRenderMode,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # ZAxis
        ZAxisAxisTitle,
        ZAxisDistanceBetweenTicks,
        ZAxisLogScale,
        ZAxisLinearScale,
        ZAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class LinePlot3D(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Line plot 3D"
    figure_function = "px.line_3d"
    required_configs = [XAxis, YAxisWithSingleColumn, ZAxis]
    optional_configs = [
        LineGroup,
        Color,
        LineType,
        MarkTextLabel,
        HoverTitle,
        HoverInfoColumns,
        XAxisErrorBar,
        XAxisNegativeErrorBar,
        YAxisErrorBar,
        YAxisNegativeErrorBar,
        ZAxisErrorBar,
        ZAxisNegativeErrorBar,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        LineTypeTheme,
        LineTypeStyleForValue,
        XAxisMinMaxRange,
        YAxisMinMaxRange,
        ZAxisMinMaxRange,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisLogScale,
        XAxisLinearScale,
        XAxisRotateAxisLabels,
        XAxisCategoryOrder,
        XAxisType,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisLogScale,
        YAxisLinearScale,
        YAxisRotateAxisLabels,
        # ZAxis
        ZAxisAxisTitle,
        ZAxisDistanceBetweenTicks,
        ZAxisLogScale,
        ZAxisLinearScale,
        ZAxisRotateAxisLabels,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class ScatterMatrix(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Scatter matrix"
    figure_function = "px.scatter_matrix"
    optional_configs = [
        FigureSelectColumns,
        Color,
        MarkShape,
        MarkSize,
        HoverTitle,
        HoverInfoColumns,
        FigureCategoryOrders,
        FigureColumnLabels,
        ColorScaleType,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        MarkTheme,
        MarkStyleForValue,
        ColorOpacity,
        MarkMaxSize,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        Animation_DemandTest,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class ParallelCoordinates(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Parallel coordinates"
    figure_function = "px.parallel_coordinates"
    optional_configs = [
        FigureSelectColumns,
        Color,
        FigureColumnLabels,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class ParallelCategories(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Parallel categories"
    figure_function = "px.parallel_categories"
    optional_configs = [
        FigureSelectColumns,
        Color,
        FigureColumnLabels,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        # other
        ShapeDrawLine,
        ShapeDrawRectangle,
        FigureAutoSize,
        LegendTitle,
    ]


class CandlestickChart(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Candlestick chart"

    # ATTENTION: this is a hotfix to support a general plotly figure
    # START OF HOTFIX
    # TODO: we need to differentiate the abstraction between general plotly figure and plotly express figure
    figure_function = None

    def _get_figure_code(self, code_results):
        return "go.Figure()"

    def get_code(self):
        return Code(imports="import plotly.graph_objects as go")

    # END OF HOTFIX

    required_configs = [CandlestickProperties]
    optional_configs = [
        # FigureTitle,  # does not work yet because it uses kwarg code that only works for PlotlyExpressFigures
        # FigureWidth,  # does not work yet because it uses kwarg code that only works for PlotlyExpressFigures
        # FigureHeight,  # does not work yet because it uses kwarg code that only works for PlotlyExpressFigures
        FigureExportAsStaticImage,
        FigureExportAsJSON,
        FigureExportAsPlotlyFile,
        # XAxis
        XAxisTitle,
        XAxisDistanceBetweenTicks,
        XAxisRotateAxisLabels,
        # YAxis
        YAxisAxisTitle,
        YAxisDistanceBetweenTicks,
        YAxisRotateAxisLabels,
        # other
        FigureAutoSize,
        LegendTitle,
        XAxisRangeSlider,
        XAxisDefaultDateRangeSelectors,
    ]


class Treemap(AuthorizedPlugin, PlotlyFigurePlugin):
    name = "Treemap"
    figure_function = "px.treemap"

    required_configs = [TreemapHierarchy]
    recommended_configs = [TreemapHint]
    optional_configs = [
        # Attention: we do not support the kwargs: names, parents, ids because
        # they are based on an old, unintuitive data format
        TreemapSectorSize,
        TreemapSectorSizeDisplayMode,
        TreemapMaxDepth,
        TreemapAggregationFunctionHint,
        Color,
        ColorContinuousTheme,
        ColorContinuousThemeRange,
        ColorContinuousThemeMidpoint,
        ColorDiscreteTheme,
        ColorStyleForDiscreteValue,
        HoverTitle,
        HoverInfoColumns,
        # custom_data kwarg is not supported because this can only be used in dash
        FigureColumnLabels,
        FigureTitle,
        FigureTheme,
        FigureWidth,
        FigureHeight,
    ]


#########################################################################################################
#########################################################################################################
##################### End of Figure(s)
#########################################################################################################
#########################################################################################################


class FigureSelector(PlotCreatorBlock):
    """
    The PlotCreatorBlock that creates the dropdown for selecting the figure type
    """

    name = "Figure type"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = []
        for plugin in PlotlyFigurePlugin.get_plugins():
            options.append(
                {
                    "value": plugin,
                    "label": plugin.name,
                    "description": plugin.description,
                }
            )
        self.singleselect = Singleselect(
            options=options,
            placeholder="Choose figure type",
            focus_after_init=True,
            set_soft_value=True,
            width="xl",
            on_change=self.update_figure_type,
        )
        self.figure_type = self.singleselect.value(plot_creator=self.plot_creator)

    def update_figure_type(self, _=None):
        """
        This method should be called when the selected figure changed.
        The method will update its internal state and notify other classes about the event.
        """
        self.figure_type = self.singleselect.value(plot_creator=self.plot_creator)
        self.figure_type.__bam_figure_got_selected__()
        self.plot_creator.figure_type_did_change()

    def render(self):
        self.set_content(self.singleselect, show_name_label=True)

    def get_figure_type(self):
        return self.figure_type


class PlotCreatorManager(BlockManager):
    """
    The class that manages the plot creator lifecycle and all of its blocks.
    Also, the class manages the central plot creator commands and notifies the individual blocks.
    In addition, it provides helper methods like `has_similar_config`.
    """

    def __init__(self, *args, df_manager=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.df_manager = df_manager
        self.df_is_outdated = False

        self.df_outdated_note = DfOutdatedNote(plot_creator=self)
        self.add_block(self.df_outdated_note)

        self.figure_selector = FigureSelector(plot_creator=self)
        self.add_block(self.figure_selector)
        self.add_class("bamboolib-overflow-visible")

        self.config_selector = ConfigurationSelector(plot_creator=self)
        self.add_block(self.config_selector)

        self.sampling = Sampling(plot_creator=self)
        self.add_block(self.sampling)

        self.renderer = ResultRenderer(plot_creator=self)
        self.add_block(self.renderer)

        # Manually trigger the first figure_update in order to finalize the init process
        # ATTENTION: it is important to only update the figure type once the figure_selector is setup
        # AND the class is fully created etc because this has many downstream effects
        # and many other classes depend on the fact that the figure_selector is fully set up and functional
        # Before, we triggered the events as part of the __init__ process of the
        # figure_selector and that did not work out
        self.figure_selector.update_figure_type()

    def df_did_change(self):
        """
        Notify the plot creator that the Dataframe of the df_manager did change
        """
        self.df_is_outdated = True
        self.df_outdated_note.render()
        for config in self.get_all_configs():
            config.df_did_change()

    def refresh_ui(self):
        """
        Request a total UI refresh
        """
        self.df_is_outdated = False
        self.df_outdated_note.render()
        for config in self.get_all_configs():
            config.adjust_to_new_df()
        self.force_figure_update()

    def request_figure_update(self):
        """
        Request a normal figure update. This is in contrast to `force_figure_update` because
        the request might be denied if some prohibiting condition is present.
        Currently, no such conditions are known but there is a WASG that those might arise.
        """
        self.force_figure_update()

    def force_figure_update(self):
        """
        Force a figure update. This is only denied when the Dataframe is outdated.
        """
        if self.df_is_outdated:
            return  # dont update the figure when the df is outdated

        can_be_rendered_reply = self.get_figure_type().can_be_rendered()
        if can_be_rendered_reply is True:
            code = self.get_figure_type().get_final_code()
            result_name = self.get_figure_name()
            get_exception_message = self.get_figure_type().get_exception_message
            self.renderer.show_code_result(
                code, result_name, on_exception=get_exception_message
            )
        else:
            self.renderer.show_embeddable(can_be_rendered_reply)

    def get_figure_type(self):
        """
        :return Figure type object e.g. Histogram instance
        """
        return self.figure_selector.get_figure_type()

    def get_figure_type_name(self):
        """
        :return str of the figure type name
        """
        return self.figure_selector.get_figure_type().__class__.__name__

    def get_figure_name(self):
        """
        :return str, variable name of the figure, default: "fig"
        """
        return "fig"

    # maybe also later add has_exact_config when we do not want to check for family members
    def has_similar_config(self, config):
        """
        :param config: a config object
        :return bool if the plot_creator has a similar config (a config that belongs to the same family)

        Attention: if you want to make sure that the config is also valid, please use `has_similar_and_valid_config`
        """
        # Attention: this function uses a generator instead of list comprehension for speed
        # because any(generator) will break after the first truthy result
        # but a list comprehension will first create all results and then run any()
        generator = (
            config.is_similar_to(existing_config)
            for existing_config in self.get_all_configs()
        )
        return any(generator)

    def has_similar_and_valid_config(self, config):
        """
        :param config: a config object
        :return bool if the plot_creator has a valid and similar config (a config that belongs to the same family)
        """
        # Attention: very similar to `has_similar_config`
        # Attention: this function uses a generator instead of list comprehension for speed
        generator = (
            config.is_similar_to(existing_config) and existing_config.is_valid()
            for existing_config in self.get_all_configs()
        )
        return any(generator)

    def maybe_get_similar_config(self, config):
        """
        :param config: Configuration object
        :return Configuration or None, a similar config (same config family) if one exists. Otherwise, None.
        """
        result = None
        for existing_config in self.get_all_configs():
            if config.is_similar_to(existing_config):
                result = existing_config
        return result

    def get_all_configs(self):
        """
        :return a list of Configuration objects
        """
        return [config for config in self.get_all_blocks(tags="Configuration")]

    def get_columns(self):
        """
        :return list of str for all dataframe columns that are specified in valid configs. There are no duplicate column names in the list.
        """
        columns = []
        for config in self.get_all_configs():
            if config.is_valid() and hasattr(config, "get_columns"):
                columns = columns + config.get_columns()
        unique_columns = set(columns)
        return list(unique_columns)

    def figure_type_did_change(self):
        """
        Notify the plot creator that the figure type did change.
        The plot creator will notify all configs, rerender the config_selector and request a figure update.
        """
        # first notify the configs because they might change themselves
        # afterwards, let the config_selector rerender (which depends on the configs)
        for config in self.get_all_configs():
            config.figure_type_did_change()
        self.config_selector.render()
        self.request_figure_update()

    def add_config(
        self, config, index=None, after=None, before=None, after_figure_selector=None
    ):
        """
        Programmatically add a config WITHOUT RERENDERING e.g. when adding a recommended or required config. If you want to rerender the PlotCreator, use `config_got_selected`

        The config can be added EITHER onto a position, after/before a config, or after the figure_selector.

        :param config: Configuration that should be added
        :param index: int, optional, the index where to add the block
        :param after: Configuration, optional, after which to add the config
        :param before: Configuration, optional, before which to add the config
        :param after_figure_selector: bool, optional, if it should be added after the figure selector
        """
        # Why did we differentiate between adding configs with or without rerendering?
        # In an earlier version, there was a side effect that requested
        # a rerender of the ConfigurationSelector and of the Figure
        # but this resulted in some weird bugs

        if after_figure_selector:
            after = self.figure_selector
        self.add_block(config, index=index, after=after, before=before)

    def config_got_selected(self, config_class):
        """
        Notify the plot creator that a config got selected.
        The new config will be created, added before the config_selector and both
        the config_selector and the figure will be rerendered.
        If you do not want to trigger a rerender, then use `add_config` instead.

        :param config_class: the Configuration class from which to add a new instance
        """
        # IMPORTANT: this function has the side effect of rerendering the PlotCreator
        # if you do not want this, then use add_config
        config = config_class(plot_creator=self, focus_after_init=True)
        self.add_config(config, before=self.config_selector)
        self.config_selector.render()
        self.request_figure_update()

    def replace_config(self, old_config, new_config):
        """
        Replace an old_config with a new_config (without rerendering)

        :param old_config: Configuration that gets replaced
        :param new_config: Configuration that gets added
        """
        self.replace_block(old_config, new_config)
        # dont trigger a render because we are only called as side-effect of figure_type_did_change
        # and figure_type_did_change renders after itself

    def remove_config(self, config):
        """
        Remove a config from the plot creator

        :param config: Configuration object that should be removed
        """
        self.delete_block(config)
        self.config_selector.render()

        # Without the delay, the plot creator updates immediately
        # the update rerender makes it hard to delete another config
        # because the UI would jump due to the rerender
        # Often, we found ourselves deleting multiple configs at the same time
        # The delay makes this easier because the UI won't jump
        def request_update_after_short_delay():
            time.sleep(1)
            self.request_figure_update()

        execute_asynchronously(request_update_after_short_delay)

    def config_can_be_selected_by_user(self, config):
        """
        :param config: a Configuration class
        :return bool, if the config can be selected by the user from the config selector
        """
        does_not_exist_yet = not self.has_similar_config(config)
        return config.show_in_config_selector and (
            does_not_exist_yet or config.can_be_added_multiple_times
        )


class PlotCreator(AuthorizedPlugin, ViewPlugin):
    """
    A view that enables the user to create a plot
    """

    name = "Create plot"
    description = "Create plotly figure"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.plot_creator_manager = PlotCreatorManager(df_manager=self.df_manager)

    def render(self):
        # this is called during the initial render but also when the df did change
        self.set_title("Plot Creator")
        self.set_content(self.plot_creator_manager)

    # Attention: we are overriding the TabViewable method here but also copied some of its logic
    # because we do not want to call just a simple render but df_did_change on self.plot_creator_manager
    def tab_got_selected(self):
        # Attention: in the future, we should derive the info if the df is outdated based on its internal state via a hash or so
        # this way, we can detect when the user reversed the change
        # currently, we can only detect when or if the user did change the df at all at any time
        if self._df_is_outdated:
            self._df_is_outdated = False
            self.plot_creator_manager.df_did_change()
