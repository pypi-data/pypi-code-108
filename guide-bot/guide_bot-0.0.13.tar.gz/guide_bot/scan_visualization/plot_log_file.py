import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm

import guide_bot.elements.Element_straight as Straight
import guide_bot.elements.Element_elliptic as Elliptic

from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D


def radar_factory(num_vars, frame='circle'):
    """
    A matplotlib example from their webpage:
    https://matplotlib.org/stable/gallery/specialty_plots/radar_chart.html#sphx-glr-gallery-specialty-plots-radar-chart-py

    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta


def read_log_file_old(filename):
    #legend = np.genfromtxt(filename, skip_header=1, max_rows=4, dtype="unicode")

    with open(filename) as file:
        file.readline()
        free_parameters = file.readline().strip().split()
        relative_parameters = file.readline().strip().split()
        other_parameters = file.readline().strip().split()
        legend = file.readline().strip().split()

    data = np.loadtxt(filename, skiprows=5)
    return legend, free_parameters, relative_parameters, other_parameters, data


class LogParameter:
    def __init__(self):
        self.name = None
        self.owner = None
        self.type = None
        self.limits = None

    def read_line(self, line):
        """
        self.name = line[0:50].strip() # name.ljust(60)
        self.owner = line[50:50+30].strip()
        self.type = line[50+30:50+30+60].strip()
        self.limits = line[50+30+60:].strip().split(",")
        """

        line_parts = line.split()

        self.name = line_parts[0].strip()
        self.owner = line_parts[1].strip()
        self.type = line_parts[2].strip()

        if len(line_parts) > 4:
            self.limits = [line_parts[3].strip().strip(","), line_parts[4].strip()]
        else:
            self.limits = ""

    def __repr__(self):
        if isinstance(self.limits, list) and len(self.limits) == 2:
            return self.name + " " + self.owner + " " + self.type + " " + self.limits[0] + ", " + self.limits[1]
        else:
            return self.name + " " + self.owner + " " + self.type


def read_log_file(filename):
    with open(filename) as file:
        file.readline()

        second_line = file.readline()
        try:
            n_parameters = int(second_line)
            scan_name = None
            skip = n_parameters + 3
        except:
            scan_name = second_line.split(" ")[1]
            scan_name = scan_name.strip()
            n_parameters = int(file.readline())
            skip = n_parameters + 4

        parameters = []
        for _ in range(n_parameters):
            par = LogParameter()
            par.read_line(file.readline())
            parameters.append(par)

        legend = file.readline().strip().split()

    data = np.loadtxt(filename, skiprows=skip)

    return legend, parameters, data, scan_name

class GuideElementLog:
    def __init__(self, element_name, element_type):
        self.element_name = element_name
        self.element_type = element_type
        self.parameter_type = {}
        self.parameters = {}

    def add_parameter(self, key, type, value):
        self.parameter_type[key] = type
        self.parameters[key] = value

def read_guide_log_file(filename):
    with open(filename) as file:
        line = file.readline()
        guide_logs = []
        current_log = None
        while line:

            if line.strip() == "":
                line = file.readline()
                continue

            if line.startswith("Element"):
                if current_log is not None:
                    guide_logs.append(current_log)

                element_type = line.split(" ")[1]
                element_name = line.split(" ")[2]
                current_log = GuideElementLog(element_name, element_type)

            elif current_log is not None:
                par_key = line.split()[0].strip()
                par_type = line.split()[1].strip()
                par_name = line.split()[2].strip()

                current_log.add_parameter(par_key, par_type, par_name)

            line = file.readline()

    return guide_logs

def read_full_log(filename):
    legend, parameters, data, scan_name = read_log_file(filename)

    file_location = os.path.split(filename)[0]
    guide_log_filename = os.path.join(file_location, scan_name + ".guide_log")
    guide_element_logs = read_guide_log_file(guide_log_filename)

    return legend, parameters, data, guide_element_logs

def extract_parameters(guide_element, legend, data_line):

    return_dict = {}
    for simple_name in guide_element.parameters:
        instrument_parameter_name = guide_element.parameters[simple_name]
        par_index = legend.index(instrument_parameter_name)
        par_value = data_line[par_index]

        return_dict[simple_name] = par_value

    return return_dict

def plot_guide(filename):

    legend, parameters, data, guide_element_logs = read_full_log(filename)

    plot_data = data[-1, :]

    fig, axs = plt.subplots(figsize=(10,10), nrows=2, ncols=1)

    color = "k"
    for guide_element in guide_element_logs:

        if color == "k":
            color = "b"
        elif color == "b":
            color = "k"

        if guide_element.element_type == "Straight":

            par_dict = extract_parameters(guide_element, legend, plot_data)
            Straight.plot_element_horizontal(axs[0], par_dict, color=color)
            Straight.plot_element_vertical(axs[1], par_dict, color=color)

        if guide_element.element_type == "Elliptic":

            par_dict = extract_parameters(guide_element, legend, plot_data)
            Elliptic.plot_element_horizontal(axs[0], par_dict, color=color)
            Elliptic.plot_element_vertical(axs[1], par_dict, color=color)


def plot_all_foms(foldername, allowed_in_name=[], not_allowed_in_name=[]):
    fig, ax = plt.subplots(figsize=(10,9))
    for file in os.listdir():

        found_allowed = False
        for allowed in allowed_in_name:
            if allowed in file:
                found_allowed = True
                break

        if not found_allowed and len(allowed_in_name) > 0:
            continue

        found_not_allowed = False
        for not_allowed in not_allowed_in_name:
            if not_allowed in file:
                found_not_allowed = True
                break

        if found_not_allowed and len(not_allowed_in_name) > 0:
            continue

        if ".log" in file:
            legend, parameters, data, scan_name = read_log_file(file)
            fom = data[:, 0]
            fom_sort_indices = sort_permutation(fom, reverse=True)
            data_fom_sorted = data[fom_sort_indices, :]
            fom_sorted = data_fom_sorted[:, 0]

            plot_1D_fom(ax, fom, fom_sorted, label=file)

    # Shrink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.show()

def plot_log_file(filename):
    legend, parameters, data, scan_name = read_log_file(filename)

    n_guides = len(data[:, 0])

    fig1, axs = plt.subplots(figsize=(15,20), nrows=4, ncols=2)

    fom = data[:, 0]
    fom_sort_indices = sort_permutation(fom, reverse=True)

    data_fom_sorted = data[fom_sort_indices, :]
    fom_sorted = data_fom_sorted[:, 0]

    # Make plots using functions
    plot_1D_fom(axs[0, 0], fom, fom_sorted)
    plot_1D_cps(axs[1, 0], parameters, legend, data)
    plot_1D_cps(axs[1, 1], parameters, legend, data_fom_sorted)
    plot_1D_non_length(axs[2, 0], parameters, legend, data)
    plot_1D_non_length(axs[2, 1], parameters, legend, data_fom_sorted)
    plot_1D_non_length(axs[3, 0], parameters, legend, data, search="guide_sample_gap_start_")
    plot_1D_non_length(axs[3, 1], parameters, legend, data_fom_sorted, search="guide_sample_gap_start_")

    # Make experimental radial plot
    radial_parameter_plot(legend, parameters, [data_fom_sorted[-1, :]])#, data[-1, :], data[-2, :]])

    plt.show()


def sort_permutation(input, **kwargs):
    L = [(input[i], i) for i in range(len(input))]
    L.sort(**kwargs)
    sorted_start_points_first, permutation = zip(*L)
    return list(permutation)


def plot_1D_fom(ax, fom, fom_data_sorted, **kwargs):
    ax.scatter(range(len(fom)), fom, marker=".", **kwargs)
    ax.plot(fom_data_sorted, color="orange")
    ax.set_xlabel("Optimizer iteration")
    ax.set_ylabel("FOM")


def plot_1D_cps(ax, parameters, legend, data, **kwargs):
    n_guides = len(data[:, 0])
    pars_length_system_names = [par.name for par in parameters if par.owner == "length_system"]
    pars_length_system_indices = [legend.index(par) for par in pars_length_system_names]

    start_points = data[:, pars_length_system_indices]
    start_points_first = start_points[0, :]
    sort_key = sort_permutation(start_points_first)

    ax.plot(range(n_guides), start_points[:,sort_key], **kwargs)
    ax.set_xlabel("iteration")
    ax.set_ylabel("start point [m]")


def plot_1D_non_length(ax, parameters, legend, data, search=None, **kwargs):
    # Want to plot all parameters that are Free/Relative and not related to length system
    plotted_par_names = []
    for par in parameters:
        if (par.owner != "length_system"
                and par.type in ("FreeInstrumentParameter", "RelativeFreeInstrumentParameter")):
            if search is None or search in par.name:
                plotted_par_names.append(par.name)

    if len(plotted_par_names) == 0:
        return

    plotted_par_indices = [legend.index(par) for par in plotted_par_names]

    #print(len(data[:,0]))
    #print(len(data[:, plotted_par_indices]))

    n_indices = len(plotted_par_indices)
    n_guides = len(data[:, 0])
    #ax.scatter(np.ndindex((n_guides, n_indices)), data[:, plotted_par_indices], marker=".", **kwargs)
    for index in plotted_par_indices:
        ax.scatter(range(n_guides), data[:, index], marker=".", label=legend[index], **kwargs)

    #ax.plot(data[:, plotted_par_indices], alpha=0.6)
    ax.set_xlabel("Optimizer iteration")
    ax.set_ylabel("Parameter value")

def plot_correlation(ax, parameters, legend, data, par1, par2, **kwargs):

    par1_index = legend.index(par1)
    par2_index = legend.index(par2)

    max_value = np.max(data[:, par2_index])

    ax.scatter(data[:, par1_index], data[:, par2_index], marker=".", **kwargs)

    fom = data[:, 0]
    best_fom = np.min(fom)
    index_with_fom_zero = np.where(data[:, 0] == 0)
    #index_with_fom_zero = np.where(data[:, 0] > 0.1*best_fom)
    ax.scatter(data[index_with_fom_zero, par1_index], data[index_with_fom_zero, par2_index],
               marker=".", color="red", **kwargs)

    ax.plot([-max_value, 0], [max_value, 0], color="black")
    ax.plot([0, max_value], [0, max_value], color="black")
    ax.set_xlabel(par1)
    ax.set_ylabel(par2)

def radial_parameter_plot(legend, parameters, data_list):
    # Want to plot all parameters that are Free/Relative and not related to length system
    plotted_par_names = []
    for par in parameters:
        if (par.owner != "length_system"
                and par.type in ("FreeInstrumentParameter", "RelativeFreeInstrumentParameter")):
            plotted_par_names.append(par.name)

    if len(plotted_par_names) == 0:
        return

    plotted_par_indices = [legend.index(par) for par in plotted_par_names]

    N_parameters = len(plotted_par_indices)
    theta = radar_factory(N_parameters, frame="circle")

    fig, ax = plt.subplots(figsize=(10, 10), nrows=1, ncols=1, subplot_kw=dict(projection='radar'))

    if not isinstance(data_list, list):
        data_list = [data_list]

    for data in data_list:
        ax.plot(theta, data[plotted_par_indices])
        ax.fill(theta, data[plotted_par_indices], alpha=0.25)
        np_legend = np.array(legend)
        ax.set_varlabels(np_legend[plotted_par_indices])