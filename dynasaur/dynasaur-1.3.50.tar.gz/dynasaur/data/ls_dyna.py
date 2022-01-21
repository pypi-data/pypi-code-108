from numpy.lib.stride_tricks import as_strided
from enum import Enum

import numpy as np
import time as t
import copy
import lasso


from ..utils.constants import LOGConstants
from ..data.data_interface import BinoutData


class DEForc(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_force', 'y_force', 'z_force', 'displacement', 'resultant_force']
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'deforc')



class RBDout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_force', 'y_force', 'z_force', 'displacement', 'resultant_force']
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'rbdout')


class BDNout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_force', 'y_force', 'z_force', 'displacement', 'resultant_force']
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'bdnout')


class Disbout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['r_dis_axial', 'moment_s', 'rslt_nt', 'r_dis_nt', 't_dir_y', 'axial_rot',
                          's_dir_y', 'r_dis_ns', 'matid', 's_dir_x', 'torsion', 'rslt_ns', 'axial_z', 'mtype',
                          't_dir_x', 'rot_s', 'axial_y', 's_dir_z', 'rot_t', 'rslt_axial', 'moment_t', 'axial_x',
                          't_dir_z']
    ids_name = "nelb"

    def __init__(self, binout, logger, dynasaur_definitions):
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'disbout')


class PartDisbout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['r_dis_axial', 'moment_s', 'rslt_nt', 'r_dis_nt', 't_dir_y', 'axial_rot',
                          's_dir_y', 'r_dis_ns', 'matid', 's_dir_x', 'torsion', 'rslt_ns', 'axial_z', 'mtype',
                          't_dir_x', 'rot_s', 'axial_y', 's_dir_z', 'rot_t', 'rslt_axial', 'moment_t', 'axial_x',
                          't_dir_z']
    ids_name = "nelb"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'disbout')

    def get_element_ids_from_part_ids(self, part_ids):
        """

        Args:
          part_ids: 

        Returns:

        """
        part_to_element_mapping = self._binout.read(self._name, "matid")
        assert len(part_to_element_mapping.shape) == 2
        d = {}
        for part_id in part_ids:
            elments_idx_where_part = np.where(self._binout.read(self._name, "matid")[0] == part_id)[0]
            self._binout.read(self._name, )
            element_ids = self._binout.read(self._name, self.ids_name)[elments_idx_where_part]
            d[part_id] = element_ids

        return d

    def get_data_of_defined_json(self, data_offsets, type, ID, array, **kwargs):
        """

        Args:
            data_offsets: contains the object type and the first and last time dependent index that should be
                       considered e.g. [('NODE', 0, 3000)]

            type: dynasaur DataType as defined in utils.constants.DataTypeMapping (OBJECT, NODE, ...)

            ID:   Object Identifier as defined in the object.def file

            array: list of strings, consisting of  the data index in the objects definition file and the channel
                    type e.g.  ["(0, internal_energy)"]

        Returns:
          data array between data offset and delta t

        """

        part_ids = self._dynasaur_definitions.get_object_ids_from_object_name(ID, self._name)
        part_ids_to_element_ids = self.get_element_ids_from_part_ids(part_ids)

        assert (len(part_ids_to_element_ids) != 0)
        array_definition = array

        if array_definition[0].split(',')[0].strip(' (') == "all":
            converted_tuples = [(index, array_definition[0].split(',')[1].strip(' )')) for index, id_ in
                                enumerate("ids")]
        else:
            # processing data array
            converted_tuples = [(int(tuple_string.split(',')[0].strip(' (')), tuple_string.split(',')[1].strip(' )'))
                                for tuple_string
                                in array_definition]

        data_offset = 0
        data_delta_t = -1
        for (t, offset, delta_t) in data_offsets:
            if t == type:
                data_offset = offset
                data_delta_t = delta_t

        data_array = None
        for tpl in converted_tuples:
            for element_id in part_ids_to_element_ids[part_ids[tpl[0]]]:
                d = copy.copy(self.get_measurement_channel(id_=element_id, channel_name=tpl[1]))
                if tpl[1] == "time":
                    d -= d[data_offset - 1]
                data_array = d[data_offset:data_delta_t] if data_array is None else np.append(data_array, d[data_offset:data_delta_t], axis=1)

        return data_array[data_offset:data_delta_t]


class EloutIndex(Enum):
    """ """
    STRAIN = 0
    STRESS = 1

    INDEX = 2
    DATA = 3

    SHELL = 4
    SOLID = 5
    BEAM = 6

    @staticmethod
    def translate_element(name):
        """Translate element with given name

        Args:
          name: 

        Returns:

        """
        name = name.lower()
        if name == "shell":
            return EloutIndex.SHELL
        if name == "solid":
            return EloutIndex.SOLID
        if name == "beam":
            return EloutIndex.BEAM

    @staticmethod
    def translate_strain_stress(name):
        """Translate strain or stress with given name

        Args:
          name: 

        Returns:

        """
        name = name.lower()
        if name == "strain":
            return EloutIndex.STRAIN
        if name == "stress":
            return EloutIndex.STRESS


