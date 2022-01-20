#!/usr/bin/env python
# Copyright 2020 Axis Communications AB.
#
# For a full list of individual contributors, please see the commit history.
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
# -*- coding: utf-8 -*-
"""conftest.py for etos_test_runner.

If you don't know what this is for, just leave it empty.
Read more about conftest.py under:
https://pytest.org/latest/plugins.html
"""
import pytest
from etos_lib.lib.debug import Debug
from etos_lib.lib.config import Config


@pytest.fixture(scope="function", autouse=True)
def clear_etos_lib_configurations():
    """Make sure that etos library configuration is cleared after each test."""
    config = Config()
    debug = Debug()
    yield
    config.reset()
    debug.events_received.clear()
    debug.events_published.clear()
