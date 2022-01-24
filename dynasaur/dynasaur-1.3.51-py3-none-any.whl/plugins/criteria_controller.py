import os

import pint
import numpy as np

from ..plugins.plugin import Plugin, PluginInterface
from ..utils.constants import DefinitionConstants, OutputStringForPlugins, JsonConstants, LoggerSCRIPT, LOGConstants


class CriteriaController(Plugin, PluginInterface):
    """ """
    def __init__(self, calculation_procedure_def_file, object_def_file, data_source, user_function_object=None,
                 volume_def_file=None, code_type="LS-DYNA"):
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
                        object_def_file=object_def_file, data_source=data_source, volume_path=volume_def_file,
                        user_function_object=user_function_object, name=DefinitionConstants.CRITERIA,
                        code_type=code_type)

        self.init_plugin_data(update=True)
        self._data_dict = {}

    def get_defined_calculation_procedures(self):
        """
        Automatically extracts all "calculation commands" from the defined DATA VISUALIZATION objects
        (calculation_procedures.def file).
        Args:

        Returns:
            a list of dictionaries:
            i.e. [{'criteria': 'SEATBELT_B2_force_max'}, ...]

        """
        return self._dynasaur_definitions.get_criteria_calc_commands()

    def _calculate_and_store_results(self, criteria: str, dynasaur_json: dict, t_start=None, t_end=None):
        """

        Args:
          criteria:
          dynasaur_json:
          t_start: float, given in the time unit as defined in the calculation_procedures.def file f.i. 10
                             if "time":"ms" or 0.01 if "time":"s"
          t_end: float,   given in the time unit as defined in the calculation_procedures.def file f.i. 200
                             if "time":"ms" or 0.2 if "time":"s"

        Returns:
          None
        """

        self._logger.emit(LOGConstants.SCRIPT[0], "Calculating Criteria: " + criteria) #param_dict["criteria"])

        sample_offset = self._get_sample_offset(dynasaur_json, t_start, t_end)
        if sample_offset is None:
            return

        reduced_sample_offsets = self._reduce_sample_offset(dynasaur_json, sample_offset)

        if not all([off == sample_offset[0][1] for i, off, _ in sample_offset]):
            required_data = [data_type for data_type, _, _ in sample_offset]
            self._logger.emit(LOGConstants.ERROR[0],
                              "Required data " + str(required_data) + " has not the same sampling frequency.")
            return

        ret = self._get_data_from_dynasaur_json(dynasaur_json, reduced_sample_offsets)
        ret_tuple = ret if isinstance(ret, tuple) else (ret, None)
        value = ret_tuple[0]

        part_of = dynasaur_json[JsonConstants.PART_OF]
        type_of_criteria = dynasaur_json[JsonConstants.TYPE_OF_CRTITERIA]
        criteria_name = "_".join(criteria.split("_")[1:])
        if part_of not in self._data_dict.keys():
            self._data_dict.update({part_of: {}})

        if type_of_criteria not in self._data_dict[part_of].keys():
            self._data_dict[part_of].update({type_of_criteria: {}})

        if criteria_name not in self._data_dict[part_of][type_of_criteria].keys():
            value_unit = value.units if isinstance(value, pint.Quantity) else "dimensionless"
            value = value.magnitude if isinstance(value, pint.Quantity) else value
            if isinstance(value, np.ndarray):
                assert(len(value) == 1)
                value = value[0]

            self._data_dict[part_of][type_of_criteria].update({criteria_name: {OutputStringForPlugins.VALUE: value,
                                                               OutputStringForPlugins.UNIT: str(value_unit)}})

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

        self._logger.emit(LOGConstants.SCRIPT[0], self._name + LoggerSCRIPT.print_statements[1] + directory)
        if filename is None:
            filename = self._name + "_" + self._timestamp + ".csv"

        path = os.path.join(directory, filename)

        # Header information
        header_info = []
        for part_of in self._data_dict.keys():
            for criteria_type in self._data_dict[part_of]:
                for criteria_name in self._data_dict[part_of][criteria_type].keys():
                    header_info.append([part_of, criteria_type, criteria_name])

        # actual criteria quantity with corresponding unit (stored additionally to the value)
        values = [[self._data_dict[part_of][criteria_type][criteria_name][OutputStringForPlugins.UNIT],
                   self._data_dict[part_of][criteria_type][criteria_name][OutputStringForPlugins.VALUE]]
                  for part_of in self._data_dict.keys()
                  for criteria_type in self._data_dict[part_of]
                  for criteria_name in self._data_dict[part_of][criteria_type].keys()]

        # write the the csv files
        self._write_header_and_content_to_csv(path, header_info, values)
        self._logger.emit(LOGConstants.SCRIPT[0], self._name + LoggerSCRIPT.print_statements[6] + path)

    def get_data(self, part_of=None, criteria_type=None, criteria=None):
        """Get data from data dict

        Args:
          part_of:  (Default value = None)
          criteria_type:  (Default value = None)
          criteria:  (Default value = None)

        Returns:
            If the "criteria" has been calculated, a dictionary with the requested data (part_of, criteria_type,
            criteria) is returned otherwise an empty dict

        """
        if part_of is None and criteria_type is None and criteria is None:
            return self._data_dict

        elif part_of is None and criteria_type is None and criteria is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            return_dict = {}
            for counter_one, parts_of in enumerate(self._data_dict.keys()):
                for counter, criteria_t in enumerate(self._data_dict[parts_of].keys()):
                    if criteria not in self._data_dict[parts_of][criteria_t]:
                        if counter == len(self._data_dict[parts_of].keys()) - 1 \
                                and counter_one == len(self._data_dict.keys()) - 1 \
                                and len(return_dict) == 0:
                            self._logger.emit(LOGConstants.ERROR[0], criteria + " not in data dictionary")
                            return
                    else:
                        return_dict.update(self._data_dict[parts_of][criteria_t][criteria])

            return return_dict

        elif part_of is None and criteria_type is not None and criteria is None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            return_dict = {}
            for counter, parts_of in enumerate(self._data_dict.keys()):
                if criteria_type not in self._data_dict[parts_of]:
                    if counter == len(self._data_dict.keys()) - 1 and len(return_dict) == 0:
                        self._logger.emit(LOGConstants.ERROR[0], criteria_type + " not in data dictionary")
                        return
                else:
                    return_dict.update(self._data_dict[parts_of][criteria_type])

            return return_dict

        elif part_of is None and criteria_type is not None and criteria is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            return_dict = {}
            for counter, part in enumerate(self._data_dict.keys()):
                if criteria_type not in self._data_dict[part]:
                    if counter == len(self._data_dict.keys()) - 1 and len(return_dict) == 0:
                        self._logger.emit(LOGConstants.ERROR[0], criteria_type + " not in data dictionary")
                        return
                else:
                    if criteria in self._data_dict[part][criteria_type].keys():
                        return_dict.update(self._data_dict[part][criteria_type][criteria])
            return return_dict

        elif part_of is not None and criteria_type is None and criteria is None:
            if len(self._data_dict):
                if part_of not in self._data_dict.keys():
                    self._logger.emit(LOGConstants.ERROR[0], part_of + " not in data dictionary")
                    return
                return self._data_dict[part_of]
            else:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return

        elif part_of is not None and criteria_type is None and criteria is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            return_dict = {}
            if part_of not in self._data_dict.keys():
                self._logger.emit(LOGConstants.ERROR[0], part_of + " not in data dictionary")
                return
            for counter, criteria_t in enumerate(self._data_dict[part_of].keys()):
                if criteria not in self._data_dict[part_of][criteria_t].keys():
                    if counter == len(self._data_dict[part_of].keys()) - 1 and len(return_dict) == 0:
                        self._logger.emit(LOGConstants.ERROR[0], criteria + " not in data dictionary")
                        return
                else:
                    return_dict.update(self._data_dict[part_of][criteria_t][criteria])
            return return_dict

        elif part_of is not None and criteria_type is not None and criteria is None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            if part_of not in self._data_dict.keys():
                self._logger.emit(LOGConstants.ERROR[0], part_of + " not in data dictionary")
                return
            if criteria_type not in self._data_dict[part_of].keys():
                self._logger.emit(LOGConstants.ERROR[0], criteria_type + " not in data dictionary")
                return
            return self._data_dict[part_of][criteria_type]

        elif part_of is not None and criteria_type is not None and criteria is not None:
            if len(self._data_dict) == 0:
                self._logger.emit(LOGConstants.ERROR[0], " data dictionary is empty")
                return
            if part_of not in self._data_dict.keys():
                self._logger.emit(LOGConstants.ERROR[0], part_of + " not in data dictionary")
                return
            if criteria_type not in self._data_dict[part_of].keys():
                self._logger.emit(LOGConstants.ERROR[0], criteria_type + " not in data dictionary")
                return
            if criteria not in self._data_dict[part_of][criteria_type].keys():
                self._logger.emit(LOGConstants.ERROR[0], criteria + " not in data dictionary")
                return
            else:
                return self._data_dict[part_of][criteria_type][criteria]
