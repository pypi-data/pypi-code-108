import sys
import time
import subprocess
import os
import threading
import logging
import pathlib

path_to_hermes = pathlib.Path(__file__).parent.resolve().joinpath("..")
sys.path.append(str(path_to_hermes))
from ..storage import Experiment


class Execution:
    def worker(self, id):
        while True:
            # get the job number
            self.lock.acquire()
            current_job = self.finished_jobs
            self.finished_jobs += 1
            self.lock.release()

            # check whether all jobs are done
            if current_job >= self.job_number:
                return

            # get the job and extract the command
            cmd, options = self.jobs[current_job]

            # extract script_name. If started with ./  its the first word of the command
            # else it is the second one
            if cmd[0][:2] == "./":
                script_name = cmd[0][2:]
                option_start = 1
            else:
                script_name = os.path.basename(cmd[1])
                option_start = 2

            ex = Experiment.new(
                script_name, self.execution_file, current_job, self.experiment_name
            )
            identifier = ex.get_identifier()

            # rebuild command: 1. script start 2. hermes_name 3. std arguments 4. current arguments
            if not os.path.exists(cmd[option_start - 1]):
                raise FileNotFoundError("Script %s not found" % cmd[option_start - 1])

            cmd = (
                cmd[:option_start]
                + [identifier]
                + self.execution_file.get_std_args()
                + cmd[option_start:]
            )
            cmd = " ".join(cmd)

            start = time.time()
            logging.info('Launching job Nr. %d: "%s".', current_job, cmd)
            logging.info(
                "STDOUT and STDERR will be written to %s.",
                "log files" if options.log else "console",
            )
            if options.log:
                with ex.open_log_files() as (f_stdout, f_stderr):
                    completed_process = subprocess.run(
                        cmd, stdout=f_stdout, stderr=f_stderr, shell=True
                    )
            else:
                completed_process = subprocess.run(cmd, shell=True)
            end = time.time()

            if completed_process.returncode == 0:
                logging.info(
                    "Sucessfully finished job Nr. %d %s in %.2f seconds"
                    % (current_job, identifier, (end - start))
                )
            else:
                logging.critical(
                    "Job %s (Nr. %d) terminated after %.2f seconds with exit status %d"
                    % (
                        identifier,
                        current_job,
                        (end - start),
                        completed_process.returncode,
                    )
                )
                if options.log:
                    logging.info("Here is the jobs stderr:")
                    with ex.open_stderr_file() as f_stderr:
                        print(f_stderr.read())

            ex._report(start, end)

            # when debugging we might want to not save the experiment results
            # to prevent clutter and save disk space
            if self.debug:
                ex.erase()

    def run(self):
        start = time.time()
        threads = [
            threading.Thread(target=self.worker, args=[i])
            for i in range(self.num_threads)
        ]
        self.lock = threading.Lock()

        for t in threads:
            t.start()

        for t in threads:
            t.join()

        end = time.time()

    def __init__(self, execution_file, experiment_name=None, debug=False):
        self.execution_file = execution_file
        self.jobs = execution_file.executions
        self.job_number = len(self.jobs)
        self.settings = execution_file.settings
        self.num_threads = self.settings["threads"]
        self.finished_jobs = 0
        self.experiment_name = experiment_name
        self.debug = debug

    def print(self):
        for call, _ in self.jobs:
            print(call)
