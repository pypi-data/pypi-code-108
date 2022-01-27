# This file is part of Sympathy for Data.
# Copyright (c) 2019, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

from itertools import cycle

import numpy as np

import bokeh
from bokeh.plotting import figure
from bokeh.models import Range1d
from bokeh.embed import components

from bokeh.models import ColumnDataSource
from bokeh.palettes import Spectral6
from bokeh.transform import factor_cmap
from bokeh.models.widgets import Panel, Tabs

from sympathy.api import fx_wrapper


class GeneratePlots(fx_wrapper.FxWrapper):
    arg_types = ['(json, table)']

    def execute(self):
        table = self.arg[1]

        TOOLS='pan,wheel_zoom,box_zoom,reset,save'
        scatter_colors = ('red', 'blue', 'green')
        plots = {}

        # Price/year plot
        col = table['year']
        y = table['price']
        fig = figure(tools=TOOLS, plot_width=300, plot_height=300)
        fig.scatter(col, y, size=12, color='red', alpha=0.5)
        plots['price-per-year'] = fig

        # Manufacturer count
        manufacturers, counts = np.unique(table['name'], return_counts=True)

        source = ColumnDataSource(data=dict(manufacturers=manufacturers, counts=counts))

        p = figure(x_range=manufacturers, plot_height=600, toolbar_location=None, title="Manufacturer Counts")
        try:
            p.vbar(x='manufacturers', top='counts', width=0.9, source=source, legend_group="manufacturers",
                   line_color='white', fill_color=factor_cmap('manufacturers', palette=Spectral6, factors=manufacturers))
        except AttributeError:
            p.vbar(x='manufacturers', top='counts', width=0.9, source=source, legend="manufacturers",
                   line_color='white', fill_color=factor_cmap('manufacturers', palette=Spectral6, factors=manufacturers))

        p.xgrid.grid_line_color = None
        p.y_range.start = 0
        p.y_range.end = max(counts)
        p.legend.orientation = "horizontal"
        p.legend.location = "top_center"

        plots['p'] = p

        script, div = components(plots)

        res = {
            'script': script,
            'div': div,
            'bokeh_version': bokeh.__version__,
        }
        self.res[0].set(res)
