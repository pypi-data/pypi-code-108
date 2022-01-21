import abc
import inspect
import time
import numpy as np
import csv
from datetime import datetime

from lasso.dyna.Binout import Binout
from pint import UnitRegistry

from ..utils.constants import StandardFunctionsDefinition, JsonConstants, ObjectConstantsForData, \
    LoggerERROR, LoggerWARNING
from ..calc.standard_functions import StandardFunction
from ..utils.constants import LOGConstants
from ..utils.logger import ConsoleLogger
from ..data.dynasaur_definitions import DynasaurDefinitions
from ..data.data_container import DataContainer
from ..data.vps import VPSData
from ..data.madymo import MadymoData


class Plugin(object):
    """ """
    def __init__(self, calculation_procedure_def_file, object_def_file, data_source, name, user_function_object=None,
                 volume_path=None, code_type="LS-DYNA"):
        """
        Plugin constructor

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

        self._logger = ConsoleLogger()
        self._dynasaur_definitions = DynasaurDefinitions(self._logger)
        self._dynasaur_definitions.read_def(calculation_procedure_def_file)
        self._dynasaur_definitions.read_def(object_def_file)
        self._user_function = user_function_object

        if code_type == "LS-DYNA":
            binout = Binout(data_source)
            DataContainer.init_all_data_sources(binout, self._logger, self._dynasaur_definitions,
                                                volume_path=volume_path)
        elif code_type == "VPS":
            vps_data = VPSData(vps_file_path=data_source)
            DataContainer.init_all_data_sources(vps_data, self._logger, self._dynasaur_definitions,
                                                volume_path=volume_path)

        elif code_type == "MADYMO":
            madymo_data = MadymoData(madymo_file_path=data_source)
            DataContainer.init_all_data_sources(madymo_data, self._logger, self._dynasaur_definitions,
                                                volume_path=volume_path)
        else:
            self._logger.emit(LOGConstants.ERROR[0], "invalid code type try, [LS-DYNA, MADYMO, VPS]")
            return

        self._timestamp = datetime.today().strftime("%Y-%m-%d-%H-%M-%S")
        self._units = self._dynasaur_definitions.get_units()
        self._data_requirements = self._dynasaur_definitions.get_required_datatypes(name)
        # check for subset

        dynasaur_data_types = [ObjectConstantsForData.__dict__[i] for i in ObjectConstantsForData.__dict__ if not i.startswith("__")]
        req_in_ddt = [req not in dynasaur_data_types for req in self._data_requirements]

        if len(np.array(self._data_requirements)[req_in_ddt]) != 0:
            self._logger.emit(LOGConstants.ERROR[0], "Your calculation_procedure_def_file contains a data type which is"
                                                     + " not understood : "
                                                     + ", ".join(np.array(self._data_requirements)[req_in_ddt])
                                                     + "  \nAvailable types are : \n" + "\n".join(dynasaur_data_types))

        self._data = None
        self._name = name
        self._sample_types = []

        # ensure unique timestamps
        time.sleep(1)

    def _check_if_user_function(self, function_name):
        """
        check if a function is defined as user_function

        Args:
          function_name:

        Returns: True or False
        """
        attributes = inspect.getmembers(self._user_function, predicate=inspect.isfunction)
        if function_name in [att[0] for att in attributes]:
            return True
        return False

    @staticmethod
    def _kwargs_from_param_dict(param_dict, units):
        """

        Args:
          param_dict: return:
          units: 

        Returns:

        """
        kwargs = {}
        for key in param_dict:
            kwargs[key] = param_dict[key]

        return kwargs

    def _call_standard_function(self, function_name, param_dict):
        """

        Args:
          function_name: param param_dict:
          param_dict: 

        Returns:

        """
        kwargs = Plugin._kwargs_from_param_dict(param_dict, self._units)
        if self._user_function is not None:
            if self._check_if_user_function(function_name):
                function = getattr(self._user_function, function_name)
                return function(**kwargs)

        if function_name not in StandardFunction.__dict__.keys():
            self._logger.emit(LOGConstants.ERROR[0], function_name + " is not a standard function!")
            self._logger.emit(LOGConstants.ERROR[0], "Implemented functions are :\n" + "\n".join(
                [i for i in StandardFunction.__dict__.keys() if not i.startswith("__")]))

            return None
        else:
            func_ptr = StandardFunction.__dict__[function_name]
            try:
                ret = func_ptr.__func__(**kwargs)
            except (AttributeError, np.AxisError):
                ret = None
            return ret

    def _get_data_from_dynasaur_json(self, json_object, data_offsets):
        """

        Args:
          json_object: param data_offsets:
          data_offsets: 

        Returns:

        """
        if JsonConstants.FUNCTION in json_object.keys():  # expected name and params
            function_name = json_object[JsonConstants.FUNCTION][JsonConstants.NAME]
            parameter_def = json_object[JsonConstants.FUNCTION][JsonConstants.PARAM]
            param_dict = {}
            for key in parameter_def.keys():
                if type(parameter_def[key]) is dict:  # step into recursion
                    param_dict[key] = self._get_data_from_dynasaur_json(parameter_def[key], data_offsets)
                else:
                    if key == StandardFunctionsDefinition.FUNCTION_NAME:
                        param_dict[key] = {JsonConstants.NAME: parameter_def[key]}
                        continue
                    param_dict[key] = parameter_def[key]

            procesed_data = self._call_standard_function(function_name, param_dict)
            if not procesed_data is None:
                return procesed_data
            else:
                self._logger.emit(LOGConstants.ERROR[0], "Calculation of " + function_name + " aborted!")

        elif JsonConstants.VALUE in json_object.keys():
            # return np.array(json_object[JsonConstants.VALUE]) * json_object[JsonConstants.UNIT]

            unit = "dimensionless"
            if JsonConstants.UNIT in json_object:
                unit = json_object[JsonConstants.UNIT]

            return np.array(json_object[JsonConstants.VALUE]) * \
                   self._dynasaur_definitions.get_unit_dimension_from_unit(unit=unit)

        elif JsonConstants.TYPE in json_object.keys():
            data_type = json_object[JsonConstants.TYPE]
            return self._data[data_type].get_data_of_defined_json(data_offsets, **json_object)

        else:
            assert False

    def init_plugin_data(self, update):
        """

        Args:
          update: return:

        Returns:

        """
        if self._data is None or update:
            self._data = {data: DataContainer.get_data(data) for data in self._data_requirements}
            for data_name in self._data.keys():
                if self._data[data_name] is None:
                    self._logger.emit(LOGConstants.ERROR[0], data_name + LoggerERROR.print_statements[1] +
                                      ', '.join(sorted([i for i in ObjectConstantsForData.__dict__.keys()
                                                        if i[:1] != '_'])))
                if not self._data[data_name].read_binout_data():
                    self._logger.emit(LOGConstants.WARNING[0], data_name + LoggerWARNING.print_statements[3])

    def _reduce_sample_offset(self, json_object, sample_offsets):
        """

        Args:
          json_object: param data_offsets:
        
        :return sample:
          sample_offsets: 

        Returns:

        """
        self._get_data_from_json_reduce_samples(json_object)
        self._sample_types = list(set(self._sample_types))
        return_sample = []
        for sample in sample_offsets:
            if sample[0] in self._sample_types:
                return_sample.append(sample)
        self._sample_types.clear()
        return return_sample

    def _get_sample_offset(self, dynasaur_json, t_start, t_end):
        """get sample offset defined between start and end time

        Args:
          param_dict: return sample offset:

        Returns:

        """

        sample_offsets = []
        data_types_in_json = []
        self._dynasaur_definitions.get_all_data_types_from_json(d=dynasaur_json, ls=data_types_in_json)
        for key in self._data.keys():
            if key not in data_types_in_json:
                continue

            if key == "VOLUME":
                continue

            if self._data[key].get_interpolated_time() is None:
                return

            if t_start is not None and t_end is not None:
                indices = np.argwhere(
                    (t_start * self._units.time <= self._data[key].get_interpolated_time()) &
                    (self._data[key].get_interpolated_time() <= t_end * self._units.time))
                if len(indices) == 0:
                    self._logger.emit(LOGConstants.ERROR[0],
                                      "Check t_start, which was set to " + str(t_start * self._units.time))
                    return
                if t_start >= t_end:
                    t_end = self._data[key].get_()[-1]
                    self._logger.emit(LOGConstants.ERROR[0],
                                      "End time is smaller or equal as start time! End time set to " + str(t_end))
                    return

            elif t_start is not None and t_end is None:
                indices = np.argwhere(t_start * self._units.time <=
                                      self._data[key].get_interpolated_time())

            elif t_start is None and t_end is not None:
                indices = np.argwhere(self._data[key].get_interpolated_time() <=
                                      t_end * self._units.time)

            else:
                indices = np.array([np.arange(0, len(self._data[key].get_interpolated_time()))]).transpose()

            sample_offsets.append((key, indices[0][0], indices[-1][-1]))

        return sample_offsets

    def _get_data_from_json_reduce_samples(self, json_object):
        """get sample offset defined between start and end time

        Args:
          json_object: return sample offset:

        Returns:

        """
        if JsonConstants.FUNCTION in json_object.keys():  # expected name and params
            parameter_def = json_object[JsonConstants.FUNCTION][JsonConstants.PARAM]

            param_dict = {}
            for key in parameter_def.keys():
                if type(parameter_def[key]) is dict:  # step into recursion
                    param_dict[key] = self._get_data_from_json_reduce_samples(parameter_def[key])
                else:
                    param_dict[key] = parameter_def[key]
        else:  # data to obtain
            if JsonConstants.VALUE in json_object.keys():
                return np.array(json_object[JsonConstants.VALUE]) * self._dynasaur_definitions.get_units().dimensionless
            elif "strain_stress" in json_object.keys():
                self._sample_types.append(json_object[JsonConstants.TYPE])
                return json_object["strain_stress"]
            elif JsonConstants.TYPE in json_object.keys():
                self._sample_types.append(json_object[JsonConstants.TYPE])
                return json_object[JsonConstants.ARRAY]
            else:
                assert False

    def _write_header_and_content_to_csv(self, path, header_info, values):
        """

        :return:
        """
        with open(path, 'w') as csv_file:
            writer = csv.writer(csv_file, delimiter=';', lineterminator='\n')
            t_m = list(zip(*header_info))
            for key in t_m:
                writer.writerow(key)
            t_m = list(zip(*values))
            for key in t_m:
                writer.writerow(key)


class PluginInterface(metaclass=abc.ABCMeta):
    """ """

    @abc.abstractmethod
    def _calculate_and_store_results(self, *args, **kwargs):
        """

        Args:
          param_dict: return:

        Returns:

        """

    @abc.abstractmethod
    def get_defined_calculation_procedures(self):
        """

        Args:

        Returns:

        """

    def calculate(self, param_dict):
        """

        Args:
          param_dict: param to_si
          to_si:  (Default value = False)

        Returns:

        """
        param_dict_data = self._dynasaur_definitions.get_param_dict_from_command(command=param_dict)
        self._calculate_and_store_results(**param_dict_data)

    def get_object_data(self, type_, id_, strain_stress, index, channel, data_offset):
        """

        Args:
          type_: param id:
          strain_stress: param data_offset:
          id_: 
          index: 
          channel: 
          data_offset: 

        Returns:

        """
        # print(self._data)
        # part_ids = self._data[type_]._dynasaur_definitions._objects[id]._parts.keys()
        if type_ == "OBJECT":
            return self._data[type_].get_data_of_defined_json(data_offsets=[(type_, data_offset[0], data_offset[1])],
                                                              type=type_,
                                                              ID=id_,
                                                              strain_stress=strain_stress)

        else:
            return self._data[type_].get_data_of_defined_json(data_offsets=[(type_, data_offset[0], data_offset[1])],
                                                              type=type_,
                                                              ID=id_,
                                                              array=["(" + str(index) + "," + str(channel) + ")"])
