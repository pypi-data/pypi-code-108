# -*- Mode: Python; coding: utf-8; indent-tabs-mode: nil; tab-width: 4 -*-
### BEGIN LICENSE
# Copyright (C) 2013 Rémi Pannequin, Centre de Recherche en Automatique
# de Nancy remi.pannequin@univ-lorraine.fr
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License version 3, as published
# by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>
### END LICENSE



"""This module allow to create various charts from emulica results."""


import logging
import matplotlib
from matplotlib import figure, patches, colors, cm
#import cairo
#matplotlib.use('GTK3Cairo')
from matplotlib.backends.backend_pdf import FigureCanvas

logger = logging.getLogger('emulica.plot')


class Monitor(object):
    """ Collect time series of values
    Attributes:
        env - the simulation runtime
        event_times - event times
        event_values - values
    """
    def __init__(self, env):
        """Create instance
        Parameters:
            env - the simulation runtime
        """
        self.env = env
        self.event_times = [0]
        self.event_values = [0]

    def observe(self, value):
        """Add observation"""
        self.event_times.append(self.env.now)
        self.event_values.append(value)

    def tseries(self):
        """Get the event times"""
        return self.event_times

    def yseries(self):
        """Get the event values"""
        return self.event_values

    def __len__(self):
        """Return the number of events"""
        return len(self.event_times)

    def time_average(self):
        """Return the time average of the y serie, at time t=now.
        Result is area of the function defined as
            f(t) = yk if t is in [tk, tk+1],
        divided by the total time"""
        now = self.env.now
        ext_time = self.event_times + [now]
        result = 0
        for i in range(len(self.event_times)):
            result += self.event_values[i]*(ext_time[i+1] - ext_time[i])
        return result / now


class HolderChart(object):
    """A graph that show holders occupation as a function of time. several
    Holder can be displayed on the same graph
    """

    def __init__(self, name="holder occupation"):
        """Create a new instance of this graph"""
        self.name = name
        self.__fig = figure.Figure()
        self.plot = self.__fig.add_subplot(111)
        self.lines = []
        self.labels = []
        self.legend = dict()
        self.max = 0
        self.t_end = 0

    def process_trace(self, times, values):
        """Make data suitable for a "step" plot."""
        res_s = []
        res_t = []
        cur_v = values[0]
        res_s.append(cur_v)
        res_t.append(times[0])
        for (v, t) in zip(values[1:], times[1:]):
            res_s.append(cur_v)
            res_t.append(t)
            cur_v = v
            res_s.append(v)
            res_t.append(t)
        res_s.append(cur_v)
        res_t.append(self.t_end)
        self.max = max(values)
        return (res_t, res_s)

    def add_serie(self, name, holder):
        """Add a line in the graph."""
        monitor = holder.monitor
        #check whether there is actually some traces in the monitor
        if not monitor:
            raise Exception(_("no monitor on this holder."))
        times = monitor.tseries()
        values = monitor.yseries()
        self.t_end = monitor.env.now
        (times, values) = self.process_trace(times, values)
        self.t_end = max(self.t_end, max(times) + 1)
        self.plot.set_ylabel(name)
        line = self.plot.plot(times, values, linewidth=1.0)
        converter = colors.ColorConverter()
        self.legend[name] = converter.to_rgba(line[0].get_color())

    def __finish_plot(self):
        """Finish drawing the plot and set mics options."""
        self.plot.set_xlabel(_("time"))
        self.plot.set_ylabel(_("holder occupation"))
        self.plot.set_title(self.name)
        self.plot.grid(True)
        self.plot.set_ylim(0, self.max + 1)

    def create_canvas(self):
        """Return a cairo embeddable widget."""
        self.__finish_plot()
        canvas = FigureCanvas(self.__fig)
        canvas.set_size_request(-1, 200)
        return canvas

    def save(self, filename, size=(8, 4)):
        """save the chart in a file"""
        self.__finish_plot()
        canvas = FigureCanvas(self.__fig)
        self.__fig.set_canvas(canvas)
        self.__fig.set_size_inches(size)
        self.__fig.savefig(filename, dpi=100)


