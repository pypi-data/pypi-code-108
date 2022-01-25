from shlex import split
from typing import Optional

import click
from gql import Client, gql
from rich.table import Table

from grid.cli.observables.base import BaseObservable
from grid.cli.utilities import get_experiment_duration_string, get_experiment_queued_duration_string, get_param_values


class Experiment(BaseObservable):
    def __init__(self, client: Client, identifier: str):
        self.client = client
        self.run_name = identifier

        super().__init__(client=client)

    # This doesn't seem to be called
    def get_history(self, experiment_id: Optional[str] = None, is_global: Optional[bool] = False):
        """
        Parameters
        ----------
        experiment_id: Optional[str]
            Experiment ID
        is_global: Optional[bool], default False
            Returns status of session from everyone in the team
        """
        self.spinner.start()
        self.spinner.text = 'Getting Experiments ...'

        query = gql(
            """
        query (
            $runName: ID!
        ) {
            getExperiments(runName: $runName) {
                name
                status
                invocationCommands
                createdAt
                finishedAt
                commitSha
                run {
                    runId
                }
                startedRunningAt
            }
        }
        """
        )
        params = {'runName': self.run_name}

        result = self.client.execute(query, variable_values=params)
        if not result['getExperiments']:
            click.echo(f'No experiments available for run "{self.run_name}"')
            return

        self.spinner.text = 'Done!'
        self.spinner.ok("✔")
        self.spinner.stop()
        table = self.render_experiments(result['getExperiments'])
        self.console.print(table)

    def get(self, is_global: Optional[bool] = False):
        """
        Parameters
        ----------
        is_global: Optional[bool], default False
            if True, returns status of experiment(s) of the everyone in the team (TODO)
        """
        with self.spinner:
            self.spinner.text = 'Fetching experiment status ...'

            # User can pass runs as username:experiment_name to fetch other users runs
            username = None
            run_name = self.run_name
            split = self.run_name.split(":")
            if len(split) > 2:
                raise ValueError(f"Error while parsing {self.run_name}. Use the format <username>:<experiment-name>")
            elif len(split) == 2:
                username = split[0]
                run_name = split[1]

            query = gql(
                """
            query (
                $runName: ID!, $username: String
            ) {
                getExperiments(runName: $runName, username: $username) {
                    name
                    status
                    invocationCommands
                    createdAt
                    finishedAt
                    commitSha
                    run {
                        runId
                    }
                    startedRunningAt
                }
            }
            """
            )
            params = {'runName': run_name, "username": username}
            result = self.client.execute(query, variable_values=params)

            experiments = result['getExperiments']
            if not experiments:
                click.echo(f'No experiments available for run "{self.run_name}"')
                return

        table = self.render_experiments(experiments)
        self.console.print(table)
        return result

    @staticmethod
    def render_experiments(experiments) -> Table:
        base_columns = [
            'Experiment',
            'Command',
            'Status',
            'Queued Duration',
            'Run Duration',
        ]
        if not experiments:
            return BaseObservable.create_table(columns=base_columns)

        command = experiments[0]['invocationCommands']
        toks = split(command)
        hparams = [tok.replace('--', '') for tok in toks if '--' in tok]

        table_columns = base_columns + hparams
        table = BaseObservable.create_table(columns=table_columns)

        for experiment in experiments:
            # Split hparam vals
            command = experiment['invocationCommands']
            base_command, *hparam_vals = get_param_values(command)

            duration_str = get_experiment_duration_string(
                created_at=experiment['createdAt'],
                started_running_at=experiment['startedRunningAt'],
                finished_at=experiment['finishedAt']
            )
            queued_duration_str = get_experiment_queued_duration_string(
                created_at=experiment['createdAt'],
                started_running_at=experiment['startedRunningAt'],
            )
            table.add_row(
                experiment['name'], base_command, experiment['status'], queued_duration_str, duration_str, *hparam_vals
            )
        return table

    def follow(self, is_global: Optional[bool] = False):
        pass
