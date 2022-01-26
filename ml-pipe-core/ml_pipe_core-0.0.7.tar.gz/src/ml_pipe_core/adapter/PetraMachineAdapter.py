from typing import List, Tuple, Optional

import numpy as np

try:
    import PyTine as pt
except:
    pass

try:
    from K2I2K_os import K2I2K_os
except:
    pass

from .PetraAdapter import PetraAdapter, SqlDBConnector
from .BPMAdapter import BPMAdapter
from ..config import KAFKA_SERVER_URL, MYSQL_USER, MYSQL_PORT, MYSQL_PW, MYSQL_HOST


def get_position_of_element_in_other_list(other_l: List[str], ref_l: List[str]) -> Tuple[bool, Optional[int]]:
    """[summary]
    Iterates over ref_l and yield a Tuple with True and index of the current element in other_l, if the current element is other_l. If not is returns (False. None)
        Example:
            get_position_of_element_in_other_list(['a','c','b'], ['a', 'b', 'c', 'd'])
            ((True, 0), (True, 2), (True, 1), (False, None))
    :param other_l: subset of ref_l
    :type other_l: List[str]
    :param ref_l: List to be iterated
    :type ref_l: List[str]
    :raises ValueError: If other_l is not a subset of ref_l
    :return: Yields a tuple at each step. The first element is a boolean which is True if the current element is in in_l, the second
            element is the index of the current element in in_l. If the current element is not in in_l (False, None) is yield.
    :rtype: Tuple[bool, Optional[int]]
    :yield: Yields a tuple at each step. The first element is a boolean which is True if the current element is in in_l, the second
            element is the index of the current element in in_l. If the current element is not in in_l (False, None) is yield.
    :rtype: Iterator[Tuple[bool, Optional[int]]]
    """
    names_indices = {k: v for v, k in enumerate(other_l)}
    found_idx_count = 0
    for name in ref_l:
        found_idx = names_indices.get(name)
        if found_idx != None:
            found_idx_count += 1
            yield name, True, found_idx
        else:
            yield name, False, None
    if found_idx_count != len(other_l):
        print("Unknown name in names")
        raise ValueError("Element of other_l is not in ref_l")


