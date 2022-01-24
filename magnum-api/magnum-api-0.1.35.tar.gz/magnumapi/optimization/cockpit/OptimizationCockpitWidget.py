from itertools import accumulate
from typing import List

import pandas as pd

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from magnumapi.geometry.GeometryPlot import GeometryPlot
from magnumapi.optimization.GeneticOptimization import GeneticOptimization
from magnumapi.optimization.design_variable.Individual import Individual
from magnumapi.optimization.logger.Logger import Logger
from magnumapi.optimization.config.OptimizationConfig import OptimizationConfig
from magnumapi.optimization.constants import SCORE_KEYWORD


class OptimizationCockpitWidget:
    """ A class providing a plotly widget for an optimization cockpit. The cockpit displays:
    - progress of the optimization
    - objective variable table
    - comparison of fitness function of a selected individual to the current best one
    - comparison of design variables of a selected individual to the current best one
    - selected geometry overview
    The cockpit is interactive and allows for selecting an individual to display its geometry

    """

    def __init__(self,
                 gen_opt: GeneticOptimization,
                 logger_df: pd.DataFrame,
                 config: OptimizationConfig,
                 is_log_y=False) -> None:
        """ Constructor of an OptimizationCockpitWidget instance

        :param gen_opt: genetic optimization instance
        :param logger_df: a dataframe with logger
        :param config: optimization config instance
        :param is_log_y: if True, than the score plot has logarithmic y-scale
        """
        self.gen_opt = gen_opt
        self.min_logger_df = Logger.extract_min_rows_from_logger_df(logger_df, self.gen_opt.n_pop)
        self.config = config
        self.is_log_y = is_log_y

        fig = make_subplots(
            rows=3, cols=2,
            shared_xaxes=False,
            vertical_spacing=0.03,
            column_widths=[0.35, 0.65],
            row_heights=[0.15, 0.2, 0.65],
            specs=[[{"type": "xy"}, {"type": "table"}], [{"type": "xy", "rowspan": 2}, {"type": "scatter"}],
                   [None, {"type": "scatter"}]]
        )

        self.widget = go.FigureWidget(fig)

    def show(self) -> go.FigureWidget:
        """ Method displaying the widget by returning the field that contains it.

        :return: optimization cockpit widget
        """
        return self.widget

    def build(self) -> None:
        """ Method building the optimization cockpit widget with plotly library

        """
        self.update_title(len(self.min_logger_df), self.min_logger_df.loc[self.min_logger_df.index[-1], SCORE_KEYWORD])

        # Display fitness function graph with callback
        self.display_fitness_function_graph(row=2, col=2)

        index_best = self.min_logger_df.index[-1]

        # Display selected generation objective table
        obj_best_df = create_objective_table(self.config, self.min_logger_df, index_best)
        self.display_objective_table(obj_best_df)

        # Display fitness function comparison graph
        self.display_fitness_function_comparison_graph(obj_best_df, obj_best_df, row=1, col=1)

        # Display design variables graph
        self.display_design_variables_graph(index_best, index_best, row=2, col=1)

        # Display geometry graph
        self.display_geometry_graph(index_best, row=3, col=2)

        # Create callback function
        def callback(object: "OptimizationCockpitWidget"):
            def update_point(trace, points, selector):
                index = points.point_inds[0]

                # Update selected generation objective table
                widget_data = object.widget.data[1]
                obj_df = create_objective_table(object.config, object.min_logger_df, index)
                OptimizationCockpitWidget.update_objective_table(widget_data, obj_df)

                # Clear remaining graphs before display
                object.widget.data = [object.widget.data[0], object.widget.data[1]]

                # Display fitness function comparison graph
                object.display_fitness_function_comparison_graph(obj_df, obj_best_df, row=1, col=1)

                # Display design variables graph
                object.display_design_variables_graph(index, index_best, row=2, col=1)

                # Display geometry graph
                object.display_geometry_graph(index, row=3, col=2)

                object.update_title(index, object.min_logger_df.loc[index, SCORE_KEYWORD])

            return update_point

        scatter = self.widget.data[0]
        self.widget.layout.hovermode = 'closest'
        scatter.on_click(callback(self))

    def update_title(self, index_gen: int, fitness_function: float) -> None:
        """ Method updating the widget title with generation index and fitness function value

        :param index_gen: generation index (0-based)
        :param fitness_function: fitness function value
        """
        self.widget.update_layout(
            height=1000,
            showlegend=False,
            title_x=0.5,
            title_text="Optimization Cockpit - index: %d - fitness function: %f" % (index_gen, fitness_function),
        )

    def display_fitness_function_graph(self, row=2, col=2) -> None:
        """ Method displaying the fitness function graph in the widget at a given index (row and column)

        :param row: row index of the graph (1-based)
        :param col: column index of the graph (1-based)
        """
        self.widget.add_trace(
            go.Scatter(
                x=self.min_logger_df.index.values,
                y=self.min_logger_df[SCORE_KEYWORD].values,
                mode="lines+markers",
                name="fitness",
            ),
            row=row, col=col
        )
        if self.is_log_y:
            self.widget.update_yaxes(type='log', row=row, col=col)

    def display_objective_table(self, obj_df: pd.DataFrame) -> None:
        """ Method displaying the objective table in the widget

        :param obj_df: a dataframe with information to be displayed
        """
        obj_trans_df = transpose_objective_table(obj_df)

        self.widget.add_trace(
            go.Table(
                header=dict(
                    values=obj_trans_df.columns,
                    font=dict(size=10),
                    align="left"
                ),
                cells=dict(
                    values=[obj_trans_df[k].tolist() for k in obj_trans_df.columns],
                    align="left")
            ),
            row=1, col=2)

    @staticmethod
    def update_objective_table(widget_data, obj_df: pd.DataFrame) -> None:
        """ Static method updating the objective table

        :param widget_data: reference to the table widget in the cockpit
        :param obj_df: new objective dataframe
        """
        obj_trans_df = transpose_objective_table(obj_df)

        widget_data.cells = dict(
            values=[obj_trans_df[k].tolist() for k in obj_trans_df.columns],
            align="left")

    def display_fitness_function_comparison_graph(self,
                                                  obj_df: pd.DataFrame,
                                                  obj_best_df: pd.DataFrame,
                                                  row=1,
                                                  col=1) -> None:
        """ Method displaying a fitness function comparison graph. The bar graph contains contributions of each of the
        objectives.

        :param obj_df: objective table for a selected individual
        :param obj_best_df: objective table for the best individual
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """
        objective_variables = obj_df.index.values
        fitness_actual = obj_df['objective_weighted'].values
        fitness_best = obj_best_df['objective_weighted'].values

        cum_fitness_actual = list(accumulate(fitness_actual))
        cum_fitness_best = list(accumulate(fitness_best))

        hover_text_actual = ['%s: %f' % obj_fitness for obj_fitness in zip(objective_variables, fitness_actual)]
        hover_text_best = ['%s: %f' % obj_fitness for obj_fitness in zip(objective_variables, fitness_best)]

        n = len(objective_variables)
        for i in range(n):
            trace = go.Bar(
                x=[cum_fitness_best[n - i - 1], cum_fitness_actual[n - i - 1]],
                y=['Best', 'Actual'],
                hovertext=[hover_text_best[n - i - 1], hover_text_actual[n - i - 1]],
                orientation='h',
                hoverinfo='text',
                offsetgroup=1
            )
            self.widget.append_trace(trace, row, col)

    def display_design_variables_graph(self, index_act: int, index_best: int, row=2, col=1) -> None:
        """ Method displaying the design variables graph. The graph compares a selected individual with the best one.

        :param index_act: index of a selected individual (0-based)
        :param index_best: index of the best individual (0-based)
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """

        trace_best = self._prepare_bar_plot_with_fraction(index_best, 'Best')
        trace_act = self._prepare_bar_plot_with_fraction(index_act, 'Actual')

        self.widget.add_traces([trace_best, trace_act], rows=row, cols=col)

    def _prepare_bar_plot_with_fraction(self, index: int, name: str) -> go.Bar:
        return go.Bar(x=prepare_fractions_for_bar_plot(self.gen_opt.design_variables, self.min_logger_df, index),
                      hovertext=prepare_hover_texts_for_bar_plot(self.gen_opt.design_variables, self.min_logger_df, index),
                      y=[dv.get_compact_variable_name() for dv in self.gen_opt.design_variables],
                      name=name,
                      orientation='h')

    def display_geometry_graph(self, index: int, row=3, col=2) -> None:
        """ Method displaying a geometry preview for a selected index.

        :param index: index of a selected individual
        :param row: row index of the graph in the widget (1-based)
        :param col: column index of the graph in the widget (1-based)
        """
        fit_row = self.min_logger_df[self.min_logger_df.index == index]
        fit_dct = fit_row.to_dict('records')[0]
        individual = Individual(self.gen_opt.design_variables)
        for gen_dv in individual.gen_dvs:
            gen_dv.value = fit_dct[gen_dv.get_compact_variable_name()]
        geometry = self.gen_opt.model_runner.model_translator.update_geometry(individual)
        geometry.build_blocks()

        go_scatter = GeometryPlot._create_plotly_scatters(geometry.blocks)

        # To avoid plotting issues in case the number of turns is smaller than in the first plot
        max_number_of_blocks = int(sum([dv.xu for dv in self.gen_opt.design_variables if dv.variable == 'nco']))
        for i in range(max_number_of_blocks - len(go_scatter)):
            go_scatter.append(go.Scatter(x=[], y=[]))

        self.widget.add_traces(go_scatter, rows=row, cols=col)


