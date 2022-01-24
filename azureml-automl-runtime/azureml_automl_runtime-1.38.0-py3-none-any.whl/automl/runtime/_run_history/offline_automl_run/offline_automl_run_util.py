# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List
import os

from azureml.automl.runtime._run_history.offline_automl_run.offline_automl_run import OfflineAutoMLRun


class OfflineAutoMLRunUtil:
    """Utility methods for offline AutoML runs."""

    @staticmethod
    def create_child_run(path: str, parent_run_id: str, iteration: int, pipeline_spec: str) -> OfflineAutoMLRun:
        """Create a child run."""
        child_run_id = "{}_{}".format(parent_run_id, iteration)
        run_history_data_folder = OfflineAutoMLRunUtil.get_run_history_data_folder(path, parent_run_id)
        child_run = OfflineAutoMLRunUtil.get_run(run_history_data_folder, child_run_id)
        child_run.add_properties({
            'iteration': str(iteration),
            'pipeline_spec': pipeline_spec,
            'runTemplate': 'automl_child'
        })
        return child_run

    @staticmethod
    def get_all_sibling_child_runs(child_run: OfflineAutoMLRun) -> List[OfflineAutoMLRun]:
        """Get all sibling child runs."""
        folder_containing_all_child_runs = os.path.dirname(child_run.run_folder)
        child_run_ids_and_folders = [
            (f.name, f.path) for f in os.scandir(folder_containing_all_child_runs)
            if f.is_dir() and os.path.basename(folder_containing_all_child_runs) in f.name]
        return [OfflineAutoMLRun(run_id, run_folder) for (run_id, run_folder) in child_run_ids_and_folders]

    @staticmethod
    def get_run(run_history_data_folder: str, run_id: str) -> OfflineAutoMLRun:
        """Get an offline run from the run history data folder and run id."""
        run_folder = os.path.join(run_history_data_folder, run_id)
        return OfflineAutoMLRun(run_id, run_folder)

    @staticmethod
    def get_run_history_data_folder(path: str, parent_run_id: str) -> str:
        """Get run history data folder given AutoML config path and parent run id."""
        return os.path.abspath(os.path.join(path, parent_run_id))
