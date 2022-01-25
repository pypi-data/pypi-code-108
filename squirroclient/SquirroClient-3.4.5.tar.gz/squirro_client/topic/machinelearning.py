import base64
import io
import json
import logging
import re
import tarfile
import time

log = logging.getLogger(__name__)


class ExecutionError(Exception):
    """Error in executing a machine learning job"""

    pass


class MachineLearningMixin(object):
    def _inject_ml_models(self, config, ml_models, dereference=True):
        if ml_models:
            try:
                with io.BytesIO() as binary_data:
                    with tarfile.open(
                        fileobj=binary_data, mode="w|gz", dereference=dereference
                    ) as tar:
                        tar.add(ml_models, arcname=".", recursive=True)
                    config["ml_models"] = base64.b64encode(
                        binary_data.getvalue()
                    ).decode("utf-8")
            except Exception as e:
                log.exception(e)
                raise ValueError(e)

    #
    # Machine Learning workflows
    #
    def new_machinelearning_workflow(self, project_id, name, config, ml_models=None):
        """Create a new Machine Learning Workflow.

        :param project_id: Id of the Squirro project.
        :param name: Name of Machine learning workflow.
        :param config: Dictionary of Machine learning workflow config.
            Detailed documentation here: https://squirro.atlassian.net/wiki/spaces/DOC/pages/337215576/Squirro+Machine+Learning+Documentation  # noqa
        :param ml_models: Directory with ml_models to be uploaded into the workflow
            path
        """

        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)

        ml_workflow = {"name": name, "config": config}

        # Inject token
        ml_workflow["squirro_token"] = self.refresh_token

        # Inject ml_models
        self._inject_ml_models(ml_workflow, ml_models)

        res = self._perform_request(
            "post", url, data=json.dumps(ml_workflow), headers=headers
        )
        return self._process_response(res, [201])

    def get_machinelearning_workflows(self, project_id):
        """Return all Machine Learning workflows for a project.

        :param project_id: Id of the Squirro project.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = base_url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_machinelearning_workflow(self, project_id, ml_workflow_id):
        """Return a specific Machine Learning Workflow in a project.

        :param project_id: Id of the project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)

        res = self._perform_request("get", url, headers=headers)
        return self._process_response(res)

    def get_machinelearning_workflow_assets(
        self, project_id, ml_workflow_id, write_to_disk=None
    ):
        """Return all the binary assets like trained models associated with a
        Machine Learning Workflow.

        :param project_id: Id of the project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param write_to_disk: Boolean. Wheather or not to write the exported
            ML workflow assets to the disk.
        """
        url = "{}/v0/{}/projects/{}/machinelearning_workflows/{}/model"
        headers = {"Content-Type": "application/json"}

        url = url.format(self.topic_api_url, self.tenant, project_id, ml_workflow_id)

        res = self._perform_request("get", url, headers=headers)

        if res.status_code != 200:
            res.raise_for_status()

        if write_to_disk:
            exported_file = self._get_file_name(res)
            with open(exported_file, "wb") as exported_asset:
                exported_asset.write(res.content)
                log.info("Exported ML assets to ./%s", exported_file)
            return

        return {"data": res.content, "headers": res.headers}

    def modify_machinelearning_workflow(
        self, project_id, ml_workflow_id, name=None, config=None, ml_models=None
    ):
        """Modify an existing Machine Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param name: Name of Machine learning workflow.
        :param config: Dictionary of Machine Learning workflow config.
            Detailed documentation here: https://squirro.atlassian.net/wiki/spaces/DOC/pages/337215576/Squirro+Machine+Learning+Documentation  # noqa
        :param ml_models: Directory with ml_models to be uploaded into the workflow
            path.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        ml_workflow_update = {}

        # Inject ml_models
        self._inject_ml_models(ml_workflow_update, ml_models)

        # Compose ml_workflow object
        if name is not None:
            ml_workflow_update["name"] = name
        if config is not None:
            ml_workflow_update["config"] = config

        url = "/".join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request(
            "put", url, data=json.dumps(ml_workflow_update), headers=headers
        )
        return self._process_response(res, [204])

    def delete_machinelearning_workflow(self, project_id, ml_workflow_id):
        """Delete a Machine Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    def run_machinelearning_workflow(
        self, project_id, ml_workflow_id, data, asynchronous=False
    ):
        """Run a Machine Learning workflow directly on Squirro items.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param data: Data to run through Machine Learning workflow.
        :param asynchronous: Whether or not to run Machine Learning workflow
            asynchronously (recommended for large data batches).
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        params = {}
        if asynchronous:
            params["asynchronous"] = asynchronous

        url = "/".join([base_url, ml_workflow_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request(
            "post", url, data=json.dumps(data), headers=headers, params=params
        )
        res = self._process_response(res)

        if not asynchronous:
            return res

        ml_job_id = res["ml_job_id"]
        self.wait_for_machinelearning_job(project_id, ml_workflow_id, ml_job_id)
        try:
            ml_job = self.get_machinelearning_job(
                project_id, ml_workflow_id, ml_job_id, include_results=True
            )["machinelearning_job"]
            return {"items": ml_job.get("results")}
        except Exception as e:
            log.exception(e.error)
            return {"items": [], "error": e.error}

    #
    # Machine Learning jobs
    #
    def new_machinelearning_job(
        self, project_id, ml_workflow_id, type, scheduling_options=None
    ):
        """Create a new Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine learning workflow.
        :param type: Type of the Machine Learning job. Possible values are
            `training` and `inference`.
        :param scheduling_options: Scheduling options for the job

        Example::

            >>> client.new_machinelearning_job(
                    project_id='2aEVClLRRA-vCCIvnuEAvQ',
                    ml_workflow_id='129aVASaFNPN3NG10-ASDF',
                    type='training',
                    scheduling_options={"time_based":{"repeat_every":"1d"}})
            '13nv0va0svSDv3333v'
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        data = {"type": type, "scheduling_options": scheduling_options}
        url = "/".join([base_url, ml_workflow_id, "jobs"])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("post", url, data=json.dumps(data), headers=headers)
        return self._process_response(res, [201])

    def get_machinelearning_jobs(
        self, project_id, ml_workflow_id, include_internal_jobs=None
    ):
        """Return all the Machine Learning jobs for a particular Machine
        Learning workflow.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param include_internal_jobs: Bool, whether or not to include the
            internal jobs. Generally, you should not need to get these jobs as
            these jobs are used to optimize the inference runs.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id, "jobs"])
        url = url.format(self.topic_api_url, self.tenant, project_id)

        params = {}
        if include_internal_jobs:
            params["include_internal_jobs"] = include_internal_jobs
        res = self._perform_request("get", url, params=params, headers=headers)
        return self._process_response(res)

    def get_machinelearning_job(
        self,
        project_id,
        ml_workflow_id,
        ml_job_id,
        include_run_log=None,
        last_n_log_lines=None,
        include_results=None,
    ):
        """Return a particular Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        :param include_run_log: Boolean flag to optionally fetch the last run
            log of the job.
        :param last_n_log_lines: Integer to fetch only the last n lines of the
            last run log.
        :param include_run_log: Boolean flag to optionally fetch the last run
            results.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id, "jobs", ml_job_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)

        params = {}
        if include_run_log:
            params["include_run_log"] = include_run_log
        if last_n_log_lines:
            params["last_n_log_lines"] = last_n_log_lines
        if include_results:
            params["include_results"] = include_results

        res = self._perform_request("get", url, params=params, headers=headers)
        return self._process_response(res)

    def delete_machinelearning_job(self, project_id, ml_workflow_id, ml_job_id):
        """Delete a Machine Learning job.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id, "jobs", ml_job_id])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("delete", url, headers=headers)
        return self._process_response(res, [204])

    def kill_machinelearning_job(self, project_id, ml_workflow_id, ml_job_id):
        """Kills a Machine Learning job if it is running.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id, "jobs", ml_job_id, "kill"])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("post", url, headers=headers)
        return self._process_response(res, [201])

    def run_machinelearning_job(self, project_id, ml_workflow_id, ml_job_id):
        """Schedules a Machine Learning job to run now.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        """
        base_url = "{}/v0/{}/projects/{}/machinelearning_workflows"
        headers = {"Content-Type": "application/json"}

        url = "/".join([base_url, ml_workflow_id, "jobs", ml_job_id, "run"])
        url = url.format(self.topic_api_url, self.tenant, project_id)
        res = self._perform_request("post", url, headers=headers)
        return self._process_response(res, [201])

    def wait_for_machinelearning_job(
        self, project_id, ml_workflow_id, ml_job_id, max_wait_time=600
    ):
        """Wait for the first run of the Machine Learning job to complete.
        Often useful in automated scripts where you would want to wait for a
        job to finish after setting it up to inspect logs or results.

        :param project_id: Id of the Squirro project.
        :param ml_workflow_id: Id of the Machine Learning workflow.
        :param ml_job_id: Id of the Machine Learning job.
        :param max_wait_time: Maximum time to wait for Machine Learning job
            (default: 600s).
        """
        start_time = time.time()
        while True:
            job = self.get_machinelearning_job(project_id, ml_workflow_id, ml_job_id)[
                "machinelearning_job"
            ]

            if job.get("total_runs", 0) > 0:
                log.info("Not waiting as the job has already ran once.")
                return
            if job.get("last_success_at") is not None:
                break
            elif job.get("last_error_at") is not None:
                raise ExecutionError(job.get("last_error"))
            else:
                time.sleep(1)
            if (time.time() - start_time) > max_wait_time:
                raise ValueError("max_wait_time has been exceeded!")

    def _get_file_name(self, res):
        # Default file name
        file_name = "ml_workflow_assets.tar.gz"

        # File name from the header
        cd_header = res.headers.get("Content-Disposition")
        if cd_header:
            file_name = re.findall("filename=(.+)", cd_header)[0]

        return file_name