class ProductChart(object):
    """
    A gantt chart that focus on products
    """
    def __init__(self, name=_("product life-cycle"), limit=50):
        """Create a new instance of a ProductChart"""
        self.name = name
        self.limit = limit
        self.__fig = figure.Figure()
        self.plot = self.__fig.add_subplot(111)
        self.rows = []
        self.legend = dict()
        self.colormap = cm.ScalarMappable(cmap=cm.gist_rainbow)
        self.colormap.set_clim(0, 10)

    def add_serie(self, name, prod):
        """Add data correponding to a new product. Basicaly, it is adding a line
        in a gantt chart, with its PID as title. Create and Dispose time are marked as
        tick vertical line."""
        if len(self.rows) > self.limit:
            logger.warning(_("Too many row in product chart, add_serie is ignored..."))
            return
        space_tr = []
        i = -1
        for i in range(len(prod.space_history) - 1):
            space_tr.append((prod.space_history[i][0],
                             prod.space_history[i+1][0] - prod.space_history[i][0]))
            space = prod.space_history[i][1]
            if not space in self.legend:
                self.legend[space] = color_from_int(self.colormap, len(self.legend) + 1)
        i += 1
        space_tr.append((prod.space_history[i][0], prod.dispose_time - prod.space_history[i][0]))
        space = prod.space_history[i][1]
        if not space in self.legend:
            self.legend[space] = color_from_int(self.colormap, len(self.legend) + 1)
        y = len(self.rows) + 0.35
        self.plot.broken_barh(space_tr,
                              (y, 0.3),
                              facecolors=[self.legend[s[1]] for s in prod.space_history])
        #draw line and annotations for
        for shape_tr in prod.shape_history:
            self.plot.hlines([y + 0.35], [shape_tr[0]], [shape_tr[1]], lw=3)
            self.plot.text(shape_tr[0], y + 0.37, "{0}, {1}".format(shape_tr[2], shape_tr[3]))
        #draw lines for create time and dispose time
        self.plot.vlines([prod.create_time, prod.dispose_time], [y], [y+0.5], lw=3)
        self.rows.append(prod.pid)

    def __create_plot(self):
        """Create actual plot"""
        self.plot.set_ylim(0, len(self.rows))
        self.plot.set_xlabel('time')
        self.plot.set_yticks([i+0.5 for i in range(len(self.rows))])
        self.plot.set_yticklabels(self.rows)
        self.plot.set_yticklabels(self.rows)
        self.plot.grid(True)

    def save(self, filename, size=(8, 4)):
        """save the chart in a file"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        self.__fig.set_canvas(canvas)
        self.__fig.set_size_inches(size)
        self.__fig.savefig(filename, dpi=100)

    def create_canvas(self):
        """Return a cairo embeddable widget"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        return canvas


class Legend(object):
    def __init__(self, data):
        """Create a new plot to display legend entries"""
        self.data = data
        self.__fig = figure.Figure()
        self.plot = self.__fig.add_subplot(111, aspect='equal')
        self.plot.set_axis_off()

    def __create_plot(self):
        self.plot.set_ylim(0, len(self.data)*1.5)
        self.plot.set_xlim(0, 10)
        i = 0
        for (t, c) in self.data.items():
            rect = patches.Rectangle((0, i*1.5), 1, 1, edgecolor='black', facecolor=c)
            self.plot.add_patch(rect)
            self.plot.annotate(t, (2, i*1.5+0.3))
            i += 1

    def save(self, filename, size=(8, 4)):
        """save the chart in a file"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        self.__fig.set_canvas(canvas)
        self.__fig.set_size_inches(size)
        self.__fig.savefig(filename, dpi=100)

    def create_canvas(self):
        """Return a cairo embeddable widget"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        return canvas