class EloutObject(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = []
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions, volume_path=None):
        """

        :param binout:
        :param logger:
        :param dynasaur_definitions:
        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'elout')
        self._data_mapping_part_id_to_element_type = {}
        self._data_mapping_element_id_to_part_id = {}
        self._data_mapping_part_id_to_element_ids = {}
        self._data = {}

        self._file_data_mapping_element_id_to_volume = None
        self._data_mapping_part_id_to_volume = {}
        self._data_mapping_part_id_to_element_id_to_volume = {}
        self._volume_path = volume_path

        self._time = None

    def get_interpolated_time(self):
        """:return: no data interpolation for stress and strain types"""
        return self._time

    def get_data_of_defined_json(self, data_offsets: list, type: str, ID: str, strain_stress: str,
                                 strain_stress_type: str = None, **kwargs):
        """
        overridden get_data_of_defined_json function.

        Args:
            data_offsets: contains the object type and the first and last time dependent index that should be
                       considered e.g. [('OBJECT', 0, 3000)]

            type: dynasaur DataType as defined in utils.constants.DataTypeMapping (OBJECT, NODE, ...)

            ID:   Object Identifier as defined in the object.def file

            strain_stress:  "Strain" or "Stress"

            strain_stress_type: "green_lagrange"



        Returns:
            object_data

        """

        assert(self._dynasaur_definitions.is_object_defined(ID))
        assert(strain_stress in ["Strain", "Stress"])
        assert(strain_stress_type in [None, "Green_Lagrange"])

        strain_stress_idx = EloutIndex.translate_strain_stress(strain_stress)

        part_ids = []

        element_count = 0

        part_data = {}
        part_index = {}
        element_type = None
        part_volume = None
        el_by_part_id_el_id = None

        for (dynasaur_data_type, offset, delta_t) in data_offsets:
            if dynasaur_data_type == type:
                data_offset = offset
                data_delta_t = delta_t

        def log_to_green_lagrange_strain(log_strain):
            """
                Takes the principle logarithmic strains and returns the principle Green-Lagrange strains

                Args:
                    log_strain: principle strains (time_steps x object_elems x 3)

                Returns: Converted Green Lagrange strain
            """

            return (np.exp(log_strain) ** 2 - 1) / 2

        time_step_indices = list(range(data_offset, data_delta_t))

        if self._dynasaur_definitions.is_object_defined(tmp_object=ID):

            # check if the defined object consists of element_sets
            if self._dynasaur_definitions.is_object_element_set(tmp_object=ID):
                element_sets = self._dynasaur_definitions.get_object_element_set(tmp_object=ID)

                for element_set_id, element_set in enumerate(element_sets):
                    part_index[element_set_id] = []
                    part_data[element_set_id] = []
                    for element_id in element_set:
                        part_id = self.get_part_id_by_element_ids(element_id, strain_stress_idx)
                        if part_id is None:
                            continue

                        index, data = self.get_part_data(strain_stress_idx, part_id, element_id=element_id,
                                                         time_step_indices=time_step_indices)

                        if strain_stress_type == "Green_Lagrange":
                            data = log_to_green_lagrange_strain(data)

                        if len(part_data[element_set_id]) == 0:
                            part_data[element_set_id] = data
                        else:
                            part_data[element_set_id] = np.hstack((part_data[element_set_id], data))

                        if len(part_index[element_set_id]) == 0:
                            part_index[element_set_id] = index
                        else:
                            part_index[element_set_id] = np.vstack((part_index[element_set_id], index))

                        element_ids = self.get_element_ids_of_part_data(index)
                        # print(", ".join([str(i) for i in element_ids]))
                        element_count += len(element_ids)
                        element_type = self.get_element_type_from_part_id(part_id, strain_stress_idx)

                        part_volume = self.get_part_volume_by_part_ID()
                        el_by_part_id_el_id = self.get_element_volume_by_part_id_and_element_id()

                part_ids = part_data.keys()

            # object defined through parts
            else:
                part_ids = self.get_part_ids_by_object_name(ID, strain_stress_idx)
                part_ids_defined = self._dynasaur_definitions.get_parts_of_defined_object(ID)
                if len(part_ids) != len(part_ids_defined):
                    unresolved_part_ids = [part_id_defined for part_id_defined in
                                           part_ids_defined if part_id_defined not in part_ids]

                    self._logger.emit(LOGConstants.WARNING[0],
                                      "Unresolved parts in your object definition with ID " + ID + " : " + ", ".join([str(i) for i in unresolved_part_ids])
                                      + ". Available parts are : " + ", ".join([str(i)for i in self._get_part_ids(strain_stress_idx)]))

                for part_id in part_ids:
                    index, data = self.get_part_data(strain_stress_idx, part_id, time_step_indices=time_step_indices)

                    if strain_stress_type == "Green_Lagrange":
                        data = log_to_green_lagrange_strain(data)

                    part_data[part_id] = data
                    part_index[part_id] = index

                    element_ids = self.get_element_ids_of_part_data(index)
                    # print(", ".join([str(i) for i in element_ids]))
                    element_count += len(element_ids)
                    element_type = self.get_element_type_from_part_id(part_id, strain_stress_idx)

                    # TODO: check if volume is defined
                    part_volume = self.get_part_volume_by_part_ID()
                    el_by_part_id_el_id = self.get_element_volume_by_part_id_and_element_id()

        else:
            self._logger.emit(LOGConstants.WARNING[0],
                              "OBJECT " + ID + " is not defined in your object definition file")

        return {"part_ids": part_ids,
                "part_data": part_data,
                "part_idx": part_index,
                "time_step_indices": time_step_indices,
                "element_type": element_type,
                "part_value": part_volume,
                "el_by_part_id_el_id": el_by_part_id_el_id,
                "time": self.get_interpolated_time()[time_step_indices]}

    def _read_volume_data_from_file_volume(self, path_to_volume):
        """:return:

        Args:
          path_to_volume: 

        Returns:

        """
        if self._file_data_mapping_element_id_to_volume is not None:
            return True

        if self._volume_path is None:
            return False

        self._logger.emit(LOGConstants.READ_VOLUME[0], "read volume data")

        try:
            tmp_file = open(self._volume_path)
        except:
            self._logger.emit(LOGConstants.ERROR[0], "volume: could not read Volume.def file!")
            return False

        tmp_data = np.array([line.split() for line in tmp_file.readlines() if line[0].isdigit()])
        self._file_data_mapping_element_id_to_volume = {int(key): float(value) for (key, value) in tmp_data}

        self._logger.emit(LOGConstants.READ_VOLUME[0], "done reading volume!")
        tmp_file.close()
        return True

    def _init_data_volume(self, data_mapping_part_id_to_element_ids):
        """

        Args:
          data_mapping_part_id_to_element_ids: return:

        Returns:

        """
        if len(self._data_mapping_part_id_to_volume) != 0:
            return True

        error_part_ids = []
        for part_id, elements in data_mapping_part_id_to_element_ids.items():
            try:
                part_volumes = {element_id: self._file_data_mapping_element_id_to_volume[element_id] for element_id in
                                elements}
                self._data_mapping_part_id_to_volume[part_id] = sum(part_volumes.values())
                self._data_mapping_part_id_to_element_id_to_volume[part_id] = part_volumes
            except:
                error_part_ids.append(part_id)

        if len(error_part_ids) != 0:
            objects = self._dynasaur_definitions.get_defined_objects_containing_parts(error_part_ids)
            self._logger.emit(LOGConstants.READ_VOLUME[0], "Warning: could not assign volume for parts (" +
                              ", ".join(map(str, error_part_ids)) + ") of objects (" + ", ".join(objects) + ")")

        return True

    def get_part_volume_by_part_ID(self):
        """

        Args:
          part_id: return:

        Returns:

        """
        return self._data_mapping_part_id_to_volume

    def get_element_volume_by_part_id_and_element_id(self):
        """

        Args:
          part_id: param element_id:

        Returns:

        """
        return self._data_mapping_part_id_to_element_id_to_volume

    def _append_data(self, index_matrix, data_tensor, strain_stress_type, element_type):
        """

        Args:
          index_matrix: param data_tensor:
          strain_stress_type: param element_type:
          data_tensor: 
          element_type: 

        Returns:

        """
        if strain_stress_type not in self._data:
            self._data[strain_stress_type] = {}

        self._data[strain_stress_type][element_type] = {}
        # indexing: [element id, part id, integration point]
        self._data[strain_stress_type][element_type][EloutIndex.INDEX] = index_matrix

        # shape: [time]:[element id, part id, integration point]:[lambda1, lambda2, lambda3]
        #
        # e.g.: 7 time steps, 3 parts, each part 2 elements with 2 integration points, 3 eigenvalues
        # e.g.: results in shape of (7, 12, 3)
        self._data[strain_stress_type][element_type][EloutIndex.DATA] = data_tensor

    def _append_mapping_part_id_to_element_type(self, index_matrix, strain_stress_type, element_type):
        """

        Args:
          index_matrix: param strain_stress_type:
          element_type: return:
          strain_stress_type: 

        Returns:

        """
        if strain_stress_type not in self._data_mapping_part_id_to_element_type:
            self._data_mapping_part_id_to_element_type[strain_stress_type] = {}

        unique_part_ids = np.unique(index_matrix[:, 1])
        for part_id in unique_part_ids:
            if part_id not in self._data_mapping_part_id_to_element_type[strain_stress_type]:
                self._data_mapping_part_id_to_element_type[strain_stress_type][part_id] = element_type
            else:
                self._logger.emit(LOGConstants.ERROR[0], "elout: part consists of multiple element types")
                self._logger.emit(LOGConstants.ERROR[0], "elout: could not read")
                self._data = {}

    def _append_mapping_element_id_to_part_id(self, index_matrix, strain_stress_type, elout_elem):
        """

        Args:
          index_matrix: param strain_stress_type:
          elout_elem: return:
          strain_stress_type: 

        Returns:

        """
        if strain_stress_type not in self._data_mapping_element_id_to_part_id:
            self._data_mapping_element_id_to_part_id[strain_stress_type] = {}

        # elout_elem can be solid, shell or beam ...
        if elout_elem not in self._data_mapping_element_id_to_part_id[strain_stress_type]:
            self._data_mapping_element_id_to_part_id[strain_stress_type][elout_elem] = {}

        # TODO: find a faster method to filter unique element ids paired with part ids
        abc = {tuple(row) for row in index_matrix[:, [0, 1]]}
        unique_element_part_tuple = np.vstack(tuple({tuple(row) for row in index_matrix[:, [0, 1]]}))
        for element_part_tuple in unique_element_part_tuple:
            if element_part_tuple[0] not in self._data_mapping_element_id_to_part_id[strain_stress_type][elout_elem]:
                self._data_mapping_element_id_to_part_id[strain_stress_type][elout_elem][element_part_tuple[0]] = \
                    element_part_tuple[1]
            else:
                self._logger.emit(LOGConstants.ERROR[0], "elout: one element is in multiple parts!")
                self._logger.emit(LOGConstants.ERROR[0], "elout: could not be read")
                self._data = {}

    def _append_mapping_part_id_to_element_ids(self, strain_stress_type):
        """

        Args:
          strain_stress_type: return:

        Returns:

        """
        if strain_stress_type not in self._data_mapping_element_id_to_part_id:
            return

        if strain_stress_type not in self._data_mapping_part_id_to_element_ids:
            self._data_mapping_part_id_to_element_ids[strain_stress_type] = {}

        for elout_elem in self._data_mapping_element_id_to_part_id[strain_stress_type]:
            for element_id in self._data_mapping_element_id_to_part_id[strain_stress_type][elout_elem]:
                part_id = self._data_mapping_element_id_to_part_id[strain_stress_type][elout_elem][element_id]
                if part_id not in self._data_mapping_part_id_to_element_ids[strain_stress_type]:
                    self._data_mapping_part_id_to_element_ids[strain_stress_type][part_id] = []
                self._data_mapping_part_id_to_element_ids[strain_stress_type][part_id].append(element_id)

    def _concatenated_ranges(self, ranges_list):
        """

        Args:
          ranges_list: return:

        Returns:

        """
        ranges_list = np.array(ranges_list, copy=False)
        base_range = np.arange(1, ranges_list.max() + 1)
        base_range = as_strided(base_range,
                                shape=ranges_list.shape + base_range.shape,
                                strides=(0,) + base_range.strides)
        return base_range[base_range <= ranges_list[:, None]]

    def _get_data(self, part_id, strain_stress_type):
        """

        Args:
          part_id: param strain_stress_type:
          strain_stress_type: 

        Returns:

        """
        if part_id not in self._data_mapping_part_id_to_element_type[strain_stress_type]:
            return None

        element_type = self._data_mapping_part_id_to_element_type[strain_stress_type][part_id]
        return self._data[strain_stress_type][element_type]

    def _get_all_part_ids(self):
        """:return:"""
        return np.unique([y for x in [list(self._data_mapping_part_id_to_element_type[vals].keys()) for vals in
                                      self._data_mapping_part_id_to_element_type] for y in x])

    def _get_part_ids(self, strain_stress_type):
        """

        Args:
          strain_stress_type: return:

        Returns:

        """
        if strain_stress_type not in self._data_mapping_part_id_to_element_type:
            return []
        return list(self._data_mapping_part_id_to_element_type[strain_stress_type].keys())

    def _get_elout_data_and_extend(self, elout_elem, name, extendable_indices):
        """get the data from binout and extend the given indices with dummy values

        Args:
          elout_elem: param name:
          extendable_indices: return:
          name: 

        Returns:

        """
        if extendable_indices.size == 0:
            return self._binout.read("elout", elout_elem, name).reshape((-1, 1))

        # merge lower and upper integration points for
        if name.startswith("eps_") and elout_elem == "shell":
            # flatted_data_array = np.list(sum(self._binout.read("elout", elout_elem, name),()))
            # list(sum(self._binout.read("elout", elout_elem, name),()))
            lower = list(sum(self._binout.read("elout", elout_elem, "lower_" + name), ()))
            upper = list(sum(self._binout.read("elout", elout_elem, "upper_" + name), ()))
            nr_elements = len(lower)
            ind_array = np.arange(1, nr_elements + 1)
            flatted_data_array = np.insert(lower, ind_array, upper)
        else:
            flatted_data_array = list(sum(self._binout.read("elout", elout_elem, name), ()))

        zeros = np.zeros(len(extendable_indices))

        a = np.insert(flatted_data_array, extendable_indices, zeros).reshape((-1, 1)),

        return a[0]

    def _info_matrix(self, elout_elem, time, what):
        """duplicate all entries of first time entry.
            part id, integration points, element id

        Args:
          elout_elem: 
          time: 
          what: 

        Returns:

        """

        mat = []
        ids = []
        ipts = []
        if (elout_elem == "shell" or elout_elem == "beam") and what == "stress":
            # ok
            nip = np.tile(self._binout.read(self._name, elout_elem, 'nip')[0], time.shape[0]).flatten()
            if len(nip) != 0:
                mat = np.repeat(np.tile(self._binout.read(self._name, elout_elem, 'mat')[0], time.shape[0]).flatten(),
                                nip).reshape((-1, 1))
                ipts = self._concatenated_ranges(nip).reshape(-1, 1)
                ids = np.repeat(np.tile(self._binout.read(self._name, elout_elem, 'ids')[0], time.shape[0]).flatten(),
                                nip).reshape((-1, 1))

        elif elout_elem == "shell" and what == "strain":
            # ok
            nr_elements = time.shape[0] if isinstance(self._binout.read(self._name, elout_elem, 'ids')[0],
                                                      np.intp) else len(
                self._binout.read(self._name, elout_elem, 'ids')[0]) * time.shape[0]
            rep_strain = np.repeat([2], nr_elements, axis=0)
            ids = np.repeat(np.tile(self._binout.read(self._name, elout_elem, 'ids')[0], time.shape[0]).flatten(),
                            rep_strain).reshape((-1, 1))
            mat = np.repeat(np.tile(self._binout.read(self._name, elout_elem, 'mat')[0], time.shape[0]).flatten(),
                            rep_strain).reshape((-1, 1))
            ipts = np.repeat([[1, 2]], nr_elements, axis=0).reshape(-1, 1)

        elif elout_elem == "solid":
            # ok
            mat = np.tile(self._binout.read(self._name, elout_elem, 'mtype')[0], time.shape[0]).flatten().reshape(
                -1, 1)
            ipts = np.ones(mat.size).reshape(-1, 1)
            ids = np.tile(self._binout.read(self._name, elout_elem, 'ids')[0], time.shape[0]).flatten().reshape(-1,
                                                                                                                1)

        if len(mat) == 0 or len(ids) == 0 or len(ipts) == 0:
            self._logger.emit(LOGConstants.READ_BINOUT[0], "nothing to extract")
            return None

        return (np.concatenate((ids, mat, ipts), axis=1)).astype(int)

    def _indices_of_destroyed_elements(self, elout_elem, type_):
        """indices list of destroyed elements over time
        used to insert dummy values [used for padding to full sized matrix
            -> meaning, each element is available over the entire time]
        
        Functionality:
           in case elements are the destroyed during the simulation
           ids = self._binout.read(self._name, elout_elem, 'ids') has different lengths for each timestep
        
        NOTE:
            if   : stress - shell : extensions for the integration points
        RETURN
            return 1.) insert_index

        Args:
          elout_elem: param type_:
          type_: 

        Returns:

        """

        array = []
        insert_indices = np.array([], dtype=int)
        ind = np.array([], dtype=int)

        ids = self._binout.read(self._name, elout_elem, 'ids')

        # check if elements have been destroyed
        if np.issubdtype(type(ids[0]), np.integer): # or isinstance(ids[0], np.int64):
            ids = [np.array([i]) for i in ids]
        if sum([len(i) - len(ids[0]) for i in ids]) == 0:
            return insert_indices, ind

        # if stress and shell, there might be various integration points:
        #    the read ids have to be extended accordingly
        if type_ == "stress" and elout_elem == "shell" or type_ == "stress" and elout_elem == "beam":
            nip = self._binout.read(self._name, elout_elem, 'nip')
            ids_nip = []
            for i in range(0, ids.shape[0]):
                id = np.repeat(ids[i], nip[i]).reshape((-1, 1))
                ids_nip.append(id)

            ids = np.array(ids_nip)

        len_indices = 0

        # calculate where dummy values have to be inserted -> guarantees equal length for each timestep
        #  1) insert_indices
        #  2) the real index of the element
        for i in range(0, ids.shape[0]):
            logic_intersection = np.in1d(ids[0], ids[i])
            array.append(
                np.where(np.logical_not(logic_intersection)))  # np.where(np.logical_not(np.in1d(ids[0], ids[i])))])
            indices = np.where(np.logical_not(logic_intersection))
            if indices[0].size != 0:
                insert_indices = np.append(insert_indices, indices[0] + len(ids[0]) * i - np.arange(len_indices,
                                                                                                    len_indices + len(
                                                                                                        indices[
                                                                                                            0])))
                ind = np.append(ind, indices[0] + len(ids[0]) * i)

                len_indices += len(indices[0])

        return insert_indices, ind

    def _set_nans(self, w_stress_strain, ind):
        """set dummy values to NaN (done for deleted elements)

        Args:
          w_stress_strain: principle components of the strain stress tensor numpy array with shape (n x 3)
          ind: list of indices, which have to padded with nans

        Returns:

        """
        if ind.size != 0:
            self._logger.emit(LOGConstants.WARNING[0], "Evaluated object contains failed elements!")
            w_stress_strain[ind] = np.tile(np.array([np.NaN]), 3)

    def _assign_stresses(self, elout_elem):
        """calculate stress from the elout_elem

        Args:
          elout_elem: return:

        Returns:

        """

        if elout_elem != "solid" and elout_elem != "shell" and elout_elem != "beam":
            return

        self._logger.emit(LOGConstants.READ_BINOUT[0], "elout: initialize stress " + elout_elem)
        self._logger.emit(LOGConstants.READ_BINOUT[0], "assign stresses for " + elout_elem + " elements")
        start = t.time()

        time = self._binout.read(self._name, elout_elem, 'time').flatten()

        elem_part_ipts_info = self._info_matrix(elout_elem, time, what="stress")

        if elem_part_ipts_info is None:
            return

        # 1) get indices of destroyed elements
        (insert_indices, ind) = self._indices_of_destroyed_elements(elout_elem, "stress")
        self._nummber_of_deleted_elements = len(insert_indices)
        self._ids_of_deleted_elements = ind

        # 2) extract sigma
        if elout_elem == "shell" or elout_elem == "solid":
            sig = np.concatenate((self._get_elout_data_and_extend(elout_elem, "sig_xx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_xy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_zx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_xy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_yy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_yz", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_zx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_yz", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sig_zz", insert_indices)), axis=1)

        elif elout_elem == "beam":
            # sigma_11 = sig_xx, sigma_12 = sig_xy, sigma_31 = sig_zx
            sig = np.concatenate((self._get_elout_data_and_extend(elout_elem, "sigma_11", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sigma_12", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sigma_31", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "sigma_12", insert_indices),
                                  np.zeros((elem_part_ipts_info.shape[0], 1)),
                                  np.zeros((elem_part_ipts_info.shape[0], 1)),
                                  self._get_elout_data_and_extend(elout_elem, "sigma_31", insert_indices),
                                  np.zeros((elem_part_ipts_info.shape[0], 1)),
                                  np.zeros((elem_part_ipts_info.shape[0], 1))), axis=1)

        self._logger.emit(LOGConstants.READ_BINOUT[0], ("extract data took : " + str(t.time() - start)))

        # 3) get eigenvalues of the matrix
        self._logger.emit(LOGConstants.READ_BINOUT[0], "calc eigenvalue")

        start = t.time()
        w_stress = np.linalg.eigvalsh(np.reshape(sig, (-1, 3, 3)))
        self._set_nans(w_stress, ind)
        self._logger.emit(LOGConstants.READ_BINOUT[0], ("calc eigenvalues took : " + str(t.time() - start)))

        time_step_size = len(time)
        element_type = EloutIndex.translate_element(elout_elem)
        # shape: [time]:[element id, part id, integration point]:[lambda1, lambda2, lambda3]
        #
        # e.g.: 7 time steps, 3 parts, each part 2 elements with 2 integration points, 3 eigenvalues
        # e.g.: results in shape of (7, 12, 3)
        data_tensor = w_stress.reshape(time_step_size, int(w_stress.shape[0] / time_step_size), w_stress.shape[1])

        # indexing: [element id, part id, integration point]
        index_matrix = elem_part_ipts_info[0:int(elem_part_ipts_info.shape[0] / time_step_size), :].astype(int)

        self._append_data(index_matrix, data_tensor, EloutIndex.STRESS, element_type)
        self._append_mapping_part_id_to_element_type(index_matrix, EloutIndex.STRESS, element_type)
        self._append_mapping_element_id_to_part_id(index_matrix, EloutIndex.STRESS, elout_elem)

    def _assign_strains(self, elout_elem):
        """

        Args:
          elout_elem: return:

        Returns:

        """
        # check the cases where to reject to read strains (if shells or solids do not have an epsilon component)
        self._logger.emit(LOGConstants.READ_BINOUT[0], ("assign strains for " + elout_elem + " elements"))

        if elout_elem != "solid" and elout_elem != "shell":
            self._logger.emit(LOGConstants.READ_BINOUT[0], "nothing to extract")
            return

        if elout_elem == "shell" and "lower_eps_xx" not in self._binout.read(self._name, elout_elem):
            self._logger.emit(LOGConstants.READ_BINOUT[0], "nothing to extract")
            return

        if elout_elem == "solid" and "eps_xx" not in self._binout.read(self._name, elout_elem):
            self._logger.emit(LOGConstants.READ_BINOUT[0], "nothing to extract")
            return

        self._logger.emit(LOGConstants.READ_BINOUT[0], "elout: initialize strain " + elout_elem)

        start = t.time()

        # depends on elout_elem
        time = self._binout.read(self._name, elout_elem, 'time').flatten()
        elem_part_ipts_info = self._info_matrix(elout_elem, time, what="strain")

        if elem_part_ipts_info is None:
            return

        (insert_indices, ind) = self._indices_of_destroyed_elements(elout_elem, "strain")

        if elout_elem == "shell":
            nr_elements = time.shape[0] if isinstance(self._binout.read(self._name, elout_elem, 'ids')[0],
                                                      np.intp) else len(
                self._binout.read(self._name, elout_elem, 'ids')[0]) * time.shape[0]

            ind_array = np.arange(1, nr_elements + 1)
            eps = np.concatenate((np.insert(
                self._get_elout_data_and_extend(elout_elem, "lower_eps_xx", insert_indices).flatten(), ind_array,
                self._get_elout_data_and_extend(elout_elem, "upper_eps_xx", insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_xy",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_xy",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_zx",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_zx",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_xy",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_xy",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_yy",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_yy",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_yz",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_yz",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_zx",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_zx",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_yz",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_yz",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1),
                                  np.insert(self._get_elout_data_and_extend(elout_elem, "lower_eps_zz",
                                                                            insert_indices).flatten(), ind_array,
                                            self._get_elout_data_and_extend(elout_elem, "upper_eps_zz",
                                                                            insert_indices).flatten()).reshape(-1,
                                                                                                               1)),
                                 axis=1)

        elif elout_elem == "solid":
            eps = np.concatenate((self._get_elout_data_and_extend(elout_elem, "eps_xx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_xy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_zx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_xy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_yy", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_yz", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_zx", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_yz", insert_indices),
                                  self._get_elout_data_and_extend(elout_elem, "eps_zz", insert_indices)), axis=1)

        self._logger.emit(LOGConstants.READ_BINOUT[0], ("extract data took : " + str(t.time() - start)))
        self._logger.emit(LOGConstants.READ_BINOUT[0], "calc eigenvalue")
        start = t.time()

        w_strain = np.linalg.eigvalsh(np.reshape(eps, (-1, 3, 3)))
        self._set_nans(w_strain, ind)
        self._logger.emit(LOGConstants.READ_BINOUT[0], ("calc eigenvalues took : " + str(t.time() - start)))

        time_step_size = len(time)
        element_type = EloutIndex.translate_element(elout_elem)
        # shape: [time]:[element id, part id, integration point]:[lambda1, lambda2, lambda3]
        #
        # e.g.: 7 time steps, 3 parts, each part 2 elements with 2 integration points, 3 eigenvalues
        # e.g.: results in shape of (7, 12, 3)
        data_tensor = w_strain.reshape(time_step_size, int(w_strain.shape[0] / time_step_size), w_strain.shape[1])

        # indexing: [element id, part id, integration point]
        index_matrix = elem_part_ipts_info[0:int(elem_part_ipts_info.shape[0] / time_step_size), :].astype(int)

        self._append_data(index_matrix, data_tensor, EloutIndex.STRAIN, element_type)
        self._append_mapping_part_id_to_element_type(index_matrix, EloutIndex.STRAIN, element_type)
        self._append_mapping_element_id_to_part_id(index_matrix, EloutIndex.STRAIN, elout_elem)

    def read_binout_data(self):
        """function will be called before a plugin controller is instantiated which needs elout data
        :return: True when data is read in, False when no data available

        Args:

        Returns:

        """
        # data already read
        if len(self._data) != 0:
            return True

        # no elout in binout
        if self._name not in self._binout.read():
            return False

        # actual elout read
        elements = self._binout.read(self._name)

        if len(elements) == 0:
            return False

        self._logger.emit(LOGConstants.READ_BINOUT[0], 'read elout data ...')

        #
        # Problem if the timed data from the element has different lengths
        # might be due to error termination
        #
        time_lengths = [len(self._binout.read(self._name, elem, 'time').flatten()) for elem in elements]

        assert (all([time_lengths[0] == length for length in time_lengths]))

        self._time = self._binout.read(self._name, elements[0], 'time') * self._dynasaur_definitions.get_units().time

        for elout_elem in elements:
            if elout_elem not in ['shell', 'solid', 'beam'] or len(
                    self._binout.read(self._name, elout_elem, 'ids')) == 0:
                self._logger.emit(LOGConstants.WARNING[0], elout_elem + " not supported or does not contain ids")
                continue

            # if elout_elem == 'beam':
            #     # write time and and timestep
            #     if not self._check_negative_intersection(self._binout.read(self._name, elout_elem)):
            #         return False
            #     self._init_data_(elem_name=elout_elem)

            self._assign_stresses(elout_elem)
            self._assign_strains(elout_elem)

        self._append_mapping_part_id_to_element_ids(EloutIndex.STRAIN)
        self._append_mapping_part_id_to_element_ids(EloutIndex.STRESS)

        self._dynasaur_definitions.define_dynasaur_everything(self._get_all_part_ids())

        # append general data to the self._data
        self._logger.emit(LOGConstants.READ_BINOUT[0], "done reading elout!")

        if self._read_volume_data_from_file_volume(self._volume_path):
            return self._init_data_volume(self.get_data_mapping_part_i_dto_element_ids(EloutIndex.STRAIN))

        return True

    def get_data_mapping_part_i_dto_element_ids(self, strain_stress_type):
        """

        Args:
          strain_stress_type: return:

        Returns:

        """
        return self._data_mapping_part_id_to_element_ids[strain_stress_type]

    def get_element_type_from_part_id(self, part_id, strain_stress_type):
        """

        Args:
          part_id: param strain_stress_type:
          strain_stress_type: 

        Returns:

        """
        return self._data_mapping_part_id_to_element_type[strain_stress_type][part_id]

    def get_defined_objects(self):
        """:return:"""
        return self._dynasaur_definitions.get_defined_objects_containing_parts(self._get_all_part_ids())

    def get_part_ids_by_object_name(self, object_name, strain_stress_type):
        """

        Args:
          object_name: param strain_stress_type:
          strain_stress_type: 

        Returns:

        """
        return self._dynasaur_definitions.get_parts_by_object_containing_part_ids(object_name,
                                                                                  self._get_part_ids(
                                                                                      strain_stress_type))

    def get_element_ids_by_part_id(self, part_id, strain_stress_type):
        """

        Args:
          part_id: param strain_stress_type:
          strain_stress_type: 

        Returns:

        """
        return self._data_mapping_part_id_to_element_ids[strain_stress_type][part_id]

    def get_part_id_by_element_ids(self, element_id, strain_stress_type):
        """

        Args:
          element_id: param strain_stress_type:
          strain_stress_type:

        Returns:

        """
        for element_type in self._data_mapping_element_id_to_part_id[strain_stress_type]:
            if element_id in self._data_mapping_element_id_to_part_id[strain_stress_type][element_type]:
                return self._data_mapping_element_id_to_part_id[strain_stress_type][element_type][element_id]

        else:
            self._logger.emit(LOGConstants.WARNING[0], f'Element ID {element_id} not found')
            return

    def get_part_data(self, strain_stress_type, part_id, element_id=None, time_step_indices=None):
        """description: return filtered index matrix and data tensor over all time steps for a given part_id
            will return all element, part, integration combinations
        
        optional parameter element_id: filter additional element_id with part_id
            will return just the element part combination with all their integration points
        
        optional parameter time_step_indices: reduce tensor for given time step indices
            will return a reduced data tensor with the given time step indices
            if None: will return all time steps -> full tensor

        Args:
          strain_stress_type: param part_id:
          element_id: param time_step_indices: (Default value = None)
          part_id: 
          time_step_indices:  (Default value = None)

        Returns:

        """
        tmp_data = self._get_data(part_id, strain_stress_type)

        if element_id is None:
            row_index = np.where(tmp_data[EloutIndex.INDEX][:, 1] == part_id)[0]
        else:
            row_index = \
                np.where((tmp_data[EloutIndex.INDEX][:, 1] == part_id) & (
                        tmp_data[EloutIndex.INDEX][:, 0] == element_id))[
                    0]

        if time_step_indices is None:
            data = tmp_data[EloutIndex.DATA][:, row_index, :]
        else:
            data = (tmp_data[EloutIndex.DATA][:, row_index, :])[time_step_indices, :, :]

        return tmp_data[EloutIndex.INDEX][row_index, :], data

    def get_element_type_name(self, element_id, strain_stress_type):
        """

        Args:
          element_id: param strain_stress_type:
          strain_stress_type: 

        Returns:

        """
        element_types = []
        for element_type in self._data_mapping_element_id_to_part_id[strain_stress_type].keys():
            if element_id in self._data_mapping_element_id_to_part_id[strain_stress_type][element_type]:
                part_id = self._data_mapping_element_id_to_part_id[strain_stress_type][element_type][element_id]
                element_types.append(self._data_mapping_part_id_to_element_type[strain_stress_type][part_id].name)
        return element_types

    def get_integration_point_indices_of_part_data_by_element_id(self, index, element_id):
        """further filtering by element_id of given results from getPartData()
        
        index and data are return values of getPartData()
        
        return row indices of filtered elements
         - returns list with one indices when just one integration point is available
         - returns list with multiple indices when multiple integration points are available

        Args:
          index: param element_id:
          element_id: 

        Returns:

        """
        return np.where(index[:, 0] == element_id)[0]

    def get_element_ids_of_part_data(self, index):
        """parameter uses index matrix of getPartData()
        using this function instead of the data_mappings will enhance performance
        
        get element IDs of filtered getPartData()

        Args:
          index: return:

        Returns:

        """
        return np.unique(index[:, 0])


class Elout(BinoutData):
    """ """
    # applies for beam elements!
    DATA_CHANNEL_TYPES = ['axial', 'shear_s', 'shear_t', 'moment_s', 'moment_t', 'torsion']
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'elout')

    def __init_data__(self, subdatatypes=[]):
        """

        :param elem_name:
        :return:
        """
        self._time = self._binout.read(*subdatatypes, 'time').flatten() * self._dynasaur_definitions.get_units().time
        self._time_interp = self._interp_time(self._time)
        self._ids = np.array(self._binout.read(*subdatatypes, self.__class__.ids_name)[0])
        try:
            len(self._ids)
        except TypeError:
            # case if beam data sequence consists only of one element!
            self._ids = np.array([self._ids])
        self._read_data_channels(subdatatypes=subdatatypes)

    def _get_subdatatypes_to_reach_binout_data(self, ls, ls_subdatatypes):
        """

        Args:
          ls: param ls_subdatatypes:
          ls_subdatatypes: 

        Returns:

        """
        ls_subdatatypes.append([self._name, 'beam'])


class Abstat(BinoutData):
    """ """
    # applies for beam elements!
    DATA_CHANNEL_TYPES = ['dm_dt_out', 'pressure', 'internal_energy', 'density', 'surface_area', 'dm_dt_in', 'dm_dt_outp',
                          'reaction', 'volume', 'gas_temp', 'total_mass', 'dm_dt_outv']

    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'abstat')


class AbstatCPM(BinoutData):
    """ """
    # applies for beam elements!
    DATA_CHANNEL_TYPES = ['dm_dt_out', 'pressure', 'internal_energy', 'density', 'surface_area', 'dm_dt_in',
                          'inflator_e', 'reaction', 'volume', 'gas_temp', 'total_mass', 'pres_particle', 'Trans_ke']

    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'abstat_cpm')


class Glstat(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['global_y_velocity', 'internal_energy', 'kinetic_energy', 'percent_increase', 'ts_element',
                          'energy_ratio_wo_eroded', 'spring_and_damper_energy', 'eroded_kinetic_energy',
                          'num_bad_shells', 'energy_ratio', 'external_work', 'time_step', 'global_z_velocity',
                          'global_x_velocity', 'eroded_internal_energy', 'time', 'total_energy',
                          'system_damping_energy', 'hourglass_energy', 'sliding_interface_energy', 'cycle', 'ts_eltype',
                          'joint_internal_energy', 'eroded_hourglass_energy', 'nzc', 'added_mass',
                          'resultant_global_velocity', 'ts_part']

    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'glstat')

    def _get_subdatatypes_to_reach_binout_data(self, ls, ls_subdatatypes):
        """

        Args:
          ls: param ls_subdatatypes:
          ls_subdatatypes: 

        Returns:

        """
        ls_subdatatypes.append([ls[0]])

    def _read_data_channels(self, subdatatypes=[]):
        """initialisation of self._data
        
        function reads available binout data and interpolates it to a targeted interpolation time
        creates subset of available channels (in binout) and defined DATA_CHANNEL_TYPES for Glstat
        INFO: own implementation in glstat.py due to missing ids for glstat data

        Args:
          subdatatypes:  (Default value = [])

        Returns:

        """
        data = {}
        available_channels = [value for value in self.__class__.DATA_CHANNEL_TYPES if
                              value in self._binout.read(self._name)]
        self._ids = np.array([0])
        for key in available_channels:
            type_data = self._binout.read(self._name, key)

            if type_data.shape[0] != 0:
                assert len(type_data.shape) == 1

                type_data = type_data[:self._time_interp.shape[0]].reshape(-1, 1)
                data_interp = np.zeros(shape=(self._time_interp.shape[0], 1))
                for i in range(data_interp.shape[1]):
                    data_interp[:, i] = np.interp(self._time_interp,
                                                  self._time[:self._time_interp.shape[0]], type_data[:, i])
                data[key] = data_interp

        self._data = {**self._data, **data}

    def get_measurement_channel(self, id_, channel_name):
        """returns interpolated data of the channel name from self._data
        identified by channel_name

        Args:
          id_: 
          channel_name: 

        Returns:

        """

        unit = self._get_unit_dimension_from_channel_name(channel_name)

        if channel_name == 'time':
            return self._time_interp.reshape(-1, 1)

        if channel_name not in self._data.keys():
            self._logger.emit(LOGConstants.ERROR[0], str(id_) + ' has no data with the identifier : ' + channel_name)
            return []
        self._logger.emit(LOGConstants.DATA_PLUGIN[0], 'ENERGY_GLOBAL read from channel name: ' + channel_name)

        d = self._data[channel_name]
        return d * unit


class Matsum(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_momentum', 'y_rbvelocity', 'z_rbvelocity', 'internal_energy', 'kinetic_energy',
                          'max_shell_mass', 'y_momentum', 'mass', 'eroded_kinetic_energy', 'brick_id', 'max_brick_mass',
                          'shell_id', 'eroded_internal_energy', 'z_momentum', 'hourglass_energy',
                          'eroded_hourglass_energy', 'x_rbvelocity', 'energy_ratio', 'eroded_energy_ratio',
                          'x_rbacceleration', 'y_acceleration', 'z_acceleration', 'x_rbdisplacement',
                          'y_rbdisplacement', 'z_rbdisplacement', 'resultant_displacement', 'resultant_velocity',
                          'resultant_acceleration', 'resultant_momentum', 'x_acceleration', 'y_acceleration',
                          'z_acceleration']

    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization i.e. call BinoutData constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'matsum')


class RigidBody(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['local_ax', 'local_ay', 'local_az', 'local_dx', 'local_dy', 'local_dz', 'local_vx',
                          'local_vy', 'local_vz', 'local_rax', 'local_ray', 'local_raz', 'local_rdx', 'local_rdy',
                          'local_rdz', 'local_rvx', 'local_rvy', 'local_rvz', 'global_x', 'global_y', 'global_z',
                          'global_dx', 'global_dy', 'global_dz', 'global_ax', 'global_ay', 'global_az', 'global_vx',
                          'global_vy', 'global_vz', 'global_rax', 'global_ray', 'global_raz', 'global_rdx',
                          'global_rdy', 'global_rdz', 'global_rvx', 'global_rvy', 'global_rvz', 'dircos_11',
                          'dircos_12', 'dircos_13', 'dircos_21', 'dircos_22', 'dircos_23', 'dircos_31', 'dircos_32',
                          'dircos_33']
    ids_name = "ids"

    def __init__(self, data, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition
        :param: cody type(MADYMO/LS DYNA)

        :return:
        """

        BinoutData.__init__(self, data, logger, dynasaur_definitions, 'rbdout')


