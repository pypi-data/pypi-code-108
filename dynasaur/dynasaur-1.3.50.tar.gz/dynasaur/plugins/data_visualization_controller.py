import os
import copy

import pint
import numpy as np

from ..io.ISO_MME_Converter import ISOMMEConverter
from ..plugins.plugin import PluginInterface, Plugin
from ..utils.constants import DataPluginConstants, DefinitionConstants, LoggerSCRIPT, LOGConstants


class DataVisualizationController(PluginInterface, Plugin):
    """ """

    def __init__(self, calculation_procedure_def_file, object_def_file, data_source, user_function_object=None,
                 code_type="LS-DYNA"):
        """
        Initialization of the controller, which calls the Plugin constructor

        Args:
            calculation_procedure_def_file: path to calculation_procedure file
            object_def_file: path to object_def file
            data_source: path to binout
            user_function_object:
            code_type: [LS-DYNA, VPS, MADYMO]
            dynasaur definition

        Returns:
            Instance of the DataVisualizationController
        """
        Plugin.__init__(self, calculation_procedure_def_file=calculation_procedure_def_file,
                        object_def_file=object_def_file, data_source=data_source, name=DefinitionConstants.DATA_VIS,
                        user_function_object=user_function_object, code_type=code_type)

        self.init_plugin_data(update=True)
        self._data_dict = {}

    def get_defined_calculation_procedures(self):
        """
        Automatically extracts all "calculation commands" from the defined DATA VISUALIZATION objects
        (calculation_procedures.def file).
        Args:

        Returns:
            a list of dictionaries:
            i.e. [{'visualization': 'SEATBELT_B2_force', 'x_label': 'Time', 'y_label': 'Displacement'}]

        """
        return self._dynasaur_definitions.get_data_vis_calc_commands()

    def get_data(self, part_of=None, visualization=None):
        """
        Interface to retrieve calculated "visualizations".

        Args:
          part_of:  (Default value = None)
          visualization:  (Default value = None)

        Returns:
            If the "visualization" has been caluclated, a dictionary with the requested data (part_of, visualization)
            is returned otherwise an empty dict
        """
        if part_of is None and visualization is None:
            return self._data_dict

        elif part_of is None and visualization is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], "data dictionary is empty")
                return
            return_dict = {}
            for counter, parts_of in enumerate(self._data_dict.keys()):
                if visualization not in self._data_dict[parts_of]:
                    if counter == len(self._data_dict.keys()):
                        self._logger.emit(LOGConstants.ERROR[0], visualization + "not in data dictionary")
                        return
                else:
                    return_dict.update(self._data_dict[parts_of][visualization])

            return return_dict

        elif part_of is not None and visualization is None:
            if len(self._data_dict):
                return self._data_dict[part_of]
            else:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return

        elif part_of is not None and visualization is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0],
                                  "No data available.")
                return
            if part_of not in self._data_dict.keys():
                self._logger.emit(LOGConstants.ERROR[0],
                                  "For Region " + part_of + " no calculated results are available.")
                return
            if visualization not in self._data_dict[part_of].keys():
                self._logger.emit(LOGConstants.ERROR[0], visualization + " has not been calculated")
                return
            else:
                return self._data_dict[part_of][visualization]

    def write_ISO_MME(self, path_to_dir=None, test=False):
        """

        Args:
          path_to_dir: param test: (Default value = None)
          test:  (Default value = False)

        Returns:

        """
        converter = ISOMMEConverter()
        converter.write_ISOMME(path_to_dir=path_to_dir, data=self.get_data(),
                               dynasaur_definitions=self._dynasaur_definitions, logger=self._logger, test=test)

    def write_CSV(self, directory, filename=None):
        """
        creates a csv file at given file location (directory  + filename).
        if filename is None , a default file is created (<PLUGIN_NAME>_<timestamp>)

        Args:
          directory: path/to/directory
          filename: return: None (Default value = None)

        Returns:
          None

        """
        if os.path.isdir(directory) is None:
            self._logger.emit(LOGConstants.ERROR[0], self._name + ": csv_file_dir is not a directory")
            return

        if filename is None:
            filename = self._name + "_" + self._timestamp + ".csv"

        self._logger.emit(LOGConstants.SCRIPT[0], self._name + LoggerSCRIPT.print_statements[1] + directory)
        path = os.path.join(directory, filename)

        d = self._get_padded_data_dict()

        if d is None or len(d) == 0:
            return

        # header information
        header_info = []
        for part_of in d.keys():
            for visualization in d[part_of].keys():
                header_info.append([part_of,  visualization, d[part_of][visualization]["x_label"],
                                    d[part_of][visualization]["x_unit"]])
                header_info.append([part_of, visualization, d[part_of][visualization]["y_label"],
                                    d[part_of][visualization]["y_unit"]])

        # actual data
        values = []
        for part_of in d.keys():
            for visualization in d[part_of].keys():
                values.append(d[part_of][visualization]["X"])
                values.append(d[part_of][visualization]["Y"])

        list_lengths = [len(i) for i in values]
        assert(all([a == list_lengths[0] for a in list_lengths]))

        # writing data to csv (header_info and values must to passed)
        self._write_header_and_content_to_csv(path, header_info, values)

        self._logger.emit(LOGConstants.SCRIPT[0], self._name + LoggerSCRIPT.print_statements[6] + path)

    def _calculate_and_store_results(self, visualization: str, dynasaur_json: dict, x_label=None, y_label=None,
                                     t_start=None, t_end=None):
        """
            called from calculate() function. Various sanity checks are done

        Args:
          visualization:
          dynasaur_json:
          x_label:
          y_label:
          t_start:
          t_end:

        Returns: None

        """
        self._logger.emit(LOGConstants.SCRIPT[0], "Calculating Visualization: " + visualization)

        sample_offsets = self._get_sample_offset(dynasaur_json=dynasaur_json, t_start=t_start, t_end=t_end)
        if sample_offsets is None:
            return None

        reduced_sample_offsets_x = self._reduce_sample_offset(dynasaur_json[DataPluginConstants.X], sample_offsets)
        reduced_sample_offsets_y = self._reduce_sample_offset(dynasaur_json[DataPluginConstants.Y], sample_offsets)

        x_data = self._get_data_from_dynasaur_json(json_object=dynasaur_json[DataPluginConstants.X],
                                                   data_offsets=reduced_sample_offsets_x)
        if x_data is np.NaN or x_data is None:
            return None

        y_data = self._get_data_from_dynasaur_json(json_object=dynasaur_json[DataPluginConstants.Y],
                                                   data_offsets=reduced_sample_offsets_y)
        if y_data is np.NaN or y_data is None:
            return None

        # The calculated visualization is "visualization" is stored to _data_dict with the corresponding part_of.
        part_of = visualization.split("_")[0]
        visualization = "_".join(visualization.split("_")[1:])
        x_data = x_data.flatten()
        y_data = y_data.flatten()

        if part_of not in self._data_dict.keys():
            self._data_dict.update({part_of: {}})

        y_unit = y_data.units if isinstance(y_data, pint.Quantity) else "dimensionless"
        x_unit = x_data.units if isinstance(x_data, pint.Quantity) else "dimensionless"
        x_data = x_data.magnitude if isinstance(x_data, pint.Quantity) else x_data
        y_data = y_data.magnitude if isinstance(y_data, pint.Quantity) else y_data

        self._data_dict[part_of][visualization] = {"X": x_data,
                                                         "x_label": x_label,
                                                         "x_unit": x_unit,
                                                         "Y": y_data,
                                                         "y_label": y_label,
                                                         "y_unit": y_unit}


    def _get_padded_data_dict(self):
        """
        Creates a new dictionary based on _data_dict,
        "visualizations" are padded with Nones to the maximum length of all calculated visualizations.

        Returns:
            a padded copy of _data_dict
        """
        d = copy.deepcopy(self._data_dict)
        length = DataVisualizationController._get_maximum_length(d)
        for part_of in d.keys():
            for visualization in d[part_of].keys():
                if len(d[part_of][visualization]["X"]) < length or len(d[part_of][visualization]["Y"]) < length:
                    index_x = len(d[part_of][visualization]["X"])
                    padding_x = [None] * (length - index_x)
                    if isinstance(d[part_of][visualization]["X"], pint.Quantity):
                        padding_x *= d[part_of][visualization]["X"].units
                    d[part_of][visualization]["X"] = np.concatenate((d[part_of][visualization]["X"], padding_x))

                    index_y = len(d[part_of][visualization]["Y"])
                    padding_y = [None] * (length - index_y)
                    if isinstance(d[part_of][visualization]["X"], pint.Quantity):
                        padding_y *= d[part_of][visualization]["X"].units
                    d[part_of][visualization]["Y"] = np.concatenate((d[part_of][visualization]["Y"], padding_y))
        return d

    @staticmethod
    def _get_maximum_length(data_dict):
        """
        determine the maximum length of the calculated "visualizations" in data_dict.
        Necessary, when data_dict is written to a .csv file

        Args:
          data_dict: 

        Returns:
            max length: integer
        """

        if len(data_dict.keys()) == 0:
            return 0

        # traverse the data_dict and extract the length of X, Y respectively
        # data_dict[<part_of>][<visualization_name>]["X"]
        # data_dict[<part_of>][<visualization_name>]["Y"]
        return np.max([[len(data_dict[p][d]["X"]), len(data_dict[p][d]["Y"])] for p in data_dict.keys()
                       for d in data_dict[p].keys()])
