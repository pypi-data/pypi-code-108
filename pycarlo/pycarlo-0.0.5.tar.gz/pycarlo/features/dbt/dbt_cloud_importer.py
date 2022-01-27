from typing import Optional, Callable

from pycarlo.common import settings, get_logger
from pycarlo.core import Client
from pycarlo.features.dbt.dbt_importer import DbtImporter
from pycarlo.features.dbt.dbt_cloud_client import DbtCloudClient
from pycarlo.features.dbt.queries import CREATE_PROJECT

_ARTIFACT_MANIFEST = 'manifest.json'
_ARTIFACT_RUN_RESULTS = 'run_results.json'

logger = get_logger(__name__)


class DbtCloudImporter:
    """
    Import manifest and run results from dbt cloud to Monte Carlo
    """
    def __init__(self,
                 dbt_cloud_client: Optional[DbtCloudClient] = None,
                 client: Optional[Client] = None,
                 dbt_importer: Optional[DbtImporter] = None,
                 print_func: Optional[Callable] = logger.info):
        self._client = client or Client()
        self._print_func = print_func
        self._dbt_importer = dbt_importer or DbtImporter(
            mc_client=self._client,
            print_func=print_func
        )
        self._dbt_client = dbt_cloud_client or DbtCloudClient()

    def import_dbt_cloud(self,
                         project_id: Optional[str] = None,
                         job_id: Optional[str] = None,
                         manifest_only: Optional[bool] = False,
                         default_resource: Optional[str] = None):
        """
        Use dbt API to gather all projects.
        For each project, gather all jobs.
        For each job, retrieve the latest run.
        For each latest run, retrieve manifest.json and run_results.json artifacts, and import to MC
        """
        if project_id:
            status, project = self._dbt_client.get_project(project_id)
            projects = [project]
        else:
            status, projects = self._dbt_client.get_projects()

        all_jobs = []
        if job_id:
            status, job = self._dbt_client.get_job(job_id)
            all_jobs.append((job['id'], job['name']))
        else:
            for project in projects:
                name, project_id = project['name'], project['id']
                self._print_func(f'Project: {name} ({project_id})')

                self._create_dbt_project(project_id)

                # Get all jobs in project
                status, jobs = self._dbt_client.get_jobs(project_id)

                for job in jobs:
                    job_name, job_id = job['name'], job['id']
                    self._print_func(f'* Found Job: {job_name} ({job_id})')
                    all_jobs.append((job_id, job_name))

        self._print_func('')

        for job_id, job_name in all_jobs:
            self._print_func(f'Processing job: {job_name} ({job_id})')
            status, runs = self._dbt_client.get_runs(job_definition_id=job_id)
            if not runs:
                self._print_func(f'No runs found for job')
                continue

            # Get first run that is complete
            for run in runs:
                if run['is_complete']:
                    break
            run_id = run['id']

            try:
                run_steps = run.get('run_steps', [])
                run_logs = '\n'.join([step['logs'] for step in run_steps])

                run_results = self._dbt_client.get_run_artifact(run_id=run_id, artifact_path=_ARTIFACT_RUN_RESULTS)
                manifest = self._dbt_client.get_run_artifact(run_id=run_id, artifact_path=_ARTIFACT_MANIFEST)

                self._print_func("=================================================")
                self._print_func(f"Importing manifest for run id={run_id}")
                self._print_func("=================================================")
                self._dbt_importer.import_dbt_manifest(
                    dbt_manifest=manifest,
                    project_name=run['project_id'],
                    default_resource=default_resource
                )

                if not manifest_only:
                    self._print_func("=================================================")
                    self._print_func(f"Importing run results for run id={run_id}")
                    self._print_func("=================================================")
                    self._dbt_importer.import_run_results(
                        dbt_run_results=run_results,
                        project_name=run['project_id'],
                        run_id=run['id'],
                        run_logs=run_logs
                    )
            except Exception as e:
                self._print_func(f'Could not import data from run, id={run_id}, reason={e}')

    def _create_dbt_project(self, project_id: str):
        self._client(
            query=CREATE_PROJECT,
            variables=dict(
                projectName=project_id,
                source='DBT_CLOUD'
            )
        )