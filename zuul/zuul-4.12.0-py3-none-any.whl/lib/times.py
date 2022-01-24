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

import logging

import cachetools


class Times:
    """Obtain estimated build times"""

    log = logging.getLogger("zuul.times")

    def __init__(self, sql, statsd):
        self.sql = sql
        self.statsd = statsd
        self.cache = cachetools.TTLCache(8192, 3600)

    def start(self):
        pass

    def stop(self):
        pass

    def join(self):
        pass

    def _getTime(self, key):
        tenant, project, branch, job = key
        previous_builds = self.sql.getBuilds(
            tenant=tenant,
            project=project,
            branch=branch,
            job_name=job,
            final=True,
            result='SUCCESS',
            limit=10,
            sort_by_buildset=True)
        times = [x.duration for x in previous_builds if x.duration]
        if times:
            estimate = float(sum(times)) / len(times)
            self.cache.setdefault(key, estimate)
            return estimate
        return None
        # Don't cache a zero value, so that new jobs get an estimated
        # time ASAP.

    def getEstimatedTime(self, tenant, project, branch, job):
        key = (tenant, project, branch, job)
        ret = self.cache.get(key)
        if ret is not None:
            return ret

        if self.statsd:
            with self.statsd.timer('zuul.scheduler.time_query'):
                return self._getTime(key)
        else:
            return self._getTime(key)
