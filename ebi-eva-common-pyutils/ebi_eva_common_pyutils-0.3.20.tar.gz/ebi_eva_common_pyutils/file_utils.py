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


from enum import Enum
from ebi_eva_common_pyutils.command_utils import run_command_with_output


class FileDiffOption(Enum):
    NOT_IN = 1
    COMMON = 2


def file_diff(file1_path: str, file2_path: str, diff_option: FileDiffOption, output_file_path: str):
    if diff_option == FileDiffOption.NOT_IN:
        run_command_with_output("Finding entries in {0} not in {1}".format(file1_path, file2_path),
                                "comm -23 {0} {1} > {2}".format(file1_path, file2_path, output_file_path))
    elif diff_option == FileDiffOption.COMMON:
        run_command_with_output("Finding entries common to {0} and {1}".format(file1_path, file2_path),
                                "comm -12 {0} {1} > {2}".format(file1_path, file2_path, output_file_path))