class PetraMachineAdapter(PetraAdapter):
    def __init__(self, energy=6.063, bpm_unit='mm', path_to_bpm_calibr_file='src/ml_pipe_core/adapter/bpm_settings', path_to_constants_file='constants.csv', custom_db_connector=None):
        super().__init__(custom_db_connector=custom_db_connector)
        self.bpm_adapter = BPMAdapter(units=bpm_unit, path_to_calibr_file=path_to_bpm_calibr_file, path_to_constants_file=path_to_constants_file)
        self.debug_mode = False
        self.energy = energy
        self.get_property = 'Strom.Soll'

        # name list with all device names of the optic
        self.hcor_group_names = self.get_hcor_device_names(apply_filter=False)
        self.vcor_group_names = self.get_vcor_device_names(apply_filter=False)

        # uppercase
        self.hcor_group_names = [p.upper() for p in self.hcor_group_names]
        self.vcor_group_names = [p.upper() for p in self.vcor_group_names]

        #  hash tables used by _map_names_to_group_name_indices for fast name to idx mapping
        self._hcor_group_name_idx_map = {name: idx for idx, name in enumerate(self.hcor_group_names)}
        self._vcor_group_name_idx_map = {name: idx for idx, name in enumerate(self.vcor_group_names)}

        self.cors_size = {'PeCorH': len(self.hcor_group_names), 'PeCorV': len(self.vcor_group_names)}

    def get_values_by_group(self, group: str):
        group_res = pt.get(f"/PETRA/Cms.PsGroup/{group}", self.get_property, size=self.cors_size[group])['data']
        print(f'read {group}: {len(group_res)} values')
        return group_res

    def get_value(self, name):
        return pt.get(f"/PETRA/Cms.MagnetPs/{name}", self.get_property)['data']

    def get_values_by_names(self, names):
        result = []
        for name in names:
            try:
                res = self.get_value(name)
                result.append(res)
            except Exception as e:
                print(name, e)
        return result

    def get_hcor_device_names(self, apply_filter=True) -> List[str]:
        device = 'PeCorH'
        cor_group_size = pt.get(f"/PETRA/Cms.PsGroup/{device}", "GroupSize")['data']
        names = pt.get(f"/PETRA/Cms.PsGroup/{device}", "GroupDevices", size=cor_group_size)['data']
        if apply_filter:
            return self.cor_names_filter(names)
        return names

    def get_vcor_device_names(self, apply_filter=True):
        device = 'PeCorV'
        cor_group_size = pt.get(f"/PETRA/Cms.PsGroup/{device}", "GroupSize")['data']
        names = pt.get(f"/PETRA/Cms.PsGroup/{device}", "GroupDevices", size=cor_group_size)['data']
        if apply_filter:
            return self.cor_names_filter(names)
        return names

    def _map_names_to_group_name_indices(self, names: List[str], group='PeCorH'):
        """[summary]
        Maps the names to the indices in the group name list.
        :param names: Names of the correctors in uppercase. Note: The names have to be in the corrector group
        :type names: List[str]
        :param group: Corrector group can be 'PeCorH' or 'PeCorV', defaults to 'PeCorH'
        :type group: str, optional
        :raises KeyError: If names are not in the group
        :return: A list of indices
        :rtype: [type]
        """
        indices = []
        cors_name_idx_map = self._hcor_group_name_idx_map if group == 'PeCorH' else self._vcor_group_name_idx_map
        for name in names:
            found_idx = cors_name_idx_map.get(name)
            if found_idx == None:
                raise KeyError(f"name {name} is not in {group} group.")
            indices.append(found_idx)
        return indices

    def get_cor_parallel(self, names: List[str], group='PeCorH') -> List[float]:
        indices = self._map_names_to_group_name_indices(names=names, group=group)

        currents = self.get_values_by_group(group)
        filtered_currents = [currents[idx] for idx in indices]
        print(f"names: len {len(names)} curr len {len(filtered_currents)}")
        return filtered_currents

    def get_cor_serial(self, names: List[str]) -> List[float]:
        currents = []
        for name in names:
            currents.append(self.get_value(name))
        return currents

    def get_hcors(self, names: List[str], is_group_call=True) -> List[float]:
        currents = []
        if is_group_call:
            currents = self.get_cor_parallel(names, group='PeCorH')
        else:
            currents = self.get_cor_serial(names)

        return self.current2strength(names, currents)

    def get_vcors(self, names: List[str], is_group_call=True) -> List[float]:
        currents = []
        if is_group_call:
            currents = self.get_cor_parallel(names, group='PeCorV')
        else:
            currents = self.get_cor_serial(names)
        return self.current2strength(names, currents)

    def strength2current(self, names, strengths):
        kk = K2I2K_os(names, psStrength=strengths, energy=self.energy, debug=None)
        return kk.psCurrent

    def current2strength(self, names, currents):
        kk = K2I2K_os(names, psCurrent=currents, energy=self.energy, debug=None)
        return kk.psStrength

    def set_group_values(self, name, values):
        if self.debug_mode:
            print(f"Debug Mode set_group_value: name: {name} values: {values}")
        else:
            address = f"/PETRA/Cms.PsGroup/{name}"
            print(address)
            print(len(values))
            print(type(values))
            print(self.get_property)
            pt.set(address=address,
                   property=self.get_property,
                   input=values,
                   format='FLOAT',
                   size=len(values),
                   mode='WRITE')

        return

    def set_value(self, name, value):
        if self.debug_mode:
            print(f"Debug Mode set_value: name: {name} value: {value}")
        else:
            pt.set(f"/PETRA/Cms.MagnetPs/{name}", self.get_property, value)

    def set_cor_parallel(self, names: List[str], in_strenghts: List[float], ref, current_offsets: List[float] = None, group='PeCorV'):
        currents = []
        print(f"names: len {len(names)} current len {len(in_strenghts)}")
        in_currents = self.strength2current(names, in_strenghts)

        if current_offsets:
            for idx, _ in enumerate(in_currents):
                in_currents[idx] += current_offsets[idx]

        for name, is_strength_set, in_strengths_idx in get_position_of_element_in_other_list(other_l=names, ref_l=ref):
            if is_strength_set:
                currents.append(in_currents[in_strengths_idx])
                print(f"name: {name}, current: {in_currents[in_strengths_idx]}. use new value")
            else:
                curr = self.get_value(name)
                currents.append(curr)  # get current for name
                print(f"name: {name}, current: {curr}. use old value")
        self.set_group_values(group, currents)

    def set_cor_serial(self, names: List[str], in_strenghts: List[float], current_offsets: List[float] = None):

        in_currents = self.strength2current(names, in_strenghts)

        # if current_offsets:
        #    for idx, _ in enumerate(in_currents):
        #        in_currents[idx] += current_offsets[idx]

        for name, current in zip(names, in_currents):
            print(f"name: {name}, current: {current}.")
            self.set_value(name, current)

    def set_vcors(self, names: List[str], in_strenghts: List[float], current_offsets: List[float] = None, is_group_call=True):
        if is_group_call:
            self.set_cor_parallel(names, in_strenghts, self.vcor_group_names, current_offsets=current_offsets, group='PeCorV')
        else:
            self.set_cor_serial(names, in_strenghts)

    def set_hcors(self, names: List[str], in_strenghts: List[float], current_offsets: List[float] = None, is_group_call=True):
        if is_group_call:
            self.set_cor_parallel(names, in_strenghts, self.hcor_group_names, current_offsets=current_offsets, group='PeCorH')
        else:
            self.set_cor_serial(names, in_strenghts)

    def get_bpms(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        data, names = self.bpm_adapter.get_orbit()
        off_go, _ = self.bpm_adapter.get_offsets_go()
        x = data[:, 0] - off_go[:, 0]  # - ref[:,0]
        y = data[:, 1] - off_go[:, 1]  # - ref[:,1]
        return x, y, names

    def get_ddxy(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        return self.bpm_adapter.read(n_turns=n_turns)

    def get_dd_sum(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        return self.bpm_adapter.read_sum(n_turns=n_turns)
