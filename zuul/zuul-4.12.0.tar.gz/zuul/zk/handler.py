# Copyright 2021 Acme Gating, LLC
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from concurrent.futures import ThreadPoolExecutor

from kazoo.handlers.threading import SequentialThreadingHandler


class PoolSequentialThreadingHandler(SequentialThreadingHandler):
    def __init__(self):
        super().__init__()
        self._pool_executor = None

    def start(self):
        self._pool_executor = ThreadPoolExecutor(max_workers=10)
        super().start()

    def stop(self):
        super().stop()
        if self._pool_executor:
            self._pool_executor.shutdown()
        self._pool_executor = None

    def short_spawn(self, func, *args, **kwargs):
        self._pool_executor.submit(func, *args, **kwargs)
