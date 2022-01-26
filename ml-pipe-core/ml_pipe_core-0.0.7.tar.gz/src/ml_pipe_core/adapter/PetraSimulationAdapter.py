from typing import List, Tuple
import mysql.connector
import numpy as np

from .PetraAdapter import PetraAdapter, SqlDBConnector
from ..message import Message, dataclasses
from ..event_utls.producer import Producer
from ..config import KAFKA_SERVER_URL, MYSQL_USER, MYSQL_PORT, MYSQL_PW, MYSQL_HOST
from ..logger import logging
from .simulation_db_types import TABLE_NAMES, MAGNET_TABLE_TYPES

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)


@dataclasses.dataclass
class SimTableUpdated(Message):
    hcor: Tuple[str, float]
    vcor: Tuple[str, float]
    bpm: Tuple[str, float]


class PetraSimulationAdapter(PetraAdapter):

    def __init__(self, energy=6.063, custom_db_connector=None):
        super().__init__(custom_db_connector = custom_db_connector)
        self.debug_mode = False

        self.commands = []
        self.db_connector.wait_until_table_is_created(TABLE_NAMES.MAGNETS)
        self.db_connector.wait_until_table_is_created(TABLE_NAMES.BPM)
        self.db_connector.wait_until_table_is_created(TABLE_NAMES.TWISS)
        self.db_connector.wait_until_table_is_created(TABLE_NAMES.MULTI_TURN_BPM)

        self.energy = energy
        self.get_property = 'Strom.Soll'

        self.bpm_names = self.get_bpm_device_names()

        self.hcors_names = {name: rank for rank, name in enumerate(self.get_hcor_device_names())}
        self.vcors_names = {name: rank for rank, name in enumerate(self.get_vcor_device_names())}

        self._producer = Producer(KAFKA_SERVER_URL)
        _logger.debug("PetraSimulationAdapter initialized.")

    def get_group_values(self, name):
        pass

    def get_named_values(self, names):
        pass

    def get_hcor_device_names(self, apply_filter=True) -> List[str]:
        sql_select_Query = f"select name from {TABLE_NAMES.MAGNETS} where type='{MAGNET_TABLE_TYPES.HCOR}' order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = [res[0] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        cursor.close()
        if apply_filter:
            return self.cor_names_filter(res)
        return res

    def get_vcor_device_names(self, apply_filter=True) -> List[str]:
        sql_select_Query = f"select name from {TABLE_NAMES.MAGNETS} where type='{MAGNET_TABLE_TYPES.VCOR}' order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = [res[0] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        cursor.close()
        if apply_filter:
            return self.cor_names_filter(res)
        return res

    def _create_get_val_by_name_query(self, table: str, names: List[str], type: str) -> str:
        names_with_sql_seperator = ["'"+name+"'" for name in names]
        return f"select name, value from {table} where name in ({','.join(names_with_sql_seperator)}) and type='{type}'"

    def get_hcors(self, names: List[str], is_group_call=True) -> List[float]:
        sql_select_Query = self._create_get_val_by_name_query(TABLE_NAMES.MAGNETS, names, MAGNET_TABLE_TYPES.HCOR)
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = {res[0]: res[1] for res in cursor.fetchall()}
        self.db_connector.sql_con.commit()
        cursor.close()
        return [res[name] for name in names]

    def get_vcors(self, names: List[str], is_group_call=True) -> List[float]:
        sql_select_Query = self._create_get_val_by_name_query(TABLE_NAMES.MAGNETS, names, MAGNET_TABLE_TYPES.VCOR)
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = {res[0]: res[1] for res in cursor.fetchall()}
        self.db_connector.sql_con.commit()
        cursor.close()
        return [res[name] for name in names]

    def get_bpm_lengths(self) -> List[str]:
        sql_select_Query = f"select name, length from {TABLE_NAMES.BPM}"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        names = [res[0] for res in cursor.fetchall()]
        lengths = [res[1] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        cursor.close()
        return names, lengths

    def set_bpm_lengths(self, name_length_pairs: Tuple[str, float]):
        try:
            data = []
            for name, length in name_length_pairs:
                data.append((length, name))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update bpm set length = %s where name = %s", data)
            self.db_connector.sql_con.commit()
            cursor.close()
        except mysql.connector.Error as error:
            _logger.info(f"set_bpm_lengths: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def set_hcors(self, names: List[str], strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        if self.debug_mode:
            for name, value in zip(names, strengths):
                _logger.debug(f"Debug mode:  name = {name} strength = '{value}'")
            return
        try:
            data = []
            for name, value in zip(names, strengths):
                data.append((value, name, MAGNET_TABLE_TYPES.HCOR))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update magnets set value = %s where name=%s and type=%s", data)
            self.db_connector.sql_con.commit()
            cursor.close()

        except mysql.connector.Error as error:
            _logger.info(f"set_hcors: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def set_vcors(self, names: List[str], strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        if self.debug_mode:
            for name, value in zip(names, strengths):
                _logger.debug(f"Debug mode:  name = {name} strength = '{value}'")
            return
        try:
            data = []
            for name, value in zip(names, strengths):
                data.append((value, name, MAGNET_TABLE_TYPES.VCOR))
                #sql_update_query = f"Update {TABLE_NAMES.MAGNETS} set value = {value} where name='{name}' and type='{MAGNET_TABLE_TYPES.VCOR}'"
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update magnets set value =%s where name=%s and type=%s", data)
            self.db_connector.sql_con.commit()
            cursor.close()

        except mysql.connector.Error as error:
            _logger.info(f"set_vcors: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def get_bpm_device_names(self) -> List[str]:
        sql_select_Query = f"select name from {TABLE_NAMES.BPM} order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = [res[0] for res in cursor.fetchall()]
        self.db_connector.sql_con.commit()
        cursor.close()
        return res

    def set_bpms(self, names: List[str], bmp_coords: np.ndarray):
        if self.debug_mode:
            for idx, name in enumerate(names):
                _logger.debug(f"Debug mode:  name = {name} bpm_coords = '{bmp_coords[idx]}'")
            return
        _logger.debug("Call set_bpms")
        try:
            data = []
            for idx, name in enumerate(names):
                data.append((bmp_coords[idx, 0], bmp_coords[idx, 1], name))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update bpm set x=%s, y=%s where name = %s", data)
            self.db_connector.sql_con.commit()
            cursor.close()

        except mysql.connector.Error as error:
            _logger.info(f"set_bpms: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def get_bpms(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        _logger.debug("Call get_bpms")
        sql_select_Query = f"select x, y, name from {TABLE_NAMES.BPM} order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        result = cursor.fetchall()
        self.db_connector.sql_con.commit()
        cursor.close()
        x = np.array([res[0] for res in result])
        y = np.array([res[1] for res in result])
        names = [res[2] for res in result]
        return x, y, names

    def get_multi_turn_bpms(self):
        _logger.debug("Call get_multi_turn_bpms")
        sql_select_Query = f"select x, y, name from {TABLE_NAMES.MULTI_TURN_BPM} order by pos"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        result = cursor.fetchall()
        self.db_connector.sql_con.commit()
        cursor.close()
        merged_x_bytes = b''
        merged_y_bytes = b''
        for res in result:
            merged_x_bytes += res[0]
            merged_y_bytes += res[1]

        names = [res[2] for res in result]
        n_bpms = len(names)
        x = np.frombuffer(merged_x_bytes, dtype=float)
        x = x.reshape(n_bpms, int(len(x)/n_bpms))
        y = np.frombuffer(merged_y_bytes, dtype=float)
        y = y.reshape(n_bpms, int(len(y)/n_bpms))
        return x, y, names

    def set_multi_turn_bpms(self, names: List[str], x: np.ndarray, y: np.ndarray):
        """[summary]
        :param names: [description]
        :type names: List[str]
        :param x: [description]
        :type x: np.ndarray
        :param y: [description]
        :type y: np.ndarray
        :raises TypeError: [description]
        """
        _logger.debug("Call set_multi_turn_bpms")
        if self.debug_mode:
            for idx, name in enumerate(names):
                _logger.debug(f"Debug mode:  name = {name} x = {x[idx]} y = {y[idx]}")
            return
        if x.dtype != float or x.dtype != float:
            raise TypeError("x and y have to be a numpy float array.")
        try:
            data = []
            for idx, name in enumerate(names):
                data.append((x[idx, :].tobytes(), y[idx, :].tobytes(), name))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update bpm_multiturn set x=%s, y=%s where name=%s", data)
            self.db_connector.sql_con.commit()
            cursor.close()

        except mysql.connector.Error as error:
            _logger.info(f"set_multi_turn_bpms: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def set_twiss(self, names: List[str], mat: List[List[float]]):
        """[summary]

        :param names: Names of the diffrent twiss parameters
        :type names: List[str]
        :param mat: 2D Matrix each row contains a diffrent twiss parameter. Order [beta_x, beta_y, D_x, D_y]
        :type mat: List[List[float]]
        """
        try:
            data = []
            for name, row in zip(names, mat):
                beta_x, beta_y, D_x, D_y = row
                data.append((beta_x, beta_y, D_x, D_y, name))
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update twiss set beta_x = %s, beta_y = %s, D_x = %s, D_y = %s where name = %s", data)
            self.db_connector.sql_con.commit()
            cursor.close()
        except mysql.connector.Error as error:
            _logger.info(f"set_twiss: Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def get_twiss(self, names: List[str]) -> List[List[float]]:
        """[summary]

        :param names: Names of the requested twiss paramters
        :type names: List[str]
        :return: 2D Matrix each row contains a diffrent twiss parameter.
        :rtype: List[List[float]]
        """
        sql_select_Query = f"select name, beta_x, beta_y, D_x, D_y from {TABLE_NAMES.TWISS}"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        name_to_twiss = {res[0]: res[1:] for res in cursor.fetchall()}
        self.db_connector.sql_con.commit()
        cursor.close()
        return [name_to_twiss[name] for name in names if name in name_to_twiss]
