from typing import Optional

import click

from montecarlodata import settings
from montecarlodata.config import Config
from montecarlodata.dataimport.dbt import DbtImportService
from montecarlodata.dataimport.dbt_cloud_client import DbtCloudClient
from montecarlodata.dataimport.dbt_run_results import DbtRunResultsImportService
from montecarlodata.errors import complain_and_abort, manage_errors
from montecarlodata.queries.catalog import CREATE_PROJECT
from montecarlodata.utils import GqlWrapper


class DbtCloudImportService:
    def __init__(self,
                 config: Config,
                 dbt_cloud_client: Optional[DbtCloudClient] = None,
                 gql_wrapper: Optional[GqlWrapper] = None):
        self._config = config
        self._gql_wrapper = gql_wrapper or GqlWrapper(
            mcd_id=config.mcd_id,
            mcd_token=config.mcd_token,
            disable_handle_errors=True
        )

        if not settings.DBT_CLOUD_API_TOKEN or not settings.DBT_CLOUD_ACCOUNT_ID:
            complain_and_abort('Must set DBT_CLOUD_API_TOKEN and DBT_CLOUD_ACCOUNT_ID environment variables!')

        self._dbt_client = dbt_cloud_client or DbtCloudClient(
            dbt_cloud_api_token=settings.DBT_CLOUD_API_TOKEN,
            dbt_cloud_account_id=settings.DBT_CLOUD_ACCOUNT_ID
        )

    @manage_errors
    def import_dbt_cloud(self,
                         project_id: Optional[str] = None,
                         job_id: Optional[str] = None,
                         manifest_only: Optional[bool] = False):
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
                click.echo(f'Project: {name} ({project_id})')

                self._create_dbt_project(project_id)

                # Get all jobs in project
                status, jobs = self._dbt_client.get_jobs(project_id)

                for job in jobs:
                    job_name, job_id = job['name'], job['id']
                    click.echo(f'* Found Job: {job_name} ({job_id})')
                    all_jobs.append((job_id, job_name))

        click.echo('')

        for job_id, job_name in all_jobs:
            click.echo(f'Processing job: {job_name} ({job_id})')
            status, runs = self._dbt_client.get_runs(job_definition_id=job_id)
            if not runs:
                click.echo(f'No runs found for job')
                continue

            run = runs[0]
            run_id = run['id']

            try:
                run_steps = run.get('run_steps', [])
                run_logs = '\n'.join([step['logs'] for step in run_steps])

                run_results = self._dbt_client.get_run_artifact(run_id=run_id, artifact_path='run_results.json')
                manifest = self._dbt_client.get_run_artifact(run_id=run_id, artifact_path='manifest.json')

                click.echo("=================================================")
                click.echo(f"Importing manifest for run id={run_id}")
                click.echo("=================================================")
                manifest_importer = DbtImportService(
                    config=self._config,
                    dbt_manifest=manifest,
                    disable_handle_errors=True
                )
                manifest_importer.import_dbt_manifest(
                    project_name=run['project_id']
                )

                if not manifest_only:
                    click.echo("=================================================")
                    click.echo(f"Importing run results for run id={run_id}")
                    click.echo("=================================================")
                    run_results_importer = DbtRunResultsImportService(
                        config=self._config,
                        dbt_run_results=run_results,
                        disable_handle_errors=True
                    )
                    run_results_importer.import_run_results(
                        project_name=run['project_id'],
                        run_id=run['id'],
                        run_logs=run_logs
                    )
            except Exception as e:
                click.echo(f'Could not import data from run, id={run_id}, reason={e}')

    def _create_dbt_project(self, project_id):
        self._gql_wrapper.make_request_v2(
            query=CREATE_PROJECT,
            operation='createDbtProject',
            variables=dict(
                projectName=project_id,
                source='DBT_CLOUD'
            )
        )