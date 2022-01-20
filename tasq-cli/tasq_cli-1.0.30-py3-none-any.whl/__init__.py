from tasq_cli import jobs
from tasq_cli import upload
from tasq_cli import settings

VERSION = settings.VERSION

def upload_csv(file_name, project_id, tag):
    """Upload a csv of images to the project.
        :type file_name: string
        :param file_name: full path to the file name to upload
        :type project_id: int
        :param project_id: Project id
        :type tag: string
        :param tag: Tag name
    """
    upload.upload_csv(file_name, project_id, tag)

def run_job(project_id, tag):
    """Run a new job within a project for all images marked by the tag
    :type project_id: int
    :param project_id: Project id
    :type tag: string
    :param tag: Tag name
    """
    return jobs.run_job(project_id, tag)

def list_jobs(project_id):
    """list all the jobs in the project
    :type project_id: int
    :param project_id: Project id
    """
    return jobs.list_jobs(project_id)


def export_job(job_id, raw, worker_data):
    """export data from a job given its id
    :type job_id: int
    :param job_id: the job id
    :type raw: boolean
    :param raw: if true, exports raw annotations (e.g. flat json structure)
    :type worker_data: boolean
    :param worker_data: if true, the export file will include the worker data and calibrations
    """
    return jobs.export_job(job_id, raw, worker_data)

