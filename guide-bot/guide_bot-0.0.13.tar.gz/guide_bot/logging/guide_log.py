import os

from guide_bot.parameters.instrument_parameters import FreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import RelativeFreeInstrumentParameter
from guide_bot.parameters.instrument_parameters import FixedInstrumentParameter
from guide_bot.parameters.instrument_parameters import DependentInstrumentParameter


class RunInfo:
    """
    Container for information from a single optimization step

    Saves the optimizer state and figure of merit from a step in the
    optimization.
    """

    def __init__(self, optimized_x, fom):
        self.optimized_x = optimized_x
        self.fom = fom


class History:
    """
    Container for RunInfo instances for each step in the optimization

    Keeps a history of optimizer states and figure of merits organized in
    RunInfo instances.
    """

    def __init__(self):
        """
        Starts a history container
        """
        self.histories = []

    def add_run_info(self, optimized_x, fom):
        """
        Appends information to the history

        Parameters
        ----------

        optimized_x : list
            Optimizer state, list of values for each free parameter

        fom : float
            Figure of merit attained by optimized_x state
        """
        self.histories.append(RunInfo(optimized_x, fom))


class LogFile:
    def __init__(self, filename):
        # check filename is available, otherwise change it
        if os.path.isdir(filename):
            counter = 0
            new_name = filename + "_" + str(counter)
            while os.path.isdir(new_name):
                counter = counter + 1
                new_name = filename + "_" + str(counter)

        self.filename = filename

        # Start file
        with open(self.filename, "w") as file:
            file.write("Log file from python guide_bot\n")

        self.parameter_names = None

    def write_header(self, instr_parameters, scan_name):
        self.parameter_names = [par.name for par in instr_parameters.all_parameters]

        with open(self.filename, "a") as file:
            file.write("scan_name: " + scan_name + "\n")
            file.write(str(len(self.parameter_names)) + "\n")
            for par in instr_parameters.all_parameters:
                file.write(par.name.ljust(50) + "\t")
                if par.category is None:
                    file.write(" " * 20)
                else:
                    file.write(par.category.ljust(20))

                file.write(type(par).__name__.ljust(40))

                if isinstance(par, RelativeFreeInstrumentParameter):
                    file.write(str(par.static_lower) + ", " + str(par.static_upper))
                elif isinstance(par, FreeInstrumentParameter):
                    file.write(str(par.get_lower_bound()) + ", " + str(par.get_upper_bound()))

                file.write("\n")

            file.write("FOM" + " \t")
            file.write("sim_start_t" + " \t")
            file.write("sim_end_t" + " \t")
            for par_name in self.parameter_names:
                file.write(par_name + " \t")
            file.write("\n")

    def write_parameter_line(self, fom, t_start, t_end, parameter_dict):
        with open(self.filename, "a") as file:
            file.write(str(fom) + " \t")

            file.write(str(t_start) + "\t")
            file.write(str(t_end) + "\t")

            for parameter_name in self.parameter_names:
                value = parameter_dict[parameter_name]
                file.write(str(value) + " \t")
            file.write("\n")
