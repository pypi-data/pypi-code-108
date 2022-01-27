from typing import Dict, Optional, Tuple, Union

import requests

class DbtCloudClient:
    def __init__(self,
                 dbt_cloud_api_token: str,
                 dbt_cloud_account_id: str,
                 dbt_cloud_base_url: str = 'https://cloud.getdbt.com/api/v2'):
        self._dbt_cloud_api_token = dbt_cloud_api_token
        self._dbt_cloud_api_endpoint = f'{dbt_cloud_base_url}/accounts/{dbt_cloud_account_id}'

    def get_projects(self) -> Tuple[Dict, Dict]:
        return self._get('/projects/')

    def get_project(self, project_id: str) -> Tuple[Dict, Dict]:
        return self._get(f'/projects/{project_id}')

    def get_jobs(self, project_id: str) -> Tuple[Dict, Dict]:
        return self._get('/jobs/', params=dict(
            project_id=project_id
        ))

    def get_job(self, job_id: str) -> Tuple[Dict, Dict]:
        return self._get(f'/jobs/{job_id}')

    def get_runs(self,
                 limit: int = 1,
                 order_by: str = '-finished_at',
                 job_definition_id: Optional[str] = None,
                 include_related: str = '["run_steps","debug_logs"]') -> Tuple[Dict, Dict]:
        params = dict(
            order_by=order_by,
            limit=limit,
            include_related=include_related
        )
        if job_definition_id:
            params['job_definition_id'] = job_definition_id
        return self._get('/runs/', params=params)

    def get_run_artifact(self, run_id: int, artifact_path: str) -> Dict:
        return self._get(f'/runs/{run_id}/artifacts/{artifact_path}', return_payload=True)

    def _get(self, path: str, params: Dict = {}, return_payload: bool = False) -> Union[Tuple[Dict, Dict], Dict]:
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