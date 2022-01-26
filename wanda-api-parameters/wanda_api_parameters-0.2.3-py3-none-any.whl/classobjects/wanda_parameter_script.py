# Local imports
from wanda_api_parameters.parameters_api import (
    WKEY_SERIES,
    WKEY_FIGURE,
    WKEY_MODEL,
    WKEY_ROUTE,
    WKEY_POINT,
    WKEY_CASE,
    WKEY_APPENDIX,
    WKEY_CASE_TITLE,
    WKEY_CASE_DESCRIPTION,
    WKEY_DESCRIPTION,
    WKEY_CHAPTER,
    WKEY_PRJ_NUMBER,
    WBIN,
    XLS_CASE,
    XLS_CASE_NAME,
    XLS_CASE_NUMBER,
    XLS_CASE_INCLUDE,
    XLS_CASE_APPENDIX,
    XLS_CASE_CHAPTER,
    XLS_CASE_EXTRA,
    XLS_CASE_DESCRIPTION,
    XLS_OUTPUT,
    XLS_ROUTEPTS,
    XLS_RPLOT,
    XLS_PLOT_TITLE,
    XLS_TPLOT,
    XLS_PLOT_FIG,
    XLS_PLOT_PLOT,
    XLS_PLOT_NAME,
    XLS_PLOT_PROP,
    XLS_PLOT_LEGEND,
    XLS_PLOT_TIMES,
    XLS_PLOT_XLABEL,
    XLS_PLOT_YLABEL,
    XLS_PLOT_XMIN,
    XLS_PLOT_YMIN,
    XLS_PLOT_XMAX,
    XLS_PLOT_YMAX,
    XLS_PLOT_XSCALE,
    XLS_PLOT_YSCALE,
    XLS_PLOT_YTICK,
    XLS_PLOT_XTICK,
    WKEY_MAP,
    open_model,
    yaml_reader,
)
from wanda_api_parameters.classobjects import WandaScenario, FigureData
# General package imports
from collections import (defaultdict)
import multiprocessing as mp
import os
import pywanda
import pandas as pd
from PyPDF2 import PdfFileMerger
import queue
import time
import zipfile
from typing import List