class GanttChart(object):
    """
    A Gantt chart showing colored horizontal bar to show activity of resources...

    Attributes:
        name -- the name of the graph
        plot -- the chart's plot
    """
    def __init__(self, name=_("gantt chart")):
        """Create a new instance of a GanttChart
        Arguments:
            name -- The name of the chart (default="gantt chart")
            legend -- a dictionary of the form (entry: color_name)
        """
        self.name = name
        self.__fig = figure.Figure()
        #self.__fig.hold(False)
        self.plot = self.__fig.add_subplot(111)
        self.rows = []
        self.legend = {'setup': (0.4, 0.4, 0.4, 1), 'failure': (0, 0, 0, 0.5)}
        self.colormap = cm.ScalarMappable(cmap=cm.jet)
        self.colormap.set_clim(0, 10)

    def process_trace(self, name, trace):
        """Return a condensed trace"""
        failures = list()
        condensed = list()
        epsilon = pow(10, -6)
        if trace:
            #remove failures from the list
            for tr in trace:
                p = tr[2]
                if p == 'failure':
                    failures.append(tr)
            for tr in failures:
                trace.remove(tr)
            #condensate the rest
            p = name+trace[0][2]#this is useful when different resources execute prog with the same name
            start = trace[0][0]
            end = trace[0][1]
            for tr in trace[1:]:
                if tr[0] == tr[1]:
                    pass
                elif tr[2] == p and abs(tr[0] - end) < (end * epsilon):
                    end = tr[1]
                else:
                    condensed.append((start, end, p))
                    start = tr[0]
                    p = name+tr[2]
                    end = tr[1]
            condensed.append((float(start), float(end), p))
            #add legend entries
            for (start, end, p) in condensed:
                if not p in self.legend.keys():
                    self.legend[p] = color_from_int(self.colormap, len(self.legend))
        else:
            condensed.append((0, 0, 'failure'))
            logger.warning(_("Adding an empty trace to gantt chart"))
        return (condensed, failures)

    def add_serie(self, name, module):
        """Add a new resource trace (i.e. a new line) to the gantt chart. The
        module object must have a trace attribute that is a list of tuples of
        the form: (start, end, state)

        Arguments:
            name -- the name of the resource
            module -- the module
        """
        trace = module.trace
        #condensate the trace
        (condensed, failures) = self.process_trace(name, trace)
        #add to plot
        y = 10*(len(self.rows)+1)
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in condensed],
                              (y, 6),
                              color=[self.legend[tr[2]] for tr in condensed])
        #add text on the bars
        for tr in condensed:
            if not ('setup' in tr[2] or 'failure' in tr[2]):
                self.plot.text(tr[0], y + 7, tr[2][len(name):], va='bottom')
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in failures],
                              (y, 3),
                              color='black')
        self.plot.broken_barh([(tr[0], tr[1] - tr[0]) for tr in failures],
                              (y+6, 3),
                              color='black')
        self.rows.append(name)

    def __create_plot(self):
        """Create actual plot"""
        i = len(self.rows)
        self.plot.set_ylim(5, (i * 10) + 15)
        self.plot.set_xlabel('time')
        self.plot.set_yticks([(y + 1) * 10 + 5 for y in range(i)])
        self.plot.set_yticklabels(self.rows)
        self.plot.grid(True)

    def save(self, filename, size=(8, 4)):
        """Save the chart in a file"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        self.__fig.set_canvas(canvas)
        self.__fig.set_size_inches(size)
        self.__fig.savefig(filename, dpi=100)

    def create_canvas(self):
        """Return a cairo embeddable widget"""
        self.__create_plot()
        canvas = FigureCanvas(self.__fig)
        #canvas.set_size_request(-1, 100 + 30 * len(self.rows))
        return canvas


def color_from_int(colormap, n):
    """Return a color in the colormap the correspond to the integer n (greater than zero).
    if n is lower than 10, the nth element of the colormap is returned, if greater, there is
    a shift added to avoid same color: 1/2 (11-20), 1/4(21-30), 3/4, 1/16, 3/16, 5/16, ...
    """
    from math import log, floor
    seq = n % 10
    if seq > 10:
        r = n//10
        p = floor(log(r, 2))
        shift = (2 * (r - pow(2, p)) + 1)/(pow(2, p + 1))
    else:
        shift = 0
    return colormap.to_rgba((seq+shift))

