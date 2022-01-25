import abc

from whizbang.data.databricks.databricks_client_args import DatabricksClientArgs
from whizbang.data.databricks.databricks_context_factory import IDatabricksContextFactory
from whizbang.data.databricks.databricks_job_context import IDatabricksJobContext
from whizbang.domain.models.databricks.databricks_job import DatabricksJob
from whizbang.domain.models.databricks.databricks_job_instance import DatabricksJobInstance
from whizbang.domain.repository.databricks.databricks_repository_base import DatabricksRepositoryBase, IDatabricksRepository
from whizbang.domain.shared_types.databricks_api_type import DatabricksApiType


class IDatabricksJobRepository(IDatabricksRepository):
    @abc.abstractmethod
    def run_job(self, client_args: DatabricksClientArgs, job_instance: DatabricksJobInstance):
        """"""

    @abc.abstractmethod
    def get_job_runs(self, client_args: DatabricksClientArgs, job_id: str):
        """"""


class DatabricksJobRepository(DatabricksRepositoryBase, IDatabricksJobRepository):
    def __init__(self, context_factory: IDatabricksContextFactory):
        DatabricksRepositoryBase.__init__(self, databricks_context_factory=context_factory)

    @property
    def context_type(self) -> str: return DatabricksApiType.job

    def create(self, client_args: DatabricksClientArgs, t_object: DatabricksJob):
        context: IDatabricksJobContext = self._get_context(client_args)

        result = context.create_job(
            job_dict=t_object.job_dict
        )
        return result

    def get(self, client_args: DatabricksClientArgs):
        context: IDatabricksJobContext = self._get_context(client_args)
        result = context.get_jobs()
        existing_jobs = []
        if result != {}:
            result = result['jobs']
            for job in result:
                existing_jobs.append(DatabricksJob(job))
        return existing_jobs

    def update(self, client_args: DatabricksClientArgs, t_object: DatabricksJob):
        context: IDatabricksJobContext = self._get_context(client_args)
        job_dict = {}
        job_dict.update({'job_id': t_object.job_dict['job_id']})
        t_object.job_dict.pop('job_id')
        job_dict.update({'new_settings': t_object.job_dict})
        result = context.update_job(
            job_dict=job_dict
        )
        return result

    def run_job(self, client_args: DatabricksClientArgs, job_instance: DatabricksJobInstance):
        context: IDatabricksJobContext = self._get_context(client_args)
        job_id = job_instance.job_id
        jar_params = job_instance.jar_params
        notebook_params = job_instance.notebook_params
        python_params = job_instance.python_params
        spark_submit_params = job_instance.spark_submit_params
        result = context.run_job(
            job_id=job_id,
            jar_params=jar_params,
            notebook_params=notebook_params,
            python_params=python_params,
            spark_submit_params=spark_submit_params
        )
        return result

    def get_job_runs(self, client_args: DatabricksClientArgs, job_id: str):
        context: IDatabricksJobContext = self._get_context(client_args)
        result = context.get_job_runs(job_id=job_id)
        return result
