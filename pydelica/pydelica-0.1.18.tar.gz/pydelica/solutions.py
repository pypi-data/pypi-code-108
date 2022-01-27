from typing import Dict
from pydelica.exception import ResultRetrievalError
import pandas as pd
import os
import logging
import glob


class SolutionHandler:
    """Stores solutions extracted from a Modelica simulation"""

    def __init__(self, session_directory: str):
        """Extract solution information from a given session directory

        Parameters
        ----------
        session_directory : str
            directory from a simulation session
        """
        self._logger = logging.getLogger("PyDelica.Solutions")
        self._session_dir = session_directory
        self._solutions: Dict[str, pd.DataFrame] = {}

    def retrieve_session_solutions(self) -> Dict[str, pd.DataFrame]:
        """Retrieve any stored solutions

        Returns
        -------
        Dict[str, pd.DataFrame]
            solutions extracted from valid results files

        Raises
        ------
        ResultRetrievalError
            If no CSV result files were found within the session directory
        """
        _has_csv = glob.glob(os.path.join(self._session_dir, "*.csv"))

        if not _has_csv:
            raise ResultRetrievalError

        for out_file in _has_csv:
            if "_res" not in out_file:
                continue
            self._logger.debug("Reading results from output file '%s'", out_file)
            _key = out_file.split("_res")[0]
            self._solutions[_key] = pd.read_csv(_has_csv[0])
        return self._solutions

    def get_solutions(self) -> Dict[str, pd.DataFrame]:
        return self._solutions