class WandaParameterScript:
    """
    Control a WANDA model with a parameter script based on either a YAML or XLS-file. One of the file-formats has to be
    specified. The parser automatically uses the selected file format. However, there is no support for scenarios that
    use both an XLS aswell as a YAML-file format.

    The functionality of the parameter script has been extended with the YAML-file format. In the example directory
    several examples of both an XLS-file and YAML-file are given.

    Parameters
    ----------
    wanda_model: str
        Complete path specification to the wanda model.
    wanda_bin: str, default: c:\Program Files (x86)\Deltares\Wanda 4.6\Bin\\
        The path to the Wanda BIN directory.
    excel_file: str
        Complete path to the input parameters of the scenarios in an XLS-file format.
    yaml_file: str
        Complete path to the input parameters of the scenarios in a YAML-file format.
    only_figures: bool, default False
        The boolean can be used to reprocess already defined (i.e., processed) scenarios.
    """

    def __init__(
            self,
            wanda_model: str,
            excel_file: str = None,
            yaml_file: str = None,
            wanda_bin: str = WBIN,
            only_figures: bool = False,
            unzip_model: bool = True
    ):
        # Function components
        self.wanda_model = wanda_model
        self.wanda_bin = wanda_bin
        self.excel_file = excel_file
        self.yaml_file = yaml_file
        self.only_figures = only_figures
        self.unzip_model = unzip_model
        # Initialize directories
        self.model_dir = os.path.split(wanda_model)[0]
        self.figure_dir = os.path.join(self.model_dir, WKEY_FIGURE)
        # Empty components (initialize)
        self.scenarios = []
        self.output_component = []
        self.output_properties = []
        self.output_value = []
        self.appendix = {}
        self.output_filled = False
        # Define model
        self.model = None
        # Set parse excel/yaml
        self.yaml_parsed = False
        self._postprocess_pdf = False
        # create missing directories
        if not os.path.isdir(self.figure_dir):
            os.mkdir(self.figure_dir)
        # Open model
        # A model must not be opened to have the parameter script work in parallel. Otherwise, a PyWanda object is
        # already created that cannot be closed.
        #self.open_model(self.model_dir)

    def open_model(self, export_dir: str = None):
        """
        Open a Wanda model. The (implicit) parameters are defined by the class:
            unzip_bool: bool, default: False
                Unzip the model or work with the already present wanda model.
            wanda_model: str,
                The wanda model to open.
            model_dir: str,
                The path of the wanda_model

        Parameters
        ----------
        export_dir: str, default: Path to the model directory.
            Export the opened model to a specific file path. The export directory is required when the base model
            is extracted from a zip-file.

        """
        # Set the export directory.
        if export_dir is None:
            export_dir = self.model_dir
        # Open the base model.
        self.model = open_model(fn=self.wanda_model,
                                export_dir=export_dir,
                                unzip=self.unzip_model,
                                model_dir=self.model_dir)

    def parse_excel_file(self):
        """
        A class-method to generate scenarios based on a XLS-file.
        """

        # TODO: Replace string values with a default/option file. Then you won't have to change the variable strings over
        # the whole document when a variable is replaced.

        # Read the excel columns
        input_data = pd.read_excel(self.excel_file, XLS_CASE)
        output = pd.read_excel(self.excel_file, XLS_OUTPUT)
        series = pd.read_excel(self.excel_file, XLS_TPLOT)
        routes = pd.read_excel(self.excel_file, XLS_RPLOT)
        route_points = pd.read_excel(self.excel_file, XLS_ROUTEPTS)
        # Create the required input columns for figures and text_data
        figures = self.parse_figure_columns(series=series)
        figures.update(self.parse_figure_columns(series=routes))
        text_data = self.parse_text_columns(point_data=route_points)

        column_start = input_data.columns.get_loc(XLS_CASE_NAME) + 1
        # Creat the appropriate data structures for each line in the case-file xls
        for i in range(len(input_data.values)):
            # check if there number is a Nan, this means the row is not used and should be skipped.
            if input_data[XLS_CASE_NUMBER][i] != input_data[XLS_CASE_NUMBER][i]:
                continue
            # checking if the row is included or not
            if input_data[XLS_CASE_INCLUDE][i] != 1:
                continue
            # Define the case number
            number = int(input_data[XLS_CASE_NUMBER][i])
            # Define the appendix files
            pdf_file = input_data[XLS_CASE_APPENDIX][i] + "_" + f"{number:03}" + ".pdf"
            if input_data[XLS_CASE_APPENDIX][i] in self.appendix:
                self.appendix[input_data[XLS_CASE_APPENDIX][i]].append(pdf_file)
            else:
                self.appendix[input_data[XLS_CASE_APPENDIX][i]] = [pdf_file]
            # Define the plot data (transformation between wanda keys and case keys)
            plot_data = {
                WKEY_DESCRIPTION: input_data[XLS_CASE_DESCRIPTION][0],
                WKEY_PRJ_NUMBER: input_data[XLS_CASE_INCLUDE][0],
                WKEY_CASE_TITLE: input_data[XLS_CASE_DESCRIPTION][i],
                WKEY_CASE_DESCRIPTION: input_data[XLS_CASE_EXTRA][i],
                WKEY_APPENDIX: input_data[XLS_CASE_APPENDIX][i],
                WKEY_CHAPTER: input_data[XLS_CASE_CHAPTER][i],
                WKEY_CASE: input_data[XLS_CASE_NUMBER][i],
            }
            # Define the scenarios
            self.scenarios.append(
                WandaScenario(
                    model=self.wanda_model,
                    wanda_bin=self.wanda_bin,
                    name=input_data[XLS_CASE_NAME][i],
                    figure_data=figures,
                    plot_data=plot_data,
                    text_data=text_data,
                    only_figure=self.only_figures,
                )
            )
            # looping over all parameters and adding them to the scenario
            # TODO: This is an error prone operation.
            for j in range(column_start, len(input_data.axes[1])):
                self.scenarios[-1].add_parameter(
                    component_name=input_data.axes[1][j],
                    property_name=input_data[input_data.axes[1][j]][0],
                    value=input_data[input_data.axes[1][j]][i],
                )
            # Define the scenarios
            for j in range(0, len(output.values)):
                if not self.output_filled:
                    self.output_component.append(output.values[j][0])
                    self.output_properties.append(output.values[j][1])
                    self.output_value.append(output.values[j][2])
                # TODO: Check this! Again an error prone operation!
                self.scenarios[-1].add_output(
                    component_name=output.values[j][0],
                    property_name=output.values[j][1],
                    kind=output.values[j][2]
                )
            # Add all components from the series object
            for comp, prop, fig_number, plot_number, legend in zip(
                    series[XLS_PLOT_NAME], series[XLS_PLOT_PROP], series[XLS_PLOT_FIG], series[XLS_PLOT_PLOT],
                    series[XLS_PLOT_LEGEND]
            ):
                self.scenarios[-1].add_output(component_name=comp,
                                              property_name=prop,
                                              kind=WKEY_SERIES,
                                              fig_number=fig_number,
                                              plot_number=plot_number,
                                              legend=legend)
            # Add all components from the routes object
            for comp, prop, fig_number, plot_number, legend in zip(
                    routes[XLS_PLOT_NAME], routes[XLS_PLOT_PROP], routes[XLS_PLOT_FIG], routes[XLS_PLOT_PLOT],
                    routes[XLS_PLOT_LEGEND]
            ):
                self.scenarios[-1].add_output(component_name=comp,
                                              property_name=prop,
                                              kind=WKEY_ROUTE,
                                              fig_number=fig_number,
                                              plot_number=plot_number,
                                              legend=legend)
            self.output_filled = True

    def create_yaml_scenario(self, data: dict):
        """
        A class-method to generate scenarios based on a YAML-file that has been parsed with the parse_yaml_file class-
        method.

        Parameters
        ----------
        data: dict
            A dictionary with yaml data per scenario. The dictionary has been generated with the parse_yaml_file
            class-method.
        """
        # Define the scenarios
        for scenario in data['scenarios']:
            # Check scenario settings
            if data['scenarios'][scenario].get('steady') is None:
                data['scenarios'][scenario]['steady'] = True
            if data['scenarios'][scenario].get('unsteady') is None:
                data['scenarios'][scenario]['unsteady'] = True
            if data['scenarios'][scenario].get('si-units') is None:
                data['scenarios'][scenario]['si-units'] = False
            # Create each scenario.
            plot_data = {}
            plot_data.update(data['project'])
            plot_data.update(data['scenarios'][scenario]['project'])
            self.scenarios.append(
                WandaScenario(
                    model=self.wanda_model,
                    wanda_bin=self.wanda_bin,
                    name=data['scenarios'][scenario]['description'],
                    figure_data=self.create_yaml_figures(data=data),
                    plot_data=plot_data,
                    text_data=self.create_yaml_points(data=data),
                    only_figure=self.only_figures,
                    run_steady=data['scenarios'][scenario]['steady'],
                    run_unsteady=data['scenarios'][scenario]['unsteady'],
                    switch_si_units=data['scenarios'][scenario]['si-units'],
                )
            )
            # Define the appendix files
            if any([idx for idx in ['tplots', 'rplots', 'pplots', 'mapplots'] if data.get(idx) is not None]):
                self._postprocess_pdf = True
                pdf_file = "{}_{:03d}.pdf".format(plot_data['Appendix'], plot_data['Case number'])
                if plot_data['Appendix'] in self.appendix:
                    self.appendix[plot_data['Appendix']].append(pdf_file)
                else:
                    self.appendix[plot_data['Appendix']] = [pdf_file]

            # Append output to the scenarios
            if data.get('output') is not None:
                for sub_dict in data['output']:
                    if (sub_dict['Name'].lower() != 'none') and (sub_dict.get('Name') is not None):
                        # Append text data.
                        self.output_component.append(sub_dict['Name'])
                        self.output_properties.append(sub_dict['key'])
                        self.output_value.append(sub_dict['value'])
                        # Append to scenarios
                        self.scenarios[-1].add_output(
                            component_name=sub_dict['Name'],
                            property_name=sub_dict['key'],
                            kind=sub_dict['value']
                        )
            # Append parameters to the scenarios.
            for changes_dict in data['scenarios'][scenario]['changes']:
                for prop_dict in changes_dict['properties']:
                    for comp_key in changes_dict['components']:
                        if prop_dict.get('istable') is None:
                            prop_dict['istable'] = False

                        if prop_dict['istable']:
                            self.scenarios[-1].add_table(
                                component_name=comp_key,
                                property_name=prop_dict['key'],
                                table=pd.DataFrame(prop_dict['table']),
                            )
                        else:
                            if prop_dict['key'].lower() == 'disuse':
                                if prop_dict.get('value') is None:
                                    val = True
                                else:
                                    val = prop_dict.get('value')
                            else:
                                val = prop_dict.get('value')
                            self.scenarios[-1].add_parameter(
                                component_name=comp_key,
                                property_name=prop_dict.get('key'),
                                value=val,
                            )
            # Append plots
            plot_type = {'tplots': WKEY_SERIES, 'rplots': WKEY_ROUTE, 'pplots': WKEY_POINT, "mapplots": WKEY_MAP}
            for key_plot in list(plot_type.keys()):
                # Each figure number (a, b) is contained in a dictionary
                if data.get(key_plot) is not None:
                    for sub_dict in data[key_plot]:
                        if type(sub_dict) is dict:
                            # Each sub plot is contained in a dictionary
                            for sub_plot in sub_dict['plots']:
                                # Each sub plot may contain multiple components.
                                for sub_comp in sub_plot['components']:
                                    self.scenarios[-1].add_output(component_name=sub_comp['name'],
                                                                  property_name=sub_comp['property'],
                                                                  kind=plot_type[key_plot],
                                                                  fig_number=sub_dict['fig'],
                                                                  plot_number=sub_plot['plot'],
                                                                  legend=sub_comp['Legend'],
                                                                  property_dict=sub_comp.get('extra_properties'))
            # TODO: Where is this used?
            self.output_filled = True
            self.yaml_parsed = True

    def create_yaml_figures(self, data:dict):
        """
        A method used in the class-method create_yaml_scenario.

        Create figures from yaml key list.

        Parameters
        ----------
        data: dict
            A scenario dictionary in yaml format

        Returns
        -------
        figure_dict: dict
            A dictionary of figures to be generated from the yaml-format.

        """
        # Create empty figure dictionary
        figure_dict = {}
        # Loop over figures
        for key_plot in ['tplots', 'rplots', 'pplots', 'mapplots']:
            # Each figure number (a, b) is contained in a dictionary
            if data.get(key_plot) is not None:
                for sub_dict in data[key_plot]:
                    if type(sub_dict) is dict:
                        # Each sub plot is contained in a dictionary
                        sub_figures = {}
                        for sub_plot in sub_dict['plots']:
                            # Create axis
                            xaxis = [float(str(sub_plot.get(idx)).replace('None', 'nan')) for idx
                                     in ["Xmin", "Xtick", "Xmax", "Xscale"]]
                            yaxis = [float(str(sub_plot.get(idx)).replace('None', 'nan')) for idx
                                     in ["Ymin", "Ytick", "Ymax", "Yscale"]]
                            caxis = [float(str(sub_plot.get(idx)).replace('None', 'nan')) for idx
                                     in
                                     ["Cmin", "Ctick", "Cmax", "Cscale"]]
                            # Create times
                            for comp in sub_plot['components']:
                                if (comp.get('times') is None):
                                    times =[]
                                else:
                                    if len(comp['times']) > 0:
                                        if type(comp['times']) is not str:
                                            times = comp['times']
                                        else:
                                            times = []
                                    else:
                                        times =[]

                            # Create figure
                            sub_figures[sub_plot['plot']] = FigureData(title=sub_plot['title'],
                                                                       x_label=sub_plot['Xlabel'],
                                                                       y_label=sub_plot['Ylabel'],
                                                                       c_label=sub_plot.get('Clabel'),
                                                                       x_axis= tuple(xaxis),
                                                                       y_axis= tuple(yaxis),
                                                                       c_axis= tuple(caxis),
                                                                       times=times)
                    figure_dict[sub_dict['fig']] = sub_figures
        return figure_dict

    def create_yaml_points(self, data: dict):
        """
        A method used in the class-method create_yaml_scenario.

        Parse node locations from the yaml file.

        Parameters
        ----------
        data: dict
            A scenario dictionary in yaml format

        Returns
        -------
        point_data_parsed: dict
            A dictionary of poiont data to be generated from the yaml-format.

        """
        point_data_parsed = {}
        if data.get('textplots') is not None:
            for sub_dict in data['textplots']:
                if type(sub_dict) is dict:
                    # Each sub plot is contained in a dictionary
                    sub_figures = defaultdict(list)
                    for sub_plot in sub_dict['plots']:
                        temp_dict = {idx: float(str(sub_plot.get(idx)).replace('None', 'nan')) for idx in ["x", "y", "dx", "dy"]}
                        # Add text
                        if sub_plot.get('text') is not None:
                            temp_dict['text'] = sub_plot.get('text')
                        else:
                            temp_dict['text'] = 'None'
                        # Add marker
                        if sub_plot.get('marker') is not None:
                            temp_dict['marker'] = sub_plot.get('marker')
                        else:
                            temp_dict['marker'] = 'ro'
                        # Add marker
                        if sub_plot.get('line') is not None:
                            temp_dict['line'] = sub_plot.get('line')
                        else:
                            temp_dict['line'] = '-k'
                        # Add intercept
                        if sub_plot.get('intercept') is not None:
                            temp_dict['intercept'] = sub_plot.get('intercept')
                        else:
                            temp_dict['intercept'] = 'None'
                        sub_figures[sub_plot['plot']].append(temp_dict)
                    # Add data structure.
                    point_data_parsed[sub_dict['fig']] = sub_figures
        return point_data_parsed

    def parse_yaml_file(self):
        """
        Generate scenarios by parsing a YAML scenario-file.
        """
        # Read the yaml data
        input_data = yaml_reader(file_path=self.yaml_file)
        # Set scenarios.
        self.create_yaml_scenario(data=input_data)

    def parse_text_columns(self, point_data: pd.DataFrame):
        """
        Parse the text columns from a XLS scenario-file

        Parameters
        ----------
        point_data: pd.DataFrame
            A scenario dictionary of point data in XLS scenario-format

        Returns
        -------
        point_data_parsed: dict
            A dictionary of poiont data to be generated from the XLS-format.

        """
        point_data_parsed = {}
        for fig, plot_num, x, y, text, dx, dy in zip(
                point_data["fig"],
                point_data["plot"],
                point_data["x"],
                point_data["y"],
                point_data["text"],
                point_data["dx"],
                point_data["dy"],
        ):
            if fig in point_data_parsed:
                if plot_num in point_data_parsed[fig]:
                    point_data_parsed[fig][plot_num].append({'x':x, 'y':y, 'dx':dx, 'dy':dy, 'text':text})
                else:
                    point_data_parsed[fig][plot_num] = [{'x':x, 'y':y, 'dx':dx, 'dy':dy, 'text':text}]
            else:
                point_data_parsed[fig] = {plot_num: [{'x':x, 'y':y, 'dx':dx, 'dy':dy, 'text':text}]}
        return point_data_parsed

    def parse_figure_columns(self, series: pd.DataFrame):
        """
        A method used in the class-method create_xls_scenario.

        Create figures from XLS key list.

        Parameters
        ----------
        series: pd.DataFrame
            A scenario dataframe in XLS format

        Returns
        -------
        figure_dict: dict
            A dictionary of figures to be generated from the XLS-format.
        """
        figure_dict = {}
        for i in range(len(series[XLS_PLOT_FIG])):
            # Times is the number of times a single plot is recreated at different time intervals.
            times = []
            if XLS_PLOT_TIMES in series:
                index = series.columns.get_loc(XLS_PLOT_TIMES)
                times.append(series.values[i][index])
                index += 1
                # TODO: Remove the unnamed method and think of a "nicer" method!
                while series.columns[index][0:7] == "Unnamed":
                    if series.values[i][index] == series.values[i][index]:  # check for nan
                        times.append(series.values[i][index])
                    index += 1
            if not (series[XLS_PLOT_FIG][i] in figure_dict):
                x_axis = (
                    series[XLS_PLOT_XMIN][i],
                    series[XLS_PLOT_XTICK][i],
                    series[XLS_PLOT_XMAX][i],
                    series[XLS_PLOT_XSCALE][i],
                )
                y_axis = (
                    series[XLS_PLOT_YMIN][i],
                    series[XLS_PLOT_YTICK][i],
                    series[XLS_PLOT_YMAX][i],
                    series[XLS_PLOT_YSCALE][i],
                )
                # Generat plot dictionary
                figure_dict[series[XLS_PLOT_FIG][i]] = {
                    series[XLS_PLOT_PLOT][i]: FigureData(
                        title=series[XLS_PLOT_TITLE][i],
                        x_label=series[XLS_PLOT_XLABEL][i],
                        y_label=series[XLS_PLOT_YLABEL][i],
                        x_axis=x_axis,
                        y_axis=y_axis,
                        times=times,
                    )
                }
            elif not (series[XLS_PLOT_PLOT][i] in figure_dict[series[XLS_PLOT_FIG][i]]):
                x_axis = (
                    series[XLS_PLOT_XMIN][i],
                    series[XLS_PLOT_XTICK][i],
                    series[XLS_PLOT_XMAX][i],
                    series[XLS_PLOT_XSCALE][i],
                )
                y_axis = (
                    series[XLS_PLOT_YMIN][i],
                    series[XLS_PLOT_YTICK][i],
                    series[XLS_PLOT_YMAX][i],
                    series[XLS_PLOT_YSCALE][i],
                )
                figure_dict[series[XLS_PLOT_FIG][i]][series[XLS_PLOT_PLOT][i]] = FigureData(
                    title=series[XLS_PLOT_TITLE][i],
                    x_label=series[XLS_PLOT_XLABEL][i],
                    y_label=series[XLS_PLOT_YLABEL][i],
                    x_axis=x_axis,
                    y_axis=y_axis,
                    times=times,
                )

        return figure_dict

    def run_scenarios(self, n_workers: int = 1):
        """
        Execute the scenarios in the scenario dictionary.

        Parameters
        ----------
        n_workers: int, default=1
            Number of workers to perform the scenario calculations on.

        Notes
        -----
        The number of workers does currently not limit the number of exectued workers. A thorough test of the
        mutliprocessing functionality is required.

        TODO: Test the multiprocessing functionality.
        """
        # Run scenario's
        if n_workers == 1:
            result = self.run_single_process()
        else:
            result = self.run_multi_process(n_workers=n_workers)
        # Post-process results
        self.postprocess(result=result)

    def run_single_process(self):
        """
        Execute scneario files in a serial manner.

        Returns
        -------
        result: List
            A list with results from the scenario calculations.

        """
        result = []
        for scenario in self.scenarios:
            print("Processing {}".format(scenario.name))
            result.append(scenario.run_scenario())
        return result

    def run_multi_process(self, n_workers: int = 2):
        """
        Execute scneario files in a parallel manner.

        Parameters
        ----------
        n_workers: int, default=1
            Number of workers to perform the scenario calculations on.

        Returns
        -------
        result: List
            A list with results from the scenario calculations.

        Notes
        -----
        The number of workers does currently not limit the number of exectued workers. A thorough test of the
        mutliprocessing functionality is required.

        TODO: Test the multiprocessing functionality and/or improve with RAY (https://docs.ray.io/en/latest/multiprocessing.html)

        """
        tasks_to_accomplish = mp.Queue()
        tasks_that_are_done = mp.Queue()
        processes = []
        for scenario in self.scenarios:
            tasks_to_accomplish.put(scenario.run_scenario)
        # creating processes
        for w in range(n_workers):
            p = mp.Process(target=self.do_work, args=(tasks_to_accomplish, tasks_that_are_done))
            processes.append(p)
            p.start()
        # completing process
        print("waiting for processes to finish")
        for p in processes:
            p.join()
        # print the output
        result = []
        while not tasks_that_are_done.empty():
            res = tasks_that_are_done.get()
            result.append(res)
        return result

    def do_work(self, tasks_to_accomplish: mp.Queue, tasks_that_are_done: mp.Queue):
        """
        A class-method used in the run_multi_process class-method.

        Parameters
        ----------
        tasks_to_accomplish: mp.Queue
            A Queue object of Python's multiprocessing functionality containing the tasks to be executed.
        tasks_that_are_done: mp.Queue
            A Queue object of Python's multiprocessing functionality containing the tasks that have been executed.

        Returns
        -------
        """
        while True:
            try:
                '''
                    try to get task from the queue. get_nowait() function will 
                    raise queue.Empty exception if the queue is empty. 
                    queue(False) function would do the same task also.                '''
                task = tasks_to_accomplish.get_nowait()
            except queue.Empty:
                break
            else:
                '''
                    if no exception has been raised, add the task completion 
                    message to task_that_are_done queue
                '''
                print(task)
                result = task()
                tasks_that_are_done.put(result)
                time.sleep(0.5)
        return

    def merge_pdf(self, input_files: List, output_file: str):
        """
        Create a combined PDF file of the presults from the different scenarios.

        Parameters
        ----------
        input_files: List of str
            A list of strings referring to the respective PDF files.
        output_file: str
            Complete file specification for the output PDF file.
        """
        merger = PdfFileMerger()
        for pdf in input_files:
            merger.append(pdf)
        merger.write(output_file)
        merger.close()

    def postprocess_pdf(self):
        """
        Create a combined PDF file of the presults from the different scenarios.

        TODO: Define the type of exception that we try to catch with the except statement!
        """
        # combine pdfs into ond pdf.
        for appendix in self.appendix:
            try:
                print('Merged multiple PDF-files into a single document')
                self.merge_pdf([os.path.join(self.figure_dir, file) for file in self.appendix[appendix]],
                               os.path.join(self.figure_dir, "{}.pdf".format(appendix)))
            except:
                print('Failed to merge multiple PDF-files into a single document')

    def result_to_xlsx(self, result: dict):
        """
        Create xlsx file from the result.

        Parameters
        ----------
        result: dict
            A dictionary containing the data from output per scenario.

        Returns
        -------

        """
        # Output result data to xlsx
        writer = pd.ExcelWriter("{}.xlsx".format(os.path.splitext(self.wanda_model)[0]), engine='xlsxwriter')

        # Output sheet
        result_dict = {}
        for sub_result in result:
            result_dict = dict(result_dict, **sub_result)
        pd.DataFrame(result_dict).T.to_excel(writer, sheet_name='Output')
        # Create input dict
        result_dict = {}
        for scenario in self.scenarios:
            result_dict[scenario.name] = {" ".join([parameter.wanda_component, parameter.wanda_property]):
                                              parameter.value for parameter in scenario.parameters}
        pd.DataFrame(result_dict).T.to_excel(writer, sheet_name='Input')
        writer.save()

    def postprocess_yaml(self, result: dict):
        """
        Post-process the data from the WANDA model and retrieve the results for a parameter script based on either an
        XLS or YAML-file. The postprocess class_method requires the run_scenarios method to be used.

        Parameters
        ----------
        result: List
            A list of results from the run_scenarios class-method.

        Notes
        -----
        The YAML-files should have the standard format specified by Deltares.

        todo: Implement a method to generate an empty YAML-file

        """
        # Get the results and append them to the output structure.
        self.output_component.insert(0, "Scenario")
        self.output_properties.insert(0, "Name")
        self.output_value.insert(0, " ")

        # Write to xlsx
        self.result_to_xlsx(result=result)
        # Combine pdf files
        if self._postprocess_pdf:
            self.postprocess_pdf()

    def postprocess_xls(self, result: dict):
        """
        Post-process the data from the WANDA model and retrieve the results for a parameter script based on a XLS-file.
        The postprocess class_method requires the run_scenarios method to be used.

        Parameters
        ----------
        result: List
            A list of results from the run_scenarios class-method.

        Notes
        -----
        The XLS-files should have the standard format specified by Deltares.

        todo: Implement a method to generate an empty XLS-file


        """
        # Get the results and append them to the output structure.
        self.output_component.insert(0, "Scenario")
        self.output_properties.insert(0, "Name")
        self.output_value.insert(0, " ")

        # Create xlsx output
        self.result_to_xlsx(result=result)
        # postprocess pdf
        self.postprocess_pdf()

    def postprocess(self, result):
        """"
        Post-process the data from the WANDA model and retrieve the results for a parameter script based on either an
        XLS or YAML-file. The postprocess class_method requires the run_scenarios method to be used.

        Parameters
        ----------
        result: List
            A list of results from the run_scenarios class-method.

        """
        if self.yaml_parsed:
            self.postprocess_yaml(result=result)
        else:
            self.postprocess_xls(result=result)

    def zip_models(self, fn_path: str = None, delete_original: bool = False):
        """"Zip models and delete corresponding data files.

        Parameters
        ----------
        fn_path: str, default = Path to the model directory of the wanda_model
            Path to the model directory or the directory that needs to be cleaned. Default will get the models in the
            model folder.
        delete_original: bool, default = False
            Delete the original Wanda model files.
        """
        if fn_path is None:
            fn_path = os.path.join(self.model_dir, WKEY_MODEL)
        list_files = os.listdir(os.path.join(fn_path))
        list_files = [file for file in list_files if not file.endswith(".zip")]
        list_files_unique = list(set([os.path.splitext(file)[0] for file in list_files]))
        # List case files
        case_files = [scen.name for scen in self.scenarios]
        list_files_unique = [file for file in list_files_unique if any(st in file for st in case_files)]
        # Zip each unique case
        for case in list_files_unique:
            with zipfile.ZipFile(os.path.join(fn_path, "{}.zip".format(case)), "w") as zipF:
                zip_files = [os.path.join(fn_path, file) for file in list_files if case == os.path.splitext(file)[0]]
                for file in zip_files:
                    arcname = os.path.split(file)[1]
                    zipF.write(file, arcname, compress_type=zipfile.ZIP_DEFLATED)
                    # if delete_original:
                    #     os.remove(file)

    def unzip_models(self, fn_path: str = None, fn_file: str = None):
        """"
        Unzip models if the option only-figures is enabled or by calling the method.

        The unzip models functionality prevents NEFIS exceptions on the Wanda-files.

        Parameters
        ----------
        fn_path: str, default = Path to the model directory of the wanda_model
            Path to the model directory or the directory that needs to be cleaned. Default will get the models in the
            model folder.
        fn_file: str, default = extract all zip folders.
            Extract the file specified by the fn_file in the folder fn_path or wanda_model directory. Otherwise, all
            zip-files available in the fn_path or wanda_model directory are extracted.


        """
        # Define standard model path
        if fn_path is None:
            fn_path = os.path.join(self.model_dir, WKEY_MODEL)
        # Define files
        if fn_file is None:
            list_files = os.listdir(os.path.join(fn_path))
            list_files_unique = list(set([os.path.splitext(file)[0] for file in list_files if file.endswith(".zip")]))
            # List case files
            case_files = [scen.name for scen in self.scenarios]
            list_files_unique = [file for file in list_files_unique if any(st in file for st in case_files)]
        else:
            list_files_unique = list(fn_file)
        # Unzip each folder
        if len(list_files_unique) > 0:
            for case in list_files_unique:
                with zipfile.ZipFile(os.path.join(fn_path, "{}.zip".format(case)), "r") as zipF:
                    zipF.extractall(fn_path)



if __name__ == '__main__':
    import zipfile
    from wanda_api_parameters.parameters_api import (empty_directory)
    # Specify the example filename
    fn = "ASR_Future_Network"
    #fn = "PipeHill_Airvessel"
    fp = os.path.join(os.getcwd(), "example", fn)
    # Clean up model directory
    only_figures = False
    if not only_figures:
        empty_directory(dir_path=os.path.join(fp, "models"))
        # Unzip wdi
        with zipfile.ZipFile(os.path.join(fp, "{}.zip".format(fn)), "r") as zip_ref:
            zip_ref.extractall(fp)
    # Clean up figure directory
    empty_directory(dir_path=os.path.join(fp, "figures"))
    # Run model-
    WPS = WandaParameterScript(wanda_model=os.path.join(fp, "{}.wdi".format(fn)),
                               yaml_file=os.path.join(fp, "{}.yaml".format(fn)),
                               only_figures=only_figures
                               )
    # Read the excel configuration file
    #WPS.parse_yaml_variables()
    WPS.parse_yaml_file()
    # Run the model
    WPS.run_scenarios(n_workers=1)
    # Clean up models
    WPS.zip_models()
