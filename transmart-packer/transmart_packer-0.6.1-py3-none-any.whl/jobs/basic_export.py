import logging

from packer.export import save

try:
    from transmart.api.v2.data_structures import ObservationSet
except ImportError as e:
    logging.warning(f'Import errors for {__file__!r}: {str(e)}')

from packer.task_status import Status
from ..tasks import BaseDataTask, app

logger = logging.getLogger(__name__)


@app.task(bind=True, base=BaseDataTask)
def basic_export(self: BaseDataTask, constraint, **params):
    """
    Task that export transmart api client observation dataframe to tsv file.

    :param self: Required for bind to BaseDataTask
    :param constraint: should be in job_parameters.
    :param params: optional job parameters:
        - custom_name: name of the job and export file
    """
    obs_json = self.observations_json(constraint)
    self.update_status(Status.RUNNING, 'Observations gotten, transforming.')

    if 'custom_name' in params:
        custom_name = params['custom_name']
    else:
        logger.debug(f'No custom name supplied. Use task id as such {self.task_id}.')
        custom_name = self.task_id

    self.update_status(Status.RUNNING, 'Writing export to disk.')
    obs_df = ObservationSet(obs_json).dataframe
    save(obs_df, self.task_id, custom_name)
