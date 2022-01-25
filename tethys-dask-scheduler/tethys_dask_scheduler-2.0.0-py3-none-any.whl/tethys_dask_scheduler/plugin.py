import logging
import click
from distributed.diagnostics.plugin import SchedulerPlugin
from tornado.httpclient import AsyncHTTPClient

logger = logging.getLogger("distributed.scheduler")


class TethysSchedulerPlugin(SchedulerPlugin):

    def __init__(self, scheduler, tethys_endpoint='http://localhost:8000'):
        """
        Constructor.

        Args:
            scheduler (distributed.Scheduler): The scheduler instance this plugin is bound to.
            tethys_endpoint (str): Tethys host to send transition updates to.
        """
        self.tethys_endpoint = tethys_endpoint
        self.scheduler = scheduler

    def transition(self, key, start, finish, *args, **kwargs):
        """
        Hook that is called each time a task changes status. Push status of jobs Tethys is tracking to Tethys.

        Args:
            key (str): unique identifier of the task associated with the current update.
            start (str): Start state of transition. One of released, waiting, processing, memory, error.
            finish (str): Final state of transition.
            *args, **kwargs: More options passed when transitioning. This may include worker ID, compute time, etc.
        """
        # Only update Tethys on tasks (keys) it cares about
        tracked_key = self.scheduler.get_metadata(keys=[key], default=False)

        if tracked_key:
            # Build update dask job status request against bound Tethys host
            combined_status = '{}-{}'.format(start, finish)
            url = self.tethys_endpoint + '/update-dask-job-status/' + key + '/?status=' + combined_status

            # Prevent deadlock
            if start != 'released':
                # Submit update request to Tethys Asynchronously
                http_client = AsyncHTTPClient()
                http_client.fetch(url, method='GET')


@click.command()
@click.option('--tethys-host', type=str, default='http://localhost:8000',
              help='Tethys Portal hostname that is accessible by scheduler.')
def dask_setup(scheduler, tethys_host):
    if not tethys_host.startswith('http'):
        tethys_host = 'http://' + tethys_host
    plugin = TethysSchedulerPlugin(scheduler=scheduler, tethys_endpoint=tethys_host)
    logger.info(f'Tethys Host at: {tethys_host:>25}')
    scheduler.add_plugin(plugin)
