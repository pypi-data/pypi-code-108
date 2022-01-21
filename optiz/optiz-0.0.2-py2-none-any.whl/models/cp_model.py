import os
from typing import Any, Callable
from ortools.sat.python import cp_model

from ..constants import OUTPUT_DIR
from ..utils import create_if_not_exists


class CPSolSaver(cp_model.CpSolverSolutionCallback):
    def __init__(self, name: str, variables, sol_to_str: Callable[[Any], str], output_dir=OUTPUT_DIR):
        cp_model.CpSolverSolutionCallback.__init__(self)
        create_if_not_exists(output_dir)
        self.__variables = variables
        self.__solution_count = 0
        self._name = name
        self._output_dir = output_dir
        self._sol_to_str = sol_to_str

    def OnSolutionCallback(self):
        self.__solution_count += 1
        save_path = os.path.join(self._output_dir, f"{self._name}.txt")
        variables = [self.Value(v) for v in self.__variables]
        with open(save_path, "w") as f:
            f.write(self._sol_to_str(variables))

    def SolutionCount(self):
        return self.__solution_count
