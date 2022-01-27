import numpy as np
import plotly.express as px
import plotly.graph_objects as po
from kinalite.experiment import Experiment


def plot_experiment_results(experiment: Experiment, order = None):
    if experiment.results is None:
        results = experiment.calculate_results()
    else:
        results = experiment.results

    if order is None:
        result = experiment.calculate_best_result()
    else:
        result = experiment.calculate_results([float(order)])[0]

    scores_fig = px.scatter(x=[r.order for r in results], y=[r.score for r in results], labels={'y': 'Error', 'x': 'Order'}, title=f'Order scores in {experiment.name}')
    scores_fig.show()

    curves_fig = po.Figure()
    curves_fig.add_trace(po.Scatter(x=result.x[0], y=result.y[0], mode='markers', name='Exp 1'))
    curves_fig.add_trace(po.Scatter(x=result.x[1], y=result.y[1], mode='markers', name='Exp 2'))
    curves_fig.update_layout(title=f'Order in {experiment.name}', xaxis_title=f'Σ[{experiment.name}]^{result.order:.2}', yaxis_title='[P]')
    curves_fig.show()


def plot_experiment_data(dataframe, column_a_index, column_b_index):
    figure = po.Figure()
    figure.add_trace(po.Scatter(x=dataframe[dataframe.columns[0]], y=dataframe[dataframe.columns[column_a_index]], mode='markers', name='A'))
    figure.add_trace(po.Scatter(x=dataframe[dataframe.columns[0]], y=dataframe[dataframe.columns[column_b_index]], mode='markers', name='B'))
    figure.show()