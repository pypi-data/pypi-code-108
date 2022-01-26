import logging

from ..table_transformations.csr_transformations import from_obs_json_to_export_csr_df
from ..table_transformations.utils import filter_rows

from packer.task_status import Status
from ..tasks import BaseDataTask, app
from ..export import save

logger = logging.getLogger(__name__)


@app.task(bind=True, base=BaseDataTask)
def csr_export(self: BaseDataTask, constraint, **params):
    """
    Reformat hypercube data into a specific export file.
    Export table with ID columns being CSR entities IDs

    :param self: Required for bind to BaseDataTask
    :param constraint: mandatory tranmsart api constraint to get data for.
    :param params: optional job parameters:
        - row_filter: constraint to filter rows
        - custom_name: name of the job and export file
    """
    obs_json = self.observations_json(constraint)
    self.update_status(Status.RUNNING, 'Observations gotten, transforming.')
    export_df = from_obs_json_to_export_csr_df(obs_json)
    if 'row_filter' in params:
        self.update_status(Status.RUNNING, 'Observations for the row filter gotten, transforming.')
        row_filter_constraint = params['row_filter']
        row_filter_obs_json = self.observations_json(row_filter_constraint)
        row_export_df = from_obs_json_to_export_csr_df(row_filter_obs_json)
        self.update_status(Status.RUNNING, 'Removing extra rows based on the row filter.')
        export_df = filter_rows(export_df, row_export_df)

    if 'custom_name' in params:
        custom_name = params['custom_name']
    else:
        logger.debug(f'No custom name supplied. Use task id as such {self.task_id}.')
        custom_name = self.task_id
    self.update_status(Status.RUNNING, 'Writing export to disk.')
    save(export_df, self.task_id, custom_name)

