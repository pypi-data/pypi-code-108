"""Run helpers."""

from datetime import datetime
from .pipeline import get_latest_pipeline_version
from kfp import Client
from kfp_server_api.models.api_run_detail import ApiRunDetail
from typing import Dict

# import subprocess
import time
import json
from tabulate import tabulate


class Runner:
    """Manage pipeline runs."""

    def __init__(self, client: Client):
        """Set the kubeflow client."""
        self.client = client

    def run(
        self,
        pipeline_version_id: str,
        experiment_name: str,
        params: Dict = {},
    ) -> ApiRunDetail:
        """Trigger a run of a pipeline version."""
        run_id = "run-" + datetime.now().strftime("%Y%m%d-%H%M%S")
        experiment = self.client.create_experiment(name=experiment_name)
        # pipeline_version rather than pipeline_id is the recommended way to create pipeline runs
        # https://github.com/kubeflow/pipelines/issues/3418
        # kfp/_client.py:380

        # https://www.kubeflow.org/docs/pipelines/reference/api/kubeflow-pipeline-api-spec/#/definitions/apiRunDetail
        return self.client.run_pipeline(
            experiment.id,
            job_name=run_id,
            version_id=pipeline_version_id,
            params=params,
        )

    def run_latest(
        self,
        pipeline_name: str,
        experiment_name: str,
        params: Dict = {},
    ) -> ApiRunDetail:
        """Trigger run of latest version of pipeline by just its name."""
        latest_version = get_latest_pipeline_version(self.client, pipeline_name)
        if latest_version is None:
            return
        return self.run(
            pipeline_version_id=latest_version.id,
            experiment_name=experiment_name,
            params=params,
        )


def _display_run(client, namespace, run_id, watch):
    run = client.get_run(run_id).run
    _print_runs([run])
    if not watch:
        return
    # argo_workflow_name = None
    while True:
        time.sleep(1)
        run_detail = client.get_run(run_id)
        run = run_detail.run
        if (
            run_detail.pipeline_runtime
            and run_detail.pipeline_runtime.workflow_manifest  # noqa: W503
        ):
            manifest = json.loads(run_detail.pipeline_runtime.workflow_manifest)
            if manifest["metadata"] and manifest["metadata"]["name"]:
                # argo_workflow_name = manifest["metadata"]["name"]
                break
        if run_detail.run.status in ["Succeeded", "Skipped", "Failed", "Error"]:
            print("Run is finished with status {}.".format(run_detail.run.status))
            if run_detail.run.status != "Succeeded":
                raise Exception(f"run failed with status {run_detail.run.status}")
            return
    # if argo_workflow_name:
    #     subprocess.run(["argo", "watch", argo_workflow_name, "-n", namespace])
    #     _print_runs([run])


def _print_runs(runs):
    headers = ["run id", "name", "status", "created at"]
    data = [[run.id, run.name, run.status, run.created_at.isoformat()] for run in runs]
    print(tabulate(data, headers=headers, tablefmt="grid"))
