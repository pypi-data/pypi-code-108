from datetime import datetime, timezone
from typing import Dict, Optional

import click
from gql import Client, gql

from grid import list_runs
from grid.cli.observables.base import BaseObservable
from grid.cli.utilities import get_abs_time_difference, string_format_timedelta
import grid.sdk.env as env
from grid.sdk.runs import RunState


def get_runs(client: Client, run_name: Optional[str], team_id: Optional[str] = None) -> Dict:
    params = {'runName': run_name, "teamId": team_id}

    query = gql(
        """
        query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                createdAt
                experiments {
                    experimentId
                }
                nExperiments
                nFailed
                nCancelled
                nRunning
                nCompleted
                nQueued
                nPending
                projectId
                userDetails {
                    username
                }
            }
        }
        """
    )

    result = client.execute(query, variable_values=params)
    return result['getRuns']


def get_runs_history(client: Client, run_name: Optional[str], team_id: Optional[str] = None) -> Dict:
    params = {'runName': run_name, "teamId": team_id}

    query = gql(
        """
         query (
            $runName: ID, $teamId: ID
        ) {
            getRuns (runName: $runName, teamId: $teamId) {
                name
                createdAt
                experiments {
                    experimentId
                }
                nExperiments
                nFailed
                nCancelled
                nRunning
                nCompleted
                nQueued
                userDetails {
                    username
                }
            }
        }
        """
    )

    result = client.execute(query, variable_values=params)
    return result['getRuns']


