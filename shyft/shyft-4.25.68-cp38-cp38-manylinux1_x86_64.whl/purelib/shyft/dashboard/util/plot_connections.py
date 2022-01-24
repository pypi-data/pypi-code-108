import numpy as np
from bokeh.io import output_file, show
from bokeh.models import (Range1d, ColumnDataSource, LabelSet)
from bokeh.plotting import figure

# TODO: to do refactor this such that it takes an composable_app or class with ports
# TODO: methods to plot connections


def plot_ports(self) -> None:
    name = self.__class__.__name__
    output_file("ports_{}.html".format(name), title="Defined ports for {}".format(name), mode='inline')
    fig = self._generate_port_figure()
    show(fig)


def plot_ports_notebook(self) -> None:
    fig = self._generate_port_figure()
    handle = show(fig, notebook_handle=True)
    return handle


def _generate_port_figure(self):

    name = self.__class__.__name__

    n_receiver = len(self.receiver.registered_attributes)
    n_sender = len(self.sender.registered_attributes)

    n_ports_max = max(n_receiver, n_sender)
    n_ports_min = min(n_receiver, n_sender)

    x_b = 0.05
    x_max = (4 + 2 * (n_ports_max - 1)) * x_b
    y_max = x_b * 2
    x_vals_max_ports = (np.arange(n_ports_max) + 1) * 2 * x_b
    x_b_min = x_max / (n_ports_min + 1)
    x_vals_min_ports = (np.arange(n_ports_min) + 1) * x_b_min

    fig = figure(title="Defined ports for {}".format(name), toolbar_location=None, tools='pan',
                 x_axis_location=None, y_axis_location=None)

    fig.grid.grid_line_color = None
    fig.x_range = Range1d(-2 * x_b, x_max + 2 * x_b)
    fig.y_range = Range1d(-(x_max + 2 * x_b), x_max + 2 * x_b)

    if n_receiver > n_sender:
        x_receiver = x_vals_max_ports
        x_sender = x_vals_min_ports
    else:
        x_receiver = x_vals_min_ports
        x_sender = x_vals_max_ports

    # receiver glyphs
    receiver_color = '#E36042'
    source_receiver = ColumnDataSource(
        data=dict(x=x_receiver, y=[y_max + x_b * 0.5] * n_receiver, names=self.receiver.registered_attributes,
                  angle=[0.5] * n_receiver))
    labels = LabelSet(x='x', y='y', text='names', level='glyph',
                      x_offset=13, y_offset=-4, source=source_receiver, angle='angle', text_font_size='16pt',
                      text_color=receiver_color)
    fig.multi_line([[x, x] for x in x_receiver], [[y_max, y_max + x_b * 0.5] for y in x_receiver], line_width=6,
                   color=receiver_color)
    fig.scatter(x='x', y='y', size=15, source=source_receiver, color=receiver_color)
    fig.add_layout(labels)

    # sender glyphs
    sender_color = '#58BD3C'
    source_sender = ColumnDataSource(
        data=dict(x=x_sender, y=[-x_b * 0.5] * n_sender, names=self.sender.registered_attributes,
                  angle=[-0.5] * n_sender))
    labels_sender = LabelSet(x='x', y='y', text='names', level='glyph',
                             x_offset=5, y_offset=-12, source=source_sender, angle='angle', text_font_size='16pt',
                             text_color=sender_color)
    fig.multi_line([[x, x] for x in x_sender], [[0, -x_b * 0.5] for y in x_sender], line_width=6,
                   color=sender_color)
    fig.rect(x='x', y='y', source=source_sender, width=x_b / 4, height=x_b / 4, color=sender_color)
    fig.add_layout(labels_sender)

    fig.patch(x=[0, x_max, x_max, 0], y=[0, 0, y_max, y_max], color='#dae8e3')
    name_label = LabelSet(x=x_b, y=y_max * 0.20, x_units='data', y_units='data', text=[name], render_mode='css',
                          text_font_size='24pt')
    fig.add_layout(name_label)

    return fig