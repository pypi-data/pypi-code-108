
from syncer import sync
from unacatlib.unacast.operator.v1 import IndexJobOperatorServiceStub, GetJobStatusResponse
import time

from halo import Halo

from unacatlib.unacast.index.v1 import IndexStatus, IndexEvent, Index

class IndexJob(object):
  
    def __init__(self, catalog: 'Catalog', job_id: str):
      self._catalog = catalog
      self._index_job_operator_service: IndexJobOperatorServiceStub = catalog._client.index_job_operator_service

      self._job_id = job_id
      self._last_status = None
      
    def status(self, refresh=False):
      return self._fetch_status() if self._last_status is None or refresh else self._last_status

    def wait(self, timeout_seconds=60*60, poll_interval_seconds=10) -> GetJobStatusResponse:
      """
      Waits until job is done, times out or fails. Upon timeout or fails an Exception is thrown.
      """
      spinner = Halo(text="Waiting to start...", spinner='dots')
      spinner.start()
      start_time = time.time()
      while time.time() - start_time < timeout_seconds:
        status = self._fetch_status()

        spinner.text = "{}/{} Tasks Completed".format(status.tasks_completed, status.tasks)

        if status.tasks_failed > 0:
          spinner.stop()
          raise Exception("failed tasks", status.error_details)

        if status.is_ready:
          spinner.stop()
          return status

        time.sleep(poll_interval_seconds)

      spinner.stop()
      raise Exception("timeout")

    def _fetch_status(self) -> GetJobStatusResponse:
      res = sync(
        self._index_job_operator_service.get_index_job_status(
          job_id = self._job_id
        )
      )

      self._last_status = res

      return res
    
    