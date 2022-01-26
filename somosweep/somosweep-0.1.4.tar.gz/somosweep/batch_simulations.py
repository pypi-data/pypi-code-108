# Be sure to run this file from the "region_of_acquisition" folder
#     cd examples/region_of_acquisition
#
import yaml
import time
import multiprocessing as mp
import os
import sys

from somosweep import iter_utils


class BatchSimulation:
    """
    Run a batch of SoMo or SoMoGym simulations.
    
    *Note: this turns out
    to be more generally-applicable than just for SoMo. You can pass
    in any function and runch batches.*

    Examples
    --------
    >>> def experiment_runner(sweep_args):
    ...     for key in sweep_args:
    ...         print(key,sweep_args[key])
    ...
    ... data_path = "data/sim_sweep"
    ... batchsim = somosweep.BatchSimulation()
    ... batchsim.load_run_list(data_path, recalculate=True)
    ... batchsim.run_from_function(
    ...     run_function=experiment_runner,
    ...     parallel=True,
    ...     num_processes=None,
    ... )
    """
    def __init__(self):
        self.num_cpus = os.cpu_count()
        self.tmp_path = "_tmp"


    def mute(self):
        """
        Mute the terminal output
        """
        sys.stdout = open(os.devnull, "w")


    def _run_parallel(self, run_function, num_processes=None):
        """
        Run the batch with parallel processing

        Parameters
        ----------
        run_function : function
            A function (or class with __call__ function defined)
            that runs your experiment.
        num_processes : int
            Number of separate processes to spawn. Default one
            process per CPU core.

        Returns
        -------
        success : bool
            Success flag (was everything successful?)
        """

        # Use all processors
        if num_processes is None:
            num_processes = self.num_cpus

        elif num_processes > self.num_cpus:
            print(
                "WARNING: Using %d processes on %d CPUs"
                % (num_processes, self.num_cpus)
            )

        pool = mp.Pool(num_processes)
        pool.map(run_function, self.run_params, 1)

        return True

    def _run_sequential(self, run_function):
        """
        Explicitly run the batch sequentially in a loop

        Parameters
        ----------
        run_function : function
            A function (or class with __call__ function defined)
            that runs your experiment.

        Returns
        -------
        success : bool
            Success flag (was everything successful?)
        """

        for param_set in self.run_params:
            run_function(param_set)

        return True

    def load_run_list(self, run_folder, recalculate=False):
        """
        Load the run todo list from a file

        Parameters
        ----------
        run_folder : str
            The top-level folder of the sweep (where the run todo
            list is stored)
        recalculate : bool
            Decide whether to overwrite existing data. If False,
            runs with existing data are skipped.
        """

        todo_filename="_runs_todo.yaml"
        runs_todo = iter_utils.load_yaml(os.path.join(run_folder, todo_filename))
        self._generate_run_params(runs_todo,recalculate)
    
    
    def set_run_list(self, run_list, recalculate=False):
        """
        Set the run todo list directly

        Parameters
        ----------
        run_list : list
            List of run config file names
        recalculate : bool
            Decide whether to overwrite existing data. If False,
            runs with existing data are skipped.
        """
        self._generate_run_params(run_list, recalculate)


    def _generate_run_params(self, runs_todo, recalculate):
        """
        Generate the run parameter list with correct arguments

        Parameters
        ----------
        run_list : list
            List of run config file names
        recalculate : bool
            Decide whether to overwrite existing data. If False,
            runs with existing data are skipped.
        """
        self.run_params = [
            {"filename": run, "index": idx, "replace": recalculate, "tmp_path": self.tmp_path}
            for run, idx in zip(runs_todo, range(len(runs_todo)))
        ]


    def run_from_function(self, run_function, parallel=False, num_processes=None):
        """
        Run experiments from a function (or suitable Class)

        Parameters
        ----------
        run_function : function
            A function (or class with __call__ function defined)
            that runs your experiment.
            
        parallel : bool
            Decide whether to use parallel processing
        num_processes : int
            If using parallel processing, set the number of separate
            processes to spawn. Default is one process per CPU core.

        Raises
        ------
        ValueError
            If the number of processes is less than 1
        """
        # Check inputs
        if (num_processes is not None) and parallel:
            if num_processes<1:
                raise ValueError("The number of processes must be at least 1")
        
        # Run experiments
        try:
            iter_utils.add_tmp(self.tmp_path)
            start = time.time()
            if parallel:
                self._run_parallel(run_function, num_processes)
            else:
                self._run_sequential(run_function)

            end = time.time()
            iter_utils.delete_tmp(self.tmp_path)

            print("____________________________")
            print(
                "TOTAL TIME: %0.1f sec (%0.2f min)"
                % ((end - start), (end - start) / 60)
            )
            print("____________________________")

        except KeyboardInterrupt:
            print("\n" + "BATCH TERMINATED EARLY")
            iter_utils.delete_tmp(self.tmp_path)
