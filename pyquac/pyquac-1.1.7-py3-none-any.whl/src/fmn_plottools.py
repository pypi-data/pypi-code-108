"""
plot tools provides fast and elegant solution for plotting quantum experiment data
"""
from typing import Union, Iterable
import pandas as pd
import numpy as np
import cufflinks as cf
import plotly.graph_objects as go

from plotly.offline import init_notebook_mode

# to make notebook's plots still active after rebooting the Kernel:
import plotly.io as pio


def notebook_offline_settings():
    pio.renderers.default = 'notebook'

    init_notebook_mode(connected=True)
    cf.go_offline()


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
                    x_axis_title: str = 'Currents, A',
                    y_axis_title: str = 'Frequencies, Hz',
                    colorbar_text: str = None,
                    logo: bool = True
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

        notebook_offline_settings()

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
        Title = title + Sub_title

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
            autosize=True,
            separators='.',
            paper_bgcolor=paper_clr,
            plot_bgcolor=bg_clr)

        """upd numbers formatting. See more https://plotly.com/python/tick-formatting/"""
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
                    x=1, y=1.09,
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

        fig.show('notebook')

    @staticmethod
    def decorate_figure(fig: go._figure.Figure = None, *,
                        theme: str = 'dark',
                        cmap: Union[str, Iterable] = ['#ffd200', '#cb2d3e'],
                        title: str = 'Two Tone Spectroscopy',
                        sub_title: str = None,
                        x_axis_title: str = 'Currents, A',
                        y_axis_title: str = 'Frequencies, Hz',
                        colorbar_text: str = None,
                        logo: bool = True,
                        y_logo_pos: float = 1.09
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

        notebook_offline_settings()

        """More figure|plot settings here: https://plotly.com/python/reference/layout/"""

        """Adding subtitle"""
        Sub_title = '' if sub_title is None else '<br>' + '<i>' + sub_title + '</i>'
        Title = title + Sub_title

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
            autosize=True,
            separators='.',
            paper_bgcolor=paper_clr,
            plot_bgcolor=bg_clr)

        """upd numbers formatting. See more https://plotly.com/python/tick-formatting/"""
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
                    source='https://raw.githubusercontent.com/cldougl/plot_images/add_r_img/vox.png',
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
