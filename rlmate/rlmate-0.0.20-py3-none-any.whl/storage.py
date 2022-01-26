import os
import sys
import importlib
import shutil
import logging
from datetime import datetime
from pathlib import Path
import itertools
import contextlib
import time
import numpy as np
import torch
import pandas as pd
import matplotlib

# path_to_hermes = pathlib.Path(__file__).parent.resolve().joinpath("..")
# sys.path.append(str(path_to_hermes))
from .core import bot
from .core import settings as st
from .result import Result
from . import plot as hplt

import git


def _is_loaded(module_name: str) -> bool:
    return module_name in sys.modules


# https://stackoverflow.com/questions/14989858/get-the-current-git-hash-in-a-python-script
def get_current_commit_hash(default_commit="00000"):
    """Provided a repo return the hash of commit HEAD points to

    :param repo: git.Repo
    """
    try:
        repo = git.Repo(".", search_parent_directories=True)
    except:
        logging.warning("Unable to retrieve commit hash for repo head")
        return default_commit
    try:
        return repo.head.object.hexsha
    except:
        try:
            return repo.head.commit.hexsha
        except:
            logging.warning("Unable to retrieve commit hash for repo head")
            return default_commit


class Experiment:
    """Experiment class mainly taking care of storage. Every instance of the class will be unqiuely
    associated with a specific experiment directory and a script that was executed
    as part of the experiment.

    Experiment instances are used for the storage of important information, e.g. when it was executed,
    what were the command line arguments passed to the experiment script, what kind of data/results were generated
    during experiment execution, (...).

    It also provides ways of loading experiments from disk and methods for convenient access to the experiment
    information.
    """

    # FIELD NAME CONSTANTS
    COMMIT_HASH_N = "commit_hash"
    START_TIME_N = "start_time"
    END_TIME_N = "end_time"
    EXECUTION_TIME_N = "execution_time"
    COMMENT_N = "comments"

    # FILE NAME CONSTANTS
    INFO_FILE_NAME = "hermes.info"
    RE_EXECUTION_FN = "re_execution.hermes"
    SCRIPT_OPTIONS_FN = "exec_arguments"
    STDOUT_FN = "stdout.log"
    STDERR_FN = "stderr.log"

    TIME_FMT = "%Y_%m_%d_%H%M%S%f"

    def __init__(self, identifier, path_to_experiment, commit_hash, start_time):
        """This constructor should NEVER be used explicitly
        Use the classmethods Experiment.new when creating new experiments
        and Experiment.load when accessing finished experiments.

        :param identifier: the unqiue experiment identifier as a string
        :param path_to_experiment: the unique directory (as string or path-like object),
               built from the identifier, the script that was executed and the hermes experiments path.
        :param commit_hash: hash of the commit that was observed when running the script as string
        :param start_time: the time when this Experiment was created as datetime object
        """
        self.identifier = identifier
        self.path_to_experiment = Path(path_to_experiment)
        self.commit_hash = commit_hash
        self.start_time = start_time
        self.options = None

    @classmethod
    def new(cls, script_name, execution_file, job_idx, experiment_name):
        """
        **This method is used internally by CLI Hermes and not intended to be used outside of that scope.**

        Create a new Experiment instance for some job about to be executed

        :meta private:

        :param script_name: The name of the script the job takes care of as string
        :param execution_file: The ExecutionFile object (as created from some .hermes file) that is currently being handled
        :param job_idx: The execution index of the job as int
        :param experiment_name: name of the experiment as string. If provided this included in the experiment identifier
        """

        # get data relevant at start of experiment
        start_time = datetime.now()
        settings = execution_file.settings
        commit_hash = get_current_commit_hash()

        # check if experiments directory exists, if not make it
        path_to_experiments = Path(settings["path_to_experiments"])
        path_to_experiments = path_to_experiments.joinpath("experiments")
        if not os.path.exists(path_to_experiments):
            logging.info("Creating new directory %s" % path_to_experiments)
            os.mkdir(path_to_experiments)

        # check if [...]/experiments/script_name exists, if not create it
        script_name = script_name.replace(".py", "").lstrip().rstrip()
        path_to_script_directory = path_to_experiments.joinpath(script_name)
        if not path_to_script_directory.exists():
            logging.info("Creating script directory %s" % path_to_script_directory)
            try:
                os.mkdir(path_to_script_directory)
            except FileExistsError:
                # data race doesnt matter
                logging.warning(
                    "Script directory %s already exists, skipping creation."
                    % path_to_script_directory
                )

        # create directory [...]/experiments/script_name/experimentname
        path_to_experiment = path_to_script_directory.joinpath(experiment_name)
        if not path_to_experiment.exists():
            logging.info("Creating experiment directory %s" % path_to_experiment)
            os.mkdir(path_to_experiment)
            try:
                os.mkdir(path_to_experiment)
            except FileExistsError:
                # data race doesnt matter
                logging.warning(
                    "Experiment directory %s already exists, skipping creation"
                    % path_to_experiment
                )

        # create directory [...]/experiments/script_name/experimentname/date_commitnumber[4]
        # if it already exists throw an error
        experiment_identifier = [
            start_time.strftime(Experiment.TIME_FMT),
            str(job_idx),
            commit_hash[-5:],
        ]
        experiment_identifier = "_".join(experiment_identifier)
        path_to_experiment = path_to_experiment.joinpath(experiment_identifier)
        if path_to_experiment.exists():
            logging.error(
                "Cannot create new Experiment - Experiment Directory already exists: %s",
                path_to_experiment,
            )
        logging.info("Creating job directory %s", path_to_experiment)
        os.mkdir(path_to_experiment)

        experiment = cls(
            experiment_identifier, path_to_experiment, commit_hash, start_time
        )
        options = execution_file.get_hermes_options(job_idx)
        experiment.set_options(options)

        # store execution file in info
        reexec_file_destination = experiment.file(Experiment.RE_EXECUTION_FN)
        execution_file.create_single_execution_hermesfile(
            reexec_file_destination, job_idx
        )

        # store commit hash in info
        experiment._add_to_info(Experiment.COMMIT_HASH_N, commit_hash)

        # copy before execution
        experiment._copy_files_before_execution()

        # store options given in script
        args = execution_file.get_exec_arguments(job_idx)
        experiment.store_script_arguments(*args)

        # touch log files
        experiment.file(Experiment.STDOUT_FN).touch()
        experiment.file(Experiment.STDERR_FN).touch()

        return experiment

    @classmethod
    def load(cls, path_to_experiment):
        """
        Create an Experiment object for a finished experiment

        :param path_to_experiment:
        :type path_to_experiment: Union[str, os.PathLike]
        """
        assert Experiment.is_experiment(
            path_to_experiment
        ), "The given path does not store any hermes experiment"
        p = Path(path_to_experiment)
        identifier = str(p.parts[-1])
        info = Experiment.read_info(path_to_experiment)
        commit_hash = info["commit_hash"]
        try:
            start_time = datetime.strptime(info["start_time"], Experiment.TIME_FMT)
        except:
            try:
                start_time = float(info["start_time"])
                logging.info(
                    "Failed to load experiment start time as datetime object, loaded as floating point number instead."
                )
            except:
                start_time = None
                logging.warning("Failed to load experiment start time.")

        experiment = cls(identifier, path_to_experiment, commit_hash, start_time)

        return experiment

    @property
    def exec_args(self):
        """
        A set of the execution arguments that were stored for this experiment, e.g.
        {"-lr 0.001", "--gradclip"}

        :return: The set of execution arguments
        :rtype: set[str]
        """
        if hasattr(self, "_exec_args"):
            return self._exec_args
        else:
            with open(
                self.path_to_experiment.joinpath(Experiment.SCRIPT_OPTIONS_FN), "r"
            ) as f:
                lines = f.readlines()
            lines = [
                line.rstrip().lstrip()
                for line in lines
                if len(line.replace(" ", "")) > 0
            ]
            self._exec_args = set(lines)
            return self._exec_args

    @property
    def exec_args_dict(self):
        """
        A dictionary mapping execution argument names to values as specified in the execution file used to run this experiment.

        :return: The execution argument dictionay
        :rtype: dict[str, Any]
        """
        if hasattr(self, "_exec_args_dict"):
            return self._exec_args_dict
        else:
            self._exec_args_dict = {}
            for arg in self.exec_args:
                aux = arg.split(" ")
                if len(aux) <= 1:
                    key = aux[0]
                    val = True
                elif len(aux) == 2:
                    key, val = aux
                    try:
                        val = float(val)
                    except:
                        val = str(val)
                elif len(aux) > 2:
                    logging.warning("Unknown exec argument format: %s" % arg)
                    key = aux[0]
                    vals = aux[1:]
                    try:
                        val = [int(val) for val in vals]
                    except:
                        try:
                            val = [float(val) for val in vals]
                        except:
                            val = [str(val) for val in vals]
                if key in self._exec_args_dict:
                    try:
                        self._exec_args_dict[key].append(val)
                    except:
                        self._exec_args_dict[key] = [self._exec_args_dict[key], val]
                else:
                    self._exec_args_dict[key] = val
            return self._exec_args_dict

    @property
    def scores_file(self):
        """
        Returns the path to the scores file stored in this experiment as a pathlib.Path
        """
        return self.file("%s.scores" % self.identifier)

    def file(self, file):
        """

        :param file: Name of a file
        :type file: Union[str, os.PathLike]

        :return: the path to the file in the experiment directory
        :rtype: pathlib.Path
        """
        return self.path_to_experiment.joinpath(file)

    def load_state_dict(self, pth_name, net=None):
        """
        Load a state dictionary

        :param pth_name: .pth state dict file name
        :type pth_name: str

        :param net: optionally load state dict into this network module
        :type net: torch.nn.Module, optional
        """
        pth_file = self.file(pth_name)

        try:
            device = net.device
        except:
            device = torch.device("cpu")

        try:
            state_dict = torch.load(pth_file, map_location=device)
        except FileNotFoundError:
            logging.critical("Unable to find this pth file.")
            return None
        if net is None:
            return state_dict
        else:
            net.load_state_dict(state_dict)
            net.eval()
            return net

    def list_pth_files(self):
        """
        Return a list of all .pth files (i.e. pytorch state dictionaries) within the experiment directory

        :return: the list
        :rtype: list[str]
        """
        return list(pth_path.name for pth_path in self.path_to_experiment.glob("*.pth"))

    def scores(self):
        """
        Loads the scores from the experiments' scores file

        :return: The scores
        :rtype: numpy.ndarray
        """
        try:
            with open(self.scores_file, "r") as f:
                return np.array([float(line) for line in f])
        except FileNotFoundError:
            logging.error(
                "Tried to load scores, but not scores file %s was not found."
                % self.scores_file
            )

    @property
    def result(self):
        """
        Load the pyhermes result associated with this experiment, if it exists
        :return: pyhermes.result.Result
        :raises RuntimeError: if the experiment does not contain a pyhermes result
        """
        if hasattr(self, "_result"):
            return self._result
        else:
            result_files = list(self.path_to_experiment.glob("*.result"))
            if len(result_files) == 0:
                raise RuntimeError("Experiment does not contain a pyhermes result")
            if len(result_files) > 1:
                logging.warning(
                    "Experiment contains more than one result file, loading the first one only"
                )
            self._result = Result.load(result_files[0])
            return self._result

    def load_network_class(self, keys=["--neural_network_file", "-nnf"], default="fcn"):
        # always extend path to experiment directory to load copied files from there.
        path = str(self.path_to_experiment.absolute())
        sys.path.append(path)
        if all(key not in self.exec_args_dict for key in keys):
            logging.warning(
                "Experiment at path %s does not specify neural network file in exec args (given keys %s). Using default network name."
                % (self.path_to_experiment, str(keys))
            )
            name = default
            network_module = importlib.import_module(name)
            return network_module.Network

        network_classes = dict()
        for key in keys:
            if key not in self.exec_args_dict:
                continue
            nnf_string = self.exec_args_dict[key]
            if not nnf_string.endswith(".py"):
                nnf_string += ".py"
            nnf = Path(nnf_string)
            possible_paths = [nnf]
            try:
                nnf_string_short = nnf_string.split(".")[-2] + ".py"
                possible_paths.append(Path(nnf_string_short))
            except:
                pass

            for possible_path in possible_paths:
                print(possible_path)

                try:
                    network_module = importlib.import_module(possible_path.stem)
                    network_classes[key] = network_module.Network
                except:
                    continue

        if len(network_classes) == 1:
            return list(network_classes.values())[0]
        elif len(network_classes) == 0:
            logging.warning(
                "Unable to load any network classes from %s." % self.path_to_experiment
            )
            return None
        else:
            return network_classes

    @staticmethod
    def is_experiment(path):
        """
        Check if a given directory represents a hermes experiment.

        :param path: path to the directory
        :type path: Union[str, os.PathLike]

        :return: whether the path represents an experiment
        :rtype: bool
        """
        p = Path(path)
        assert p.exists(), "Path must exist"
        return p.is_dir() and len(list(p.glob("hermes.info"))) >= 1

    @staticmethod
    def load_all(path):
        """
        Iterate over all subdirectories of a given parent directory and load all experiments from present experiment directories

        :param path: The parent directory.

        :return: A list of experiment
        :rtype: ExperimentList
        """
        p = Path(path)
        return ExperimentList(
            Experiment.load(subpath)
            for subpath in p.iterdir()
            if Experiment.is_experiment(subpath)
        )

    @staticmethod
    def read_info(path_to_experiment):
        """
        Try to read the `hermes.info` of a hermes experiment directory and return it as dictionary

        :param path_to_experiment: path to the experiment directory
        :type path_to_experiment: Union[str, os.PathLike]

        :return: experiment info
        :rtype: dict[str, str]
        """
        with open(os.path.join(path_to_experiment, "hermes.info"), "r") as f:
            info = dict()
            for line in f.readlines():
                key, val = line.split(":")
                info[key] = val
        return info

    @property
    def info_dict(self):
        """
        Similar to :func:`~Experiment.read_info`, but as instance property rather than staticmethod

        :return: experiment info
        :rtype: dict[str, str]
        """
        if hasattr(self, "_info_dict"):
            return self._info_dict
        else:
            self._info_dict = Experiment.read_info(self.path_to_experiment)
            return self._info_dict

    @contextlib.contextmanager
    def open_log_files(self, mode="r+"):
        """
        Context manager for opening the STDOUT and STDERR log files.

        Usage:

        .. code-block:: python

           from pyhermes.storage import Experiment
           exp = Experiment.load(...)
           with exp.open_log_files(mode='r') as f_stdout, f_stderr:
              # do stuff

        :param mode: The filemode e.g. 'w', 'a', ... Defaults to 'r+'.
        """
        f_stdout = open(self.file(Experiment.STDOUT_FN), mode)
        f_stderr = open(self.file(Experiment.STDERR_FN), mode)
        yield f_stdout, f_stderr
        f_stdout.close()
        f_stderr.close()

    @contextlib.contextmanager
    def open_stderr_file(self, mode="r"):
        """
        Context manager for opening the STDERR file only

        :param mode: The filemode e.g. 'w', 'a', ... Defaults to 'r+'.
        """
        f_stderr = open(self.file(Experiment.STDERR_FN), mode)
        yield f_stderr
        f_stderr.close()

    def store_script_arguments(self, positionals, flags, options, mode="w"):
        """
        Store the scripts options/parameters (e.g. -lr 0.005) in human-readable form

        :param positionals:
        :param flags:
        :param options: a dictionary created by ExecutionFile.get_job_options

        :meta private:
        """
        with open(self.file(Experiment.SCRIPT_OPTIONS_FN), mode) as f:
            for positional in positionals:
                f.write("%s\n" % positional)
            for flag in flags:
                f.write("%s\n" % flag)
            for option, value in options.items():
                f.write("%s %s\n" % (option, value))

    def append_script_argument(self, positionals=None, flags=None, options=None):
        self.store_script_arguments(positionals, flags, options, mode="a")

    def _copy_files_before_execution(self):
        """
        Called by Experiment.new. Copies files specified with -cb hermes option
        :meta private:
        """
        for file_name in self.options.cb:
            self.copy_file(file_name)

    def _copy_files_after_execution(self):
        """
        Called by Experiment.report. Copies files specified with -ca hermes option
        :meta private:
        """
        for file_name in self.options.ca:
            self.copy_file(file_name)

    def _move_files_after_execution(self):
        """
        Called by Experiment.report. Moves files specified with -ma hermes option
        :meta private:
        """
        for file_name in self.options.ma:
            self.move_file(file_name)

    def store_comments(self):
        """
        Store comments given by -c option either through main call or hermes option
        :meta private:
        """
        self._add_to_info(
            Experiment.COMMENT_N, ",".join(cmt for cmt in self.options.comment)
        )

    def set_options(self, options):
        """Setter for hermes options. Called by Experiment.new

        :param options: A Namespace object as returned by ExecutionFile.hermes_option_parser and Experiment.union_options
        :meta private:
        """
        self.options = options

    def get_identifier(self):
        """

        :return: the unique hermes identifier assigned to this experiment
        :rtype: str
        """
        return self.identifier

    def copy_file(self, path_to_file, new_file_name=None):
        """Method to copy a file to the unique experiment directory.

        :param path_to_file: A string or path-like object
        :param new_file_name: Optional new name for the copy. If None, the basename of
               path_to_file is used.
        :meta private:
        """
        file_name = new_file_name if new_file_name else os.path.basename(path_to_file)
        if not os.path.exists(path_to_file):
            logging.error(
                "File to be copied to experiment directory %s does not exist: %s",
                self.path_to_experiment,
                path_to_file,
            )
        shutil.copyfile(path_to_file, self.file(file_name))

    def move_file(self, path_to_file, new_file_name=None):
        """Method to move a file to the unique epxeriment directory.

        :param path_to_file: A string or path-like object
        :param new_file_name: Optional new name for the moved file. If None, the basename of
               path_to_file is used.
        :meta private:
        """
        file_name = new_file_name if new_file_name else os.path.basename(path_to_file)
        if not os.path.exists(path_to_file):
            logging.error(
                "File to be moved to experiment directory %s does not exist: %s",
                self.path_to_experiment,
                path_to_file,
            )
        shutil.move(path_to_file, self.file(file_name))

    def _add_to_info(self, key, value):
        """Internal method to add a line "key:value" to the hermes.info file.
        This file captures general information such as execution time, start time, ...

        :param key: The name of the object to be stored as string
        :param value: The object to be stored. Any object that implements __str__
        :meta private:
        """
        with open(self.file(Experiment.INFO_FILE_NAME), "a") as f:
            f.write("%s:%s\n" % (key, str(value)))

    def store_times(self, start_time, end_time):
        """Internal method that stores job start time, end time and execution time (i.e. difference of the former two)

        :param start_time: System time [s] as measured just before job is launched
        :param end_time: System time [s] as measured just after job terminates
        :meta private:
        """
        execution_time = end_time - start_time
        start_time = datetime.fromtimestamp(start_time)
        end_time = datetime.fromtimestamp(end_time)
        self._add_to_info(
            Experiment.START_TIME_N, start_time.strftime(Experiment.TIME_FMT)
        )
        self._add_to_info(
            Experiment.END_TIME_N, end_time.strftime(Experiment.TIME_FMT)
        )
        self._add_to_info(Experiment.EXECUTION_TIME_N, str(execution_time))

    def _fetch_new_files(self):
        """
        Scan the working directory for files containing the experiment identifier
        and move them to the experiment directory
        :meta private:
        """
        dir_list = os.listdir(".")
        for part in dir_list:
            # skip parts of the directory that don't contain the idx
            if self.identifier not in part:
                continue
            self.move_file(part)

    def telegram_notifications(self, start_time, end_time):
        if self.options.message:
            self.bot_handler = bot.Bot_handler()

            message = "Job " + str(self.identifier) + " was completed\n"

            if len(self.exec_args) != 0:
                message += "Options: "
                for opt in self.exec_args:
                    message += str(opt) + " "
                message += "\n"
            else:
                message += "No further options were specified\n"

            message += "Duration: %.2f seconds" % (end_time - start_time)

            if len(self.scores()) != 0:
                pic_path = "tmp_trainingplot.png"
                matplotlib.use("agg")
                hplt.plot_training_progress_from_experiment(self, path=pic_path)

                self.bot_handler.picture(pic_path, caption=message)
                os.remove(pic_path)
            else:
                self.bot_handler.message(message)

    def _report(self, start_time, end_time):
        """
        Called by Execution once the job for this experiment is finished.
        Used to transmit job execution info and makes sure all storage operations
        scheduled to take place after execution are carried out.

        :param start_time: Job start_time
        :param end_time: Job end_time
        :meta private:
        """
        self.store_times(start_time, end_time)
        self._copy_files_after_execution()
        self._move_files_after_execution()
        self._fetch_new_files()
        self.store_comments()
        self.telegram_notifications(start_time, end_time)

    def erase(self):
        logging.info("Erasing job directory %s", self.path_to_experiment)
        shutil.rmtree(self.path_to_experiment)


