from typing import List

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
from ipyaggrid import Grid

from magnumapi.geometry.blocks.Block import Block
from magnumapi.geometry.primitives.Arc import Arc


class GeometryPlot:
    @classmethod
    def plotly_geometry_blocks(cls, geometry, figsize=(750, 750), xlim=(0, 80), ylim=(0, 80)):
        """ Method plotting blocks with plotly library

        :param figsize: size of the figure on a display
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        go_scatters = cls._create_plotly_scatters(geometry.blocks)

        fig = go.Figure(go_scatters)
        fig.update_layout(
            autosize=False,
            width=figsize[0],
            height=figsize[1],
            yaxis_range=ylim,
            xaxis_range=xlim,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)'
        )
        fig.add_trace(px.scatter(x=[0], y=[0]).data[0])
        fig.update_xaxes(title=dict(text='x, [mm]'))
        fig.update_yaxes(title=dict(text='y, [mm]'))
        fig.show()

    @staticmethod
    def _create_plotly_scatters(blocks: List[Block]) -> List[go.Scatter]:
        """ Static method creating a list of plotly scatter instances

        :param blocks: list of blocks to convert to plotly scatter
        :return: a list of plotly scatter instances
        """
        go_scatter = []
        index = 1
        for block in blocks:
            for area in block.areas:
                x = [line.p1.x for line in area.lines]
                y = [line.p1.y for line in area.lines]
                x.append(area.get_line(0).p1.x)
                y.append(area.get_line(0).p1.y)

                go_scatter.append(go.Scatter(x=x, y=y, fill="toself", fillcolor='white', marker=dict(size=1),
                                             name='turn' + str(index), line=go.scatter.Line(color='blue')))
                index += 1

        return go_scatter

    @staticmethod
    def plot_blocks(geometry, figsize=(10, 10), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        """ Method plotting all blocks with matplotlib library

        :param figsize: size of a figure on a screen
        :param is_grid: if True, then the grid is displayed, otherwise False
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        ax.grid(is_grid)

        for block in geometry.blocks:
            block.plot_block(ax)

        plt.show()

    @staticmethod
    def plot_bare_blocks(geometry, figsize=(15, 15), is_grid=True, xlim=(0, 80), ylim=(0, 80)) -> None:
        """ Method plotting bare (uninsulated) areas for all blocks in a geometry

        :param figsize: size of a figure on a screen
        :param is_grid: if True, then the grid is displayed, otherwise False
        :param xlim: limits in x-direction
        :param ylim: limits in y-direction
        """
        fig, ax = plt.subplots(figsize=figsize)
        ax.set_aspect('equal', 'box')
        ax.grid(is_grid)
        ax.set_xlim(xlim)
        ax.set_ylim(ylim)
        for block in geometry.blocks:
            block.plot_bare_block(ax)

        plt.show()

    @staticmethod
    def plotly_homogenized_geometry_blocks(geometry, figsize=(65, 65), xlim=(0, 80), ylim=(0, 80)):

        lines = []
        arcs = []

        index = 1
        for block in geometry.blocks:
            line_bottom = block.areas[0].get_line(0)
            arc_outer = block.areas[0].get_line(1)
            line_top = block.areas[0].get_line(2)
            arc_inner = block.areas[0].get_line(3)

            arcs.append(dict(type="path",
                             path=Arc.describe_ellipse_arc(a=arc_inner.get_radius(),
                                                           b=arc_inner.get_radius(),
                                                           start_angle=arc_inner.get_start_angle_in_rad(),
                                                           end_angle=arc_inner.get_end_angle_in_rad()),
                             line_color="black"))

            arcs.append(dict(type="path",
                             path=Arc.describe_ellipse_arc(a=arc_outer.get_radius(),
                                                           b=arc_outer.get_radius(),
                                                           start_angle=arc_outer.get_start_angle_in_rad(),
                                                           end_angle=arc_outer.get_end_angle_in_rad()),
                             line_color="black"))

            lines.append(go.Scatter(x=[line_bottom.p1.x, line_bottom.p2.x],
                                    y=[line_bottom.p1.y, line_bottom.p2.y],
                                    fill="toself", fillcolor='white', marker=dict(size=1),
                                    name='block' + str(index), line=go.scatter.Line(color='black')))

            lines.append(go.Scatter(x=[line_top.p1.x, line_top.p2.x],
                                    y=[line_top.p1.y, line_top.p2.y],
                                    fill="toself", fillcolor='white', marker=dict(size=1),
                                    name='block' + str(index), line=go.scatter.Line(color='black')))

            index += 1

        fig = go.Figure(lines)
        fig.update_layout(
            autosize=False,
            width=figsize[0],
            height=figsize[1],
            xaxis_range=xlim,
            yaxis_range=ylim,
            showlegend=False,
            plot_bgcolor='rgba(0,0,0,0)',
            shapes=arcs
        )
        fig.add_trace(px.scatter(x=[0], y=[0]).data[0])
        fig.update_xaxes(title=dict(text='x, [mm]'))
        fig.update_yaxes(title=dict(text='y, [mm]'))
        fig.show()

    @staticmethod
    def display_definition_table(df: pd.DataFrame) -> Grid:
        """ Static method displaying a definition table in an editable format in a notebook

        :param df: a dataframe to be displayed
        :return: an object to be displayed in a notebook
        """
        column_defs = [{'headername': c, 'field': c} for c in df.columns]

        grid_options = {
            'columnDefs': column_defs,
            'enableSorting': True,
            'enableFilter': True,
            'enableColResize': True,
            'enableRangeSelection': True,
            'rowSelection': 'multiple',
        }

        return Grid(grid_data=df,
                    grid_options=grid_options,
                    quick_filter=True,
                    show_toggle_edit=True,
                    sync_on_edit=True,
                    export_csv=True,
                    export_excel=True,
                    theme='ag-theme-balham',
                    show_toggle_delete=True,
                    columns_fit='auto',
                    index=False)
