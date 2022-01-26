import logging
from datetime import datetime
from typing import Optional, Any, List, Tuple

import mlflow
from mlflow.entities import Experiment as MlflowExperiment, Run as MlflowRun
from mlflow.tracking import MlflowClient
from mlflow.entities import Run

from vectice.adapter.adapter import Adapter, ActiveRun
from vectice.api._utils import read_env
from vectice.models import Artifact, JobRun, Job, Metric, Property, RunnableJob, Artifacts

VECTICE_RUN_TAG = "vectice.run.id"
_STATUSES_MAP = {
    "RUNNING": "STARTED",
    "SCHEDULED": "SCHEDULED",
    "FINISHED": "COMPLETED",
    "FAILED": "FAILED",
    "KILLED": "ABORTED",
}

_STATUSES_VECTICE_TO_MLFLOW = {
    "STARTED": "RUNNING",
    "SCHEDULED": "SCHEDULED",
    "COMPLETED": "FINISHED",
    "FAILED": "FAILED",
    "ABORTED": "KILLED",
}

UNWANTED_TAGS = ["mlflow.log-model.history"]


class MlflowAdapter(Adapter):
    def __init__(self, project_token: str, autocode: bool = False, tracking_uri: str = None, registry_uri: str = None):
        super().__init__(project_token=project_token, autocode=autocode)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._mlflow_tracking_uri, self._mlflow_registry_uri = read_env("MLFLOW_TRACKING_URI", "MLFLOW_REGISTRY_URI")
        if tracking_uri is not None:
            self._mlflow_tracking_uri = tracking_uri
        if registry_uri is not None:
            self._mlflow_registry_uri = registry_uri

        if mlflow.get_tracking_uri() is None:
            mlflow.set_tracking_uri(self._mlflow_tracking_uri)
        if mlflow.get_registry_uri() is None:
            mlflow.set_registry_uri(self._mlflow_registry_uri)
        self._mlflow_client = MlflowClient(self._mlflow_tracking_uri, self._mlflow_registry_uri)

    @property
    def tracking_uri(self) -> Optional[str]:
        """MLflow tracking URI"""
        return self._mlflow_tracking_uri

    @tracking_uri.setter
    def tracking_uri(self, mlflow_tracking_uri: str):
        self._mlflow_tracking_uri = mlflow_tracking_uri
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        self._mlflow_client = MlflowClient(mlflow_tracking_uri, self._mlflow_registry_uri)

    @property
    def registry_uri(self) -> Optional[str]:
        """MLflow registry URI"""
        return self._mlflow_registry_uri

    @registry_uri.setter
    def registry_uri(self, mlflow_registry_uri: str):
        self._mlflow_registry_uri = mlflow_registry_uri
        mlflow.set_registry_uri(mlflow_registry_uri)
        self._mlflow_client = MlflowClient(self._mlflow_tracking_uri, mlflow_registry_uri)

    # Fluent usage
    def create_run(self, name: str, job_type: Optional[str] = None, run_name: Optional[str] = None) -> RunnableJob:
        mlflow.set_experiment(name)
        return super().create_run(name, job_type, run_name)

    def start_run(
        self, runnable_job: Optional[RunnableJob] = None, inputs: Optional[List[Artifact]] = None
    ) -> ActiveRun:
        ml_run = mlflow.start_run()
        job, run, output_artifacts = self._extract_from_mlflow(ml_run, runnable_job=runnable_job)
        runnable_job = self.get_current_runnable_job(runnable_job)
        runnable_job.job = job
        runnable_job.run = run
        return super().start_run(runnable_job, inputs)

    def end_run(self, *args, **kwargs):
        if mlflow.active_run() is None:
            self._logger.warning("No active run found.")
            return None
        active_run = args[0]
        ml_run_id = mlflow.active_run().info.run_id
        kwargs["status"] = _STATUSES_VECTICE_TO_MLFLOW[kwargs["status"]]
        mlflow.end_run(**kwargs)
        ml_run = self._mlflow_client.get_run(ml_run_id)
        job, run, output_artifacts = self._extract_from_mlflow(ml_run)
        active_run.job.update(job.__dict__)
        active_run.run.update(run.__dict__)
        self._mlflow_client.set_tag(ml_run.info.run_id, VECTICE_RUN_TAG, active_run.run["id"])
        super().end_run(active_run, output_artifacts)

    # Sync-up functions from MLflow to Vectice

    def save_all_experiments(self) -> None:
        """Import all MLflow experiments along with all their runs into Vectice jobs."""
        experiments = self._mlflow_client.list_experiments()
        for ml_exp in experiments:
            self.__save_experiment(ml_exp)

    def save_experiment(self, experiment_id: str) -> None:
        """Import one MLflow experiment along with all its runs into Vectice job."""
        ml_exp = self._mlflow_client.get_experiment(experiment_id)
        self.__save_experiment(ml_exp)

    def save_experiment_by_name(self, name: str) -> None:
        """Import one MLflow experiment retrieved by its name into Vectice job."""
        ml_exp = self._mlflow_client.get_experiment_by_name(name)
        if ml_exp is None:
            raise ValueError(f"Experiment with name={name} does not exist.")
        self.__save_experiment(ml_exp)

    def save_run(
        self,
        run: Any,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        """Import one MLflow run into Vectice job run."""
        if isinstance(run, (mlflow.ActiveRun, Run)):
            return self.__save_run(run, inputs, outputs)
        else:
            raise RuntimeError("Incompatible object provided.")

    def __save_experiment(self, experiment: MlflowExperiment) -> None:
        runs = self._mlflow_client.search_runs([experiment.experiment_id], order_by=["attributes.start_time DESC"])
        for run in runs:
            if not run.data.tags.get(VECTICE_RUN_TAG):
                self.__save_run(run)
            else:
                logging.info(f"cancelling save of run {run.info.run_id} as it is already saved in vectice")

    def __save_run(
        self,
        ml_run: mlflow.ActiveRun,
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        job, run, mapped_output_artifacts = self._extract_from_mlflow(ml_run)
        runnable_job = RunnableJob(job, run)
        active_run = super().start_run(runnable_job, inputs)
        if active_run is not None:
            run_id: Optional[int] = int(active_run.run["id"])
            self._mlflow_client.set_tag(ml_run.info.run_id, VECTICE_RUN_TAG, run_id)
        else:
            run_id = None
        if outputs is not None:
            mapped_output_artifacts.extend(outputs)
        super().end_run(active_run, mapped_output_artifacts)
        return run_id

    def _extract_from_mlflow(
        self, mlflow_run: MlflowRun, experiment: MlflowExperiment = None, runnable_job: Optional[RunnableJob] = None
    ) -> Tuple[Job, JobRun, List[Artifact]]:
        ml_exp = experiment or self._mlflow_client.get_experiment(mlflow_run.info.experiment_id)
        job = self._extract_job(ml_exp, runnable_job)
        run = self._extract_run(mlflow_run, runnable_job)
        output_artifacts = self._extract_outputs(mlflow_run, ml_exp)
        return job, run, output_artifacts

    @staticmethod
    def _extract_job(experiment: MlflowExperiment, runnable_job: Optional[RunnableJob] = None) -> Job:
        job_type = None
        if runnable_job:
            job_type = runnable_job.job.type
        return Job(experiment.name, type=job_type if job_type else None)

    @staticmethod
    def _extract_run(mlflow_run: MlflowRun, runnable_job: Optional[RunnableJob] = None) -> JobRun:
        tags = []
        run_name = None
        for tag in mlflow_run.data.tags.items():
            if tag[0] not in UNWANTED_TAGS:
                tags.append(Property(tag[0], tag[1]))
        if runnable_job:
            run_name = runnable_job.run.name
        return JobRun(
            startDate=datetime.fromtimestamp(mlflow_run.info.start_time / 1000),
            endDate=datetime.fromtimestamp(mlflow_run.info.end_time / 1000) if mlflow_run.info.end_time else None,
            status=_STATUSES_MAP[mlflow_run.info.status],
            name=run_name if run_name else None,
        ).with_extended_properties(tags)

    def _extract_outputs(self, mlflow_run: MlflowRun, experiment: MlflowExperiment) -> List[Artifact]:
        # Extract MLflow params and metrics as Vectice Model Version
        metrics = self._extract_metrics(mlflow_run)
        properties = self._extract_model_properties(mlflow_run)
        result = (
            Artifacts.create_model_version()
            .with_parent_name(experiment.name)
            .with_user_version(mlflow_run.info.run_id)
            .with_algorithm(mlflow_run.data.tags.get("estimator_name"))
            .with_extended_metrics(metrics)
            .with_extended_properties(properties)
        )
        return [result]

    def _extract_metrics(self, mlflow_run: MlflowRun) -> List[Metric]:
        metrics: List[Metric] = []
        for key in mlflow_run.data.metrics.keys():
            for m in self._mlflow_client.get_metric_history(mlflow_run.info.run_id, key):
                metrics.append(Metric(m.key, m.value, datetime.fromtimestamp(m.timestamp / 1000)))
        return metrics

    def _extract_model_properties(self, mlflow_run: MlflowRun) -> List[Property]:
        properties = []
        for prop in mlflow_run.data.params.items():
            properties.append(Property(prop[0], prop[1]))
        try:
            properties.append(
                Property(
                    "mlflow_url",
                    f"{mlflow.get_tracking_uri()}/#/experiments/{mlflow_run.info.experiment_id}/runs/{mlflow_run.info.run_id}",
                )
            )
        except Exception as e:
            self._logger.warning(f"Mlflow url failed to generate due to {e}")
        return properties
