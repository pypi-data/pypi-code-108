import datetime
import logging
import os
from typing import Optional

import mlflow
import pandas as pd
import streamlit as st
import whylogs
from mlflow.entities import ViewType
from mlflow.tracking import MlflowClient

from mlfoundry_ui.constants import MLRUNS_FOLDER_NAME
from mlfoundry_ui.webapp.dashboard_constants import *

logger = logging.getLogger(__name__)


class MLFoundryData:
    def __init__(self, mlruns_path: Optional[str] = None):
        # TODO (frizwankhan): Add support for remote.
        if mlruns_path is None:
            mlruns_path = os.path.abspath(MLRUNS_FOLDER_NAME)
        if not os.path.exists(mlruns_path):
            raise Exception(f"{mlruns_path} does not exist.")
        # TODO (nikunjbjj): Figure out if this is the cleanest solution we have.
        # MLFlow requires the URI to start with file. This might need to change when we add support for remote.
        if not mlruns_path.startswith("file:"):
            mlruns_path = "file:" + mlruns_path
        self.mlruns_path = mlruns_path
        mlflow.set_tracking_uri(mlruns_path)
        self.mlflow_client = MlflowClient()

    def get_runs_in_project(self, project_id):
        try:
            all_runs = self.mlflow_client.list_run_infos(
                project_id, run_view_type=ViewType.ALL
            )
        except Exception as e:
            err_msg = f"Problem happened fetching runs for project id {project_id}. Error is {e}"
            st.warning(err_msg)
            logger.exception(err_msg)
            return

        run_name_to_id_dict = {}
        for run in all_runs:
            try:
                # TODO (niikunjbjj): Check if MLFlow has an API to fetch run tags
                with mlflow.start_run(
                    run_id=run.run_id, experiment_id=project_id
                ) as run1:
                    run1_tags = run1.data.tags
                run_name = run1_tags.get(RUN_NAME_TAG, "")
                if run_name == "":
                    logger.warning(f"Couldn't find run_name for run id {run.run_id}")
                    continue
                run_name_to_id_dict[run_name] = run.run_id
            except Exception as e:
                logger.warning(
                    f"Problem fetching detail of run with run_id {run.run_id}. Skipping. Error {e}"
                )
        return run_name_to_id_dict

    @st.experimental_memo(suppress_st_warning=True)
    def get_model_type(_self, run_id):
        # TODO(Rizwan): streamlit doesnt know how to hash self,
        #  so to specify it to not hash it we are adding a underscore before it
        # Have to find a proper solution to hash self
        with mlflow.start_run(run_id=run_id) as run1:
            run1_tags = run1.data.tags

        return run1_tags.get(MODEL_TYPE_TAG)

    def project_options(self):
        try:
            experiments = self.mlflow_client.list_experiments(view_type=ViewType.ALL)
        except Exception as e:
            err_msg = f"Could not fetch logged experiments. Error {e}"
            st.warning(err_msg)
            logger.exception(err_msg)
            return

        project_name_to_id_dict = {}
        for exp in experiments:
            try:
                if exp.experiment_id == "0":  # Removing the default e
                    continue
                project_name_to_id_dict[exp.name] = exp.experiment_id
            except Exception as e:
                logger.warning(
                    f"Problem fetching detail of run with experiment id {exp.experiment_id} and name {exp.name}. "
                    f"Skipping. Error {e}"
                )
        return project_name_to_id_dict

    @st.experimental_memo(suppress_st_warning=True)
    def get_metrics(_self, run_ids):
        # TODO(Rizwan): streamlit doesnt know how to hash self, so to specify it to not hash
        #  it we are adding a underscore before it
        # Have to find a proper solution to hash self
        metrics = []
        for run_id in run_ids:
            run = _self.mlflow_client.get_run(run_id)
            run_name = run.data.tags[RUN_NAME_TAG]
            run_metrics = run.data.metrics

            for metric in run_metrics.keys():
                metric_list = []
                for metric_item in _self.mlflow_client.get_metric_history(
                    run_id, metric
                ):
                    metric_list.append(metric_item.value)
                if len(metric_list) < 2:
                    metric_list = metric_list[0]
                metrics.append([metric, metric_list, run_id, run_name])
        return pd.DataFrame(
            metrics,
            columns=[
                METRIC_DF_KEY_COL,
                METRIC_DF_VALUE_COL,
                METRIC_DF_RUNID_COL,
                METRIC_DF_RUN_NAME_COL,
            ],
        )

    @st.experimental_memo(suppress_st_warning=True)
    def get_artifact(_self, run_id, artifact_name):
        # TODO(Rizwan): streamlit doesnt know how to hash self, so to specify it to not hash
        #  it we are adding a underscore before it
        # Have to find a proper solution to hash self
        try:
            return _self.mlflow_client.download_artifacts(run_id, artifact_name)
        except Exception as e:
            err_msg = f"Artifact {artifact_name} not found. Exception: {e}"
            st.warning(err_msg)
            logger.exception(err_msg)
            return

    @st.experimental_memo(suppress_st_warning=True)
    def get_whylogs_summary(_self, run_id):
        # TODO(Rizwan): streamlit doesnt know how to hash self, so to specify it to not hash
        #  it we are adding a underscore before it
        # Have to find a proper solution to hash self

        dir_path = _self.get_artifact(run_id, WHYLOGS_ARTIFACT_DIR)
        if dir_path is None:
            return

        if len(os.listdir(dir_path)) == 0:
            return None

        whylogs_session = whylogs.get_or_create_session()
        profiles = []
        for file in os.listdir(dir_path):
            profile = whylogs_session.new_profile(
                dataset_name="in-memory", dataset_timestamp=datetime.datetime.now()
            )
            profile = profile.read_protobuf(os.path.join(dir_path, file))
            profiles.append(profile)

        # merging profiles
        profile = profiles[0]
        for i in range(1, len(profiles)):
            profile = profile.merge(profiles[i])

        profile_summary = profile.flat_summary()
        return profile_summary

    def get_mlruns_path(self):
        return self.mlruns_path
