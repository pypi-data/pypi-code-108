# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""
Class for AutoML pipeline step that using PRS.
"""
from typing import Any, Dict, List, Optional, Union
from abc import ABC, abstractmethod
import datetime
from multiprocessing import current_process
import os
import pandas as pd
from pathlib import Path
from subprocess import PIPE, Popen
import sys
import tempfile
import uuid

from azureml.core import Run
from azureml.automl.core.console_writer import ConsoleWriter
from azureml.automl.core.shared import log_server
from .train_helper import Arguments, MetadataFileHandler


# Clearing this environment variable avoids periodic calls from
# dprep log uploading to Run.get_context() and cause RH throttling
# when running at scale. It looks like this logging path repeatedly uploads timespan
# tracing data to the PRS step itself from each worker.
os.environ['AZUREML_OTEL_EXPORT_RH'] = ''

# Batch / flush metrics in the many models scenario
os.environ["AZUREML_METRICS_POLLING_INTERVAL"] = '30'

# Once the metrics service has uploaded & queued metrics for processing, we don't
# need to wait for those metrics to be ingested on flush.
os.environ['AZUREML_FLUSH_INGEST_WAIT'] = ''

# This is needed since CE and requirements.txt dont match due to known constraint.
os.environ['DISABLE_ENV_MISMATCH'] = 'True'


class AutoMLPRSRunBase(ABC):
    """
    Base class for AutoML PRS step run.

    :param current_step_run: Current step run object, parent of AutoML run.
    :param automl_settings: AutoML settings dictionary.
    :param process_count_per_node: Process count per node.
    """

    def __init__(
            self,
            current_step_run: Run,
            automl_settings: Optional[Dict[str, Any]] = None,
            process_count_per_node: Optional[int] = None,
    ) -> None:
        """
        This class is used for PRS steps in AutoML pipeline builders.

        :param current_step_run: Current step run object, parent of AutoML run.
        :param automl_settings: AutoML settings dictionary.
        :param process_count_per_node: Process count per node.
        """
        self.current_step_run = current_step_run
        self.automl_settings = automl_settings
        self.process_count_per_node = process_count_per_node
        self._temp_path = tempfile.mkdtemp()
        self.output_file_path = []  # type: List[str]
        self.metadata_file_handler = MetadataFileHandler(self._temp_path)
        self._console_writer = ConsoleWriter(sys.stdout)

        output_folder = os.path.join(os.environ.get("AZ_BATCHAI_INPUT_AZUREML", ""), "temp/output")
        self._console_writer.println("{}.output_folder:{}".format(__file__, output_folder))
        working_dir = os.environ.get("AZ_BATCHAI_OUTPUT_logs", "")
        ip_addr = os.environ.get("AZ_BATCHAI_WORKER_IP", "")
        self.log_dir = os.path.join(working_dir, "user", ip_addr, current_process().name)
        t_log_dir = Path(self.log_dir)
        t_log_dir.mkdir(parents=True, exist_ok=True)

        # Try stopping logging server in the parent minibatch process.
        # Otherwise, the logging server will progressively consume more and more CPU, leading to
        # CPU starvation on the box. TODO: diagnose why this happens and fix
        try:
            if hasattr(log_server, "server") and log_server.server is not None:
                log_server.server.stop()
        except Exception as e:
            self._console_writer.println(
                "Stopping the AutoML logging server in the entry script parent process failed with exception: {}"
                .format(e))

        self._console_writer.println("init()")

    @abstractmethod
    def get_automl_run_prs_scenario(self):
        """Get the PRS run scenario"""
        pass

    @abstractmethod
    def get_run_result(self, output_file: str) -> pd.DataFrame:
        """Get the result of each run."""
        pass

    @abstractmethod
    def get_prs_run_arguments(self) -> Arguments:
        """Get the run arguments for subprocess."""
        pass

    def combine_result_list(self, result_list: List[pd.DataFrame]) -> pd.DataFrame:
        """
        Combine the parallel run results into one.

        :param result_list: A list of run results.
        :return: A dataframe that contains the result.
        """
        return pd.concat([rl for rl in result_list if rl is not None])

    def dumps_dataframe(self, df: pd.DataFrame) -> str:
        """
        Dumps the input dataframe to a parquet file.

        :param df: The input dataframe.
        :return: The output file path.
        """
        data_path = os.path.join(self._temp_path, self.format_temp_parquet_name(df))
        df.to_parquet(data_path)
        self._console_writer.println("Finished writing pandas dataframe to : {}".format(data_path))
        return data_path

    def format_temp_parquet_name(self, input_data: pd.DataFrame) -> str:
        """
        Return the unique parquet file name.

        :param input_data: The input data frame.
        :return: The unique parquet file name.
        """
        self._console_writer.println(str(input_data.head(1)))
        return "{}.parquet".format(uuid.uuid4())

    def generate_output_df_path(self, input_data_files: List[str]) -> None:
        """
        Generate the unique output parquet file names for each input file.

        :param input_data: The input data frame.
        """
        self.output_file_path = [
            os.path.join(self._temp_path, "{}.parquet".format(uuid.uuid4())) for _ in input_data_files
        ]

    def run(self, input_data: Union[pd.DataFrame, List[str]]) -> pd.DataFrame:
        """
        Train one or more partitions of data

        :param input_data: Input dataframe or file.
        :return: The processed or generated data frame with the output.
        """

        self._console_writer.println("Entering run()")
        self._console_writer.println("InputData type: {}".format(type(input_data)))

        self.write_metadata_file()

        os.makedirs('./outputs', exist_ok=True)
        result_list = []  # type:  List[Any]

        date1 = datetime.datetime.now()
        self._console_writer.println('starting ' + str(date1))

        # ****************************
        # Handle tabular dataset input:
        # Writing to file would take(input_data.to_csv(tabular_input_file, index=False) few seconds,
        #    but it is better than sending dataframe across process which may involve  marshalling/unmarshalling
        # *****************************
        if isinstance(input_data, pd.DataFrame):
            self._console_writer.println("Training using tabular dataset.")
            input_data_files = [self.dumps_dataframe(input_data)]
        else:
            # for file dataset.
            input_data_files = input_data

        self.generate_output_df_path(input_data_files)

        for input_data_file, output_file in zip(input_data_files, self.output_file_path):
            self._run_subprocess_for_file(input_data_file, output_file)
            result_list.append(self.get_run_result(output_file))
            self._console_writer.println(str(result_list))
        self._console_writer.println("Constructing DataFrame from results")
        result = self.combine_result_list(result_list)

        date2 = datetime.datetime.now()
        self._console_writer.println('ending ' + str(date2))
        self._console_writer.println("Ending run()\n")
        return result

    def write_metadata_file(self) -> None:
        """Write the metadata file."""
        # Write metadata files to disk, so they can be consumed by subprocesses that run AutoML
        arguments = self.get_prs_run_arguments()
        self.metadata_file_handler.write_args_to_disk(arguments)
        self.metadata_file_handler.write_automl_settings_to_disk(self.automl_settings)
        self.metadata_file_handler.write_run_dto_to_disk(self.current_step_run._client.run_dto)

    def _run_subprocess_for_file(self, input_data_file: str, output_file: str) -> None:
        self._console_writer.println("Launch subprocess to run AutoML on the data")
        env = os.environ.copy()
        # Aggressively buffer I/O from the subprocess
        env['PYTHONUNBUFFERED'] = '0'
        subprocess = Popen(
            self._build_subprocess_command(input_data_file, output_file), env=env, stdout=PIPE, stderr=PIPE)
        if hasattr(subprocess, "stdout") and subprocess.stdout is not None:
            for line in subprocess.stdout:
                self._console_writer.println(line.decode().rstrip())
        subprocess.wait()
        self._console_writer.println("Subprocess completed with exit code: {}".format(subprocess.returncode))
        if hasattr(subprocess, "stderr") and subprocess.stderr is not None:
            subprocess_stderr = subprocess.stderr.read().decode().rstrip()
        if subprocess_stderr:
            self._console_writer.println("stderr from subprocess:\n{}\n".format(subprocess_stderr))
        if subprocess.returncode != 0:
            raise Exception("AutoML training subprocess exited unsuccessfully with error code: {}\n"
                            "stderr from subprocess: \n{}\n".format(subprocess.returncode, subprocess_stderr))

    def _build_subprocess_command(self, input_data_file: str, output_file_path: str) -> List[str]:
        """
        Build the command for subprocess.

        :param input_data_file: The input datafile.
        :param output_file_path: The output file of the run.
        :return: A list of string that consisting the subprocess command.
        """
        return [
            sys.executable,
            os.path.join(os.path.dirname(os.path.realpath(__file__)), 'run_prs_driver.py'),
            input_data_file,
            self.metadata_file_handler.data_dir,
            self.get_automl_run_prs_scenario(),
            output_file_path
        ]
