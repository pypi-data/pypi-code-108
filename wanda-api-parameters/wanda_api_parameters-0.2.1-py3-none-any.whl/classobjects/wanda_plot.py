import copy
from datetime import datetime
from typing import List, Tuple

import pandas as pd
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
from matplotlib import (cm, ticker)
import matplotlib.pyplot as plt
import matplotlib as mpl
import cmocean
# Add cmocean colormaps
[plt.register_cmap(map_name, cmocean.cm.cmap_d.get(map_name)) for map_name in cmocean.cm.cmapnames if map_name not in plt.colormaps()]
[plt.register_cmap("{}_r".format(map_name), cmocean.cm.cmap_d.get(map_name).reversed()) for map_name in cmocean.cm.cmapnames if "{}_r".format(map_name) not in plt.colormaps()]

import copy
import numpy as np
import os
import pywanda

from scipy.interpolate import interp1d

from wanda_api_parameters.parameters_api import (figtable, get_route_data, get_syschar)


def plot_7box(
        figure,
        title,
        case_title,
        case_description,
        proj_number,
        section_name,
        fig_name,
        company_name="Deltares",
        software_version="Wanda 4.6",
        company_image=None,
        date=None,
        fontsize: float = 8,
        logo_name: str = "Deltares_logo.png",

):
    """
    Creates box around and in the plot window. Also fills in some info about the calculation.
    Based on the 7-box WL-layout.

    Parameters
    ----------
    figure: str,
    title: str,
        Title of the current case.
    case_title: str,
        Title of the current case.
    case_description: str,
        Description of the case.
    proj_number: str,
        The project number of the current case.
    section_name: str,
        The section name.
    fig_name: str,
        Name of the current figure (right hand side, middlerow)
    companYname: str, default = Deltares
        The company name (bottem image)
    software_version: str, defauult = Wanda 4.6
        The software version used to generate the graphs.
    company_image: str, optional
        The image to plot behind the right hand bottom.
    date: str, optional
        The date will be set to today (default) or any other date if specified.
    fontsize: float, default = 8
        Fontsize of the plot.
    logo_name: str, default = Deltares_logo.png
        The logo to be specified on the backside of the right hand bottom.
    """
    # Define locations of vertical and horizontal lines
    xo = 0.04
    yo = 0.03
    textbox_height = 0.75

    v0 = 0.0 + xo
    v1 = 0.62 + xo
    v2 = 0.81
    v3 = 1.0 - xo

    h0 = 0.0 + yo
    h1 = 1.2 * textbox_height / 29.7 + yo
    h2 = 2.4 * textbox_height / 29.7 + yo
    h3 = 3.6 * textbox_height / 29.7 + yo

    ax = plt.axes([0, 0, 1, 1], facecolor=(1, 1, 1, 0))

    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)

    l1 = ax.axhline(y=h3, xmin=v0, xmax=v3, linewidth=1.5, color="k")
    l2 = ax.axvline(x=v1, ymin=h0, ymax=h3, linewidth=1.5, color="k")
    l3 = ax.axhline(y=h1, xmin=v0, xmax=v3, linewidth=1.5, color="k")
    l4 = ax.axvline(x=v2, ymin=h0, ymax=h1, linewidth=1.5, color="k")
    l5 = ax.axvline(x=v2, ymin=h2, ymax=h3, linewidth=1.5, color="k")
    l6 = ax.axhline(y=h2, xmin=v1, xmax=v3, linewidth=1.5, color="k")

    #     bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    #     width, height = bbox.width * fig.dpi, bbox.height * fig.dpi
    #     linewidth = 2
    rect = Rectangle((xo, yo), 1 - (2 * xo), 1 - (2 * yo), fill=False, linewidth=1.5)
    ax.add_patch(rect)

    # Case title and description
    text1 = "\n".join((title, case_title, case_description))
    figure.text(
        v0 + 0.01,
        (h3 - (h3 - h1) / 2.0),
        text1,
        verticalalignment="center",
        horizontalalignment="left",
        color="black",
        fontsize=fontsize,
        )

    # Section name/number
    figure.text(
        (v1 + (v2 - v1) / 2.0),
        h2 + (h3 - h2) / 2.0,
        section_name,
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
        )

    # Project number
    figure.text(
        (v1 + (v2 - v1) / 2.0),
        (h0 + (h1 - h0) / 2.0),
        int(proj_number),
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
    )

    # Company name
    figure.text(
        (v0 + (v1 - v0) / 2.0),
        (h0 + (h1 - h0) / 2.0),
        company_name,
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
    )

    # Create datestamp
    if date != date or date is None:
        today = datetime.date(datetime.now())
    else:
        today = date
    figure.text(
        (v2 + (v3 - v2) / 2.0),
        h2 + (h3 - h2) / 2.0,
        today.strftime("%d-%m-%Y"),
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
        )

    # Figure name
    figure.text(
        (v2 + (v3 - v2) / 2.0),
        (h0 + (h1 - h0) / 2.0),
        software_version,
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
    )

    # Print WANDA version
    figure.text(
        (v1 + (v3 - v1) / 2.0),
        h1 + (h2 - h1) / 2.0,
        fig_name,
        verticalalignment="center",
        horizontalalignment="center",
        color="black",
        fontsize=fontsize,
        )

    img = company_image
    if company_image is None:
        try:
            module_dir, module_filename = os.path.split(__file__)
            image_path = os.path.join(module_dir, "image_data", logo_name)
            img = plt.imread(image_path)
        except FileNotFoundError:
            img = np.zeros([100, 100, 3], dtype=np.uint8)
            img.fill(255)  # or img[:] = 255
    imgax = figure.add_axes([v1, h0, v3 - v1, h3 - h0], zorder=-10)
    imgax.imshow(img, alpha=0.3, interpolation="none")
    imgax.axis("off")