class Run(BaseObservable):
    def __init__(self, identifier: Optional[str] = []):
        self.identifier = identifier
        super().__init__(spinner_load_type="Runs")

    def get(self, is_global: Optional[bool] = False):
        """
        Gets the run status; either for a single run or all runs for
        user.

        Parameters
        ----------
        is_global: Optional[bool], default False
            if True, returns status of experiment(s) of the everyone in the team (TODO)
        run_name:
            name of the run to get status of
        """
        self.spinner.start()
        self.spinner.text = 'Getting Run status...'
        try:
            # TODO - show runs from all the clusters
            runs = list_runs(is_global=is_global)
            self.spinner.text = 'Done!'
        except Exception as e:
            self.spinner.fail("✘")
            self.spinner.stop()
            if env.DEBUG:
                click.echo(str(e))
            raise click.ClickException(f'Query to Grid failed. {e}')

        if is_global:
            table_cols = [
                'Run',
                'Status',
                'Created By',
                'Duration',
                'Experiments',
                'Running',
                'Queued',
                'Completed',
                'Failed',
                'Stopped',
            ]
        else:
            table_cols = [
                'Run',
                'Status',
                'Duration',
                'Experiments',
                'Running',
                'Queued',
                'Completed',
                'Failed',
                'Stopped',
            ]

        table = BaseObservable.create_table(columns=table_cols)

        #  Whenever we don't have yet submitted experiments,
        table_rows = 0
        for run in runs:
            # we only have 3 statuses for runs
            # running (if something is running)
            # TODO - move status to Enum
            is_running = run.status == "RUN_STATE_RUNNING"

            # We classify queued and pending into queued
            # TODO - standardize the string here and the actual status
            n_queued = run.experiment_counts.get("pending", 0)
            n_running = run.experiment_counts.get("running", 0)
            n_failed = run.experiment_counts.get("failed", 0)
            n_succeeded = run.experiment_counts.get("succeeded", 0)
            n_cancelled = run.experiment_counts.get("cancelled", 0)

            # If anything is queued, the the status of the entire
            # run is queued. All other statuses are running in
            # all other conditions.
            if n_queued > 0:
                status = 'queued'

            # If you have anything running (and nothing queued)
            # then, mark the run as running.
            elif is_running:
                status = 'running'

            # If it doesn't match the conditions above, just
            # skip this row and add the row and put it in history.
            else:
                # don't render table because it should be in history
                continue

            # Calculate the duration column
            delta = get_abs_time_difference(datetime.now(timezone.utc), run.created_at)
            duration_str = string_format_timedelta(delta)

            if is_global:
                table.add_row(
                    run.name, status, run.user.username, duration_str, str(len(run.experiments)), str(), str(n_queued),
                    str(n_succeeded), str(n_failed), str(n_cancelled)
                )
            else:
                table.add_row(
                    run.name, status, duration_str, str(len(run.experiments)), str(n_running), str(n_queued),
                    str(n_succeeded), str(n_failed), str(n_cancelled)
                )

            #  Let's count how many rows have been added.
            table_rows += 1

        #  Close the spinner.
        self.spinner.ok("✔")
        self.spinner.stop()

        # If there are no Runs to render, add a
        # placeholder row indicating none are active.
        if table_rows == 0:
            table.add_row("None Active.", *[" " for i in range(len(table_cols) - 1)])

        self.console.print(table)

        #  Print useful message indicating that users can run
        #  grid history.
        history_runs = len(runs) - table_rows
        if history_runs > 0:
            click.echo(f'{history_runs} Run(s) are not active. Use `grid history` ' 'to view your Run history.\n')

        return {'getRuns': runs}

    def get_history(self, is_global: Optional[bool] = False, run_name: Optional[str] = None):
        """
        Fetches a complete history of runs. This includes runs that
        are not currently active.

        Parameters
        ----------
        is_global: Optional[bool], default False
            Returns status of session from everyone in the team
        """
        self.spinner.start()
        self.spinner.text = 'Getting Runs ...'
        try:
            # TODO - show runs from all the clusters
            runs = list_runs(is_global=is_global)
            self.spinner.text = 'Done!'
        except Exception as e:
            self.spinner.fail("✘")
            self.spinner.stop()
            if env.DEBUG:
                click.echo(str(e))
            raise click.ClickException(f'Query to Grid failed. {e}')

        if is_global:
            table_cols = ['Run', 'Created By', 'Created At', 'Experiments', 'Failed', 'Stopped', 'Completed']
        else:
            table_cols = ['Run', 'Created At', 'Experiments', 'Failed', 'Stopped', 'Completed']
        table = BaseObservable.create_table(columns=table_cols)

        for run in runs:
            if run_name and run_name != run.name:
                continue
            n_failed = run.experiment_counts.get(RunState.FAILED.value, 0)
            n_succeeded = run.experiment_counts.get(RunState.SUCCEEDED.value, 0)
            n_cancelled = run.experiment_counts.get(RunState.CANCELLED.value, 0)

            # Calculate the duration column
            delta = get_abs_time_difference(datetime.now(timezone.utc), run.created_at)
            duration_str = string_format_timedelta(delta)

            if is_global:
                table.add_row(
                    run.name, run.user.username, duration_str, str(len(run.experiments)), str(n_failed),
                    str(n_cancelled), str(n_succeeded)
                )
            else:
                table.add_row(
                    run.name, duration_str, str(len(run.experiments)), str(n_failed), str(n_cancelled),
                    str(n_succeeded)
                )

        #  Close the spinner.
        self.spinner.ok("✔")
        self.spinner.stop()

        # Add placeholder row if no records are available.
        if not runs:
            table.add_row("No History.", *[" " for i in range(len(table_cols) - 1)])

        self.console.print(table)

        return runs

    def follow(self, is_global: Optional[bool] = False):  # pragma: no cover
        pass

    def _get_task_run_dependencies(self, run_name: str):
        """Gets dependency data for a given Run"""
        query = gql(
            """
        query (
            $runName: ID!
        ) {
            getRunTaskStatus (
                runName: $runName
            ) {
                success
                message
                runId
                name
                dependencies {
                    taskId
                    status
                    taskType
                    message
                    error
                }
            }
        }
        """
        )
        params = {'runName': run_name}

        #  Make GraphQL query.
        result = None
        try:
            result = self.client.execute(query, variable_values=params)
            if not result['getRunTaskStatus']['success']:
                raise Exception(result['getRunTaskStatus'])
        except Exception as e:  # skipcq: PYL-W0703
            self.spinner.fail("✘")
            self.spinner.stop()

            raise click.ClickException(f'Could not retrieve task dependencies. Error: {str(e)}')

        if result:
            dependencies = result['getRunTaskStatus']['dependencies']
            return dependencies
        return None
