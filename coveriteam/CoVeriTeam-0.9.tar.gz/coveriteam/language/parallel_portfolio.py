# This file is part of CoVeriTeam, a tool for on-demand composition of cooperative verification systems:
# https://gitlab.com/sosy-lab/software/coveriteam
#
# SPDX-FileCopyrightText: 2020 Dirk Beyer <https://www.sosy-lab.org>
#
# SPDX-License-Identifier: Apache-2.0

import logging
import multiprocessing as mp
import signal
import subprocess as sp
import sys
import traceback
from queue import Queue
from textwrap import indent
from typing import List

import pkg_resources

from coveriteam import util
from coveriteam.language import CoVeriLangException
from coveriteam.language.actor import Actor
from coveriteam.language.composition import CompositeActor
from coveriteam.language.mpi_execution import constants
from coveriteam.language.mpi_execution.mpi_util import Settings
from coveriteam.language.mpi_execution.process_sync import QueueManager
from coveriteam.language.mpi_execution.command_building import get_command
from benchexec.result import RESULT_CLASS_FALSE  # noqa: F401,F403,E261
from benchexec.result import RESULT_CLASS_TRUE  # noqa: F401,F403,E261
from coveriteam.language.artifact import *  # noqa F401, F403


class ParallelPortfolio(CompositeActor):
    """
    This class is a Portfolio Composition. It will execute all given actors in parallel and the first
    acceptable result (e.g true or false) will be returned.
    """

    actors: list
    _input_artifact: dict
    _output_artifacts: dict
    counter: int = 0
    success_condition: str

    settings: Settings

    _mpi_found: bool

    EXECUTING_USING_MPI = 1
    EXECUTING_USING_MULTIPROCESSING = 2
    NOT_EXECUTING = 0

    default_success_condition = "verdict in [RESULT_CLASS_TRUE, RESULT_CLASS_FALSE]"

    execution_status: int = NOT_EXECUTING

    def __init__(
        self, actor_list: List[Actor], success_condition=default_success_condition
    ):
        self.__type_check(actor_list)
        self.actors = actor_list

        if not isinstance(success_condition, str):
            raise CoVeriLangException(f"{success_condition} has to be a string")

        self.success_condition = success_condition

        # Type check successful, so every actor requires and produces the same artifacts
        self._input_artifacts = actor_list[0].get_input_artifacts()
        self._output_artifacts = actor_list[0].get_output_artifacts()

        self.settings = Settings(
            log_level=logging.root.level,
            data_model=Actor.data_model,
            trust_tool_info=Actor.trust_tool_info,
            cache_dir=util.get_INSTALL_DIR().parent,
        )

        # Check for MPI implementation
        self._mpi_found = shutil.which("mpiexec") is not None

        # Check for installed mpi4py
        self._mpi4py_found = "mpi4py" in {pkg.key for pkg in pkg_resources.working_set}

    def _act(self, **kwargs):
        # Resetting the counter, because of the possible reuse of this portfolio
        self.counter = 0

        # In this case, we are in an MPI environment, so there is no need
        # to spawn a new one, just execute this portfolio with the scheduler.
        if util.CURRENTLY_IN_MPI:
            # Scheduler import is only possible in an active MPI environment,
            # that's why it's imported here
            from coveriteam.language.mpi_execution.mpi_scheduler import Scheduler

            return Scheduler().main(portfolio=self, kwargs=kwargs)

        if self._mpi_found and self._mpi4py_found and not util.USE_PYTHON_PROCESSES:
            return self._execute_in_mpi_env(**kwargs)

        if util.USE_PYTHON_PROCESSES:
            logging.info(
                "Executing portfolio with standard python processes, according to the user input"
            )
        elif not self._mpi4py_found:
            logging.warning(
                "I didn't find mpi4py installed for this interpreter. "
                "Now using the fallback mechanism: executing using python subprocesses"
            )
        else:
            logging.warning(
                "I didn't find any MPI executable on this machine. "
                "Now using the fallback mechanism: executing using python subprocesses"
            )
        return self._execute_with_python_processes(**kwargs)

    def __str__(self):
        all_actors_as_string: str = ""
        for actor in self.actors:
            all_actors_as_string += indent(str(actor), "\t") + "\n"

        return (
            "\nPORTFOLIO"
            + self.__get_actor_type_str__()
            + "\n"
            + all_actors_as_string[:-1]
        )

    def termination_reached(self, actor_result) -> bool:
        """
        Checks if the termination expression is satisfied OR all actors have provided any result.
        Input for the termination expression is only the produced result.
        """
        # Prevent crash of whole execution, if something is wrong with the produced results.
        try:
            result = eval(self.success_condition, None, actor_result)  # noqa S307
        except TypeError as type_error:
            logging.warning(
                f"Error on evaluating "
                f"{self.success_condition} on {actor_result} \n"
                f"Error: {type_error}"
            )
            result = False

        return (
            # It is import to always check the amount of results, otherwise the
            # program will never stop, if the termination_expression is never satisfied.
            result
            or self.counter == len(self.actors)
        )

    def stop(self):
        if self.execution_status == self.EXECUTING_USING_MPI:
            self.mpi_process.terminate()
        elif self.execution_status == self.EXECUTING_USING_MULTIPROCESSING:
            for process in self.processes:
                process.terminate()

    def __type_check(self, actor_list: List[Actor]):
        """
        It is sufficient to check every input and output artifacts of the actors in the given list
        with the first actor. When this method doesn't raise an Exception, every actor in this list
        requires the same input artifacts and produces the same type of output artifacts.
        """
        # It is possible to create a portfolio with a single actor.
        if len(actor_list) == 1:
            return

        for actor in actor_list[1:]:
            if actor.get_input_artifacts() != actor_list[0].get_input_artifacts():
                raise CoVeriLangException(
                    f"Type check failed for Portfolio composition. "
                    f"Actor {actor.name()}'s required input artifacts "
                    f"are clashing with {actor_list[0].name()}'s artifacts"
                )
            if actor.get_output_artifacts() != actor_list[0].get_output_artifacts():
                raise CoVeriLangException(
                    f"Type check failed for Portfolio composition. "
                    f"Actor {actor.name()}'s output artifacts "
                    f"are clashing with {actor_list[0].name()}'s artifacts"
                )

    def _execute_in_mpi_env(self, **kwargs):
        """
        This method will execute the portfolio in an MPI environment.
        A new MPI process is spawned and this portfolio and its arguments are given to this process.
        """
        self.execution_status = self.EXECUTING_USING_MPI
        self._setup_synchronization(kwargs)

        # Environment configuration for the mpi process.
        mpi_env = os.environ.copy()
        mpi_env[constants.ENV_NAME] = ":".join(sys.path)
        mpi_env[constants.PORT] = str(QueueManager.server_port)
        mpi_env[constants.AUTH_CODE] = QueueManager.auth_code

        logging.debug("Creating new MPI environment")

        # Entering the MPI environment
        self.mpi_process = sp.Popen(
            [*get_command()],
            env=mpi_env,
        )

        queue = QueueManager.get_server_queue()

        # Wait until queue is empty to start the blocking get with the result of the mpi_execution
        queue.join()

        # Wait until the mpi execution finished
        self.mpi_process.wait()

        # Receive result. Note: There MUST be a result, otherwise this is blocking eternally
        res = queue.get()

        QueueManager.stop_server()

        if isinstance(res, Exception):
            raise res

        self.execution_status = self.NOT_EXECUTING
        return res

    def _setup_synchronization(self, kwargs):
        QueueManager.create_server(Queue())
        QueueManager.get_server_queue().put((self, kwargs))

    def _execute_with_python_processes(self, **kwargs):
        """
        Method to execute this portfolio with standard python processes from multiprocessing.
        It will return the first true or false from any actor or the last value, when no actor returns true or false
        """
        self.execution_status = self.EXECUTING_USING_MULTIPROCESSING
        self.manager = mp.Manager()
        self.finished_actor = self.manager.list()

        self.result_queue: mp.Queue = self.manager.Queue(maxsize=len(self.actors))

        self.processes = []
        finished_res = {}
        count: int = 0

        # process creation
        for actor in self.actors:
            self.processes.append(
                mp.Process(
                    target=self._execute_actor_in_process,
                    args=(actor, self.result_queue),
                    kwargs=kwargs,
                )
            )

        # process start
        for process in self.processes:
            process.start()

        def get_verdict():
            """
            Evaluates the verdict and counting all verdicts.
            True, when execution has to stop
            """
            nonlocal finished_res, count
            self.counter += 1

            finished_res = self.result_queue.get()
            self.result_queue.task_done()

            return self.termination_reached(finished_res)

        while not get_verdict():
            logging.debug(f"Received result {finished_res}")

        for process in self.processes:
            process.terminate()

        for process in self.processes:
            process.join()

        logging.debug(f"Finished processes are: {self.finished_actor}")
        self.execution_status = self.NOT_EXECUTING
        return finished_res

    def _execute_actor_in_process(self, *args, **kwargs):
        """
        Executed method in process, when using standard multiprocessing
        args[0] is the actor,
        """

        # Setup signal handler to listen to stop signal from main CoVeriTeam process
        signal.signal(signal.SIGTERM, lambda signum, frame: actor.stop())

        actor = args[0]
        result_queue: mp.Queue = args[1]

        kwargs1 = self.forward_artifacts(kwargs, {}, actor.get_input_artifacts())

        try:
            result_queue.put(actor.act(**kwargs1))
        except (SystemExit, Exception) as e:
            traceback.print_exc()
            result_queue.put(e)

        self.finished_actor.append(
            f"{actor.name()} finished with process number {mp.current_process().pid}"
        )