class PlotObject:
    def __init__(
            self,
            title,
            xlabel,
            ylabel,
            clabel=None,
            xmin=None,
            xmax=None,
            xscale=1.0,
            xtick=None,
            ymin=None,
            ymax=None,
            yscale=1.0,
            ytick=None,
            cmin=None,
            cmax=None,
            cscale=1.0,
            ctick=None,
    ):
        """
        PlotObject, base class for different types of plots

        Parameters
        ----------
        title: str,
            Title of the plot.
        xlabel: str,
            Title of the x-label. The label can be supplied in Latex format (i.e., $m^3$).
        ylabel: str,
            Title of the y-label. The label can be supplied in Latex format (i.e., $m^3$).
        clabel: str, optional
            Title of the c-label. The label can be supplied in Latex format (i.e., $m^3$).
        xmin: float, optional
            X-axis minimum value
        xmax: float, optional
            X-axis maximum value
        xscale: float, default 1.0
            X-axis scale value. The scale value is used to re-scale the x-axis.
        xtick: float, optional
            X-axis tick value
        ymin:float, optional
            Y-axis minimum value
        ymax:float, optional
            Y-axis maximum value
        yscale:float, default 1.0
            Y-axis scale value. The scale value is used to re-scale the y-axis.
        ytick:float, optional
            Y-axis tick value
        cmin:float, optional
            C-axis minimum value
        cmax:float, optional
            C-axis maximum value
        cscale:float, optional
            C-axis scale value. The scale value is used to re-scale the C-axis.
        ctick:float, default 1.0
            C-axis tick value

        Methods
        -------
        _plot_finish( ax, legendon: bool, autoscaleon: bool)
            A method to finalize the plot.
        plot(model, ax)
            A method to call the plot.
        _plot_text(ax, x, y, text_list=None)
            A method to insert text at the specified locations of the plot.
        """
        self.title = title
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.clabel = clabel
        self.xmin = xmin
        self.xmax = xmax
        self.xtick = xtick
        self.xscale = 1.0 if ((xscale is None) or np.isnan(xscale)) else xscale
        self.ymin = ymin
        self.ymax = ymax
        self.yscale = 1.0 if ((yscale is None) or np.isnan(yscale)) else yscale
        self.ytick = ytick
        self.ctick = ctick
        self.cmin = cmin
        self.cmax = cmax
        self.cscale = 1.0 if ((cscale is None) or np.isnan(cscale)) else cscale

    def _plot_finish(self, ax, legendon: bool = True, autoscaleon: bool = True):
        """
        Set default parameters for the plot such as autoscale, legend, and axis limits.

        Parameters
        ----------
        ax: pyplot Axes object
            The axes to apply the class-method to.
        legendon: bool, default True
            Set the legend to be vissible (True) or invisible (False)
        autoscaleon: bool, default True
            Scale the plot automatically.

        Returns
        -------

        """
        # Make tight on x-axis
        if autoscaleon:
            ax.autoscale(tight=True, axis="x")

        # Scale the data and axes
        for line in ax.get_lines():
            x_data, y_data = line.get_data()
            line.set_data(x_data / self.xscale, y_data / self.yscale)

        xmin, xmax = np.array(ax.get_xlim()) / self.xscale
        ymin, ymax = np.array(ax.get_ylim()) / self.yscale
        if (ymax - ymin) < 1:  #
            ymin = np.sign(ymin) * abs(ymin) * 0.9
            ymax = np.sign(ymax) * abs(ymax) * 1.1
            if ymax < 1:
                ymax = 10
        xmin = self.xmin if (self.xmin is not None) and (not np.isnan(self.xmin)) else xmin
        xmax = self.xmax if (self.xmax is not None) and (not np.isnan(self.xmax)) else xmax
        ymin = self.ymin if (self.ymin is not None) and (not np.isnan(self.ymin)) else ymin
        ymax = self.ymax if (self.ymax is not None) and (not np.isnan(self.ymax)) else ymax

        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
        # Set ticks
        if (self.xtick is not None) and (not np.isnan(self.xtick)):
            ax.set_xticks(np.arange(xmin, xmax + self.xtick, self.xtick))
        if (self.ytick is not None) and (not np.isnan(self.ytick)):
            ax.set_yticks(np.arange(ymin, ymax + self.ytick, self.ytick))
        # Add labels, grid, and other formatting
        ax.set_xlabel(self.xlabel)
        ax.set_ylabel(self.ylabel)
        ax.set_title(self.title)
        ax.grid(True, linestyle="--", alpha=0.7)

        # Plot the legend below the axes, and below the x-axis label.
        # We do this by shrinking the axes a little on the bottom.
        if legendon:
            ax.legend()
            box = ax.get_position()
            height_shrink = 0.05
            ax.set_position([box.x0, box.y0 + height_shrink, box.width, box.height - height_shrink])
            ax.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -1 * height_shrink / box.height),
                fancybox=True,
                shadow=True,
                ncol=5,
                frameon=True,
            )

    def plot(self, model, ax):
        raise NotImplementedError

    def _plot_text(self, ax, x, y, text_list=None):
        """
        Plot text and line intercepts.

        Parameters
        ----------
        ax: pyplot axes object
        x: list of lists
            A list of lists containing the x-coordinates.
        y: list of lists
            A list of lists containing the y-coordinates
        text_list: list of lists
            A list of lists containg the text to plot at each coordinate.

        Returns
        -------

        """
        if text_list is None:
            text_list = self.plot_text
        if text_list:
            for text in text_list[0]:
                if (text.get('intercept') is None) or (text.get('intercept') == 'None'):
                    ax.plot(text['x'], text['y'], text['marker'])
                    ax.text(text['x'] + text['dx'], text['y'] + text['dy'], text['text'])
                else:
                    if text.get('intercept').lower() == 'x':
                        if (text.get('text') is not None) and (text.get('text') != "None"):
                            ax.text(text['x'] + text['dy'], text['y'] + text['dy'], text['text'], ha='left',
                                    va='bottom',
                                    rotation='vertical')
                        for idx, x0 in enumerate(x):
                            yinterp = np.interp(text['x'], x0, y[idx])
                            ax.plot(text['x'], yinterp, text['marker'])
                            ax.text(text['x'] + text['dx'], yinterp + text['dy'],
                                    "{:.02f}".format(yinterp))
                        ax.plot([text['x']] * 2, [self.ymin, self.ymax], text['line'])


class PlotRoute(PlotObject):
    def __init__(
            self,
            pipes,
            annotations,
            prop,
            times,
            plot_elevation=False,
            plot_text=[],
            additional_dict: dict = None,
            *args, **kwargs
    ):
        """
        Creates a route plot or location-graph for a given route in a wanda model (route is specified by keyword. Only
        supports a single property, but allows plotting of pipeline profile in same figure

        The standard parameters for figures can also be applied.

        Parameters
        ----------
        pipes: pywanda Pipes.
            A list of pipes that should match the annotations list.
        annotations: List of str
            A list of strings with annotations per pipe component.
        prop: pywanda Property
            The property for the selected pipes on the selected route.
        times: List of floats,
            A list of floats containinng the times at which the plot should be constructed. This will for example result
            in a plot of the discharge at several time steps in the simulation.
        plot_elevation: bool, default False,
            Plot the elevation of a profile.
        plot_text: List of strings
            The string list is used to plot information at the specified locations.
        additional_dict: dict,
            Additional options from the yaml file. They are currently not implemented for this plot!
        args: Tuple.
            Additional arguments for the plot routine.
        kwargs: Tuple.
            Additional arguments for the plot routine.

        Methods
        -------
        plot(model, ax)
            Plot the route plot.
        """
        if len(pipes) != len(annotations):
            raise ValueError("Pipes list and Annotations list must have the same length")
        self.pipes = pipes
        self.annotations = annotations
        self.prop = prop
        self.times = times
        self.plot_elevation = plot_elevation
        self.plot_text = plot_text
        self.additional_dict = additional_dict
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        """
        Plot the route data

        Parameters
        ----------
        model: pywanda.WandaModel,
        ax: pyplot Axes

        Returns
        -------

        """
        # Retrieve route data.
        s_location, elevation, data, s_location_profile = get_route_data(
            model,
            self.pipes,
            self.annotations,
            self.prop,
            self.times
        )

        # TODO: Explain route plot!
        xout = []
        yout = []
        color_ind = 0
        for t, v in data.items():
            # Min/max keep their name, but floats get a 's' unit appended
            if self.prop == "Velocity" or self.prop == "Discharge":
                v = abs(v)
            # if t == 0:
            #    label = f'{self.prop}' if not isinstance(t, str) else t
            # else:
            #    label = f'{t} s' if not isinstance(t, str) else t
            label = f"{t} s" if not isinstance(t, str) else t

            if label == "max":
                ax.plot(s_location, v, label=label, linestyle="--", c="r", zorder=-1)
            elif label == "min":
                ax.plot(s_location, v, label=label, linestyle="-.", c="k", zorder=-1)
            else:
                ax.plot(s_location, v, label=label, c=f"C{color_ind}")
                color_ind += 1
            xout.append(s_location)
            yout.append(v)

        if self.plot_elevation:
            ax.plot(
                s_location_profile,
                elevation,
                label="Elevation",
                c="g",
                linewidth=2,
                alpha=0.3,
                zorder=-2,
            )
        # adding text and points to the graphs
        self._plot_text(ax=ax, x=xout, y=yout)

        # Set boundaries.
        xmin, xmax = np.array(ax.get_xlim()) / self.xscale
        ymin, ymax = np.array(ax.get_ylim()) / self.yscale
        # Add labels of all pipes.
        stepx = (xmax - xmin) * 0.05
        stepy = (ymax - ymin) * 0.05
        ax.text(xmin + stepx, ymin + stepy, self.pipes[0].get_complete_name_spec())
        ax.text(xmax - 3 * stepx, ymin + stepy, self.pipes[-1].get_complete_name_spec())
        # Finis plot
        self._plot_finish(ax)


