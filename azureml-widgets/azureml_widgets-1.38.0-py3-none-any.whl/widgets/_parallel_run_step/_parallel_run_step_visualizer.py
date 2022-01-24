# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import time

from azureml.widgets._constants import PRS_REFRESH_INTERVAL_IN_SECONDS
from azureml.widgets._parallel_run_step._data_downloader import _DataDownloader
from azureml.widgets._parallel_run_step._progress_bar import _ProgressBar


class _ParallelRunStepVisualizer(object):
    """A visualizer that real-time update the PRS job progress metrics."""

    def __init__(self, step_run):
        """Init progress_bar and data_downloader."""
        self.step_run = step_run
        self.progress_bar = _ProgressBar(0)
        data_store = step_run.experiment.workspace.get_default_datastore()
        self.data_downloader = _DataDownloader(data_store, step_run.id)

    def run(self):
        """Loop of updating progress bar."""
        self.progress_bar.display()
        while True:
            self._update_latest_progress()

            run_status = self.step_run.get_status()
            if run_status == "NotStarted":
                self.progress_bar.set_job_not_started()
            if run_status == "Queued":
                self.progress_bar.set_job_queued()
            if run_status == "Running":
                self.progress_bar.set_job_running()
            if run_status == "Finished":
                self._update_final_progress()
                self.progress_bar.set_job_completed()
                break
            elif run_status == "Failed":
                self._update_final_progress()
                self.progress_bar.set_job_failed()
                break
            elif run_status == "Canceled":
                self._update_final_progress()
                self.progress_bar.set_job_canceled()
                break

            time.sleep(PRS_REFRESH_INTERVAL_IN_SECONDS)

    def _update_progress_bar(self, progress_dict):
        """Update progress bar with new progress_dict."""
        if progress_dict:
            self.progress_bar.update(
                total_tasks=progress_dict["Total Tasks"],
                completed_tasks=progress_dict["Completed Tasks"],
                failed_tasks=progress_dict["Failed Tasks"],
                scheduled_tasks=progress_dict["Scheduled Tasks"],
                elapsed_time=progress_dict["Elapsed Time"],
                estimated_remaining_time=progress_dict["Estimated Remaining Time"],
            )

    def _update_latest_progress(self):
        """Update progress bar with latest progress in logs/sys/metrics folder."""
        progress_dict = self.data_downloader.get_latest_progress()
        self._update_progress_bar(progress_dict)

    def _update_final_progress(self):
        """Update progress bar with final progress in logs/sys/job_report folder."""
        progress_dict = self.data_downloader.get_final_progress()
        self._update_progress_bar(progress_dict)
