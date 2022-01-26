# Be sure to run this file from the "region_of_acquisition" folder
#     cd examples/region_of_acquisition
#
import os
import yaml
import numpy as np
import itertools
import copy
from functools import reduce  # forward compatibility for Python 3
import operator
import warnings

from somosweep import iter_utils


class RunGenerator:
    """
    Set up a sweep by autogenerating the correct
    filestructure and config files

    Attributes
    ----------
    data_path : str
        Path to the desired save location

    Examples
    --------
    >>> data_path = "data/sim_sweep"
    ... sweep_config = 'sweeps/sweep.yaml'
    ... run_gen = somosweep.RunGenerator(data_path)
    ... run_gen.from_file(sweep_config)
    """
    def __init__(self, data_path):
        self.data_path = os.path.abspath(data_path)


    def from_file(self, config_file):
        """
        Generate a set of run configs using a sweep config

        Parameters
        ----------
        config_file : str
            Filename of the desired config file
        """
        # Read in the configuration and get relavant parameters
        self.config = iter_utils.load_yaml(config_file)
        self.setup = self.config.get("setup", {})
        self.todo_filename = "_runs_todo.yaml"

        if self.setup.get("slices_2d", False):
            warnings.warn("Generating 2D slices is no longer supported. \
               Using simple generation instead. \
               You can use pandas to slice data afterward")

        # Generate the runs
        print("Generating run configs")
        self.make_simple(self.config)


    def generate_params(self, config):
        """
        Generate all permutations of a given set of sweep parameters

        Parameters
        ----------
        config : dict
            Sweep config dictionary to use

        Returns
        -------
        param_list : itertools.product
            A itrable object with all parameter sets (permutations of
            parameter values)
        name_list : list
            List of all parameter names (in the order the permutation
            is generated)
        permute_list : list(list)
            The list of parameter values, one inner list for each parameter.
            This list is used to generate ``param_list``
        """

        # Generate filename
        folder = self.data_path

        # Read in the sweep parameters
        sweep = config["sweep"]

        # Generate the speed parameter matrix
        name_list = []
        permute_list = []
        for var in sweep:
            name_list.append(iter_utils.parse_variable_name(var["variable"]))
            vals = var.get("values", None)
            folder_iter = var.get("folder", None)

            # Process direct values
            if isinstance(vals, list):
                permute_list.append(vals)

            # Process folder iterator
            elif isinstance(folder_iter, str):
                blacklist = var.get("file_blacklist", None)
                filter_extensions = var.get("filetypes_to_use", None)

                val_list = iter_utils.scrape_folder(
                    folder_iter, filter_extensions, blacklist
                )

                if len(val_list) != 0:
                    permute_list.append(val_list)

            # Process numeric value vector
            elif vals is None:
                permute_list.append(
                    np.linspace(var["min"], var["max"], var["num_steps"]).tolist()
                )

            else:
                raise

        param_list = itertools.product(*permute_list)

        return param_list, name_list, permute_list


    def make_simple(self, config, save_todo=True):
        """
        Make a simple set of runs using all permutations of sweep parameters

        Parameters
        ----------
        config : dict
            Sweep config file to use
        save_todo : bool
            Decide whether to save the list of runs to do in a file.

        Returns
        -------
        run_names : list
            List of filenames for every config file generated.
        """
        # Save a copy of the sweep config in the root folder
        if not os.path.exists(os.path.join(self.data_path)):
            os.makedirs(os.path.join(self.data_path))

        out_filename = os.path.join(self.data_path, "config.yaml")
        iter_utils.save_yaml(config, out_filename)

        # Generate parameters
        param_list, name_list, _ = self.generate_params(config)

        # Create all of the individual config files, and store them in folders
        run_names = []
        for set_num, param_set in enumerate(param_list):
            config_new = copy.deepcopy(config)
            if config_new.get("save",None) is None:
                config_new['save'] = {}
            config_new.pop("sweep", None)
            for idx, param in enumerate(param_set):
                var_name = name_list[idx]
                iter_utils.set_in_dict(config_new, var_name, param)

            config_new["save"]["run_name"] = "param_set_%04d" % (set_num)
            _, out_folder = iter_utils.generate_save_location(config_new, self.data_path)
            run_filename = os.path.join(out_folder, "params.yaml")
            iter_utils.save_yaml(config_new, run_filename)

            run_names.append(run_filename)

        print(" --> with %d unique parameter sets"%(len(run_names)))
        # Save the set of runs todo
        if save_todo:
            iter_utils.save_yaml(run_names, os.path.join(self.data_path,self.todo_filename))

        return run_names