class PlotSyschar(PlotObject):
    def __init__(
            self,
            component_name,
            max_flowrate,
            description,
            discharge_dataframe,
            supplier_column,
            scenario_names,
            number_of_points,
            *args,
            **kwargs,
    ):
        """
        Creates system characteristics graphs for given wanda model, flow scenarios and flow range. It automatically
        calculates the system characteristic for a given model and flow scenarios.

        Parameters
        ----------
        component_name: str,
            Name of the component the calculate the system characteristic for
        max_flowrate: float,
            Maximum flowrate
        description: str,
            Text description of this component
        discharge_dataframe: pd.DataFrame
            Pandas dataframe with discharges of other suppliers in the model
        supplier_column:
            Column name that contains the names of the Wanda components that represent the suppliers
        scenario_names:
            List of scenario names (names of columns in discharge_dataframe
        number_of_points:
            Number of steps for the system characteristic calculation. Default = 10
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        plot(model, ax)
            Plot the route plot.
        """
        self.component_name = component_name
        self.max_flowrate = max_flowrate
        self.discharge_dataframe = discharge_dataframe
        self.supplier_column = supplier_column
        self.scenario_names = scenario_names
        self.n_points = number_of_points
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        """
        Plot method for the PlotSyschar class.

        Parameters
        ----------
        model: pywanda.WandaModel
        ax: pyplot axes object

        Returns
        -------

        """
        color_ind = 0
        # suppliers = self.discharge_dataframe[self.supplier_column].tolist()
        flows = {}
        head_series = {}
        for scenario in self.scenario_names:
            print(
                f"Generating plot for {self.component_name}, max Q={self.max_flowrate * 3600 * 24:{2}.{6}} m3/day"
            )
            discharges, heads = get_syschar(
                model,
                self.discharge_dataframe,
                self.component_name,
                self.max_flowrate,
                scenario,
                self.n_points,
            )
            flows[scenario] = [q * 3600 * 24 for q in discharges]  # display discharge in m3/day
            head_series[scenario] = heads

        for scenario, heads in head_series.items():
            ax.plot(
                flows[scenario],
                heads,
                label=scenario,
                marker="o",
                linestyle="--",
                c=f"C{color_ind}",
                zorder=-1,
            )
            color_ind += 1
        self._plot_finish(ax)


class PlotTimeseries(PlotObject):
    def __init__(self, collection=List[Tuple[str, str, str]], plot_text=[], additional_dict: dict = None, *args,
                 **kwargs):
        """
        Creates a timeseries plot for a given property, only supports a single axis.

        Parameters
        ----------
        collection: List[Tuple[str, str, str]]
            A list of tuples containing the following keys: [comp_key, prop_key, label]
        plot_text: list of text.
            List of text to plot.
        additional_dict: additional options.
            Additional options have not been implemented for this plot.
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        plot(model, ax)
            Plot the route plot.
        """
        self.collection = collection
        self.plot_text = plot_text
        self.additional_dict = additional_dict
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        """
        Plot method for the PlotTimeseries class.

        Parameters
        ----------
        model: pywanda.WandaModel
        ax: pyplot axes object

        Returns
        -------

        """
        # Plot the time series
        x = model.get_time_steps()
        xout = []
        yout = []
        labelout = []
        for comp, prop, label in self.collection:
            if model.component_exists(comp):
                try:
                    prop = model.get_component(comp).get_property(prop)
                except ValueError:
                    print('Property {} not available for component {}'.format(prop, comp))
            elif model.node_exists(comp):
                try:
                    prop = model.get_node(comp).get_property(prop)
                except ValueError:
                    print('Property {} not available for component {}'.format(prop, comp))
            else:
                print('{} is not a valid component or node name!'.format(comp))
            # try:
            #     prop = model.get_component(comp).get_property(prop)
            # except ValueError:
            #     prop = model.get_node(comp).get_property(prop)
            try:
                y = [x * prop.get_unit_factor() for x in prop.get_series()]
            except RuntimeError:
                print('Could not load temporal data.')
                y = np.ones((len(x),)) * np.NaN

            ax.plot(x, y, label=label)
            xout.append(x)
            yout.append(y)
            labelout.append(label)
        # Plot the text.
        self._plot_text(ax=ax, x=xout, y=yout)

        self._plot_finish(ax)


class PlotPointTimeseries(PlotObject):
    def __init__(self,
                 collection=List[Tuple[str, str, str, List]],
                 plot_text=[],
                 additional_dict: dict = None,
                 *args,
                 **kwargs
                 ):
        """
        Creates a timeseries plot for a given property, only supports a single axis.

        Parameters
        ----------
        collection: List[Tuple[str, str, str, List]]
            A list of tuples containing the following keys: [comp_key, prop_key, label, pos]
        plot_text: list of text.
            List of text to plot.
        additional_dict: additional options.
            Additional options have not been implemented for this plot.
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        plot(model, ax)
            Plot the route plot.
        """
        collection_list = []
        for comp in collection:
            for pos in comp[3]:
                collection_list.append((comp[0], comp[1], "{} x = {:.2f}".format(comp[2], pos), pos))
        self.plot_text = plot_text
        self.collection = collection_list
        self.additional_dict = additional_dict
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        """
        Plot method for the PlotPointTimeseries class.

        Parameters
        ----------
        model: pywanda.WandaModel
        ax: pyplot axes object

        Returns
        -------

        """
        x = model.get_time_steps()
        xout = []
        yout = []
        for comp_key, prop_key, label, pos in self.collection:
            try:
                # Get property and component
                prop = model.get_component(comp_key).get_property(prop_key)
                comp = model.get_component(comp_key)
                # Determine pipe length properties
                elements = comp.get_num_elements()
                pipe_length = comp.get_property('Length').get_scalar_float()
                length_per_element = pipe_length / elements
                xpipe = np.linspace(0, pipe_length, elements)
                # Determine pipe elements
                upper_element = int(np.ceil(pos / length_per_element))
                lower_element = int(np.floor(pos / length_per_element))
                y0 = np.array(prop.get_series(lower_element))
                x0 = np.ones(y0.shape) * xpipe[lower_element]
                y1 = np.array(prop.get_series(upper_element))
                x1 = np.ones(y1.shape) * xpipe[upper_element]
                # Interpolate position.
                y = y0 + (pos - x0) * ((y1 - y0) / (x1 - x0))

            except ValueError:
                print(ValueError)
            y = list(y * prop.get_unit_factor())
            ax.plot(x, y, label=label)
            xout.append(x)
            yout.append(y)
        # Plot the text.
        self._plot_text(ax=ax, x=xout, y=yout)

        self._plot_finish(ax)