class BoundaryCondition(BinoutData):
    """ """
    # DATA_CHANNEL_TYPES = ['ids', 'energy', 'revision', 'y_force', 'zmoment', 'x_force', 'title', 'y_total',
    #                       'legend', 'version', 'xmoment', 'ymoment', 'legend_ids', 'z_force', 'date', 'time',
    #                       'etotal', 'x_total', 'z_total']
    DATA_CHANNEL_TYPES = ['energy', 'y_force', 'x_force', 'xmoment', 'ymoment', 'zmoment',
                          'z_force', 'etotal', 'x_total', 'y_total', 'z_total']

    ids_name = "ids"

    def __init__(self, data, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition
        :param: cody type(MADYMO/LS DYNA)

        :return:
        """

        BinoutData.__init__(self, data, logger, dynasaur_definitions, 'bndout')


class Nodout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['rx_velocity', 'ry_velocity', 'rz_velocity', 'rx_displacement', 'ry_displacement',
                          'rz_displacement', 'rx_acceleration', 'ry_acceleration', 'rz_acceleration', 'x_coordinate',
                          'y_coordinate', 'z_coordinate', 'x_displacement', 'y_displacement', 'z_displacement',
                          'x_velocity', 'y_velocity', 'z_velocity', 'x_acceleration', 'y_acceleration',
                          'z_acceleration', 'resultant_rotation', 'resultant_angular_velocity',
                          'resultant_angular_acceleration', 'resultant_displacement', 'resultant_velocity',
                          'resultant_acceleration']
    ids_name = "ids"

    def __init__(self, data, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition
        :param: cody type(MADYMO/LS DYNA)

        :return:
        """

        BinoutData.__init__(self, data, logger, dynasaur_definitions, 'nodout')


class JointForc(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['energy', 'resultant_moment', 'resultant_force', 'x_force',  'y_force', 'z_force',
                          'x_moment', 'y_moment', 'z_moment']
    ids_name = "ids"

    def __init__(self, data, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition
        :param: cody type(MADYMO/LS DYNA)

        :return:
        """
        name = ['jntforc', 'joints']
        BinoutData.__init__(self, data, logger, dynasaur_definitions, name)


class JointType(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['alpha_moment_stiffness', 'd(gamma)_dt', 'joint_extra2',
                          'alpha_degrees', 'alpha_moment_total', 'gamma_degrees', 'd(alpha)_dt', 'beta_degrees',
                          'alpha_moment_damping', 'beta_moment_total', 'gamma_scale_factor',
                          'beta_moment_damping', 'd(beta)_dt', 'beta_moment_stiffness']
    #TODO: Consider types: 'joint_energy', 'joint_extra1'
    ids_name = "ids"

    def __init__(self, data, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition
        :param: cody type(MADYMO/LS DYNA)

        :return:
        """
        name = ['jntforc', 'type1']
        BinoutData.__init__(self, data, logger, dynasaur_definitions, name)


class RCForc(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_moment', 'y_moment', 'z_moment', 'x_force', 'y_force', 'z_force', 'tie_count', 'mass',
                          'tie_area', 'resultant_force']

    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, "rcforc")

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

        # ids converted to m and s ... "m" and "s" [1000, 1000] --> ["1000m", "1000s"]
        if isinstance(self._binout, lasso.dyna.Binout):
            self._ids = np.array([str(i) + "s" if nr % 2 else str(i) + "m" for nr, i in enumerate(self._ids)])
        if len(self._ids.shape) > 1:
            self._ids = self._ids[0]

        self._read_data_channels(subdatatypes=subdatatypes)

        assert len(self._ids.shape) == 1


class SBTout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['belt_length', 'belt_force']
    ids_name = "belt_ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, "sbtout")


class SlipringOut(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['ring_slip']
    ids_name = "slipring_ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, "sbtout")



class Secforc(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['x_force', 'y_force', 'z_force', 'x_moment', 'y_moment', 'z_moment',
                          'x_centroid', 'y_centroid', 'z_centroid', 'total_force', 'total_moment', 'area']
    # 'total_force', 'total_moment',  'area'
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'secforc')

    def __get_indices_of_ids(self, ids):
        tmp_ids = self._ids.tolist()
        return [tmp_ids.index(val) for val in tmp_ids if val in ids]


class Sleout(BinoutData):
    """ """
    DATA_CHANNEL_TYPES = ['total_friction', 'slave', 'total_master', 'master', 'cycle',
                          'friction_energy', 'time', 'total_energy',
                          'total_slave']
    #TODO: Check TYPES with someone who is using this LS Dyna inputs
    ids_name = "ids"

    def __init__(self, binout, logger, dynasaur_definitions):
        """
        Initialization/constructor

        :param: binout
        :param: logger
        :param: dynasaur definition

        :return:
        """
        BinoutData.__init__(self, binout, logger, dynasaur_definitions, 'sleout')

    def get_measurement_channel(self, id_, channel_name):
        """returns the interpolated channel,
        Aim: Constant time interval

        Args:
          id: param channel_name:
          id_:
          channel_name:

        Returns:


        """

        unit = self._get_unit_dimension_from_channel_name(channel_name)

        if channel_name == 'time':
            return self._time.reshape(-1, 1)
        d = self._data[channel_name][:, 0] * unit
        return d
