# Copyright 2020 EMBL - European Bioinformatics Institute
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess

from ebi_eva_common_pyutils.logger import logging_config as log_cfg

logger = log_cfg.get_logger(__name__)


def run_command_with_output(command_description, command, return_process_output=False,
                            log_error_stream_to_output=False):
    process_output = ""

    logger.info("Starting process: " + command_description)
    logger.info("Running command: " + command)

    stdout = subprocess.PIPE
    # Some lame utilities like mongodump and mongorestore output non-error messages to error stream
    # This is a workaround for that
    stderr = subprocess.STDOUT if log_error_stream_to_output else subprocess.PIPE

    with subprocess.Popen(command, stdout=stdout, stderr=stderr, bufsize=1, universal_newlines=True,
                          shell=True) as process:
        for line in iter(process.stdout.readline, ''):
            line = str(line).rstrip()
            logger.info(line)
            if return_process_output:
                process_output += line + "\n"
        if not log_error_stream_to_output:
            for line in iter(process.stderr.readline, ''):
                line = str(line).rstrip()
                logger.error(line)
    if process.returncode != 0:
        logger.error(command_description + " failed! Refer to the error messages for details.")
        raise subprocess.CalledProcessError(process.returncode, process.args)
    else:
        logger.info(command_description + " - completed successfully")
    if return_process_output:
        return process_output