class PlotText(PlotObject):
    def __init__(self,
                 text: str,
                 *args,
                 **kwargs):
        """
        Creates a textbox on the page. Formatting is up to the user

        Parameters
        ----------
        text: str
            A str to be plotted on a textbox.
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        plot(model, ax)
            Plot the table.
        """
        self.text = text
        super().__init__(title="", xlabel="", ylabel="")

    def plot(self, model, ax):
        """
        Plot a text box on the axes.

        Parameters
        ----------
        model: pywanda.WandaModel.
        ax: pyplot axes object.

        Returns
        -------

        """
        props = dict(boxstyle="round", facecolor="white", alpha=0.5)
        ax.set_axis_off()
        if ax.get_legend():
            ax.get_legend().remove()
        ax.text(
            -0.1,
            1.0,
            self.text,
            transform=ax.transAxes,
            size=8,
            fontsize=8,
            verticalalignment="top",
            bbox=props,
        )
        self._plot_finish(ax)


class PlotTable(PlotObject):
    def __init__(self,
                 dataframe: pd.DataFrame,
                 columns: List[str],
                 *args,
                 **kwargs):
        """
        Creates a table on the subplot/page.

        Parameters
        ----------
        dataframe: Pandas dataframe
            A dataframe containing the data to be plotted on the graph.
        columns: list of str
            A list of str containing the column names to display in the table
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        plot(model, ax)
            Plot the table.
        """
        self.df = dataframe
        self.columns = columns
        super().__init__(title="", xlabel="", ylabel="")

    def plot(self, model, ax):
        """
        Plot a table on an existing plot.

        Parameters
        ----------
        model: pywanda.WandaModel.
        ax: pyplot Axes object.

        Returns
        -------

        """
        table = self.df[self.columns]
        header = table.columns
        table = np.asarray(table)
        ax.set_axis_off()
        if ax.get_legend():
            ax.get_legend().remove()
        colors = []
        for x in header:
            colors.append("grey")
        tab = ax.table(
            cellText=table, colLabels=header, colColours=colors, cellLoc="center", loc="center"
        )
        tab.auto_set_column_width(True)
        tab.auto_set_font_size(True)
        self._plot_finish(ax)


class PlotImage(PlotObject):
    def __init__(self,
                 image: np.ndarray,
                 *args,
                 **kwargs):
        """
        Adds an image on the subplot/page

        Parameters
        ----------
        image: numpy.ndarray
            numpy.array containing the image,  for example obtained from matplotlib.pyplot.imread()
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

       Methods
        -------
        plot(model, ax)
            Plot the image on the plot.
        """
        self.img = image
        super().__init__(*args, **kwargs)

    def plot(self, model, ax):
        """
        Plot image.

        Parameters
        ----------
        model: pywanda.WandaModel.
        ax: pyplot Axes object.

        Returns
        -------

        """
        if ax.get_legend():
            ax.get_legend().remove()
        ax.set_axis_off()
        ax.imshow(self.img)
        self._plot_finish(ax)


