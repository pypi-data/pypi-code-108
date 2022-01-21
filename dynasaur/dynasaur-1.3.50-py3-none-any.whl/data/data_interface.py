import numpy as np
import copy

from ..utils.constants import LOGConstants, JointTypeMapping, ObjectConstantsForData


class BinoutData(object):

    def __init__(self, binout, logger, dynasaur_definitions, name):
        """Initialization/constructor
            1 ) initializes members
    
            2 ) initialize the member required_data_channel_ids. List of all data_channel_ids in the calc_proc.def file ,
                i.e. {"type":"ELEMENT","ID":"id1","array":["(0, axial)"]
                    used to check if channel "axial" is part of type ELEMENT

        Args:

        Returns:

        """

        self._binout = binout
        self._logger = logger
        self._dynasaur_definitions = dynasaur_definitions
        self._name = name
        self._time = None
        self._time_interp = None
        self._data = {}
        self._ids = None
        self._required_data_channel_ids = []

        self._set_required_data_channel_ids()
        self._clean_required_data_channel_ids()

    def get_time(self):
        """getter

        Args:

        Returns:
          np.array: time column vector

        """
        return self._time

    def get_interpolated_time(self):
        """getter

        Args:

        Returns:
          np.array: interpolated time as column vector

        """
        return self._time_interp

    def get_channel_ids_from_object_name(self, object_name):
        """

        Args:
          object_name: type object_name:

        Returns:
          np.array: time

        """
        defined_ids = self._dynasaur_definitions.get_object_ids_from_object_name(object_name, self._name)
        available_ids = self.get_ids()
        # NOTE:
        # using np.intersect1d
        # causes problems if the dynasaur Object contains the same id multiple times. i.e. defined_ids = [100, 100]
        # channel_ids = np.intersect1d(defined_ids, available_ids).
        # order of defined_ids should be kept as well
        #
        channel_ids = [defined_id for defined_id in defined_ids if defined_id in available_ids]
        return channel_ids

    def get_ids(self):
        """getter

        Args:

        Returns:
          np.array: ids as numpy array (np.uint32)

        """
        return self._ids # .astype(np.uint32)

    def _interp_time(self, time_):
        """method to interpolate the given time to decimal values

        Args:
          time_: type np.array:

        Returns:
          np.array as column vector: interpolated time

        """

        time_si = time_.to_base_units()
        end_time_ = np.round(time_si[-1] - time_si[0], 3)

        # check if the time_diff is already constant:
        # https://stackoverflow.com/questions/3844801/check-if-all-elements-in-a-list-are-identical
        # https://numpy.org/doc/stable/reference/generated/numpy.allclose.html
        time_diff = np.diff(time_)
        if np.allclose(time_diff, np.tile([time_diff[0].magnitude], len(time_diff)) * self._dynasaur_definitions.get_units().time):
            return time_

        time_interp = np.linspace(time_[0], end_time_, len(time_))
        return time_interp

    def _set_required_data_channel_ids(self):
        """Function to initialize member self._required_data_channel_ids
          --> extracts the required channel_types from the calc_proc.def  (_criteria, _data_vis)
          i.e. calc_proc.def : "array": ["(0, time)"],
          self._required_data_channel_ids would be appended ["(0, time)"]

        Args:

        Returns:

        """
        for def_key in self._dynasaur_definitions.__dict__:
            if def_key == "_criteria":
                for key in self._dynasaur_definitions.__dict__[def_key].keys():
                    self._get_data_from_json(self._dynasaur_definitions.__dict__[def_key][key])
            if def_key == "_data_vis":
                for key in self._dynasaur_definitions.__dict__[def_key].keys():
                    self._get_data_from_json(self._dynasaur_definitions.__dict__[def_key][key]["x"])
                    self._get_data_from_json(self._dynasaur_definitions.__dict__[def_key][key]["y"])

    def _get_data_from_json(self, json_object):
        """recursive method to extract array
        
        inner part of the json object can be :
            * value
            * strain_stress
            * array

        Args:
          json_object: 

        Returns:

        """
        if 'function' in json_object.keys():  # expected name and params
            parameter_def = json_object['function']['param']
            for key in parameter_def.keys():
                if type(parameter_def[key]) is dict:  # step into recursion
                    self._get_data_from_json(parameter_def[key])

        else:  # data to obtain
            if "value" in json_object.keys():
                return
            elif "strain_stress" in json_object.keys():
                return
            elif "array" in json_object.keys():
                self._required_data_channel_ids.append(json_object['array'])
                return
            else:
                assert False

    def _clean_required_data_channel_ids(self):
        """clean required_data_channel_ids types, stripes each entry in self._required_data_channel_ids
        calc_proc.def : ["(0, axial)"] --> ["axial"]
        
        self._required_data_channel_ids is a casted to a set

        Args:

        Returns:
          None

        """
        _list_temp = []
        for array_temp in self._required_data_channel_ids:
            for type in array_temp:
                type = type.replace("(", "")
                type = type.replace(")", "")
                first_type = type.split(",")[0]
                second_type = type.split(",")[1]
                second_type = second_type.replace(" ", "")
                if first_type == "0" and second_type != "0":
                    if second_type in self.DATA_CHANNEL_TYPES:
                        _list_temp.append(second_type)
                elif first_type != "0" and second_type == '0':
                    if first_type in self.DATA_CHANNEL_TYPES:
                        _list_temp.append(first_type)
                else:
                    if first_type in self.DATA_CHANNEL_TYPES:
                        _list_temp.append(first_type)
                    if second_type in self.DATA_CHANNEL_TYPES:
                        _list_temp.append(second_type)
        self._required_data_channel_ids = set(_list_temp)

    def _get_subdatatypes_to_reach_binout_data(self, ls, ls_subdatatypes):
        """Recursively traverses binout data and stores the required
        subdatatypes to access data in  ls_subdatatypes
        
        i.e. binout.read("bndout", "velocity", "rigidbody") --> ["ids", "x_force"]
          ls_subdatatypes --> [["bndout", "velocity", "rigidbody"]]

        Args:
          ls: list of subdatatypes
          ls_subdatatypes: list of lists of subdatatyoes

        Returns:
          None

        """
        elements = self._binout.read(*ls)
        if self.__class__.ids_name in elements:
            ls_subdatatypes.append(ls)
            return

        for elem in elements:
            ls_copy = copy.copy(ls)
            ls_copy.extend([elem])
            self._get_subdatatypes_to_reach_binout_data(ls_copy, ls_subdatatypes)

    def _read_data_channels(self, subdatatypes=[]):
        """extracts the data_channels (conjunction of self.__class__.DATA_CHANNEL_TYPES and available in binout) and
        stores the interpolated data in self._data

        Args:
          subdatatypes(list, optional): subdatatypes to access data (Default value = [])

        Returns:
          None:: None:

        """
        data = {}
        args_ = subdatatypes

        array = []
        insert_indices = np.array([], dtype=int)
        ind = np.array([], dtype=int)

        args_temp = args_ + [self.ids_name]
        ids = self._binout.read(*args_temp)

        len_indices = 0

        # check if elements have been destroyed
        if len(ids) == 0:
            return

        if isinstance(ids[0], tuple):
            for i in range(0, ids.shape[0]):
                logic_intersection = np.in1d(ids[0], ids[i])
                array.append(np.where(np.logical_not(logic_intersection)))
                indices = np.where(np.logical_not(logic_intersection))
                if indices[0].size != 0:
                    insert_indices = np.append(insert_indices, indices[0] + len(ids[0]) * i - np.arange(len_indices,
                                                                                                        len_indices + len(
                                                                                                            indices[
                                                                                                                0])))
                    ind = np.append(ind, indices[0] + len(ids[0]) * i)
                    len_indices += len(indices[0])

        available_channels = [value for value in self.__class__.DATA_CHANNEL_TYPES if
                              value in self._binout.read(*args_)]

        for key in available_channels:
            args_temp = args_ + [key]
            type_data = self._binout.read(*args_temp)

            if type_data.shape[0] == 0:
                continue

            # check if all ids "survived"
            if len(type_data.shape) == 1:
                if not isinstance(type_data[0], tuple):  # case if only one data point available
                    type_data = type_data[:self._time_interp.shape[0]].reshape(-1, 1)
            else:
                type_data = type_data[:self._time_interp.shape[0], :]

            if len(insert_indices) != 0:  # Deleted elements should only be possible for elements
                assert (self._name == "elout")
                flatted_data_array = list(sum(type_data, ()))

                zeros = np.zeros(len(insert_indices))
                a = np.insert(flatted_data_array, insert_indices, zeros).reshape((-1, 1)),

                # shape: [time]:[element id, part id, integration point]:[lambda1, lambda2, lambda3]
                #       TODO
                # e.g.: 7 time steps, 3 parts, each part 2 elements with 2 integration points, 3 eigenvalues
                # e.g.: results in shape of (7, 12, 3)
                # data_tensor = a.reshape(time_step_size, int(a.shape[0] / time_step_size), w_stress.shape[1])
                type_data = np.reshape(a[0], (self._time_interp.shape[0], -1))

            # type_data = np.reshape(type_data, (time_interp.shape[0], -1))
            data_interp = np.zeros(shape=(self._time_interp.shape[0], type_data.shape[1]))

            for i in range(type_data.shape[1]):
                data_to_consider = min(self._time_interp.shape[0], len(type_data[:, i]))
                data_interp[:, i] = np.interp(self._time_interp.magnitude,
                                              self._time.magnitude[:data_to_consider],
                                              type_data[:data_to_consider, i])
            data[key] = data_interp

        self._data = {**self._data, **data}

    def __init_data__(self, subdatatypes=[]):
        """
        initialize members:
            * self._time
            * self._time_interp
            * self._ids

        :param subdatatypes: subdatatypes to access data in lasso.dyna.Binout
        :type subdatatypes:  list identifiers i.e. ["bndout", "velocity", "rigidbody"]]
        :returns: None
        :rtype: None
        """

        assert self._ids is None and self._time is None and self._time_interp is None

        self._time = self._binout.read(*subdatatypes, 'time').flatten() * self._dynasaur_definitions.get_units().time
        self._time_interp = self._interp_time(self._time)
        # TODO: Check if data is not there index out of range -> resulting crash
        self._ids = np.array(self._binout.read(*subdatatypes, self.__class__.ids_name))
        if len(self._ids.shape) > 1:
            self._ids = self._ids[0]

        self._read_data_channels(subdatatypes=subdatatypes)

        assert len(self._ids.shape) == 1

    def read_binout_data(self):
        """called from plugin classes (Controller) to initialize all BinoutData objects of the DataContainer (i.e. Glstat)
        
        __init_data__()
        * self._time
        * self._time_interp
        * self._ids
        
        read in the data channels as defined in __class__.DATA_CHANNEL_TYPES
        _read_data_channels()

        Args:

        Returns:
          boolean value: success on reading (True when data was read in, False when no data available)

        """
        # data already read
        if self._ids is not None:
            return True

        # i.e.  no rcforc in binout

        if isinstance(self._name, str):
            name = self._name
            display_name = self._name
        else:
            name = str(self._name[0])
            display_name = " ".join(self._name)
        if name not in self._binout.read():
            return False

        # data read
        self._logger.emit(LOGConstants.READ_BINOUT[0], 'read ' + display_name + ' data ...')

        ls = self._name if isinstance(self._name, list) else [self._name]
        ls_subdatatypes = []
        self._get_subdatatypes_to_reach_binout_data(ls, ls_subdatatypes)

        #TODO: check ls_subdatatype does the list have more items??

        # go through the extracted subdatatypes and initialize what has been found
        #   cases in where ids are in multiple subtrees are currently not supported (test case jntforces)
        for subdatatypes in ls_subdatatypes:
            data_channel_ids = self._binout.read(*subdatatypes)
            negative_intersection = self._get_negative_intersection(data_channel_ids)
            if len(negative_intersection):
                self._logger.emit(LOGConstants.WARNING[0], "binout keys: " + " ".join(data_channel_ids))
                self._logger.emit(LOGConstants.WARNING[0],
                                  "Your definition file tries to access the following undefined keys : "
                                  + " ".join(negative_intersection))

            self.__init_data__(subdatatypes)

        self._logger.emit(LOGConstants.READ_BINOUT[0], "done reading " + display_name + "!")
        if isinstance(self._name, list):
            self._name = self._name[1]
        return True

    def _get_negative_intersection(self, data_channel_ids):
        """compares the required_data_channel_ids (as defined in the calc_proc.def) with the available
        data_channel_ids of the given binout. returns a list of missing data_channel_ids

        Args:
          data_channel_ids: type data_channel_ids:

        Returns:
          list: negative_intersection: list of missing data_channel_ids

        """
        # only necessary functions
        negative_intersection = [val for val in self._required_data_channel_ids if val not in data_channel_ids]
        return negative_intersection

    def get_data_of_defined_json(self, data_offsets, type: str, ID: str, array: list, **kwargs):
        """

        Args:
            data_offsets: contains the object type and the first and last time dependent index that should be
                       considered e.g. [('NODE', 0, 3000)]

            type: dynasaur DataType as defined in utils.constants.DataTypeMapping (OBJECT, NODE, ...)

            ID:   Object Identifier as defined in the object.def file

            array: list of strings, consisting of  the data index in the objects definition file and the channel
                    type e.g.  ["(0, internal_energy)"]


        Returns:
          data array between data offset and date delta t

        """
        ids = self.get_channel_ids_from_object_name(object_name=ID)

        if len(ids) == 0:
            self._logger.emit(LOGConstants.ERROR[0], "Missing ID in binary input data, identifier: " + ID)
            return

        data_offset = 0
        data_delta_t = -1
        for (t, offset, delta_t) in data_offsets:
            if t == type:
                data_offset = offset
                data_delta_t = delta_t

        array_definition = array

        if array_definition[0].split(',')[0].strip(' (') == "all":
            converted_tuples = [(index, array_definition[0].split(',')[1].strip(' )')) for index, id_ in
                                enumerate(ids)]
        else:
            # processing data array
            converted_tuples = [(int(tuple_string.split(',')[0].strip(' (')), tuple_string.split(',')[1].strip(' )'))
                                for tuple_string
                                in array_definition]

        data_array = None
        for tpl in converted_tuples:
            if type == ObjectConstantsForData.JOINT_TYPE:
                tpl = list(tpl)
                tpl[1] = JointTypeMapping.lspp_to_dynasaur_mapping(tpl[1])
                tpl = tuple(tpl)
            d = copy.copy(self.get_measurement_channel(id_=ids[tpl[0]], channel_name=tpl[1]))
            if len(d) == 0:
                return np.NaN
            if tpl[1] == "time":
                d -= d[data_offset, 0]
            data_array = d[data_offset:data_delta_t] if data_array is None else np.append(data_array,
                                                                                          d[data_offset:data_delta_t],
                                                                                          axis=1)

        return data_array

    def _get_unit_dimension_from_channel_name(self, channel_name):
        """

        :param channel_name:
        :return:
        """

        dim_less = self._dynasaur_definitions.get_units().dimensionless
        t = self._dynasaur_definitions.get_units().time
        m = self._dynasaur_definitions.get_units().mass
        l = self._dynasaur_definitions.get_units().length
        angle = self._dynasaur_definitions.get_units().angle

        force = m * l / (t**2)
        moment = force * l
        energy = force * l
        area = l**2
        acceleration = l/(t**2)
        velocity = l/t

        r_velocity = angle/t
        r_acceleration = angle/(t**2)

        if "forc" in channel_name or "axial" in channel_name or "radial" in channel_name or "shear" in channel_name:
            return force

        elif "moment" in channel_name:
            return moment

        elif "energy" in channel_name:
            return energy

        elif "area" in channel_name:
            return area

        # mind order of if
        elif "rx_acceleration" in channel_name or "ry_acceleration" in channel_name or "rz_acceleration" in channel_name:
            return r_acceleration

        elif "acceleration" in channel_name:
            return acceleration

        # mind order of if
        elif "rx_velocity" in channel_name or "ry_velocity" in channel_name or "rz_velocity" in channel_name:
            return r_velocity

        elif "velocity" in channel_name:
            return velocity

        # mind order of if
        elif "rx_displacement" in channel_name or "ry_displacement" in channel_name or "rz_displacement" in channel_name:
            return angle

        elif "displacement" in channel_name:
            return l

        elif "ring_slip" in channel_name:
            return l

        elif "position" in channel_name:
            return l

        elif "coordinate" in channel_name:
            return l

        elif "length" in channel_name:
            return l

        elif "time" in channel_name:
            return t

        elif "mass" in channel_name:
            return m

        else:
            return self._dynasaur_definitions.get_units().dimensionless

    def get_measurement_channel(self, id_, channel_name):
        """Returns the interpolated measurement_channel, defined through
          - id_             (identifier in ids.def files)
          - channel_name    ("array" in calc_proc.def )  Aim: Constant time interval for filter operations.

        Args:
          id_: type id_: str_ or int:
          channel_name: type channel_name: str

        Returns:
          np.array: the interpolated channel

        """

        unit = self._get_unit_dimension_from_channel_name(channel_name)

        if channel_name == 'time':
            return self._time_interp.reshape(-1, 1)

        if np.issubdtype(self._ids.dtype, np.number):
            data_index = np.where(int(id_) == self._ids)[0]
        else:  # madymo case ... ids are not numeric
            data_index = np.where(id_ == self._ids)[0]

        if len(data_index) == 0:
            self._logger.emit(LOGConstants.ERROR[0], 'ID ' + str(id_) + ' not in binout')
            return []

        self._logger.emit(LOGConstants.DATA_PLUGIN[0], 'read id ' + str(id_) + ' from channel name: ' + channel_name)
        assert (len(data_index) >= 1)

        if channel_name not in self._data.keys():
            self._logger.emit(LOGConstants.ERROR[0], str(id_) + ' has no data with the identifier : ' + channel_name)
            return []

        interpolated_channel = self._data[channel_name][:, data_index]

        return interpolated_channel.reshape(-1, len(data_index)) * unit
