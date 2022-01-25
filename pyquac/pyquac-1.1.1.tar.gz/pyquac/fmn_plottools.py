"""
plot tools provides fast and elegant solution for plotting quantum experiment data
"""
from typing import Union, Iterable
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import os
from PIL import Image
from datetime import date, datetime

from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import callback_context


def _save_path(data: str, qubit_name: str = 'qubit_default_name',
               default_path: str = 'D:/Scripts/Measurement_automation/data/qubits/'):

    current_date = str(date.today())

    parent_dir = default_path
    dir_qubit = os.path.join(default_path, str(qubit_name))
    dir_date = os.path.join(dir_qubit, current_date)
    dir_tts = os.path.join(dir_date, 'two_tone_spectroscopy')

    if os.path.exists(parent_dir):

        "checking qubit dir existance"
        if not os.path.exists(dir_qubit):
            os.mkdir(dir_qubit)
        else:
            pass

        "checking date dir existance"
        if not os.path.exists(dir_date):
            os.mkdir(dir_date)
        else:
            pass

        "checking tts dir existance"
        if not os.path.exists(dir_tts):
            os.mkdir(dir_tts)
        else:
            pass

        dir_final = os.path.join(dir_tts, data)
        return dir_final
    else:
        return data


class Heatmap:
    """
    Heatmap class provides easy-to-use workspace for building interactive two tone spectroscopy plots
    """

    @staticmethod
    def plot_figure(data: pd.DataFrame = None, *, x: Union[str, np.ndarray, pd.Series, Iterable] = None,
                    y: Union[str, np.ndarray, pd.Series, Iterable] = None,
                    z: Union[str, np.ndarray, pd.Series, Iterable] = None,
                    theme: str = 'dark',
                    cmap: Union[str, Iterable] = ['#ffd200', '#cb2d3e'],
                    title: str = 'Two Tone Spectroscopy',
                    sub_title: str = None,
                    x_axis_title: str = 'Voltages, V',
                    x_axis_size: int = 13,
                    y_axis_title: str = 'Frequencies, GHz',
                    y_axis_size: int = 13,
                    colorbar_text: str = None,
                    logo: bool = False,
                    logo_local=False,
                    y_logo_pos: float = 1.09,
                    save_png: str = None,
                    save_svg: str = None,
                    qubit_number: Union[str, float] = None,
                    exponent_mode = False,
                    width = 700,
                    height = 600
                    ):

        """
        Built a complete plot of the Two Tone Spectroscopy
        :param data: (optional) Pandas data frame with 3 columns (x, y, z)
        :param x: (optional) Pandas series obj | array-like obj. Currents of Two Tone Spectroscopy
        :param y: (optional) Pandas series obj | array-like obj. Frequencies of Two Tone Spectroscopy
        :param z: (optional) Pandas series obj | array-like obj. Response of Two Tone Spectroscopy
        :param theme: ['white', 'dark'] - plot style. default - 'dark'
        :param cmap: The 'colorscale' property is a colorscale and may be specified as:
                      - A list of colors that will be spaced evenly to create the colorscale.
                        Many predefined colorscale lists are included in the sequential, diverging,
                        and cyclical modules in the plotly.colors package.
                      - A list of 2-element lists where the first element is the
                        normalized color level value (starting at 0 and ending at 1),
                        and the second item is a valid color string.
                        (e.g. [[0, 'green'], [0.5, 'red'], [1.0, 'rgb(0, 0, 255)']])
                      - One of the following named colorscales:
                            ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
                             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
                             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
                             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
                             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
                             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
                             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
                             'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
                             'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
                             'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
                             'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
                             'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
                             'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
                             'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
                             'ylorrd'].
        :param title: (Optional) Sets the plot's title. Default - 'Two Tone Spectroscopy'
        :param sub_title: (Optional) additional information about the plot. Default - None
        :param x_axis_title: (Optional) Sets the title of this axis. Default - 'Currents, A'
        :param y_axis_title: (Optional) Sets the title of this axis. Default - 'Frequencies, Hz'
        :param colorbar_text: (Optional) Sets the title of color bar. Default - None
        :param logo: (Optional) If True - shows the FMN logo at the upper right corner. Default - True
        :return:
        """

        if data is not None:
            fig = go.Figure(data=go.Heatmap(
                z=data.iloc[:, 2],
                x=data.iloc[:, 0],
                y=data.iloc[:, 1],
                colorscale=cmap))
        else:
            fig = go.Figure(data=go.Heatmap(
                z=z,
                x=x,
                y=y,
                colorscale=cmap))

        """Adding subtitle"""
        Sub_title = '' if sub_title is None else '<br>' + '<i>' + sub_title + '</i>'
        Title = title + Sub_title if qubit_number is None else title + ' (qubit ' + str(qubit_number) + ')' + Sub_title

        """Choosing colors"""
        if theme.lower() == 'white':
            fig.update_layout(template="plotly_white")
            title_clr = '#000000'
            bg_clr = '#F5F5F5'
            paper_clr = '#FAFAFA'
            grid_clr = '#757575'
        elif theme.lower() == 'dark':
            fig.update_layout(template="plotly_dark")
            title_clr = '#ffffff'
            bg_clr = '#1c1c1c'
            paper_clr = '#1c1c1c'
            grid_clr = '#757575'
        elif theme.lower() == 'pure_white':
            fig.update_layout(template="plotly_white")
            title_clr = '#000000'
            bg_clr = '#ffffff'
            paper_clr = '#ffffff'
            grid_clr = '#757575'
        else:
            fig.update_layout(template="plotly_dark")
            raise NameError

        """layout settings. See more https://plotly.com/python/reference/layout/#layout-title"""

        fig.update_layout(title={
            'text': Title,
            'font': {
                'color': title_clr
            },
            'x': 0.086
        },
            font=dict(family='Open Sans', color=title_clr),
            xaxis_title=x_axis_title,
            yaxis_title=y_axis_title,
            autosize=False,
            separators='.',
            paper_bgcolor=paper_clr,
            plot_bgcolor=bg_clr)

        fig.update_yaxes(title_font={"size": y_axis_size}, tickfont_size=y_axis_size)
        fig.update_xaxes(title_font={"size": x_axis_size}, tickfont_size=x_axis_size)

        """figure size"""
        # if width is not None:
        #     fig.update_layout(width=width)
        # elif height is not None:
        #     fig.update_layout(height=height)
        # elif (width is not None) and (height is not None):
        #     fig.update_layout(width=width, height=height)
        # else:
        #     pass
        fig.update_layout(width=width, height=height)

        """upd numbers formatting. See more https://plotly.com/python/tick-formatting/"""
        if not exponent_mode:
            fig.update_layout(yaxis=dict(showexponent='none', exponentformat='e'))
            fig.update_traces(zhoverformat='.2f')
            #fig.update_layout(xaxis=dict(showexponent='none', exponentformat='e'))
        else:
            fig.update_layout(yaxis_tickformat='.2e', xaxis_tickformat='.2e')
            fig.update_traces(zhoverformat='.2f')

        """add color bar text"""
        if colorbar_text is not None:
            fig.update_traces(colorbar_title_text=colorbar_text)
        else:
            pass

        """adding logo. See more https://plotly.com/python/images/"""
        if logo:
            fig.add_layout_image(
                dict(
                    source='https://raw.githubusercontent.com/ikaryss/pyquac/Master/images/logo_sign.png',
                    xref="paper", yref="paper",
                    x=1, y=y_logo_pos,
                    sizex=0.09,
                    sizey=0.09,
                    xanchor="right", yanchor="bottom",
                    opacity=1,
                    layer="above"))
        else:
            pass

        if logo_local:
            img = Image.open('logo_sign.png')
            fig.add_layout_image(
                dict(
                    source=img,
                    xref="paper", yref="paper",
                    x=1, y=y_logo_pos,
                    sizex=0.09,
                    sizey=0.09,
                    xanchor="right", yanchor="bottom",
                    opacity=1,
                    layer="above"))
        else:
            pass

        """grid color. See more https://plotly.com/python/axes/"""
        fig.update_layout(xaxis=dict(showgrid=True, gridcolor=grid_clr, gridwidth=0.1,
                                     zeroline=True, zerolinewidth=0.1, zerolinecolor=grid_clr),
                          yaxis=dict(showgrid=True, gridcolor=grid_clr, gridwidth=0.1,
                                     zeroline=True, zerolinewidth=0.1, zerolinecolor=grid_clr))

        if save_png is not None:
            fig.write_image(save_png)

        if save_svg is not None:
            fig.write_image(save_svg)

        return fig

    @staticmethod
    def decorate_figure(fig, *,
                        theme: str = 'dark',
                        cmap: Union[str, Iterable] = ['#ffd200', '#cb2d3e'],
                        title: str = 'Two Tone Spectroscopy',
                        sub_title: str = None,
                        x_axis_title: str = 'Voltages, V',
                        x_axis_size: int = 13,
                        y_axis_title: str = 'Frequencies, GHz',
                        y_axis_size: int = 13,
                        colorbar_text: str = None,
                        logo: bool = False,
                        logo_local=False,
                        y_logo_pos: float = 1.09,
                        qubit_number: Union[str, float] = None,
                        exponent_mode=False,
                        width=None,
                        height=None
                        ):
        """
        Built a complete plot formatter for your go.Fig object.
        :param fig: plotly.graph_objs._figure.Figure object
        :param theme: ['white', 'dark'] - plot style. default - 'dark'
        :param cmap: The 'colorscale' property is a colorscale and may be specified as:
                      - A list of colors that will be spaced evenly to create the colorscale.
                        Many predefined colorscale lists are included in the sequential, diverging,
                        and cyclical modules in the plotly.colors package.
                      - A list of 2-element lists where the first element is the
                        normalized color level value (starting at 0 and ending at 1),
                        and the second item is a valid color string.
                        (e.g. [[0, 'green'], [0.5, 'red'], [1.0, 'rgb(0, 0, 255)']])
                      - One of the following named colorscales:
                            ['aggrnyl', 'agsunset', 'algae', 'amp', 'armyrose', 'balance',
                             'blackbody', 'bluered', 'blues', 'blugrn', 'bluyl', 'brbg',
                             'brwnyl', 'bugn', 'bupu', 'burg', 'burgyl', 'cividis', 'curl',
                             'darkmint', 'deep', 'delta', 'dense', 'earth', 'edge', 'electric',
                             'emrld', 'fall', 'geyser', 'gnbu', 'gray', 'greens', 'greys',
                             'haline', 'hot', 'hsv', 'ice', 'icefire', 'inferno', 'jet',
                             'magenta', 'magma', 'matter', 'mint', 'mrybm', 'mygbm', 'oranges',
                             'orrd', 'oryel', 'oxy', 'peach', 'phase', 'picnic', 'pinkyl',
                             'piyg', 'plasma', 'plotly3', 'portland', 'prgn', 'pubu', 'pubugn',
                             'puor', 'purd', 'purp', 'purples', 'purpor', 'rainbow', 'rdbu',
                             'rdgy', 'rdpu', 'rdylbu', 'rdylgn', 'redor', 'reds', 'solar',
                             'spectral', 'speed', 'sunset', 'sunsetdark', 'teal', 'tealgrn',
                             'tealrose', 'tempo', 'temps', 'thermal', 'tropic', 'turbid',
                             'turbo', 'twilight', 'viridis', 'ylgn', 'ylgnbu', 'ylorbr',
                             'ylorrd'].
        :param title: (Optional) Sets the plot's title. Default - 'Two Tone Spectroscopy'
        :param sub_title: (Optional) additional information about the plot. Default - None
        :param x_axis_title: (Optional) Sets the title of this axis. Default - 'Currents, A'
        :param y_axis_title: (Optional) Sets the title of this axis. Default - 'Frequencies, Hz'
        :param colorbar_text: (Optional) Sets the title of color bar. Default - None
        :param logo: (Optional) If True - shows the FMN logo at the upper right corner. Default - True
        :param y_logo_pos: y position of the logo. Default = 1.09. Usually belongs to [0.9, 1.1] interval
        """

        """More figure|plot settings here: https://plotly.com/python/reference/layout/"""

        """Adding subtitle"""
        Sub_title = '' if sub_title is None else '<br>' + '<i>' + sub_title + '</i>'
        Title = title + Sub_title if qubit_number is None else title + ' (qubit ' + str(qubit_number) + ')' + Sub_title

        """Choosing colors"""
        if theme.lower() == 'white':
            fig.update_layout(template="plotly_white")
            title_clr = '#000000'
            bg_clr = '#F5F5F5'
            paper_clr = '#FAFAFA'
            grid_clr = '#757575'
        elif theme.lower() == 'dark':
            fig.update_layout(template="plotly_dark")
            title_clr = '#ffffff'
            bg_clr = '#1c1c1c'
            paper_clr = '#1c1c1c'
            grid_clr = '#757575'
        elif theme.lower() == 'pure_white':
            fig.update_layout(template="plotly_white")
            title_clr = '#000000'
            bg_clr = '#ffffff'
            paper_clr = '#ffffff'
            grid_clr = '#757575'
        else:
            fig.update_layout(template="plotly_dark")
            raise NameError

        """Color scale plotly. See more https://plotly.com/python/builtin-colorscales/"""
        fig.update_traces(colorscale=cmap)

        """layout settings. See more https://plotly.com/python/reference/layout/#layout-title"""

        fig.update_layout(title={
            'text': Title,
            'font': {
                'color': title_clr
            },
            'x': 0.086
        },
            font=dict(family='Open Sans', color=title_clr),
            xaxis_title=x_axis_title,
            yaxis_title=y_axis_title,
            autosize=False,
            separators='.',
            paper_bgcolor=paper_clr,
            plot_bgcolor=bg_clr)

        fig.update_yaxes(title_font={"size": y_axis_size}, tickfont_size=y_axis_size)
        fig.update_xaxes(title_font={"size": x_axis_size}, tickfont_size=x_axis_size)

        """figure size"""
        if width is not None:
            fig.update_layout(width=width)
        elif height is not None:
            fig.update_layout(height=height)
        elif (width is not None) and (height is not None):
            fig.update_layout(width=width, height=height)
        else:
            pass

        """upd numbers formatting. See more https://plotly.com/python/tick-formatting/"""
        if not exponent_mode:
            fig.update_layout(yaxis=dict(showexponent='none', exponentformat='e'))
            # fig.update_layout(xaxis=dict(showexponent='none', exponentformat='e'))
            fig.update_traces(zhoverformat='.2f')
        else:
            fig.update_layout(yaxis_tickformat='.2e', xaxis_tickformat='.2e')
            fig.update_traces(zhoverformat='.2f')

        """add color bar text"""
        if colorbar_text is not None:
            fig.update_traces(colorbar_title_text=colorbar_text)
        else:
            pass

        """adding logo. See more https://plotly.com/python/images/"""
        if logo:
            fig.add_layout_image(
                dict(
                    source='https://raw.githubusercontent.com/ikaryss/pyquac/Master/images/logo_sign.png',
                    xref="paper", yref="paper",
                    x=1, y=y_logo_pos,
                    sizex=0.09,
                    sizey=0.09,
                    xanchor="right", yanchor="bottom",
                    opacity=1,
                    layer="above"))
        else:
            pass

        if logo_local:
            img = Image.open('logo_sign.png')
            fig.add_layout_image(
                dict(
                    source=img,
                    xref="paper", yref="paper",
                    x=1, y=y_logo_pos,
                    sizex=0.09,
                    sizey=0.09,
                    xanchor="right", yanchor="bottom",
                    opacity=1,
                    layer="above"))
        else:
            pass

        """grid color. See more https://plotly.com/python/axes/"""
        fig.update_layout(xaxis=dict(showgrid=True, gridcolor=grid_clr, gridwidth=0.1,
                                     zeroline=True, zerolinewidth=0.1, zerolinecolor=grid_clr),
                          yaxis=dict(showgrid=True, gridcolor=grid_clr, gridwidth=0.1,
                                     zeroline=True, zerolinewidth=0.1, zerolinecolor=grid_clr))

        pass

    """
    info https://plotly.com/python/static-image-export/
    requirements:
    conda install -c conda-forge python-kaleido
    
    """

    @staticmethod
    def save_fig_as(fig, name: str = 'figure.svg', method: str = 'image', create_folder: bool = False,
                    folder_name: str = 'images'):
        """

        :param fig:
        :param name: export format options for images: [.svg (default), .pdf, .png, .jpeg, .webp]
                     HTML export
        :param method: exporting method [image (default), html]
        :param create_folder:
        :param folder_name:
        :return:
        """
        if create_folder == True:
            if not os.path.exists(folder_name):
                os.mkdir(folder_name)

            directory = folder_name + '/' + name

        else:
            directory = name

        if method == 'image':
            fig.write_image(directory)

        elif method == 'html':
            fig.write_html(directory)