class PlotMap(PlotObject):
    def __init__(self,
                 pipes: str,
                 annotations: str,
                 model: pywanda.WandaModel,
                 pipe_dir: str,
                 prop: str,
                 plot_text=[],
                 additional_dict: dict = None,
                 scenarioname: str=None,
                 *args,
                 **kwargs):
        """

        Parameters
        ----------
        pipes: str,
            Name of the document containing the shape file.
        pipe_dir: str,
            Base path to the shape file (i.e., the base path of the model directory).
        annotations: str
            Label that refers to the components in the GeoPandas Dataframe.
        model: pywanda.WandaModel
            Class containing the Wanda model.
        prop: str,
            Property to plot on the map.
        plot_text: List[str]
            Annotations to plot on the map.
        additional_dict:
            Additional properties that can be suppplied to the map plot. The dictionary can contain the following keys:
                type: str, default "MAX"
                    The type of the map plot can be chosen between (MAX, MIN)
                cmap: str, default viridis
                    Type of the color map.
                numberctick: int, default 5
                    Number of cticks on the axis.
                linewidth: float, default 1.0
                    The linewidth on the map plot.
                cbarorientation: str, default horizontal
                    The orientation of the cbar on the map plot.
                figorientation: str, default vertical
                    Orientation of the figure can be vertical or horizontal
                figpapersize: str, default A4
                    Size of the resulting pdf.
                savehtml: bool, default False,
                    Plot the map on a folium plot.
                absolute_value: bool, default False
                    Plot absolute values.
                set_under: str,
                    Color code for the under values
                set_under_value: float, default None
                    The minimum value of the map plot.
                set_under_alpha: float,
                    The shading of the under value
                set_over: str,
                    Color code for the over values
                set_over_value: float, default None
                    The maximum value of the map plot.
                set_over_alpha: float,
                    The shading of the over value

        scenarioname: str,
            Name of the scenario.
        args:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
        kwargs:
            remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

        Methods
        -------
        match_pipes()
            Match the pipes in the model with the shape-file based on annotations
        get_shape_pipes(name_list)
             Obtain the shape-file line strings that match the pipes in name_list
        plot_multiline(multiline)
            Simple plot function for a multiline object obtained from the get_shape_pipes class-method
        match_and_connect_lines(linelist, length_threshold: float = 1.0, nlimit: int = 3)
            Match the points of lines.
        nearest_point_match(line1, line2)
            Determine the nearest point match of two lines (i.e., shapely.LineString).
        connect_lines(line1, line2, idx_match: List[int])
            Connect two shapely lines based on their matched index.
        wanda_to_shape(points: np.ndarray, npoints: int, kind: str = "linear")
            Calculate the intermediate points with an arc-length method. The interpolation solves the following equation
            f(s) = (x,y) with s the distance along the curve.
        plot_interpolation_wanda_to_schape(points: np.ndarray, interpolated_points: np.ndarray, export: str = None)
            Evaluate the performance of the interpolation with the class-method wanda_to_shape.
        retrieve_bounds_cmap(model: pywanda.WandaModel, pipe_dict: dict)
            Return the bounds for the property.
        create_color_map(model: pywanda.WandaModel, pipe_dict: dict)
            Create the color map for the pipe dictionary.
        plot_folium(pipe_dict: dict,segment_values: list, cvalue: list, map_size: int = 500, filename: str=None)
            Plot the shape file data and Wanda data on a folium map.
        plot(model, ax)
            Plot the map.

        Notes
        -----
        The class required the installation of GeoPandas. The following instructions can be followed to install
        GeoPandas:
        Installing geopandas and its dependencies manually:
        1.	First and most important: do not try to directly pip install or conda install any of the dependencies –
        if you do, they will fail in some way later, often silently or obscurely, making troubleshooting difficult.
        If any are already installed, uninstall them now.
        2.	Download the wheels for GDAL, Fiona, pyproj, rtree, and shapely from Gohlke (
        https://www.lfd.uci.edu/~gohlke/pythonlibs/ ).
        Make sure you choose the wheel files that match your architecture (64-bit) and Python version (2.7 or 3.x).
        If Gohlke mentions any prerequisites in his descriptions of those 5 packages, install the
        prerequisites now (there might be a C++ redistributable or something similar listed there)
        3.	If OSGeo4W, GDAL, Fiona, pyproj, rtree, or shapely is already installed, uninstall it now.
        The GDAL wheel contains a complete GDAL installation – don’t use it alongside OSGeo4W or other distributions.
        4.	Open a command prompt and change directories to the folder where you downloaded these 5 wheels.
        5.	pip install the GDAL wheel file you downloaded. Your actual command will be something like:
        pip install GDAL-1.11.2-cp27-none-win_amd64.whl
        6.	Add the new GDAL path to the windows PATH environment variable, something like
        C:\Anaconda\Lib\site-packages\osgeo
        7.	pip install your Fiona wheel file, then your pyproj wheel file, then rtree, and then shapely.
        8.	Now that GDAL and geopandas’s dependencies are all installed, you can just pip install geopandas
        from the command prompt



        """
        # Import geometry packages
        import geopandas as gpd
        import pandas as pd
        # Scenario name
        self.scenarioname = scenarioname
        # Add additional dict
        self.additional_dict = additional_dict
        # Create geopandas data frame from shape-file
        #TODO: Remove the path of the shape-file from the dictionary.
        self.pipes = gpd.read_file(os.path.join(pipe_dir,pipes))
        # Create pipe list to connect multiple components.
        try:
            self.connection_list = pd.read_csv(os.path.join(
                pipe_dir,
                "{}.csv".format(os.path.splitext(pipes)[0]))
                , sep=';')
        except FileNotFoundError:
            self.connection_list = None
        # Load the label for the geopandas dataframe.
        self.annotations = annotations
        # Load model
        self.model = model
        # Load property to plot
        self.prop = prop
        # Load text annotations.
        self.plot_text = plot_text
        if self.additional_dict is not None:
            # Retrieve plot types
            if self.additional_dict.get('type') is not None:
                self.plot_type = self.additional_dict.get('type')
            else:
                self.plot_type = "MAX"
            # Retrieve color map
            if self.additional_dict.get('cmap') is not None:
                self.cmap_type = self.additional_dict.get('cmap')
            else:
                self.cmap_type = "viridis"
            # Tick labelsteps
            if self.additional_dict.get('numberctick') is not None:
                self.numberctick = self.additional_dict.get('numberctick')
            else:
                self.numberctick = 5
            # Set linewidth
            if self.additional_dict.get('linewidth') is not None:
                self.linewidth = self.additional_dict.get('linewidth')
            else:
                self.linewidth = 1
            # Set orientation
            if self.additional_dict.get('cbarorientation') is not None:
                self.cbarorientation = self.additional_dict.get('cbarorientation')
            else:
                self.cbarorientation = 'horizontal'

        # Initialize other plot functionality
        super().__init__(*args, **kwargs)

    def match_pipes(self) -> dict:
        """
        Match the pipes in the model with the shape-file based on annotations or based on the name of the wanda
        component.

        The class method utilizes the get_shape_pipes class method by presenting a list of strings for the pipe keys.
        These pipe keys are then matched to the shape file.

        Returns
        -------
        pipe_dict: dict,
            A dictionary with, at this point, the keys (names) that were obtained from the matching csv-file or
            wanda model. Additionally, the shapely line components are included (see lines). These lines are combined
            into a single line string.

        Notes
        -----
        self.connection_list: pd.DataFrame
            A pandas dataframe with a name similar to the model names in the pywanda.WandaModel. The dataframe contains
            for each key of the pywanda model the respective pipe keys. These pipe keys correspond to the combined
            shape file keys that are contained in a single pipe.

        """

        if self.connection_list is not None:
            # An available pd.DataFrame containing pipe names and their respective parts is used.
            pipe_dict = {}
            for pipe_comb in self.connection_list['Name']:
                pipe_comb = pipe_comb.split(',')
                name_list = [pipe_comb[0], *["PIPE {}".format(idx) for idx in pipe_comb if "PIPE" not in idx]]
                pipe_dict[pipe_comb[0]] = {"names": name_list,
                                           "lines": self.get_shape_pipes(name_list=name_list)}
        else:
            # Construct a pipe dictionary by searching the GeoPandas data frame for corresponding pipe names.
            pipe_dict = {}
            for pipe in self.model.get_all_pipes():
                if not pipe.is_disused():
                    pipe_dict[pipe.get_name()] = {"names": [pipe.get_name()],
                                                  "lines": self.get_shape_pipes(name_list=[pipe.get_name()])}
        return pipe_dict

    def get_shape_pipes(self, name_list: List[str]):
        """
        Obtain the shape-file line strings that match the pipes in name_list

        Parameters
        ----------
        name_list: List[str]
            A list of strings containing the pipe names to match to the shape-file

        Returns
        -------
        pipe_list: geometry.LineString
            Return a LineString object of the combined pipes.

        Sources
        -------
        [1] https://gis.stackexchange.com/questions/223447/welding-individual-line-segments-into-one-linestring-using-shapely
\
        """
        from shapely import (geometry, ops)
        # Strip pipe (str) from list
        names = [name.replace('PIPE','').strip() for name in name_list]
        # Retrieve index from geopandas dataframe
        idx_gpd = np.where(self.pipes.get(self.annotations).isin(names))[0]
        # If there is a match proceed
        if len(idx_gpd) > 0:
            # Load sub-data from geopandas dataframe
            gdf = self.pipes.loc[idx_gpd]
            # Check number of lines
            if len(gdf) == 1:
                multi_line = ops.linemerge(gdf.geometry.to_list())
            else:
                # Merge line strings
                multi_line = geometry.MultiLineString(gdf.geometry.to_list())
                multi_line = ops.linemerge(multi_line)
                # Check line merger (i.e., it fails for lines that are not ordered correctly)
                if type(multi_line) is geometry.MultiLineString:
                    multi_line = self.match_and_connect_lines(linelist=list(multi_line))

        else:
            print('Pipes in list: {} not found'.format(names))

        return multi_line

    def plot_multiline(self, multiline: list):
        """
        Simple plot function for a multiline object.

        Parameters
        ----------
        multiline: List of shapely.LineString elements.

        Returns
        -------

        """
        plt.figure()
        if type(multiline) is geometry.MultiLineString:
            for line in list(multiline):
                coords = np.array(line.coords)
                plt.plot(coords[:, 0], coords[:, 1], '-ok')
        elif type(multiline) is List:
            for line in multiline:
                coords = np.array(line.coords)
                plt.plot(coords[:, 0], coords[:, 1], '-ok')
        else:
            coords = np.array(multiline.coords)
            plt.plot(coords[:, 0], coords[:, 1], '-ok')
        plt.show()

    def match_and_connect_lines(self,
                                linelist,
                                length_threshold: float = 1.0,
                                nlimit: int = 3):
        """
        Match the points of lines.

        A method to search for the nearest matching point of an unconnected line. The method ensures that lines are
        matched back to front (i.e., ensures correct connectivity).

        Parameters
        ----------
        linelist: list of shapely.LineString
        length_threshold: float of threshold.
        nlimit: number of times we loop over the list

        Returns
        -------
        lines: shapely.LineString
            A combined line based on the supplied linelist.

        """
        niteration = 0
        nlimit = len(linelist) * nlimit
        lines = copy.deepcopy(linelist)
        while (len(lines) > 1) and (niteration <= nlimit):
            for idx_line in np.arange(1, len(lines)):
                idx_min, L = self.nearest_point_match(line1=lines[0], line2=lines[idx_line])
                if L <= length_threshold:
                    # match lines
                    line = self.connect_lines(line1=lines[0], line2=lines[idx_line], idx_match=idx_min)
                    # break loop
                    break
            sub_lines = lines[1:]
            sub_lines.pop(idx_line - 1)
            lines = [line, *sub_lines]
            niteration = niteration + 1
        # Print error message when iteration did not complete
        if niteration >= nlimit:
            print("Iteration limit reached for point match!")
        return lines[0]

    def nearest_point_match(self,
                            line1,
                            line2):
        """
        Determine the nearest point match of two lines.

        Parameters
        ----------
        line1: shapely.LineString
        line2: shapely.LineString

        Returns
        -------
        idx_match: matching index (side line1, side line2)
            The side of the matching pipe node.
        L: float
            distance between point match.
        """
        # Define points
        pts1 = np.c_[line1.coords[0], line1.coords[-1]].T
        pts2 = np.c_[line2.coords[0], line2.coords[-1]].T
        # Define Lnorm
        L = []
        idx_min = []
        for idx_pt in range(2):
            Ltemp = np.linalg.norm(pts2 - pts1[idx_pt, :], axis=1) ** (1 / 2)
            L.append(Ltemp.min())
            idx_min.append(np.argmin(Ltemp))
        idx_min = [np.argmin(L), idx_min[np.argmin(L)]]
        L = np.min(L)
        return idx_min, L

    def connect_lines(self,
                      line1,
                      line2,
                      idx_match: List[int]):
        """
        Connect two shapely lines.

        Parameters
        ----------
        line1: shapely.LineString
        line2: shapely.LineString
        idx_match: matching index (side line1, side line2)
            The side of the matching pipe node.

        Returns
        -------
        line: shapely.LineString
            Combined shapely line string.

        """
        from shapely import (geometry, ops)
        if idx_match == [0, 0]:  # Matched first point of x1 with first point of x2
            line = geometry.LineString(np.r_[np.flipud(np.array(line2.coords)),
                                             np.array(line1.coords)])
        elif idx_match == [1, 0]:  # Matched second point of x1 with first point of x2
            line = geometry.LineString(np.r_[np.array(line1.coords),
                                             np.array(line2.coords)])
        elif idx_match == [0, 1]:  # Matched first point of x1 with second point of x2
            line = geometry.LineString(np.r_[np.array(line2.coords),
                                             np.array(line1.coords)])
        else:  # Matched second point of x1 with second point of x2
            line = geometry.LineString(np.r_[np.array(line1.coords),
                                             np.flipud(np.array(line2.coords))])
        return line

    def wanda_to_shape(self,
                       points: np.ndarray,
                       npoints: int,
                       kind: str = "linear"):
        """
        Calculate the intermediate points with an arc-length method. The interpolation solves the following equation
        f(s) = (x,y) with s the distance along the curve.

        Parameters
        ----------
        points: np.array([points.shape[0], 2])
            The coordinates of the linestring.
        npoints: int
            The number of points to interpolate to (i.e., wanda computational nodes).
        kind: str (linear)
            Type of interpolation method.

        Returns
        -------
        interpolated_points: np.ndarray
            An array with the interpolated points as np.array([npoints, 2])

        Source
        ------
        [1] https://stackoverflow.com/questions/52014197/how-to-interpolate-a-2d-curve-in-python
        [2] https://stackoverflow.com/questions/35673895/type-hinting-annotation-pep-484-for-numpy-ndarray

        """
        # Linear length along the line:
        distance = np.cumsum(np.sqrt(np.sum(np.diff(points, axis=0) ** 2, axis=1)))
        distance = np.insert(distance, 0, 0) / distance[-1]
        # Create interpolator object
        interpolator = interp1d(distance, points, kind=kind, axis=0)
        # Interpolate points
        sdistance = np.linspace(0, 1, npoints)
        interpolated_points = interpolator(sdistance)
        return interpolated_points

    def plot_interpolation_wanda_to_schape(self,
                                           points: np.ndarray,
                                           interpolated_points: np.ndarray,
                                           export: str = None):
        """
        Evaluate the performance of the interpolation.

        Parameters
        ----------
        points: np.ndarray
            Original coordinates of the shape-file
        interpolated_points: np.ndarray
            Interpolated coordinates of the shape-file
        export: str (None)
            Save file for reference to the path specified.

        Returns
        -------

        """
        plt.figure()
        plt.plot(points[:, 0], points[:, 1], '-ok')
        plt.plot(interpolated_points[:, 0], interpolated_points[:, 1], '-ob')

        if export is not None:
            plt.savefig(export)

    def retrieve_bounds_cmap(self,
                             model: pywanda.WandaModel,
                             pipe_dict: dict):
        """
        Return the bounds for the property.

        Parameters
        ----------
        model: pywanda.WandaModel
        pipe_dict: pipe_dict
            dictionary containing the labels of the pipes.

        Returns
        -------
        min_val: float
        max_val: float
        """
        min_val = 0
        max_val = 1
        for pipe in model.get_all_pipes():
            # Retrieve pipe
            if not pipe.is_disused():
                pipe_name = pipe.get_name()
                # Try to get it from the pipe_dict
                if pipe_dict.get("PIPE {}".format(pipe_name)) is not None:
                    series_data = np.array(pipe.get_property(self.prop).get_series_pipe()) * pipe.get_property(
                        self.prop).get_unit_factor()
                    if np.min(series_data) < min_val:
                        min_val = np.min(series_data)
                    if np.max(series_data) > max_val:
                        max_val = np.max(series_data)
        return min_val, max_val

    def create_color_map(self,
                         model: pywanda.WandaModel,
                         pipe_dict: dict):
        """
        Create the color map for the pipe dictionary.

        Parameters
        ----------
        model: pywanda.WandaModel.
        pipe_dict: dict
            A dictionary containing the pipes and their properties (e.g., pipe name, LineStrings).

        Returns
        -------
        color_map: colormap object
        cvalue: np.ndarray
            A numpy array with the cvalues.

        """
        from matplotlib import cm
        # Retrieve bounds
        min_val, max_val = self.retrieve_bounds_cmap(model=model,
                                                     pipe_dict=pipe_dict)
        # Set bounds
        if (self.cmin is not None) and (not np.isnan(self.cmin)):
            min_val = self.cmin
        else:
            min_val = np.floor(min_val / 0.5) * 0.5
        if (self.cmax is not None) and (not np.isnan(self.cmax)):
            max_val = self.cmax
        else:
            max_val = np.ceil(max_val / 0.5) * 0.5
        if (self.ctick is not None) and (not np.isnan(self.ctick)):
            # Round max_val and min_val
            max_val = np.ceil(max_val / self.ctick) * self.ctick
            min_val = np.floor(min_val / self.ctick) * self.ctick
            # Retrieve number of tick values
            ctick = np.int((max_val - min_val) / self.ctick)
        else:
            ctick = 100

        # Retrieve color map.
        color_map = cm.get_cmap(self.cmap_type, len(pipe_dict)).copy()
        # Set under and over colors.
        if self.additional_dict.get('set_over') is not None:
            if self.additional_dict.get('set_over_alpha') is not None:
                color_map.set_over(self.additional_dict.get('set_over'), self.additional_dict.get('set_over_alpha'))
            else:
                color_map.set_over(self.additional_dict.get('set_over'),1)
        if self.additional_dict.get('set_under') is not None:
            if self.additional_dict.get('set_under_alpha') is not None:
                color_map.set_under(self.additional_dict.get('set_under'), self.additional_dict.get('set_under_alpha'))
            else:
                color_map.set_under(self.additional_dict.get('set_under'),1)

        # Retrieve colorbar values.
        cvalue = np.linspace(min_val,
                             max_val, ctick) * self.cscale
        return color_map, cvalue

    def plot_folium(self,
                    pipe_dict: dict,
                    segment_values: list,
                    cvalue: list,
                    map_size: int = 500,
                    filename: str=None):
        """
        Plot the shape file data and Wanda data on a folium map.

        Parameters
        ----------
        pipe_dict: dict
            A dictionary with the pipe properties.
        segment_values: list
            A list containing the values for each segment in the pipe dict.
        cvalue: list
            A list containing the c-values for the plot.
        map_size: int, default 500
            The map size to plot the shape file data on.
        filename: str, optional.
            The export name for the folium map.

        Returns
        -------

        """
        import folium

        # Convert colors
        color_map = cm.get_cmap(self.cmap_type, len(cvalue))
        ccode = [cm.colors.to_hex(color_map(idx_color)) for idx_color in range(len(cvalue))]

        # Create segments array
        segments = []
        pipe_name = []
        for pipe_key in list(pipe_dict.keys()):
            # Append each segment to the segment array
            if pipe_dict[pipe_key].get('segments') is not None:
                segments.extend(pipe_dict[pipe_key]['segments'].tolist())
                # Determine the x-position along the pipe for each segment.
                nsegments = len(pipe_dict[pipe_key]['segments'])
                pipe_length = pipe_dict[pipe_key]['length']
                xpositions = np.linspace(0, pipe_length, nsegments)
                # Create pipe name with x-position.
                pipe_name.extend(["{} x= {:.1f} (m)".format(pipe_key, xposition) for xposition in xpositions])

        # Reshape segments to array
        point_array = np.array(segments).reshape((len(segments) * 2, 2))

        # Create normalized point_array (i.e., by subtracting the mean and dividing by the max).
        segment_max = point_array.max(axis=0)
        segment_mean = point_array.mean(axis=0)
        point_array = ((point_array - segment_mean) / segment_max) * map_size
        point_array = point_array.reshape(len(segments), 2, 2)

        # Scale segment
        map = folium.Map(crs='Simple', tiles=None, zoom_start=1000)

        # Bin-data
        if any(np.isnan([self.cmin, self.cmax, self.ctick])) or not any([self.cmin, self.cmax, self.ctick]):
            if np.isnan(self.ctick) or self.ctick is None:
                ctick = 1
            else:
                ctick = self.ctick
            cmin = np.floor(min(segment_values)/ctick)
            cmax = np.ceil(max(segment_values)/ctick)
            pressure_range = np.arange(cmin, cmax + ctick, ctick)
        else:
            pressure_range = np.arange(self.cmin, self.cmax + self.ctick, self.ctick)

        #idx = np.digitize(np.array(segment_values), bins=pressure_range)

        # Group features in pressure bins.
        feature_dict = dict()
        for idx_pressure, pressure in enumerate(np.unique(pressure_range)):
            if idx_pressure == len(np.unique(pressure_range))-1:
                if self.additional_dict.get('menuname') is not None:
                    pressure_name = self.additional_dict.get('menuname')[0].format(
                        pressure)
                else:
                    pressure_name = "Pressure: p &#8805;  {:0.1f} (barg)".format(
                        pressure)
            else:
                if self.additional_dict.get('menuname') is not None:
                    pressure_name = self.additional_dict.get('menuname')[1].format(
                        pressure, pressure_range[idx_pressure + 1])
                else:
                    pressure_name = "Pressure: {:0.1f} &#8804; p &#60;  {:0.1f} (barg)".format(
                        pressure, pressure_range[idx_pressure + 1])
            feature_dict[idx_pressure] = folium.FeatureGroup(pressure_name)

        # Loop over pipes and add to corresponding feature group.
        for pipe_key in list(pipe_dict.keys()):
            if pipe_dict[pipe_key].get('segments') is not None:
                for idx_segment, pipe_segment in enumerate(pipe_dict[pipe_key]['segments']):
                    # Segment pressure
                    pressure_segment = pipe_dict[pipe_key]['cvalues'][idx_segment]
                    # Define pressure range
                    idx_pressure = np.where(pressure_segment <= pressure_range)[0]
                    # Account for values outside of pressure range
                    if len(idx_pressure) > 0:
                        idx_pressure = idx_pressure[0] - 1
                    else:
                        idx_pressure = len(pressure_range) - 1

                    if idx_pressure < 0:
                        idx_pressure = 0
                    if idx_pressure > len(pressure_range):
                        idx_pressure = len(pressure_range) - 1
                    # Color values
                    idx_color = np.where(cvalue >= pressure_segment)[0]
                    if len(idx_color) > 0:
                        idx_color = idx_color[0]
                    else:
                        idx_color = len(ccode) - 1

                    # Define pop-up
                    if self.additional_dict.get('htmlpopup') is not None:
                        html_popup = self.additional_dict.get('htmlpopup').format(
                            pipe_key,
                            pressure_segment,
                            pipe_dict[pipe_key][
                                'inner diameter'],
                            pipe_dict[pipe_key]['node height'][idx_segment, 1],
                            pipe_dict[pipe_key]['node height'][
                                idx_segment, 0]
                        )
                    else:
                        html_popup = "<b>{}</b> <br> P = {:0.2f} (barg) <br> Din = {:0.2f} (mm) <br> Hnode = {:0.2f} (m)".format(
                            pipe_key,
                            pressure_segment,
                            pipe_dict[pipe_key]['inner diameter'],
                            pipe_dict[pipe_key]['node height'][idx_segment, 1])
                    iframe = folium.IFrame(html_popup)
                    popup = folium.Popup(iframe,
                                         min_width=250,
                                         max_width=250)
                    # Tooltip
                    if self.additional_dict.get('tooltip') is not None:
                        tooltip = self.additional_dict.get('tooltip').format(
                            pipe_key,
                            pressure_segment,
                            pipe_dict[pipe_key]['node height'][idx_segment, 1],
                            pipe_dict[pipe_key]['node height'][idx_segment, 0])
                    else:
                        tooltip = "<b>{}</b> <br> P = {:0.2f} (barg)".format(
                            pipe_key,
                            pressure_segment)
                    # Define folium line
                    folium.PolyLine(np.flip(((pipe_segment-segment_mean)/segment_max)*map_size).tolist(),
                                    color=ccode[idx_color],
                                    tooltip=tooltip,
                                    popup=popup
                                    ).add_to(feature_dict[idx_pressure])

        # Add features to map.
        for feature_key in list(feature_dict.keys()):
            feature_dict[feature_key].add_to(map)

        # Add layer control
        folium.LayerControl(position='bottomright'
                            ).add_to(map)

        # Add title
        # source: https://stackoverflow.com/a/61941253/15619397
        # loc = self.scenarioname
        # title_html = '''
        #              <h3 align="center" style="font-size:16px"><b>{}</b></h3>
        #              '''.format(loc)
        # map.get_root().html.add_child(folium.Element(title_html))

        # Save map
        if filename is None:
            filename = os.path.join(os.path.split(os.path.split(self.model.get_case_path())[0])[0],
                                    'figures',
                                    "{}.html".format(self.title)
                                    )
        map.save(filename)

    def plot(self, model: pywanda.WandaModel, ax):
        """
        Plot the WANDA data on a GIS map

        Parameters
        ----------
        model: pywanda.WandaModel
        ax: pyplot axes object

        Returns
        -------

        Source
        ------
        [1] https://scipy-cookbook.readthedocs.io/items/Matplotlib_MulticoloredLine.html
        """

        # Match pipes and retrieve shapely lines
        pipe_dict = self.match_pipes()

        # Create colormap
        color_map, cvalue = self.create_color_map(model=model,
                                                  pipe_dict=pipe_dict,
                                                  )
        # Plot over pipes
        all_segments = []
        all_z_data = []
        for pipe in model.get_all_pipes():
            if not pipe.is_disused():
                # Retrieve pipe
                pipe_name = pipe.get_name()
                # Try to get it from the pipe_dict
                if pipe_dict.get("PIPE {}".format(pipe_name)) is not None:
                    # Retrieve pipe object.
                    sub_dict = pipe_dict.get("PIPE {}".format(pipe_name))
                    # Interpolate Linestring to computational nodes
                    interpolated_points = self.wanda_to_shape(points=np.array(sub_dict['lines'].coords),
                                                              npoints=pipe.get_num_elements() + 2)
                    interpolated_points = interpolated_points.reshape(-1, 1, 2)
                    # Retrieve pipe series data
                    series_data = np.array(pipe.get_property(self.prop).get_series_pipe())

                    # Set absolute value
                    if self.additional_dict.get('absolute_value') is not None:
                        if self.additional_dict.get('absolute_value'):
                            series_data = np.abs(series_data * pipe.get_property(self.prop).get_unit_factor() * self.cscale)
                    else:
                        series_data = series_data * pipe.get_property(self.prop).get_unit_factor() * self.cscale

                    # Type of plot
                    if self.plot_type.lower() == "max":
                        series_data = np.max(series_data, axis=1)
                    elif self.plot_type.lower() == "min":
                        series_data = np.min(series_data, axis=1)
                    else:
                        print('Plot type not found - assuming maximum value!')
                        series_data = np.max(series_data, axis=1)

                    # Create segments
                    segments = np.concatenate([interpolated_points[:-1], interpolated_points[1:]], axis=1)

                    # Append segments to pipe_dict
                    pipe_temp_name = "PIPE {}".format(pipe_name)
                    pipe_dict[pipe_temp_name]['segments'] = segments
                    pipe_dict[pipe_temp_name]['length'] = pipe.get_property('Length').get_scalar_float()
                    pipe_dict[pipe_temp_name]['cvalues'] = series_data
                    pipe_dict[pipe_temp_name]['inner diameter'] = pipe.get_property('Inner diameter').get_scalar_float()*pipe.get_property('Inner diameter').get_unit_factor()

                    # Append node-height
                    if pipe.get_property('Geometry input').get_scalar_str() != 'l-h':
                        dist_diff = np.diff(np.array(pipe.get_property('Profile').get_table().get_float_column('Height')))
                        dist_diff = dist_diff - pipe.get_property('Length').get_scalar_float()
                        if dist_diff == 0:
                            xdist = [0, 0]
                        else:
                            xdist = [0, *dist_diff.tolist()]
                    else:
                        xdist = pipe.get_property('Profile').get_table().get_float_column('X-distance')

                    xnodes = np.c_[xdist, pipe.get_property('Profile').get_table().get_float_column('Height')]
                    int_nodes = self.wanda_to_shape(points=xnodes, npoints=pipe.get_num_elements()+1)
                    pipe_dict[pipe_temp_name]['node height'] = int_nodes

                    # Append data and segements to larger lists
                    all_segments.extend(segments.tolist())
                    all_z_data.extend(series_data.tolist())

        # Create folium interactive map.
        scenario_name = "{scenario} {type} {prop}.html".format(scenario=self.scenarioname,
                                                               type=self.plot_type,
                                                               prop=self.prop)
        filename = os.path.join(os.path.split(os.path.split(self.model.get_case_path())[0])[0], 'figures', scenario_name)
        if self.additional_dict.get("savehtml") is not None:
            if self.additional_dict.get("savehtml"):
                self.plot_folium(pipe_dict=pipe_dict,
                                 segment_values=all_z_data,
                                 cvalue=cvalue,
                                 filename=filename
                                 )
        # Add empty lines for colorbar (required to extend colorbar
        all_segments_extend = copy.deepcopy(all_segments)
        all_z_data_extend = copy.deepcopy(all_z_data)
        for cval in [self.cmin, self.cmax]:
            all_segments_extend.extend([[[self.xmin-self.xtick, self.ymin-self.ytick],
                                         [self.xmin-self.xtick+1, self.ymin-self.ytick]]])
            all_z_data_extend.extend([cval])
        # Create line collections.
        lc = LineCollection(all_segments_extend, cmap=color_map)
        lc.set_array(np.array(all_z_data_extend))
        lc.set_linewidth(self.linewidth)

        # Get current axis
        ax = plt.gca()

        # Add line segement to current axes
        ax_lc = ax.add_collection(lc)

        # Autoscale both axis
        ax.autoscale(tight=True)
        ax.axes.set_aspect('equal')

        # Automatically adjust line colors
        fig = plt.gcf()

        # Add color map
        cbar = fig.colorbar(lc, ax=ax, orientation=self.cbarorientation, extend='both')
        if (self.ctick is not None) or (not np.isnan(self.ctick)):
            tick_values = np.arange(self.cmin, self.cmax + self.ctick, self.ctick)
        else:
            tick_values = np.linspace(cvalue.min(), cvalue.max(), self.numberctick)

        # Set tick values
        cbar.set_ticks(tick_values)
        cbar.set_ticklabels(["{:.1f}".format(i) for i in tick_values])
        cbar.set_label("{} {}".format(self.plot_type, self.clabel))

        # Set colorbar limits
        under_bool = self.additional_dict.get('set_under_value') is not None
        over_bool = self.additional_dict.get('set_over_value') is not None
        if under_bool and over_bool:
            lc.set_clim(self.additional_dict.get('set_under_value'), self.additional_dict.get('set_over_value'))
        elif under_bool:
            lc.set_clim(self.additional_dict.get('set_under_value'), np.max(tick_values))
        elif over_bool:
            lc.set_clim(np.min(tick_values), self.additional_dict.get('set_over_value'))
        else:
            lc.set_clim(np.min(tick_values), np.max(tick_values))

        # Set proper dimension for plot
        if any(np.isnan([self.xmin, self.xmax, self.xtick, self.ymin, self.ymax, self.ytick])):
            xmin, xmax = ax.get_xlim()
            ymin, ymax = ax.get_ylim()

            xlength = (xmax - xmin)
            ylength = (ymax - ymin)
            if xlength > ylength:
                ax.set_ylim(np.array([-xlength / 2, xlength / 2]) + ymin + (ymax - ymin) / 2)
            else:
                ax.set_xlim(np.array([-ylength / 2, ylength / 2]) + xmin + (xmax - xmin) / 2)

        # Adjustable line segments
        plt.sci(lc)

        # Finish plot
        self._plot_finish(ax=ax,
                          legendon=False,
                          autoscaleon=False)