def create_objective_table(config: OptimizationConfig,
                           min_logger_df: pd.DataFrame,
                           index: int
                           ) -> pd.DataFrame:
    """ Method creating the objective table by extracting weights, constraints, and weighted objectives

    :param config:
    :param min_logger_df:
    :param index: index of a selected best individual per generation
    :return: a dataframe representing the selected individual
    """
    objectives = [obj.objective for obj in config.model_runner_config.objectives]
    obj_df = pd.DataFrame(min_logger_df.loc[index, objectives])
    obj_df = obj_df.rename(columns={obj_df.columns[0]: 'objective'})

    obj_df['weights'] = obj_df.apply(lambda col: config.get_weight(col.name), axis=1)
    obj_df['constraints'] = obj_df.apply(lambda col: config.get_constraint(col.name), axis=1)
    obj_df['objective_weighted'] = obj_df['weights'] * (obj_df['objective'] - obj_df['constraints'])

    return obj_df


def transpose_objective_table(obj_df: pd.DataFrame) -> pd.DataFrame:
    """ Static method transposing the objective table for a selected best individual for a generation

    :param obj_df: input objective table
    :return: transposed input objective table
    """
    obj_trans_df = obj_df.T
    obj_trans_df = obj_trans_df.reset_index()
    obj_trans_df = obj_trans_df.rename(columns={"index": ""})
    return obj_trans_df


def prepare_fractions_for_bar_plot(design_variables: List,
                                   min_logger_df: pd.DataFrame,
                                   index: int
                                   ) -> List[float]:
    """ Prepare a list of fractions of design variable values for a bar plot display

    :param design_variables: a list of cockpit design variables
    :param min_logger_df:
    :param index:
    :return: a list of fractions for a bar plot
    """
    return [dv.get_fraction(min_logger_df.loc[index, dv.get_compact_variable_name()]) for dv in design_variables]


def prepare_hover_texts_for_bar_plot(design_variables,
                                     min_logger_df: pd.DataFrame,
                                     index: int
                                     ) -> List[float]:
    """ Prepare a list of hover texts for a bar plot display

    :param design_variables: a list of cockpit design variables
    :param min_logger_df:
    :param index:
    :return:a list of hover texts for a bar plot
    """
    return [dv.get_hover_text(min_logger_df.loc[index, dv.get_compact_variable_name()]) for dv in design_variables]
