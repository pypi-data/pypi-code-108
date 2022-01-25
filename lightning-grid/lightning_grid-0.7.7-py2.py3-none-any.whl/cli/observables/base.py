import abc
from typing import List

import click
from rich.console import Console
from rich.table import Table
from yaspin import yaspin

#  Maps backend class types to user-friendly messages.
TASK_CLASS_MAPPING = {
    'grid.core.repository_builder.RepositoryBuilder': 'Building container',
    'grid.core.cluster.Cluster': 'Creating cluster',
    'grid.core.trainer.experiment.Experiment': 'Scheduling experiment',
    'grid.core.trainer.run.RunNodePool': 'Creating node pool',
    'grid.core.trainer.interactive.InteractiveNodeTask': 'Creating interactive node',
    'grid.core.trainer.experiment.ExperimentsWarpSpeed': 'Scheduling experiment'
}

# Backend classes that we don't show to users. These
# are automatically triggered if a given user does not
# have global properties set.
TASK_CLASS_IGNORE = (
    'grid.core.clusters.deploy_tensorboard.ReconcileTensorboard',
    'grid.core.clusters.global_user_cluster.ReconcileCluster', 'grid.core.user.ReconcileUser'
)


def style_status(format_string: str, status: str):
    """
    Styles a status message using click.stye.

    Parameters
    ----------
    status: str
        Status message to style.

    Return
    ------
    styled_status: str
        Styled string
    """
    styled_status = format_string

    if status == 'failed':
        styled_status = click.style(styled_status, fg='red')
    elif status in ('finished', 'ready'):
        styled_status = click.style(styled_status, fg='green')
    elif status in ('running', 'queued', 'pending'):
        styled_status = click.style(styled_status, fg='yellow')
    elif status == 'cancelled':
        styled_status = click.style(styled_status, fg='white')

    return styled_status


class BaseObservable(abc.ABC):
    def __init__(self, client=None, spinner_load_type=""):
        self.client = client
        self.console = Console()
        self.spinner = yaspin(text=f"Loading {spinner_load_type}...", color="yellow")

    @abc.abstractmethod
    def get(self, is_global: bool):
        """
        Get the status of the resources

        Parameters
        ----------
        is_global:
            If True, returns status of resources for everyone in the team
        """

    @abc.abstractmethod
    def follow(self, is_global: bool):
        """
        Parameters
        ----------
        is_global:
            If True, returns status of resources for everyone in the team
        """

    @staticmethod
    def create_table(columns: List[str]) -> Table:
        return create_table(columns)


def create_table(columns: List[str]) -> Table:
    table = Table(show_header=True, header_style="bold green")
    table.add_column(columns[0], style='dim')
    for column in columns[1:]:
        table.add_column(column, justify='right')
    return table