def plot(model, plot_objects, *args, **kwargs):
    """
    Renders pages from the given set of subplots.

    Parameters
    ----------
    model: pywanda.WandaModel
        Wanda model used as input
    plot_objects: list of plot classes
        List of objects to plot for the current page
    args:
        remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)
    kwargs:
        remaining arguments for PlotObject (minimum: Title, xlabel, ylabel)

    """
    figsize = None
    for obj in plot_objects:
        # Set figure size and orientation.
        if figsize is None:
            if obj.additional_dict is not None:
                if obj.additional_dict.get('figorientation') is not None:
                    if obj.additional_dict.get('figorientation').lower() == 'horizontal':
                        if obj.additional_dict.get('figpapersize') is not None:
                            figsize = figtable[obj.additional_dict.get('figpapersize')][::-1]
                        else:
                            figsize = figtable['A4'][::-1]
                    else:
                        if obj.additional_dict.get('figpapersize') is not None:
                            figsize = figtable[obj.additional_dict.get('figpapersize')]
                        else:
                            figsize = figtable['A4']
                else:
                    if obj.additional_dict.get('figpapersize') is not None:
                        figsize = figtable[obj.additional_dict.get('figpapersize')]
                    else:
                        figsize = figtable['A4']
    # If no figure size is supplied use default.
    if figsize is None:
        figsize = figtable['A4']

    # Plot the figure.
    fig = plt.figure(figsize=figsize)
    plt.subplots_adjust(
        left=0.15, right=0.89, top=0.92, bottom=0.16, hspace=0.2 + (len(plot_objects) - 2) * 0.05
    )

    axes = fig.subplots(len(plot_objects), 1)

    if not hasattr(axes, "__iter__"):
        assert len(plot_objects) == 1
        axes = [axes]

    for ax, po in zip(axes, plot_objects):
        po.plot(model, ax)

    plot_7box(fig, *args, **kwargs)
    fig.set_size_inches(figsize)