class ExperimentList(list):
    """
    A wrapper around :python:`list`. Offers some useful functions for selecting/filtering
    loaded experiments. Will be extended in the future.

    These lists are typically created by :meth:`pyhermes.storage.Experiment.load_all`, but you can
    also create them in your own.
    """

    def __init__(self, exp_iterable):
        """
        Create an ExperimentList from given experiments

        :param exp_iterable: an iterable collection of experiments
        :type exp_iterable: Iterable[pyhermes.storage.Experiment]
        """
        super(ExperimentList, self).__init__(exp_iterable)
        assert all(isinstance(itm, Experiment) for itm in self)

    def filter_by_exec_args(self, *args):
        """
        :param args: Argument as strings
        :return: A new experiment list containing only those experiments which have the given args in their exec args set.

        Usage example:

        .. code-block:: python

           from pyhermes.Storage import Experiment
           path = "some path where many experiments are stored"
           experiments = Experiment.load_all(path)
           ddqn_runs = Experiment.filter_by_exec_args("--doubledqn")

        """
        args = set(args)
        return ExperimentList(exp for exp in self if args < exp.exec_args)

    def latest(self):
        """
        This method makes use of the fact hermes tracks the start time of each experiment,

        :return: The most recent experiment within the list
        :rtype: Experiment
        """
        return min(self, key=lambda exp: exp.start_time)


if _is_loaded("pandas") or _is_loaded("pd"):

    class _ExperimentFrame(pd.DataFrame):
        """
        Test doc
        """

        def __init__(self, exp_iterable):
            experiments = list(exp_iterable)
            assert all(isinstance(exp, Experiment) for exp in experiments)
            super(ExperimentFrame, self).__init__(index=range(len(experiments)))

            self["experiments"] = experiments
            union_exec_arg_keys = set(
                itertools.chain(
                    *(list(exp.exec_args_dict.keys()) for exp in experiments)
                )
            )
            for key in union_exec_arg_keys:
                self[key] = [
                    exp.exec_args_dict[key] if key in exp.exec_args_dict else None
                    for exp in experiments
                ]


else:

    class _ExperimentFrame:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("ExperimentFrame class needs pandas as requirement!")


ExperimentFrame = _ExperimentFrame
