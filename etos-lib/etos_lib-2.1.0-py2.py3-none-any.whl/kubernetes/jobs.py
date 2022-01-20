# Copyright 2020-2021 Axis Communications AB.
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
"""ETOS Library kubernets jobs handler module."""
import time
from .base import Kubernetes


class Job(Kubernetes):
    """Creating and managing jobs in kubernetes."""

    def create_job(self, body):
        """Create a namespaced kubernetes job.

        :param body: Yaml data to create job from.
        :type body: :obj:`yaml`
        :return: Response from kubernetes.
        :rtype: :obj:
        """
        return self.batch_v1.create_namespaced_job(self.namespace, body=body)

    def wait_for_job_started(self, job_name, timeout=300):
        """Wait for a kubernetes job status to become 'active'.

        :param job_name: Name of job to wait for.
        :type job_name: str
        :param timeout: How long, in seconds, to wait for job to start.
                        Default: 5 minutes.
        :type timeout: int
        :return: Job response.
        :rtype: dict
        """
        timeout = time.time() + timeout
        while time.time() < timeout:
            response = self.batch_v1.read_namespaced_job_status(
                job_name, self.namespace
            )
            status = response.status
            if status.active is not None:
                print(f"Started at: {status.start_time}")
                break
            time.sleep(1)
        return response

    def wait_for_job_finished(self, job_name, timeout=(3600 * 10)):
        """Wait for a kubernetes job status to become 'failed' or 'succeeded'.

        :param job_name: Name of job to wait for.
        :type job_name: str
        :param timeout: How long, in seconds, to wait for job to start.
                        Default: 10 hours.
        :type timeout: int
        :return: Result of the job.
        :rtype: bool
        """
        timeout = time.time() + timeout
        result = False
        while time.time() < timeout:
            response = self.batch_v1.read_namespaced_job_status(
                job_name, self.namespace
            )
            status = response.status
            # pylint:disable=no-else-break
            if status.failed is not None:
                print(f"Finished, but failed: {status}")
                result = False
                break
            elif status.succeeded is not None:
                print("Finished successfully")
                result = True
                break
            time.sleep(1)
        return result

    def delete_job(self, job_name):
        """Delete a kubernetes job.

        :param job_name: Name of job to remove.
        :type job_name: str
        """
        self.batch_v1.delete_namespaced_job(job_name, self.namespace, {})
