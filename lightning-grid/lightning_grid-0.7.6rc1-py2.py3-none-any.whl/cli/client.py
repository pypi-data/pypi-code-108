# Copyright 2020 Grid AI Inc.
import ast
import asyncio
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import urlsplit

import click
from gql import Client, gql
from gql.transport.exceptions import TransportProtocolError, TransportQueryError
from gql.transport.requests import RequestsHTTPTransport
from gql.transport.websockets import WebsocketsTransport
import requests
from rich.console import Console
import websockets
import yaspin

from grid.cli.commands import CredentialsMixin, DependencyMixin, WorkflowChecksMixin
from grid.cli.observables import BaseObservable, Experiment, InteractiveNode, Run
from grid.cli.types import ObservableType
from grid.metadata import __version__
from grid.sdk import env
from grid.sdk.utils.datastore_uploader import create_datastore_session, DatastoreUploadSession

_graphql_client: Client = None

CREDIT_CARD_ERROR_MESSAGE = "A credit card on file is needed in order to use a GPU"


@dataclass
class StaticCredentials:
    user_id: str
    api_key: str


def credentials_from_env(credential_path: Optional[str] = None) -> StaticCredentials:
    """Instantiates the GraphQL local client using local credentials."""
    # if user has environment variables, use that
    env.USER_ID = os.getenv('GRID_USER_ID')
    env.API_KEY = os.getenv('GRID_API_KEY')
    if env.USER_ID and env.API_KEY:
        return StaticCredentials(user_id=env.USER_ID, api_key=env.API_KEY)

    # otherwise overwrite look for credentials stored locally as a file
    credential_path = credential_path or os.getenv(
        'GRID_CREDENTIAL_PATH',
        Path.home() / ".grid" / "credentials.json",
    )

    P = Path(credential_path)
    if not P.exists():
        raise click.ClickException('No credentials available. Did you login?')

    with P.open() as f:
        credentials = json.load(f)

    return StaticCredentials(
        user_id=credentials['UserID'],
        api_key=credentials['APIKey'],
    )


