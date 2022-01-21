from typing import Dict, Optional, Tuple, Union, List, Any

import requests

from pycarlo.common import settings

_DEFAULT_DBT_CLOUD_BASE_URL = 'https://cloud.getdbt.com/api/v2'


class DbtCloudClient:
    """
    Simple client for dbt cloud to retrieve projects/jobs/runs
    """
    def __init__(self,
                 dbt_cloud_api_token: Optional[str] = None,
                 dbt_cloud_account_id: Optional[str] = None,
                 dbt_cloud_base_url: str = _DEFAULT_DBT_CLOUD_BASE_URL):
        self._dbt_cloud_api_token = dbt_cloud_api_token or settings.DBT_CLOUD_API_TOKEN
        self._dbt_cloud_account_id = dbt_cloud_account_id or settings.DBT_CLOUD_ACCOUNT_ID
        if not self._dbt_cloud_api_token or not self._dbt_cloud_account_id:
            raise ValueError('Must set DBT_CLOUD_API_TOKEN and DBT_CLOUD_ACCOUNT_ID environment variables!')
        self._dbt_cloud_api_endpoint = f'{dbt_cloud_base_url}/accounts/{self._dbt_cloud_account_id}'

    def get_projects(self) -> Tuple[Dict, List[Dict]]:
        """
        Get all dbt cloud projects in account. See https://docs.getdbt.com/dbt-cloud/api-v2#operation/listProjects

        :return: tuple of (response status (dict), project (List[dict]))
        """
        return self._get('/projects/')

    def get_project(self, project_id: str) -> Tuple[Dict, Dict]:
        """
        Get a single dbt project. See https://docs.getdbt.com/dbt-cloud/api-v2#operation/getProjectById

        :param project_id: dbt cloud project id
        :return: tuple of (response status (dict), project (dict))
        """
        return self._get(f'/projects/{project_id}')

    def get_jobs(self, project_id: str) -> Tuple[Dict, List[Dict]]:
        """
        Get jobs within a project. See https://docs.getdbt.com/dbt-cloud/api-v2#operation/listJobsForAccount

        :param project_id: dbt cloud project id
        :return: tuple of (response status (dict), jobs (List[dict]))
        """
        return self._get('/jobs/', params=dict(
            project_id=project_id
        ))

    def get_job(self, job_id: str) -> Tuple[Dict, Dict]:
        """
        Get a single job. See https://docs.getdbt.com/dbt-cloud/api-v2#operation/getJobById

        :param job_id: dbt cloud job id
        :return: tuple of (response status (dict), job (dict))
        """
        return self._get(f'/jobs/{job_id}')

    def get_runs(self,
                 limit: int = 5,
                 order_by: str = '-finished_at',
                 job_definition_id: Optional[str] = None,
                 include_related: str = '["run_steps","debug_logs"]') -> Tuple[Dict, Dict]:
        """
        Get runs. See https://docs.getdbt.com/dbt-cloud/api-v2#tag/Runs

        :param limit: Max number of runs to return
        :param order_by: Which field to order by
        :param job_definition_id: dbt cloud job id to filter
        :param include_related: include related objects

        :return: tuple of (response status (dict), runs (List[dict]))
        """
        params = dict(
            order_by=order_by,
            limit=limit,
            include_related=include_related
        )
        if job_definition_id:
            params['job_definition_id'] = job_definition_id
        return self._get('/runs/', params=params)

    def get_run_artifact(self, run_id: int, artifact_path: str) -> Dict:
        """
        Get run artifact. See https://docs.getdbt.com/dbt-cloud/api-v2#operation/getArtifactsByRunId

        :param run_id: dbt cloud run id
        :param artifact_path: Artifact path
        :return: artifact (dict)
        """
        return self._get(f'/runs/{run_id}/artifacts/{artifact_path}', return_payload=True)

    def _get(self, path: str, params: Dict = {}, return_payload: bool = False) -> Union[Tuple[Dict, Any], Dict]:
        response = requests.get(
            f'{self._dbt_cloud_api_endpoint}{path}',
            params=params,
            headers={
                'Authorization': f'Token {self._dbt_cloud_api_token}'
            })
        response.raise_for_status()
        payload = response.json()
        if return_payload:
            return payload
        return payload['status'], payload['data']