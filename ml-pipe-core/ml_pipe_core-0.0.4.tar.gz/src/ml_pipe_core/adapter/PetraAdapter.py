from typing import Tuple, List

import numpy as np
import mysql

from ..logger import logging
from .simulation_db_types import TABLE_NAMES
from ..config import MYSQL_USER, MYSQL_PW, MYSQL_HOST, MYSQL_PORT
from ..utils.SqlDBConnector import SqlDBConnector

_logger = logging.getLogger(__name__)
_logger.setLevel(logging.DEBUG)

if MYSQL_USER == None:
    raise Exception(f"Environment Value SIM_SQL_USER isn't set. Please set the value in .env file.")

if MYSQL_PW == None:
    raise Exception(f"Environment Value SIM_SQL_PW isn't set. Please set the value in .env file.")

if MYSQL_HOST == None:
    raise Exception(f"Environment Value SIM_SQL_HOST isn't set. Please set the value in .env file.")

_logger.debug(f"Environment SIM_SQL_HOST: {MYSQL_HOST}")


class PetraAdapter():
    def __init__(self, custom_db_connector):

        self._excluded_prefix_cor_names = []
        self.db_connector = custom_db_connector if custom_db_connector is not None else SqlDBConnector(user=MYSQL_USER, pw=MYSQL_PW, host=MYSQL_HOST, port=MYSQL_PORT, database='sim_db')
        self.db_connector.check_if_sql_db_table_exists(TABLE_NAMES.MACHINE_PARMS)
        self.active_package_id = None
        self.service_type = 'petra_sim_adapter'

    def set_cor_name_filter(self, prefix_names: List[str]):

        self._excluded_prefix_cor_names = prefix_names

    def cor_names_filter(self, names):
        if not self._excluded_prefix_cor_names:
            return names
        new_names = []
        for name in names:
            is_excluded = False
            for prefix in self._excluded_prefix_cor_names:
                if name.startswith(prefix):
                    is_excluded = True
                    break
            if not is_excluded:
                new_names.append(name)

        return new_names

    def set_machine_params(self, names, values):
        try:
            data = [(value, name) for name, value in zip(names, values)]
            cursor = self.db_connector.sql_con.cursor()
            cursor.executemany("Update machine_params set value = %s where param = %s", data)
            cursor.close()
        except mysql.connector.Error as error:
            _logger.info(f"Failed to update record to database rollback: {error}")
            self.db_connector.sql_con.rollback()

    def get_machine_params(self):
        sql_select_Query = f"select param, value from {TABLE_NAMES.MACHINE_PARMS}"
        cursor = self.db_connector.sql_con.cursor()
        cursor.execute(sql_select_Query)
        res = {res[0]: res[1] for res in cursor.fetchall()}
        self.db_connector.sql_con.commit()
        cursor.close()
        return res

    def get_hcor_device_names(self) -> List[str]:
        """[summary]
        Returns all getable an settable horizontal corrector names
        :return: List of horizontal corrector device names in uppercase
        :rtype: List[str]
        """
        raise NotImplemented()

    def get_vcor_device_names(self) -> List[str]:
        """[summary]
        Returns all getable an settable vertical corrector names
        :return: List of horizontal vertical device names in uppercase
        :rtype: List[str]
        """
        raise NotImplemented()

    def get_hcors(self, names: List[str], is_group_call=True) -> List[float]:
        """[summary]
        Gets the strengths of horizontal corrector names,
        :param names: Names of the horizontal correctors in uppercase.
        :type names: List[str]
        :param is_group_call: Read all correctors parallel which is faster if True else read serial, defaults to True
        :type is_group_call: bool, optional
        :return: List of strengths sorted by names
        :rtype: List[float]
        """
        raise NotImplemented()

    def get_vcors(self, names: List[str], is_group_call=True) -> List[float]:
        """[summary]
        Gets the strengths of vertical corrector names,
        :param names: Names of the vertical correctors. Have to be uppercase.
        :type names: List[str]
        :param is_group_call: Reads all correctors parallel which is faster if True else reads serial, defaults to True
        :type is_group_call: bool, optional
        :return: List of strengths sorted by names
        :rtype: List[float]
        """
        raise NotImplemented()

    def set_vcors(self, names: List[str], strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        """[summary]
        Set the vertical correctors.
        :param names: Names of the vertical correctors to be set in uppercase.
        :type names: List[str]
        :param in_strenghts: List of strenghts to be set.
        :type in_strenghts: List[float]
        :param current_offsets: List of offsets that will be added to the bpm's current, default to None
        :type current_offsets: List[float]
        :param is_group_call: Writes all correctors parallel which is faster if True else writes serial, defaults to True
        :type is_group_call: bool, optional
        """
        raise NotImplemented()

    def set_hcors(self, names: List[str], strengths: List[float], current_offsets: List[float] = None, is_group_call=True):
        """[summary]
        Set the horizontal correctors.
        :param names: Names of the horizontal correctors to be set in uppercase.
        :type names: List[str]
        :param in_strenghts: List of strenghts to be set.
        :type in_strenghts: List[float]
        :param current_offsets: List of offsets that will be added to the bpm's current, default to None
        :type current_offsets: List[float]
        :param is_group_call: Writes all correctors parallel which is faster if True else writes serial, defaults to True
        :type is_group_call: bool, optional
        """
        raise NotImplemented()

    def get_bpms(self) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """[summary]
        Gets the bpm coordinates and names.
        :return: A Tuple (x, y, names) where x, y are the coordinates of the bpm.
        """
        raise NotImplemented()

    def get_ddxy(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        raise NotImplemented()

    def get_dd_sum(self, n_turns=10) -> Tuple[np.ndarray, List[str]]:
        raise NotImplemented()
