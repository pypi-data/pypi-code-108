import os.path
import glob
import pandas as pd
import pywanda
from wanda_api_parameters.classobjects import WandaParameter
from wanda_api_parameters.parameters_api import (
    WKEY_FIGURE,
    WKEY_MODEL,
    WKEY_ROUTE,
    WKEY_SERIES,
    WKEY_CASE,
    WKEY_APPENDIX,
    WKEY_CASE_TITLE,
    WKEY_CASE_DESCRIPTION,
    WKEY_DESCRIPTION,
    WKEY_CHAPTER,
    WKEY_PRJ_NUMBER,
    WKEY_POINT,
    WKEY_MAP,
    WKEY_PIPES,
)
from collections import (OrderedDict, defaultdict)
from typing import (List)
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.pyplot as plt
from .wanda_plot import (plot, PlotTimeseries, PlotRoute, PlotText, PlotPointTimeseries, PlotMap)
from wanda_api_parameters.parameters_api.functions import empty_directory
import shutil

class WandaScenario:
    """
    WandaScenario a class-object that contains all the properties to run a particular model scenario.

    The scenario method includes plot properties to allow for parallel processing of the scenario's (i.e., both running
    the model and processing the model results)

    Parameters:
        :param model (str) A WANDA model object file name
        :param wanda_bin (str) The location of the WANDA Bin.
        :param figure_data (OrderdDict) Figure data contained in a dictionary format
        :param plot_data (OrderdDict) Plot data contained in a dictionary format
        :param text_data (OrderdDict) Text data contained in a dictionary format
        :param only_figure (boolean) Run model with only figures (True) or complete model (False)
        :param run_steady (boolean: True) Run model with steady
        :param run_unsteady (boolean: True) Run model with unsteady
    """

    def __init__(
        self,
        model: str,
        wanda_bin: str,
        name: str,
        figure_data,
        plot_data,
        text_data,
        only_figure: bool = False,
        run_steady: bool = True,
        run_unsteady: bool = True,
        switch_si_units: bool= False,
    ):
        self.name = name
        self.model_dir = os.path.join(os.path.split(model)[0], WKEY_MODEL)
        self._model_name = os.path.split(model)[1]
        # Switch to si units
        self.switch_si_units = switch_si_units
        # Add steady unsteady
        self.run_steady = run_steady
        self.run_unsteady = run_unsteady
        # Create folder structure
        if not os.path.isdir(self.model_dir):
            os.mkdir(self.model_dir)
        # Define new model file

        self._output_model_name = os.path.splitext(self._model_name)[0] + "_" + name
        self.model_file = os.path.join(self.model_dir,
                                       "{}.wdi".format(self._output_model_name))
        self._output_model_file = os.path.join(self.model_dir,
                                       "{}.wdo".format(self._output_model_name))
        self.only_figures = only_figure
        self._figure_dir = os.path.join(os.path.split(model)[0], WKEY_FIGURE)
        self.bin = wanda_bin
        self.parameters = []
        self.output = []
        self.figure_data = figure_data
        self.plot_data = plot_data
        self.text_data = text_data

        # Create folder structure
        if not os.path.isdir(self._figure_dir):
            os.mkdir(self._figure_dir)
        # Remove model files.
        if not self.only_figures:
            # Missing output file.
            if not os.path.isfile(self._output_model_file):
                self.only_figures = False
                # Check existence of model file.
                if os.path.isfile(self.model_file):
                    empty_directory(dir_path=self.model_dir,
                                    file_name=self._output_model_name)
                # Copy model file.
                for ext in ["wdi", "wdx"]:
                    try:
                        shutil.copyfile(
                            "{}.{}".format(os.path.splitext(model)[0], ext),
                            "{}.{}".format(os.path.splitext(self.model_file)[0], ext)
                        )
                    except FileNotFoundError:
                        continue
            elif os.path.isfile(self.model_file):
                empty_directory(dir_path=self.model_dir,
                                file_name=self._output_model_name)
                # Copy model file.
                for ext in ["wdi", "wdx"]:
                    try:
                        shutil.copyfile(
                            "{}.{}".format(os.path.splitext(model)[0], ext),
                            "{}.{}".format(os.path.splitext(self.model_file)[0], ext)
                        )
                    except FileNotFoundError:
                        continue

    def add_parameter(self, value, component_name: str, property_name: str):
        """Add parameters to the WANDA model
        :param value (str-float) Value to add to the parameter
        :param component_name (str) Component name to set
        :param property_name (str) Property name to set
        """
        self.parameters.append(WandaParameter(component_name, property_name, value=value))

    def add_table(self, table: pd.DataFrame, component_name: str, property_name: str):
        """

        Parameters
        ----------
        table: pd.DataFrame
        component_name: component name

        Returns
        -------

        """
        for key in list(table.keys()):
            self.parameters.append(WandaParameter(wanda_component=component_name,
                                                  wanda_property=property_name,
                                                  wanda_column=key,
                                                  value=table[key].to_list(),
                                                  table=True))

    def add_output(
        self, component_name, property_name, kind=None, fig_number=None, plot_number=None, legend=None, property_dict=None
    ):
        """Add output parameters to the WANDA model
        :param component_name (str) Component name to set
        :param property_name (str) Property name to set
        :param kind () Unknown
        :param fig_number (Unknown) Unknown
        :param plot_number (Unknown) Unknown
        :param legend (Unknown) Unknown
        """
        self.output.append(
            WandaParameter(
                component_name,
                property_name,
                output=kind,
                fig_number=fig_number,
                plot_number=plot_number,
                legend=legend,
                property_dict=property_dict,
            )
        )

    def run_scenario(self):
        """Run WANDA scenario"""
        try:
            # Open wanda model
            model = pywanda.WandaModel(self.model_file, self.bin)
            # Switch units
            if self.switch_si_units:
                model.switch_to_unit_SI()
            # Open model (if it exists) for figures only or set parameters and re-run models.
            if self.only_figures and os.path.isfile(self._output_model_file):
                model.reload_output()
            else:
                for parameter in self.parameters:
                    # if parameter.wanda_component in ["IWTP8", "stage1"]:
                    #     test = 0
                    parameter.set_parameter(model=model)
                model.save_model_input()
                if self.run_steady:
                    model.run_steady()
                if self.run_unsteady:
                    model.run_unsteady()
            # Retrieve results
            result = self.get_results(model)
            # Create graphs
            self.create_graphs(model)
            # Close wanda model
            model.close()
        except RuntimeError as error:
            print(error)
            print("The function run_scenario could not run the model.")
        return result

    def get_results(self, model):
        """Get results from WANDA scenario in the form of a dictionary."""
        # Create results dict
        results = {self.name: {}}
        for output in self.output:
            # Get extreme values (MIN, MAX)
            if output.output.lower() in ['min', 'max']:
                if output.wanda_component == WKEY_PIPES:
                    # Retrieve results and assign to the output
                    comps = model.get_all_pipes()
                    # Add all pipes to the property list
                    for comp in comps:
                        if not comp.is_disused():
                            temp_name = "{} {} {}".format(comp.get_name(), output.wanda_property, output.output)
                            try:
                                temp_property = comp.get_property(output.wanda_property)
                                if output.output.lower() == "min":
                                    temp_result = temp_property.get_extr_min() * temp_property.get_unit_factor()
                                else:
                                    temp_result = temp_property.get_extr_max() * temp_property.get_unit_factor()
                                results[self.name][temp_name] = temp_result
                            except ValueError:
                                print("Property {} does not exist for component {}".format(
                                    output.wanda_property,
                                    comp
                                ))
                        else:
                            test = 0
                else:
                    # Retrieve results and assign to the output
                    result, wanda_properties = output.get_result_extreme(model)
                    output.value = result
                    # Assign to the dictionary.
                    temp_name = "{} {} {}".format(output.wanda_component, output.wanda_property, output.output)
                    results[self.name][temp_name] = result
            # Get series (both routes, and series).
            output.get_series(model)
        return results

    def create_graphs(self, model: pywanda.WandaModel):
        """Get graphs from WANDA scenario"""
        # Create figure dict containing all the figures.
        figure_dict = self.create_figure_dict(model=model)
        # figure number
        number = int(self.plot_data[WKEY_CASE])
        # pdf-file path
        pdf_file = os.path.join(self._figure_dir, "{}_{:03d}.pdf".format(self.plot_data[WKEY_APPENDIX], number))
        # Delete pdf file if already exists.
        if os.path.isfile(pdf_file):
            os.remove(pdf_file)
        # Open the pdf file with PdfPages.
        with PdfPages(pdf_file) as pdf:
            # Loop over the available figures
            for figure_key in figure_dict.keys():
                # Create figure list.
                figure_list = self.create_figure_list(sub_figures=figure_dict[figure_key], figure_key=figure_key,
                                                      model=model)
                # Plot the figures from the figure list.
                plot(
                    model=model,
                    plot_objects=figure_list,
                    title=self.plot_data[WKEY_DESCRIPTION],
                    case_title=self.plot_data[WKEY_CASE_TITLE],
                    case_description=self.plot_data[WKEY_CASE_DESCRIPTION],
                    proj_number=self.plot_data[WKEY_PRJ_NUMBER],
                    section_name=self.plot_data[WKEY_CHAPTER],
                    fig_name="Fig {appendix}.{number:03} {figure}".format(appendix=self.plot_data[WKEY_APPENDIX],
                                                                          number=number,
                                                                          figure=figure_key),
                )
                pdf.savefig()
                plt.close()

    def create_figure_dict(self, model: pywanda.WandaModel) -> defaultdict:
        """

        Parameters
        ----------
        model: pywanda.WandaModel

        Returns
        -------
        ordered_figure: OrderedDict
            An ordered ditionary with all the figure components.

        """
        # create figure dict.
        figures = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        for output in self.output:
            if output.output == WKEY_SERIES:
                tuple_data = (output.wanda_component, output.wanda_property, output.legend)
            elif output.output == WKEY_POINT:
                # Retrieve x-coordinates.
                if self.figure_data[output.fig_number][output.plot_number].times is not None:
                    times = self.figure_data[output.fig_number][output.plot_number].times
                else:
                    times = [0]
                tuple_data = (output.wanda_component, output.wanda_property, output.legend, times)
            elif output.output == WKEY_MAP:
                tuple_data = {"name": output.wanda_component,
                              "property": output.wanda_property,
                              "legend": output.legend,
                              "property_dict": output.property_dict}
            elif output.output == WKEY_ROUTE:
                # If route is only a single component.
                if model.component_exists(output.wanda_component):
                    comps = [model.get_component(output.wanda_component)]
                    directions = [1]
                else:
                    comps, directions = model.get_route(output.wanda_component)

                if sum(directions) < 0:
                    # flip direction
                    comps.reverse()
                    directions.reverse()
                    directions = [-1 * x for x in directions]
                pipes = []
                pipes_dir = []
                for p, direction in zip(comps, directions):
                    if p.is_pipe():
                        pipes.append(p)
                        pipes_dir.append(direction)
                tuple_data = {"pipes":pipes, "direction": pipes_dir, "property": output.wanda_property}
            else:
                continue
            # Assign figures
            figures[output.fig_number][output.plot_number]['data'].append(tuple_data)
            figures[output.fig_number][output.plot_number]['type'].append(output.output)
        # Order the figure data
        order_figures = OrderedDict(sorted(figures.items()))
        return order_figures

    def create_text_list(self,figure_key, sub_figure_key) -> List:
        # Retrieve text data for intercepts or to point out something interesting.
        text_data = []
        if figure_key in self.text_data:
            if sub_figure_key in self.text_data[figure_key]:
                text_data.append(self.text_data[figure_key][sub_figure_key])
        return text_data

    def create_figure_list(self, figure_key, sub_figures: dict, model: pywanda.WandaModel) -> List:
        """
        Create figure list for the sub_figures of the figure dictionary.

        Parameters
        ----------
        model: pywanda.WandaModel
        figure_key: str/int
            Key of the figure dictionary to assign either labels, or components to the respective figures
        sub_figures
            Sub figure from the complete figure dictionary.

        Returns
        -------
        figure_list: A list containing all the figures of the selected sub-figure

        """

        # Create empty figure list
        figure_list = []
        # Append sub-figures
        for sub_figure_key in sub_figures.keys():
            # Retrieve sub-figure
            sub_figure = sub_figures[sub_figure_key]['data']
            figure_type= sub_figures[sub_figure_key]['type'][0]
            if figure_type == WKEY_ROUTE:
                if self.figure_data[figure_key][sub_figure_key].times is None:
                    times = [0]
                else:
                    times = self.figure_data[figure_key][sub_figure_key].times
                # Retrieve text_data
                text_data = self.create_text_list(figure_key=figure_key, sub_figure_key=sub_figure_key)
                # Append a PlotRoute to the list.
                figure_list.append(
                    PlotRoute(
                        pipes=sub_figure[0]['pipes'],
                        annotations=sub_figure[0]['direction'],
                        prop=sub_figure[0]['property'],
                        times=times,
                        title=self.figure_data[figure_key][sub_figure_key].title,
                        xlabel=self.figure_data[figure_key][sub_figure_key].x_label,
                        ylabel=self.figure_data[figure_key][sub_figure_key].y_label,
                        plot_elevation=sub_figure[0]['property'].lower() == "head",
                        plot_text=text_data,
                        xmin=self.figure_data[figure_key][sub_figure_key].x_axis[0],
                        xtick=self.figure_data[figure_key][sub_figure_key].x_axis[1],
                        xmax=self.figure_data[figure_key][sub_figure_key].x_axis[2],
                        xscale=self.figure_data[figure_key][sub_figure_key].x_axis[3],
                        ymin=self.figure_data[figure_key][sub_figure_key].y_axis[0],
                        ytick=self.figure_data[figure_key][sub_figure_key].y_axis[1],
                        ymax=self.figure_data[figure_key][sub_figure_key].y_axis[2],
                        yscale=self.figure_data[figure_key][sub_figure_key].y_axis[3],
                    )
                )
            elif figure_type == WKEY_SERIES:
                # text data
                text_data = self.create_text_list(figure_key=figure_key, sub_figure_key=sub_figure_key)
                # Add a time-series plot to the list.
                figure_list.append(
                    PlotTimeseries(
                        collection=sub_figure,
                        plot_text=text_data,
                        title=self.figure_data[figure_key][sub_figure_key].title,
                        xlabel=self.figure_data[figure_key][sub_figure_key].x_label,
                        ylabel=self.figure_data[figure_key][sub_figure_key].y_label,
                        xmin=self.figure_data[figure_key][sub_figure_key].x_axis[0],
                        xtick=self.figure_data[figure_key][sub_figure_key].x_axis[1],
                        xmax=self.figure_data[figure_key][sub_figure_key].x_axis[2],
                        xscale=self.figure_data[figure_key][sub_figure_key].x_axis[3],
                        ymin=self.figure_data[figure_key][sub_figure_key].y_axis[0],
                        ytick=self.figure_data[figure_key][sub_figure_key].y_axis[1],
                        ymax=self.figure_data[figure_key][sub_figure_key].y_axis[2],
                        yscale=self.figure_data[figure_key][sub_figure_key].y_axis[3],
                    )
                )
            elif figure_type == WKEY_MAP:
                # text data
                text_data = self.create_text_list(figure_key=figure_key, sub_figure_key=sub_figure_key)
                # Add a time-series plot to the list.
                figure_list.append(
                    PlotMap(
                        model=model,
                        pipes=sub_figure[0]['name'],
                        pipe_dir=os.path.split(self.model_dir)[0],
                        annotations=sub_figure[0]['legend'],
                        prop=sub_figure[0]['property'],
                        additional_dict=sub_figure[0]['property_dict'],
                        scenarioname=self.name,
                        plot_text=text_data,
                        title=self.figure_data[figure_key][sub_figure_key].title,
                        xlabel=self.figure_data[figure_key][sub_figure_key].x_label,
                        ylabel=self.figure_data[figure_key][sub_figure_key].y_label,
                        clabel=self.figure_data[figure_key][sub_figure_key].c_label,
                        xmin=self.figure_data[figure_key][sub_figure_key].x_axis[0],
                        xtick=self.figure_data[figure_key][sub_figure_key].x_axis[1],
                        xmax=self.figure_data[figure_key][sub_figure_key].x_axis[2],
                        xscale=self.figure_data[figure_key][sub_figure_key].x_axis[3],
                        ymin=self.figure_data[figure_key][sub_figure_key].y_axis[0],
                        ytick=self.figure_data[figure_key][sub_figure_key].y_axis[1],
                        ymax=self.figure_data[figure_key][sub_figure_key].y_axis[2],
                        yscale=self.figure_data[figure_key][sub_figure_key].y_axis[3],
                        cmin=self.figure_data[figure_key][sub_figure_key].c_axis[0],
                        ctick=self.figure_data[figure_key][sub_figure_key].c_axis[1],
                        cmax=self.figure_data[figure_key][sub_figure_key].c_axis[2],
                        cscale=self.figure_data[figure_key][sub_figure_key].c_axis[3],
                    )
                )
            elif figure_type == WKEY_POINT:
                figure_list.append(
                    PlotPointTimeseries(
                        collection=sub_figure,
                        title=self.figure_data[figure_key][sub_figure_key].title,
                        xlabel=self.figure_data[figure_key][sub_figure_key].x_label,
                        ylabel=self.figure_data[figure_key][sub_figure_key].y_label,
                        xmin=self.figure_data[figure_key][sub_figure_key].x_axis[0],
                        xtick=self.figure_data[figure_key][sub_figure_key].x_axis[1],
                        xmax=self.figure_data[figure_key][sub_figure_key].x_axis[2],
                        xscale=self.figure_data[figure_key][sub_figure_key].x_axis[3],
                        ymin=self.figure_data[figure_key][sub_figure_key].y_axis[0],
                        ytick=self.figure_data[figure_key][sub_figure_key].y_axis[1],
                        ymax=self.figure_data[figure_key][sub_figure_key].y_axis[2],
                        yscale=self.figure_data[figure_key][sub_figure_key].y_axis[3],
                    )
                )
            else:
                figure_list.append(
                    PlotTimeseries(
                        collection=sub_figure,
                        title=self.figure_data[figure_key][sub_figure_key].title,
                        xlabel=self.figure_data[figure_key][sub_figure_key].x_label,
                        ylabel=self.figure_data[figure_key][sub_figure_key].y_label,
                        xmin=self.figure_data[figure_key][sub_figure_key].x_axis[0],
                        xtick=self.figure_data[figure_key][sub_figure_key].x_axis[1],
                        xmax=self.figure_data[figure_key][sub_figure_key].x_axis[2],
                        xscale=self.figure_data[figure_key][sub_figure_key].x_axis[3],
                        ymin=self.figure_data[figure_key][sub_figure_key].y_axis[0],
                        ytick=self.figure_data[figure_key][sub_figure_key].y_axis[1],
                        ymax=self.figure_data[figure_key][sub_figure_key].y_axis[2],
                        yscale=self.figure_data[figure_key][sub_figure_key].y_axis[3],
                    )
                )
        return figure_list