class Grid(CredentialsMixin, WorkflowChecksMixin, DependencyMixin):
    """
    Interface to the Grid API.

    Attributes
    ----------
    url: str
        Grid URL
    request_timeout: int
        Number of seconds to timeout a request by default.
    client: Client
        gql client object
    grid_credentials_path: str
        Path to the Grid credentials
    default_headers: Dict[str, str]
        Header used in the request made to Grid.
    acceptable_lines_to_print: int
        Total number of acceptable lines to print in
        stdout.
    request_cooldown_duration: float
        Number of seconds to wait between continuous
        requests.

    Parameters
    ----------
    local_credentials: bool, default True
        If the client should be initialized with
        credentials from a local file or not.
    """
    url: str = env.GRID_URL
    graphql_url: str = env.GRID_URL + '/graphql'

    #  TODO: Figure out a better timeout based on query type.
    request_timeout: int = 60
    default_headers: Dict[str, str] = {'Content-type': 'application/json', 'User-Agent': f'grid-api-{__version__}'}

    grid_settings_path: str = '.grid/settings.json'
    grid_credentials_path: str = '.grid/credentials.json'

    client: Client
    transport: RequestsHTTPTransport

    available_observables: Dict[ObservableType, Callable] = {
        ObservableType.EXPERIMENT: Experiment,
        ObservableType.RUN: Run,
        ObservableType.INTERACTIVE: InteractiveNode
    }

    acceptable_lines_to_print: int = 50
    request_cooldown_duration: int = 0.1
    credentials: StaticCredentials

    def __init__(
        self,
        credential_path: Optional[str] = None,
        load_local_credentials: bool = True,
        set_context_if_not_exists: bool = True
    ):
        self.headers = self.default_headers.copy()

        #  By default, we instantiate the client with a local
        #  set of credentials.
        if load_local_credentials or credential_path:
            self._set_local_credentials(credential_path)

            #  The client will be created with a set of credentials.
            #  If we change these credentials in the context of a
            #  call, for instance "login()" then we have to
            #  re-instantiate these credentials.
            self._init_client()
        super().__init__()

    def _set_local_credentials(self, credentials_path: Optional[str] = None):
        if credentials_path:
            self.credentials = credentials_from_env(credentials_path)
        else:
            self.credentials = credentials_from_env()
        self.__set_authentication_headers(user_id=self.credentials.user_id, key=self.credentials.api_key)

    def __set_authentication_headers(self, user_id: str, key: str) -> None:
        """Sets credentials header for a client."""
        self.user_id = user_id
        self.api_key = key
        self.headers['X-Grid-User'] = user_id
        self.headers['X-Grid-Key'] = key

    def _init_client(self, websocket: bool = False) -> None:
        """
        Initializes GraphQL client. This fetches the latest
        schema from Grid.
        """
        # Check version compatibility on client initialization.
        # TODO re-enable when versioning is fixed
        # self._check_version_compatibility()

        # Print non-default
        if self.url != env.GRID_URL:
            print(f"Grid URL: {self.url}")

        if websocket:
            _url = self.url.replace('http://', 'ws://')
            _url = _url.replace('https://', 'wss://')
            _url = _url + '/subscriptions'
            self.transport = WebsocketsTransport(url=_url, init_payload=self.headers)
        else:
            self.transport = RequestsHTTPTransport(
                url=self.graphql_url, use_json=True, headers=self.headers, timeout=self.request_timeout, retries=3
            )

        try:
            # Only create a client instance if there isn't one.
            # We also check if the instantiated transport is different.
            # We'll create a new client if it is.
            global _graphql_client
            if not isinstance(_graphql_client,
                              Client) or not isinstance(_graphql_client.transport, type(self.transport)):
                _graphql_client = Client(transport=self.transport, fetch_schema_from_transport=True)

                # Initiating the context to trigger the schema fetch. This was happening
                # on the class init previously (on the above Client(...)).
                # Probably a version upgrade screwed it up.
                # Not investigating further since we are changing this soon # TODO
                if isinstance(self.transport, RequestsHTTPTransport):
                    with _graphql_client:
                        pass

            self.client = _graphql_client

        except requests.exceptions.ConnectionError:
            raise click.ClickException(f'Grid is unreachable. Is Grid online at {env.GRID_URL} ?')
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise click.ClickException('Not authorized. Did you login?')
            if e.response.status_code == 500:
                raise click.ClickException('Grid is having issues. Please again later.')
            raise click.ClickException('We encountered an unknown error.')

        except requests.exceptions.Timeout:
            raise click.ClickException('Could not reach Grid. Are you online?')

        except TransportProtocolError:
            raise click.ClickException('Not authorized. Did you login?')

        except Exception as e:
            raise click.ClickException(f"{type(e).__name__}: {e}")

    def query(self, query: str, **kwargs) -> Dict:
        """Executes a GraphQL query against Grid's API."""
        # instantiate http transport
        if not hasattr(self, "transport") or not isinstance(self.transport, RequestsHTTPTransport):
            self._init_client(websocket=False)

        values = kwargs or {}
        try:
            result = self.client.execute(gql(query), variable_values=values)
        except TransportQueryError as e:
            raise click.ClickException(e.args)
        except Exception as e:
            raise click.ClickException(f"{type(e).__name__}: {e}")
        if 'error' in result:
            raise click.ClickException(json.dumps(result['error']))
        return result

    def mutate(self, query: str, **kwargs) -> Dict:
        """Executes a GraphQL mutation against Grid's API."""
        # instantiate http transport
        if not hasattr(self, "transport") or not isinstance(self.transport, RequestsHTTPTransport):
            self._init_client(websocket=False)

        return self.query(query, **kwargs)

    def subscribe(self, query: str, **kwargs) -> Dict:
        """Streams data from a GraphQL subscription"""
        # instantiate a websocket transport
        if not hasattr(self, "transport") or not isinstance(self.transport, WebsocketsTransport):
            self._init_client(websocket=True)

        values = kwargs or {}
        try:
            stream = self.client.subscribe(gql(query), variable_values=values)
            for element in stream:
                yield element

        # If connection is suddenly closed, indicate that a known
        # error happened.
        except websockets.exceptions.ConnectionClosedError:
            raise click.ClickException("Connection closed. No new messages available.")

        except websockets.exceptions.ConnectionClosedOK:
            raise click.ClickException("Connection closed. No new messages available.")

        except asyncio.exceptions.TimeoutError:
            raise click.ClickException("Timeout waiting for messages exceeded.")

        #  Raise any other errors that the backend may raise.
        except Exception as e:  # skipcq: PYL-W0703
            raise click.ClickException(str(e))

    # skipcq: PYL-W0102
    def status(
        self,
        kind: Optional[ObservableType] = None,
        identifiers: Optional[List[str]] = None,
        follow: Optional[bool] = False,
        export: Optional[str] = None,
        is_global: Optional[bool] = False
    ) -> None:
        """
        The status of an observable object in Grid. That can be a Cluster,
        a Run, or an Experiment.

        Parameters
        ----------
        kind: Optional[ObservableType], default None
            Kind of object that we should get the status from
        identifiers: List[str], default []
            Observable identifiers
        follow: bool, default False
            If we should generate a live table with results.
        export: Optional[str], default None
            What type of file results should be exported to, if any.
        is_global: Optional[bool], default False
            Returns status of resources from everyone in the team
        """
        #  We'll instantiate a websocket client when users
        #  want to follow an observable.
        if follow:
            self._init_client(websocket=True)

        kind = kind or ObservableType.RUN

        if kind == ObservableType.EXPERIMENT:
            observable = self.available_observables[kind](client=self.client, identifier=identifiers[0])

        elif kind == ObservableType.RUN:
            if not identifiers:
                observable = self.available_observables[ObservableType.RUN](client=self.client)
            else:
                #  For now, we only check the first observable.
                #  We should also check for others in the future.
                observable = self.available_observables[kind](client=self.client, identifier=identifiers[0])

        elif kind == ObservableType.INTERACTIVE:
            # Create observable.
            observable = self.available_observables[kind](client=self.client)

        elif kind == ObservableType.CLUSTER:
            raise click.BadArgumentUsage("It isn't yet possible to observe clusters.")

        else:
            raise click.BadArgumentUsage('No observable instance created.')

        if follow:
            result = observable.follow(is_global=is_global)
        else:
            result = observable.get(is_global=is_global)

        #  Save status results to a file, if the user has specified.
        if export:
            try:

                #  No need to continue if there are not results.
                if not result:
                    click.echo('\nNo run data to write to CSV file.\n')
                    return result

                #  The user may have requested a table of
                #  Runs or Experiments, use the key that is returned
                #  by the API.
                results_key = list(result.keys())[0]

                #  Initialize variables.
                path = None
                now = datetime.now()

                #  Basic format ISO 8601
                date_string = f'{now:%Y%m%dT%H%M%S}'

                if export == 'csv':
                    path = f'grid-status-{date_string}.csv'
                    with open(path, 'w') as csv_file:

                        #  We'll exclude any List or Dict from being
                        #  exported in the CSV. We do this to avoid
                        #  generating a CSV that contains JSON data.
                        #  There aren't too many negative sides to this
                        #  because the nested data isn't as relevant.
                        sample = result[results_key][0]
                        _sample = sample.copy()
                        for k, v in _sample.items():
                            if isinstance(v, (list, dict)):
                                del sample[k]  # skipcq: PTC-W0043

                        columns = sample.keys()
                        writer = csv.DictWriter(csv_file, fieldnames=columns)
                        writer.writeheader()
                        for data in result[results_key]:
                            writer.writerow({k: v for k, v in data.items() if k in columns})

                elif export == 'json':
                    path = f'grid_status-{date_string}.json'
                    with open(path, 'w') as json_file:
                        json_file.write(json.dumps(result[results_key]))

                if path:
                    click.echo(f'\nExported status to file: {path}\n')

            #  Catch possible errors when trying to create file
            #  in file system.
            except (IOError, TypeError) as e:
                if env.DEBUG:
                    click.echo(e)

                raise click.FileError('Failed to save grid status to file\n')

        return result

    @staticmethod
    def get_experiment_id(experiment_name: str) -> str:
        """
        Get experiment ID from name.

        Parameters
        ----------
        experiment_name: str
            Experiment name

        Returns
        --------
        experiment_id: str
            Experiment ID
        """
        spinner = yaspin.yaspin(text="Getting experiment info...", color="yellow")
        try:
            # TODO refactor this when we continue the work on SDK
            from grid.cli.core import Experiment as ExperimentGridObject
            spinner.start()
            exp = ExperimentGridObject(experiment_name)
            spinner.ok("✔")
        except Exception as e:
            spinner.fail("✘")
            raise click.ClickException(
                f"Could not find experiment: {e}. "
                f"If you meant to fetch experiment owned by "
                f"another person, use the format <username>:<experiment-name>"
            )
        finally:
            spinner.stop()
        return exp.identifier

    def experiment_details(self, experiment_id: str) -> Dict[str, Any]:
        """
        Get experiment details.

        Parameters
        ----------
        experiment_id: str
            Experiment ID

        Returns
        --------
        details: Dict[str, Any]
            Experiment details
        """
        # If job is queued, notify the user that logs aren't available yet
        query = gql(
            """
        query (
            $experimentId: ID!
        ) {
            getExperimentDetails(experimentId: $experimentId) {
                experimentId
                run {
                  name
                }
                status
            }
        }
        """
        )
        params = {'experimentId': experiment_id}
        result = self.client.execute(query, variable_values=params)

        return result

    # TODO: refactor this to break into smaller methods.
    def experiment_logs(
        self,
        experiment_name: str,
        n_lines: int = 50,
        page: Optional[int] = None,
        max_lines: Optional[int] = None,
        use_pager: bool = False
    ) -> Dict[str, str]:
        """
        Gets experiment logs from a single experiment.

        Parameters
        ----------
        n_lines: int, default 200
            Max number of lines to return
        experiment_name: str
            Experiment name for a single experiment
        page: Optional[int], default None
            Which page of logs to fetch.
        max_lines: Optional[int], default None
            Maximum number of lines to print in terminal.
        use_pager: bool, default False
            If the log results should be a scrollable pager.
        """
        experiment_id = self.get_experiment_id(experiment_name=experiment_name)

        #  Starts spinner.
        spinner = yaspin.yaspin(text="Fetching logs ...", color="yellow")
        spinner.start()

        # If the experiment is in a finished state, then
        # get logs from archive.
        finished_states = ('failed', 'succeeded', 'cancelled')
        experiment_details = self.experiment_details(experiment_id=experiment_id)

        # Check if Experiment is queued.
        state = experiment_details['getExperimentDetails']['status']

        if state == 'queued':
            spinner.ok("✔")
            styled_queued = click.style('queued', fg='yellow')
            click.echo(
                f"""
                Your Experiment is {styled_queued}. Logs will be available
                when your Experiment starts.
                        """
            )
            spinner.stop()
            return

        # Check if the user has requested logs from the
        # archive explicitly or if the experiment is in a
        # finished state.
        is_archive_request = page is not None
        is_finished_state = state in finished_states
        if is_archive_request or is_finished_state:

            query = gql(
                """
            query GetLogs ($experimentId: ID!, $page: Int) {
                getArchiveExperimentLogs(experimentId: $experimentId, page: $page) {
                    lines {
                        message
                        timestamp
                    }
                    currentPage
                    totalPages
                }
            }
            """
            )
            params = {'experimentId': experiment_id, 'page': page}
            try:
                result = self.client.execute(query, variable_values=params)

            #  Raise any other errors that the backend may raise.
            except Exception as e:  # skipcq: PYL-W0703
                spinner.fail("✘")
                if 'Server error:' in str(e):
                    e = str(e).replace('Server error: ', '')[1:-1]

                message = ast.literal_eval(str(e))['message']
                raise click.ClickException(message)

            # The backend will return end empty object if no pages
            # of logs are available.
            if not result.get('getArchiveExperimentLogs') or not result['getArchiveExperimentLogs'].get('lines'):
                spinner.stop()
                raise click.ClickException(f'No logs available for experiment {experiment_name}')

            # Print message to help users read all logs.
            separator = '-' * 80
            page_command_message = f"""We will be displaying logs from the archives.

        $ grid logs {experiment_name}
    {separator}"""

            # Print messages indicating that other log pages are
            # available.
            styled_experiment_name = click.style(experiment_name, fg='blue')
            styled_state = click.style(state, fg='magenta')
            prompt_message = f"""

    The Experiment {styled_experiment_name} is in a finished
    state ({styled_state}). {page_command_message}

            """

            if is_archive_request:
                prompt_message = page_command_message

            spinner.ok("✔")
            spinner.stop()
            click.echo(prompt_message)

            # Get all log lines.
            lines = result['getArchiveExperimentLogs']['lines']
            total_lines = len(lines)
            if total_lines > self.acceptable_lines_to_print and not max_lines:
                styled_total_lines = click.style(str(total_lines), fg='red')
                too_many_lines_message = f"""    {click.style('NOTICE', fg='yellow')}: The log stream you requested contains {styled_total_lines} lines.
    You can limit how many lines to print by using:

        $ grid logs {experiment_name} --max_lines 50


    Would you like to proceed? """
                click.confirm(too_many_lines_message, abort=True, default=True)

            # Style the log lines.
            styled_logs = []
            for log in lines[:max_lines]:

                # If no timestamps are returned, fill the field
                # with dashes.
                if not log['timestamp']:
                    # Timestamps have 32 characters.
                    timestamp = click.style('-' * 32, fg='green')
                else:
                    timestamp = click.style(log['timestamp'], fg='green')

                styled_logs.append(f"[{timestamp}] {log['message']}")

            # Either print the logs in the terminal or use the pager
            # to scroll through the logs.
            if use_pager:
                click.echo_via_pager(styled_logs)
            else:
                for line in styled_logs:
                    click.echo(line, nl=False)

        # If the experiment isn't in a finished state, then
        # do a subscription with live logs.
        else:

            #  Let's first change the client transport to use
            #  a websocket transport instead of using the regular
            #  HTTP transport.
            self._init_client(websocket=True)

            subscription = gql(
                """
            subscription GetLogs ($experimentId: ID!, $nLines: Int!) {
                getLiveExperimentLogs(
                    experimentId: $experimentId, nLines: $nLines) {
                        message
                        timestamp
                }
            }
            """
            )

            params = {'experimentId': experiment_details['getExperimentDetails']['experimentId'], 'nLines': n_lines}

            # Create websocket connection.
            connection_closed_message = "Connection closed. Please try again."
            try:
                stream = self.client.subscribe(subscription, variable_values=params)

                first_run = True
                for log in stream:

                    #  Closes the spinner.
                    if first_run:
                        spinner.ok("✔")
                        first_run = False

                    #  Prints each line to terminal.
                    log_entries = log['getLiveExperimentLogs']
                    for entry in log_entries:
                        # If no timestamps are returned, fill the field
                        # with dashes.
                        if not entry['timestamp']:
                            # Timestamps have 32 characters.
                            timestamp = click.style('-' * 32, fg='green')
                        else:
                            timestamp = click.style(entry['timestamp'], fg='green')

                        click.echo(f"[{timestamp}] {entry['message']}", nl=False)

            # If connection is suddenly closed, indicate that a
            # known error happened.
            except websockets.exceptions.ConnectionClosed:
                spinner.fail("✘")
                raise click.ClickException(connection_closed_message)

            except websockets.exceptions.ConnectionClosedOK:
                spinner.fail("✘")
                raise click.ClickException('Could not continue fetching log stream.')

            # Raise any other errors that the backend may raise.
            except Exception as e:  # skipcq: PYL-W0703
                raise click.ClickException(connection_closed_message)

        #  Makes sure to close the spinner in all situations.
        #  If we don't do this, the tracker character in the terminal
        #  disappears.
        spinner.stop()

    def experiment_metrics(self, experiment_name: str, metric: str, n_lines: int = 50) -> Dict[str, str]:
        """
        Gets experiment scalar logs from a single experiment.

        Parameters
        ----------
        experiment_name: str
            Experiment name for a single experiment
        metric: str
            Metric names
        n_lines: int, default 50
            Max number of lines to return
        """
        experiment_id = self.get_experiment_id(experiment_name=experiment_name)

        #  Starts spinner.
        spinner = yaspin.yaspin(text="Fetching metrics ...", color="yellow")
        spinner.start()

        experiment_details = self.experiment_details(experiment_id=experiment_id)

        # Check if Experiment is queued.
        state = experiment_details['getExperimentDetails']['status']
        if state == 'queued':
            spinner.ok("✔")
            styled_queued = click.style('queued', fg='yellow')
            click.echo(
                f"""
    Your Experiment is {styled_queued}. Metrics will be available
    when your Experiment starts.
            """
            )
            spinner.stop()
            return

        query = gql(
            """
        query GetScalarLogs ($experimentId: ID!, $metric: String!, $startIndex: Int, $format: String) {
            getExperimentScalarLogs(experimentId: $experimentId,
                                    metric: $metric,
                                    startIndex: $startIndex,
                                    format: $format) {
                values
                steps
                nextIndex
            }
        }
        """
        )

        params = {'experimentId': experiment_id, 'metric': metric, 'startIndex': 0, 'format': 'json'}

        try:
            result = self.client.execute(query, variable_values=params)
        #  Raise any other errors that the backend may raise.
        except Exception as e:  # skipcq: PYL-W0703
            spinner.fail("✘")
            if 'Server error:' in str(e):
                e = str(e).replace('Server error: ', '')[1:-1]

            message = ast.literal_eval(str(e))['message']
            raise click.ClickException(message)

        metric = result['getExperimentScalarLogs']
        # The backend will return an empty object if no metrics
        # are available.
        if not metric or not metric['steps']:
            spinner.stop()
            raise click.ClickException(f'No metrics available for experiment {experiment_id}')

        spinner.ok("✔")
        spinner.stop()

        # TODO: Change when encoding and compression is fixed in
        # backend API
        # def decode(x: bytes, dtype: str):
        #     buf = zlib.decompress(base64.b64decode(x.encode()))
        #     out = array(dtype)
        #     out.frombytes(buf)
        #     return out

        try:
            # steps = decode(metric['steps'], 'q')
            # values = decode(metric['values'], 'd')

            steps = json.loads(metric['steps'])
            values = json.loads(metric['values'])
        #  Raise any other errors that the backend may raise.
        except Exception as e:
            spinner.fail("✘")
            if 'Server error:' in str(e):
                e = str(e).replace('Server error: ', '')[1:-1]

            message = ast.literal_eval(str(e))['message']
            raise click.ClickException(message)

        if n_lines > 0:
            steps = steps[-n_lines:]
            values = values[-n_lines:]

        # Get all metrics in lines
        lines = [f"{step:>16}  {value:.10f}\n" for step, value in zip(steps, values)]

        # Print the metrics in the terminal
        for line in lines:
            click.echo(line, nl=False)

        #  Makes sure to close the spinner in all situations.
        #  If we don't do this, the tracker character in the terminal
        #  disappears.
        spinner.stop()

    def delete_datastore(self, name: str, version: int, cluster: Optional[str] = None):
        """
        Delete datastore for user

        Parameters
        ----------
        name: str
            Datastore name
        version: int
            Datastore version
        cluster
            cluster id to operate on
        """
        mutation = gql(
            """
            mutation (
                $name: String!
                $version: Int!
                $clusterId: String
                ) {
                deleteDatastore (
                    properties: {
                            name: $name,
                            version: $version,
                            clusterId: $clusterId
                        }
                ) {
                success
                message
                }
            }
            """
        )

        params = {'name': name, 'version': version, 'clusterId': cluster}

        spinner = yaspin.yaspin(text=f'Deleting datastore {name} with version {version}', color="yellow")
        spinner.start()

        try:
            result = self.client.execute(mutation, variable_values=params)
            success = result['deleteDatastore']['success']
            message = result['deleteDatastore']['message']

            if success:
                spinner.text = "Finished deleting datastore."
                spinner.ok("✔")
            else:
                spinner.text = f'Failed to delete datastore {name} with version ' \
                               f'{version}: {message}'
                spinner.fail("✘")

        except Exception as e:  #skipcq: PYL-W0703
            spinner.fail("✘")
            raise click.ClickException(f'Failed to delete datastore {name} with version {version}. {e}')

        spinner.stop()
        return success

    def resume_datastore_session(self, session_name: str):
        """
        Resume uploading a datastore session

        Parameters
        ----------
        session_name: str
            Name of session
        """
        sessions = DatastoreUploadSession.recover_sessions()
        session = None
        for s in sessions:
            if s.session_name == session_name:
                session = s
                break

        if not session:
            self.__print_datastore_sessions(sessions)
            raise click.ClickException(
                f"No session named {session_name} found, please specify an " + "available session"
            )

        session.configure()
        try:
            session.upload()
        except Exception as e:  #skipcq: PYL-W0703
            import traceback
            traceback.print_exc()
            raise click.ClickException(f'Failed to upload datastore {session.name}. {e}')

    @staticmethod
    def __print_datastore_sessions(sessions: List[DatastoreUploadSession]):
        """
        Print the table of datastore sessions
        """
        click.echo("Available datastore incomplete uploads that can be resumed: ")
        table_cols = ['Name', 'Version', "Command to resume"]
        table = BaseObservable.create_table(columns=table_cols)
        for session in sessions:
            command = f"grid datastore resume {session.session_name}"
            table.add_row(session.name, str(session.version), command)

        console = Console()
        console.print(table)

    def list_resumable_datastore_sessions(self):
        """
        List datastores that can be resumed upload
        """
        sessions = DatastoreUploadSession.recover_sessions()
        if len(sessions) == 0:
            return

        click.echo("")
        click.echo("")
        self.__print_datastore_sessions(sessions)

    @staticmethod
    def upload_datastore(source: str, name: str, compression: bool, cluster: Optional[str] = None):
        """
        Uploads datastore to storage

        Parameters
        ----------
        source: str
           Source to create datastore from, either a local directory or a
           http url.
        name: str
           Name of datastore
        compression: str
            Enable compression, which is disabled by default
        cluster
            Cluster id to create the datastore on.

        Returns
        -------
        success: bool
            Truthy when a datastore has been uploaded
            correctly.
        """
        try:
            session = create_datastore_session(
                name=name,
                source=source,
                compression=compression,
                cluster=cluster,
            )
            session.upload()
        except Exception as e:  # skipcq: PYL-W0703
            import traceback
            traceback.print_exc()
            raise click.ClickException(f'Failed to upload datastore {name}. {e}')

        return True

    def add_ssh_public_key(self, key: str, name: str):
        return self.query(
            """
            mutation (
                $publicKey: String!
                $name: String!
            ) {
            addSSHPublicKey(name: $name, publicKey: $publicKey) {
                message
                success
                id
              }
            }
        """,
            publicKey=key,
            name=name
        )

    def list_public_ssh_keys(self, limit: int) -> List[Dict[str, str]]:
        result = self.query(
            """
            query (
                $limit: Int!,
            ) {
                getPublicSSHKeys(limit: $limit) {
                    id
                    publicKey,
                    name
              }
            }
        """,
            limit=limit,
        )
        return result['getPublicSSHKeys']

    def delete_ssh_public_key(self, key_id: str):
        self.query(
            """
            mutation (
                $id: ID!
            ) {
              deleteSSHPublicKey(id: $id) {
                message
                success
              }
            }
        """,
            id=key_id
        )

    def list_interactive_node_ssh_setting(self):
        return self.query(
            """
        query {
            getInteractiveNodes {
                name: interactiveNodeName
                ssh_url: sshUrl
                status
            }
        }
        """
        )['getInteractiveNodes']

    @staticmethod
    def _gen_ssh_config(
        interactive_nodes: List[Dict[str, Any]],
        curr_config: str,
        start_marker: str = "### grid.ai managed BEGIN do not edit manually###",
        end_marker: str = "### grid.ai managed END do not edit manually###",
    ):

        content = curr_config.splitlines()
        sol = []
        managed_part = [start_marker]
        for node in interactive_nodes:
            if node["status"] != "running":
                continue

            ssh_url = urlsplit(node['ssh_url'])
            managed_part.extend([
                f"Host {node['name']}",
                f"    User {ssh_url.username}",
                f"    Hostname {ssh_url.hostname}",
                f"    Port {ssh_url.port}",
                "    StrictHostKeyChecking accept-new",
                "    CheckHostIP no",
                "    ServerAliveInterval 15",
                "    ServerAliveCountMax 4",
                # Workarounds until https://linear.app/gridai/issue/GI-6940/switch-client-ssh-gateway-communication-to-use-ed25519-keys-over-rsa
                # is fixed
                "    HostKeyAlgorithms=+ssh-rsa",
                "    PubkeyAcceptedKeyTypes +ssh-rsa",
                "    PasswordAuthentication no",
            ])
        managed_part.append(end_marker)

        within_section = False
        added_managed_part = False
        for line in content:
            if line == start_marker:
                if added_managed_part:
                    raise ValueError("Found 2 start markers")
                if within_section:
                    raise ValueError("Found 2 start markers in row")
                within_section = True
            elif end_marker == line:
                if added_managed_part:
                    raise ValueError("Found 2+ start end")
                if not within_section:
                    raise ValueError("End marker before start marker")
                within_section = False
                sol.extend(managed_part)
                added_managed_part = True
            elif not within_section:
                sol.append(line)
        if within_section:
            raise ValueError("Found only start marker, no end one found")
        if not added_managed_part:
            sol.extend(managed_part)
        return '\n'.join(sol)

    def sync_ssh_config(self) -> List[str]:
        """
        sync local ssh config with grid's interactive nodes config

        Returns
        -------
        list of interactive nodes present
        """
        interactive_nodes = self.list_interactive_node_ssh_setting()

        ssh_config = Path(env.GRID_SSH_CONFIG)
        if not ssh_config.exists():
            ssh_config.write_text("")

        ssh_config.write_text(
            self._gen_ssh_config(
                interactive_nodes=interactive_nodes,
                curr_config=ssh_config.read_text(),
            )
        )

        return interactive_nodes

    def check_is_blocked(self, user_data: Optional[Any] = None) -> None:
        """Checks if user account is currently blocked from performing operations on Grid.

        Parameters
        ----------
        user_data:
            If user data is already fetched, pass that as an argument. If not this function will
            fetch it from graphQL directly
        """
        if not user_data:
            query = """
            query {
                getUser {
                    isVerified
                    completedSignup
                    isBlocked
                }
            }
            """
            user_data = self.query(query)["getUser"]

        if user_data.get("isVerified") is False:
            raise click.UsageError(
                f"User account not yet verified. Verify your account at {env.GRID_URL}/#/verification"
            )

        if user_data.get("completedSignup") is False:
            raise click.UsageError(
                f"You haven't yet completed registration. Please complete registration at {env.GRID_URL}/#/registration"
            )

        if user_data.get("isBlocked") is True:
            raise click.UsageError("Your account is blocked. Please reach out to support at support@grid.ai")
