# -*- coding: utf-8 -*-


class WorkerVersionMixin(object):
    def get_worker_version(self, worker_version_id: str) -> dict:
        """
        Get worker version from cache if possible, otherwise make API request
        """
        if worker_version_id is None:
            raise ValueError("No worker version ID")

        if worker_version_id in self._worker_version_cache:
            return self._worker_version_cache[worker_version_id]

        worker_version = self.request("RetrieveWorkerVersion", id=worker_version_id)
        self._worker_version_cache[worker_version_id] = worker_version

        return worker_version

    def get_worker_version_slug(self, worker_version_id: str) -> str:
        """
        Helper function to get the worker slug from element, classification or transcription.
        Gets the worker version slug from cache if possible, otherwise makes an API request.
        Returns None if there is no associated worker version.

        :type worker_version_id: A worker version UUID
        """
        worker_version = self.get_worker_version(worker_version_id)
        return worker_version["worker"]["slug"]