class Dash_app:

    @classmethod
    def configure_app(cls, data, fig, mode='inline', port=8051, interval=5e3, qubit_number=None):
        cls.fig = fig
        cls.mode = mode
        cls.interval = interval
        cls.port = port
        cls.qubit_number = qubit_number

        disabled_btn = False
        disabled_input = False
        maxx_interval = -1

        # Build App
        app = JupyterDash(__name__)
        app.layout = html.Div(
            [
                html.Button('Save CSV', id='btn-nclicks-1', n_clicks=0),
                html.Button('Save PDF', id='btn-nclicks-2', n_clicks=0),
                html.Button('Save HTML', id='btn-nclicks-3', n_clicks=0),
                html.Button('Save SVG', id='btn-nclicks-5', n_clicks=0),
                dcc.Checklist(id='checkbox',
                              options=[{'label': 'stop live upd', 'value': 'NO'}],
                              value=['YES', 'NO'],
                              labelStyle={'display': 'inline-block'}
                              ),
                html.Button('Manual upd', id='btn-nclicks-4', n_clicks=0),
                dcc.Input(
                    id="input_time",
                    type='number',
                    placeholder="Auto upd in, ms",
                    min=800,
                ),
                dcc.Graph(id="heatmap", figure=cls.fig),
                dcc.Interval(id="animateInterval", interval=cls.interval, n_intervals=0,
                             max_intervals=maxx_interval),
            ],
        )

        @app.callback(
            Output("heatmap", "figure"),
            Output("animateInterval", "max_intervals"),
            Output("animateInterval", "interval"),
            Output('btn-nclicks-4', 'disabled'),
            Output('input_time', 'disabled'),
            Input('btn-nclicks-1', 'n_clicks'),
            Input('btn-nclicks-2', 'n_clicks'),
            Input('btn-nclicks-3', 'n_clicks'),
            Input('btn-nclicks-5', 'n_clicks'),
            Input('checkbox', 'value'),
            Input('btn-nclicks-4', 'n_clicks'),
            Input('input_time', 'value'),
            Input("animateInterval", "n_intervals"),
        )
        def doUpdate(btn1, btn2, btn3, btn5, chkbx, btn4, time_val, i):

            if chkbx[-1] == 'NO':
                maxx_interval = 0
                disabled_btn = False
                disabled_input = False
            else:
                maxx_interval = -1
                disabled_btn = True
                disabled_input = True

            changed_id = [p['prop_id'] for p in callback_context.triggered][0]
            if 'btn-nclicks-1' in changed_id:

                file_name = ('TTS_' + 'q' + str(cls.qubit_number) + '_0' + str(datetime.now().strftime(
                    "_%H-%M-%S")) + '.csv' if cls.qubit_number is not None else 'TTS_' + 'q' + '_0' + str(
                    datetime.now().strftime("_%H-%M-%S")) + '.csv')

                data.get_result().to_csv(_save_path(file_name, cls.qubit_number), index=False)
            elif 'btn-nclicks-2' in changed_id:

                file_name = ('TTS_'+'q'+str(cls.qubit_number)+'_0'+str(datetime.now().strftime(
                    "_%H-%M-%S"))+'.pdf' if cls.qubit_number is not None else 'TTS_'+'q'+'_0'+str(
                    datetime.now().strftime("_%H-%M-%S"))+'.pdf')

                fig.write_image(_save_path(file_name, cls.qubit_number))
            elif 'btn-nclicks-3' in changed_id:

                file_name = ('TTS_' + 'q' + str(cls.qubit_number) + '_0' + str(datetime.now().strftime(
                    "_%H-%M-%S")) + '.html' if cls.qubit_number is not None else 'TTS_' + 'q' + '_0' + str(
                    datetime.now().strftime("_%H-%M-%S")) + '.html')

                fig.write_html(_save_path(file_name, cls.qubit_number))
            elif 'btn-nclicks-5' in changed_id:

                file_name = ('TTS_' + 'q' + str(cls.qubit_number) + '_0' + str(datetime.now().strftime(
                    "_%H-%M-%S")) + '.svg' if cls.qubit_number is not None else 'TTS_' + 'q' + '_0' + str(
                    datetime.now().strftime("_%H-%M-%S")) + '.svg')

                fig.write_image(_save_path(file_name, cls.qubit_number))

            elif 'btn-nclicks-4' in changed_id:
                z = data.njit_result
                fig.update_traces(z=z)
            else:
                pass
            if time_val:
                cls.interval = time_val

            z = data.njit_result

            return cls.fig.update_traces(z=z), maxx_interval, cls.interval, disabled_btn, disabled_input

        return app.run_server(mode=cls.mode, port=cls.port)
