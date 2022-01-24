import logging

from typing import Optional, Any, List


from vectice.adapter.adapter import Adapter
from vectice.adapter.factory import LibraryFactory
from vectice.models import (
    Artifact,
    RunnableJob,
    Job,
    JobRun,
)


logger = logging.getLogger(__name__)


# Import experiment into Vectice with all associated run (could be long !)
def save_job(project_token: str, experiment_name: str, lib: str):
    try:
        vectice = Vectice(project_token=project_token, lib=lib)
        vectice.save_job_and_associated_runs(experiment_name)
    except Exception:
        logger.exception(f"saving job {experiment_name} failed")


# Import run of experiment into Vectice
def save_after_run(
    project_token: str,
    run: Any,
    lib: Optional[str],
    inputs: Optional[List[Artifact]] = None,
    outputs: Optional[List[Artifact]] = None,
) -> Optional[int]:
    """
        Save in Vectice platform information relative to this run.
        The run object can be of several type depending on which
        lib you are using.

    :param project_token: The token of the project the job belongs to
    :param run: The run we want to save
    :param lib: Name of the lib you are using (for now, None or MLFlow)
    :param inputs: A list of inputs (artifacts) you are using in this run
    :param outputs: A list of outputs (artifacts) you are using in this run
    :return: An identifier of the saved run or None if the run can not be saved
    """
    try:
        vectice = Vectice(project_token, lib)
        return vectice.save_run(run, inputs, outputs)
    except Exception:
        logger.exception("saving run failed")
        return None


def create_run(job_name: str, job_type: Optional[str] = None) -> RunnableJob:
    """
    Create a local object of a run. Note that the run is not created in
    Vectice server (and as a consequence is NOT visible until saved after the run).

    This object will save any information relative to a run and its associated job.

    The returned instance needs to be used with associated :func:`save_after_run`

    For job types, take a look at the list in :class:`~vectice.models.JobType`

    :param job_name: The name of the job involved in the run
    :param job_type: The type of the job involved in the run
    :return: A runnable job
    """
    if job_name is None:
        raise RuntimeError("Name of job must be provided.")
    job = Job(job_name)
    if job_type is not None:
        job.with_type(job_type)
    return RunnableJob(job, JobRun())


class Vectice(Adapter):
    """
    High level class to list jobs and runs but also save runs

    The ability to toggle the autocode feature is enabled with the autocode argument. If autocode=True,
    Vectice will capture code artifacts relative to the .git file where you are executing your code. More can be found
    in the documentation at doc.vectice.com
    """

    def __new__(cls, project_token: str, lib: str = None, *args, **kwargs):
        if lib is not None:
            return LibraryFactory.get_library(project_token, lib, *args, **kwargs)
        else:
            return super().__new__(cls)

    def __init__(
        self, project_token: str, lib: Optional[str] = None, autocode: bool = False, allow_self_signed_certificate=True
    ):
        super().__init__(
            project_token=project_token, autocode=autocode, allow_self_signed_certificate=allow_self_signed_certificate
        )

    @classmethod
    def prepare_run(cls, job_name: str, job_type: Optional[str] = None) -> RunnableJob:
        """
        Create a local object of a run. Note that the run is not created in
        Vectice server (and as a consequence is NOT visible).

        The returned instance need to be used with associated :func:`~Vectice.save_after_run`

        :param job_name: The name of the job the run is related to
        :param job_type: The type of the job.
        :return: A runnable job
        """
        return create_run(job_name, job_type)

    @classmethod
    def save_after_run(
        cls,
        project_token: str,
        run: Any,
        lib: Optional[str],
        inputs: Optional[List[Artifact]] = None,
        outputs: Optional[List[Artifact]] = None,
    ) -> Optional[int]:
        """
        Save all run information in Vectice server

        :param project_token: The token of the project the job is belong to
        :param run: The run we want to save
        :param lib: The name of the lib you are using (for now, None or MLFlow)
        :param inputs: A list of inputs (artifact) you are using in this run
        :param outputs: A list of outputs (artifact) you are using in this run
        :return: An identifier of the saved run or None if the run can not be saved
        """
        return save_after_run(project_token, run, lib, inputs, outputs)
