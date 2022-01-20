# coding=utf-8
# Copyright 2022 DeepMind Technologies Limited..
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data type that's written to and returned from storage.
"""

from typing import Any, NamedTuple

import dm_env


class StepData(NamedTuple):
  """Payload that's written at every dm_env.Environment.step() call.

  `StepData` contains the data that's written to logs (i.e. to disk somewhere).

  Attributes:
    timestep: The dm_env.TimeStep generated by the environment.
    action: The action that led generated `timestep`.
    custom_data: Any client-specific data to be written along-side `timestep`
        and `action`. It must be supported by converters/codec.py.
  """
  timestep: dm_env.TimeStep
  action: Any
  custom_data: Any = None
