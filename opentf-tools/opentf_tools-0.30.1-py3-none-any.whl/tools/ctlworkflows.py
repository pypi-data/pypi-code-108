# Copyright 2021 Henix, henix.fr
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""opentf-ctl"""

import os
import sys

from time import sleep

from opentf.tools.ctlcommons import (
    _is_command,
    _get_value,
    _get_columns,
    _emit_csv,
    _ensure_uuid,
    _error,
    _warning,
    _debug,
)
from opentf.tools.ctlconfig import read_configuration
from opentf.tools.ctlnetworking import (
    _observer,
    _receptionist,
    _killswitch,
    _get,
    _delete,
    _post,
)


########################################################################

# pylint: disable=broad-except

DEFAULT_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.details.status',
    'NAME:.metadata.name',
)
WIDE_COLUMNS = (
    'WORKFLOW_ID:.metadata.workflow_id',
    'STATUS:.details.status',
    'FIRST_SEEN_TIMESTAMP:.metadata.creationTimestamp',
    'NAME:.metadata.name',
)


WATCHED_EVENTS = (
    'ExecutionCommand',
    'ExecutionResult',
    'ExecutionError',
    'ProviderCommand',
    'GeneratorCommand',
)

AUTOVARIABLES_PREFIX = 'OPENTF_RUN_'

WARMUP_DELAY = 5
REFRESH_DELAY = 10


########################################################################
# Help messages

RUN_WORKFLOW_HELP = '''Start a workflow

Examples:
  # Start the workflow defined in my_workflow.yaml
  opentf-ctl run workflow my_workflow.yaml

  # Start the workflow and wait until it completes
  opentf-ctl run workflow my_workflow.yaml --wait

  # Start the workflow and define an environment variable
  opentf-ctl run workflow my_workflow.yaml -e TARGET=example.com

  # Start a workflow and provide environment variables defined in a file
  opentf-ctl run workflow my_workflow.yaml -e variables

  # Start a workflow and provide a localy-defined environment variable
  export OPENTF_RUN_MYVAR=my_value
  opentf-ctl run workflow my_workflow.yaml  # variable 'MYVAR' will be defined

  # Start the wokflow and provide a local file
  opentf-ctl run workflow my_workflow.yaml -f key=./access_key.pem

Environment variables:
  Environment variables with an 'OPENTF_RUN_' prefix will be defined without the prefix in the workflow and while running commands in execution environment.

Options:
  -e var=value: 'var' will be defined in the workflow and while running commands in execution environment.
  -e path/to/file: variables defined in file will be defined in the workflow and while running commands in execution environment.  'file' must contain one variable definition per line, of the form 'var=value'.
  -f name=path/to/file: the specified local file will be available for use by the workflow.  'name' is the file name specified in the `resources.files` part of the workflow.
  --wait: wait for workflow completion.
  --step_depth=1: show nested steps to the given depth (only used with --wait).
  --job_depth=1: show nested jobs to the given depth (only used with --wait).

Usage:
  opentf-ctl run workflow NAME [-e var=value]... [-e path/to/file] [-f name=path/to/file]... [--wait] [--job_depth=value] [--step_depth=value] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

GET_WORKFLOW_HELP = '''Get a workflow status

Examples:
  # Get the current status of a workflow
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

  # Get the status of a workflow and wait until its completion
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --watch

  # Get the status of a workflow, showing first-level nested steps
  opentf-ctl get workflow 9ea3be45-ee90-4135-b47f-e66e4f793383 --step_depth=2

Options:
  --step_depth=1: show nested steps to the given depth.
  --job_depth=1: show nested jobs to the given depth.
  --watch: wait until workflow completion or cancellation, displaying status updates as they occur.

Usage:
  opentf-ctl get workflow WORKFLOW_ID [--step_depth=value] [--job_depth=value] [--watch] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

GET_WORKFLOWS_HELP = '''List active and recent workflows

Examples:
  # List the IDs of active and recent workflows
  opentf-ctl get workflows

  # Get the status of active and recent workflows
  opentf-ctl get workflows --output=wide

  # Get just the workflow IDs of active and recent workflows
  opentf-ctl get workflows --output=custom-columns=ID:.metadata.workflow_id

Options:
  --output=wide or -o wide: show additional information.
  --output=custom-columns= or -o custom-columns=: show specified information.

Usage:
  opentf-ctl get workflows [--output=wide] [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''

KILL_WORKFLOW_HELP = '''Kill a running workflow

Example:
  # Kill the specified workflow
  opentf-ctl kill workflow 9ea3be45-ee90-4135-b47f-e66e4f793383

Usage:
  opentf-ctl kill workflow WORKFLOW_ID [options]

Use "opentf-ctl options" for a list of global command-line options (applies to all commands).
'''


########################################################################
# Eventbus


def _file_not_found(name, err):
    _error('File not found: %s.', name)
    _debug('Error is: %s.', err)
    sys.exit(2)


def _read_variables_file(file, variables):
    """Read file and add variables.

    Abort with an error code 2 if the file does not exist or contains
    invalid content.
    """
    try:
        with open(file, 'r', encoding='utf-8') as varfile:
            for line in varfile:
                if '=' not in line:
                    _error(
                        'Invalid format in file %s, was expecting var=value.',
                        file,
                    )
                    sys.exit(2)
                var, _, value = line.strip().partition('=')
                variables[var] = value
    except FileNotFoundError as err:
        _file_not_found(file, err)


def _add_files(args, files):
    """Handling -f file command-line options."""
    process = False
    for option in args:
        if option == '-f':
            process = True
            continue
        if process:
            process = False
            name, path = option.split('=')
            try:
                files[name] = open(path, 'rb')
            except FileNotFoundError as err:
                _file_not_found(path, err)


def _add_variables(args, files):
    """Handling -e file and -e var=value command-line options."""
    # OPENTF_CONFIG and OPENTF_TOKEN are explicitly excluded to prevent
    # unexpected leak
    variables = {
        key[len(AUTOVARIABLES_PREFIX) :]: value
        for key, value in os.environ.items()
        if key.startswith(AUTOVARIABLES_PREFIX)
        and key not in ('OPENTF_CONFIG', 'OPENTF_TOKEN')
    }
    process = False
    for option in args:
        if option == '-e':
            process = True
            continue
        if process:
            process = False
            if '=' in option:
                var, _, value = option.partition('=')
                variables[var] = value
            else:
                _read_variables_file(option, variables)
    if variables:
        files['variables'] = '\n'.join(f'{k}={v}' for k, v in variables.items())


def _generate_row(workflow_id, response, columns):
    row = []
    for item in columns:
        field = item.split(':')[1]
        if field == '.metadata.workflow_id':
            row.append(workflow_id)
        if field == '.details.status':
            row.append(response['details']['status'])
        if field == '.metadata.name':
            what = response['details']['items']
            if what and what[0].get('kind') == 'Workflow':
                row.append(what[0]['metadata']['name'])
            else:
                row.append('')
        if field == '.metadata.creationTimestamp':
            what = response['details']['items']
            if what:
                row.append(what[0].get('metadata', {}).get('creationTimestamp', ''))
            else:
                row.append('')
    return row


def _generate_rows(workflows_ids, columns):
    for workflow_id in workflows_ids:
        response = _get_first_page(workflow_id)
        if response.status_code == 200:
            yield _generate_row(workflow_id, response.json(), columns)
        else:
            print(workflow_id, 'got response code', response.status_code)


def _handler_maybe_outdated(response):
    if response.status_code in (404, 405):
        _error('Could not get workflows list.  Maybe an outdated orchestrator version.')
        _debug('(Return code was %d.)', response.status_code)
    else:
        _error(
            'Could not get workflows list.  Return code was %d.',
            response.status_code,
        )
    sys.exit(2)


def list_workflows():
    """List active and recent workflows."""
    try:
        columns = _get_columns(WIDE_COLUMNS, DEFAULT_COLUMNS)
    except ValueError as err:
        _error('Invalid parameters: %s.', err)
        sys.exit(2)
    except Exception as err:
        _error('Cound not get columns specification: %s', err)

    response = _get(
        _observer(),
        '/workflows',
        'Could not get workflows list',
        handler=_handler_maybe_outdated,
    )
    workflows_ids = response['details']['items']
    _emit_csv(_generate_rows(workflows_ids, columns), columns)


def _handler_maybe_details(response):
    _error(response.json()['message'])
    if response.json().get('details'):
        _error(response.json()['details'].get('error'))
    sys.exit(1)


def run_workflow(workflow_name):
    """Run a workflow.

    # Required parameters

    - workflow_name: a file name

    # Returned value

    Returns the workflow ID if everything was OK.

    # Raised exceptions

    Abort with an error code of 1 if the workflow was not properly
    received by the orchestrator.

    Abort with an error code of 2 if a parameter was invalid (file not
    found or invalid format).
    """
    try:
        files = {'workflow': open(workflow_name, 'r', encoding='utf-8')}
        _add_files(sys.argv[4:], files)
        _add_variables(sys.argv[4:], files)

        result = _post(
            _receptionist(),
            '/workflows',
            files=files,
            statuses=(201,),
            handler=_handler_maybe_details,
        )
        print('Workflow', result['details']['workflow_id'], 'is running.')
    except FileNotFoundError as err:
        _file_not_found(workflow_name, err)
    except Exception as err:
        _error('Could not start workflow: %s.', err)
        sys.exit(2)

    if '--wait' in sys.argv:
        sleep(WARMUP_DELAY)
        get_workflow(result['details']['workflow_id'], watch=True)


def _emit_prefix(event):
    print(
        f'[{event["metadata"]["creationTimestamp"][:-7]}]',
        f'[job {event["metadata"]["job_id"]}] ',
        end='',
    )


def _emit_command(event, silent):
    if event['metadata']['step_sequence_id'] == -1:
        _emit_prefix(event)
        print(
            'Requesting execution environment providing',
            event['runs-on'],
            'for job',
            repr(event['metadata']['name']),
        )
    elif event['metadata']['step_sequence_id'] == -2:
        _emit_prefix(event)
        print(
            'Releasing execution environment for job',
            repr(event['metadata']['name']),
        )
    elif not silent:
        _emit_prefix(event)
        print(' ' * (len(event['metadata'].get('step_origin', []))), end='')
        print('Running command', event['scripts'])


def _emit_result(event, silent):
    for item in event.get('logs', []):
        _emit_prefix(event)
        print(item)
    if event['status'] == 0 or silent:
        return
    _emit_prefix(event)
    print('Status code was:', event['status'])


def _show_events(items, step_depth, job_depth):
    """Show watched events.

    Can be used to show partial items.
    """
    cancelation_event = None
    for event in items:
        silent = False
        kind = event.get('kind')
        if kind == 'Workflow':
            print('Workflow', event['metadata']['name'])
            continue
        if kind == 'WorkflowCanceled':
            cancelation_event = event
        if kind not in WATCHED_EVENTS:
            continue
        if kind == 'ExecutionError':
            _emit_prefix(event)
            print(event.get('details', {}).get('error'))
            continue

        if job_depth and len(event['metadata'].get('job_origin', [])) >= job_depth:
            silent = True
        elif step_depth and len(event['metadata'].get('step_origin', [])) >= step_depth:
            silent = True

        if kind == 'ExecutionResult':
            _emit_result(event, silent)
            continue

        if kind == 'ExecutionCommand':
            _emit_command(event, silent)
            continue

        if not silent:
            _emit_prefix(event)
            print(' ' * (len(event['metadata'].get('step_origin', []))), end='')
            print('Running action', event['metadata']['name'])
    return cancelation_event


def _get_first_page(workflow_id):
    """Return a requests.Response, to get following pages if needed."""

    def _handler_unknown_workflowid(response):
        if response.status_code == 404:
            _error(
                'Could not find workflow %s.  The ID is incorrect or too recent or too old.',
                workflow_id,
            )
            sys.exit(1)
        _error(
            'Could not get workflow %s.  Got status code %d (%s).',
            workflow_id,
            response.status_code,
            response.text,
        )
        sys.exit(1)

    return _get(
        _observer(),
        f'/workflows/{workflow_id}/status',
        handler=_handler_unknown_workflowid,
        raw=True,
    )


def _get_workflow_status(workflow_id):
    response = _get_first_page(workflow_id)
    status = response.json()

    while 'next' in response.links:
        response = _get(response.links['next']['url'])
        status['details']['items'] += response['details']['items']
    return status


def get_workflow(workflow_id, watch=False):
    """Get a workflow.

    # Required parameters

    - workflow_id: a string

    # Optional parameters

    - watch: a boolean (False by default)

    # Returned value

    The current workflow status.

    # Raised exceptions

    Abort with an error code 1 if the workflow could not be found on the
    orchestrator.

    Abort with an error code 2 if another error occurred.
    """
    _ensure_uuid(workflow_id)
    status = _get_workflow_status(workflow_id)

    current_item = 0
    job_depth = int(_get_value('--job-depth=') or 1)
    step_depth = int(_get_value('--step-depth=') or 1)

    while True:
        cancelation_event = _show_events(
            status['details']['items'][current_item:],
            job_depth=job_depth,
            step_depth=step_depth,
        )
        if not watch:
            break
        if status['details']['status'] != 'RUNNING':
            break
        current_item = len(status['details']['items'])
        while len(status['details']['items']) <= current_item:
            sleep(REFRESH_DELAY)
            status = _get_workflow_status(workflow_id)

    workflow_status = status['details']['status']
    if workflow_status == 'DONE':
        print('Workflow completed successfully.')
    elif workflow_status == 'RUNNING':
        print('Workflow is running.')
    elif workflow_status == 'FAILED':
        if (
            cancelation_event
            and cancelation_event.get('details', {}).get('status') == 'cancelled'
        ):
            print('Workflow cancelled.')
        else:
            print('Workflow failed.')
    else:
        _warning(
            'Unexpected workflow status: %s (was expecting DONE, RUNNING, or FAILED).',
            workflow_status,
        )


def kill_workflow(workflow_id):
    """Kill workflow.

    # Required parameter

    - workflow_id: a non-empty string (an UUID)

    # Raised exceptions

    Abort with an error code 1 if the orchestrator replied with an
    unexpected status code (!= 200).

    Abort with an error code 2 if an error occurred while contacting the
    orchestrator.
    """
    _ensure_uuid(workflow_id)
    _ = _delete(_killswitch(), f'/workflows/{workflow_id}')
    print(f'Killing workflow {workflow_id}.')


########################################################################
# Helpers


def print_workflow_help(args):
    """Display help."""
    if _is_command('run workflow', args):
        print(RUN_WORKFLOW_HELP)
    elif _is_command('get workflows', args):
        print(GET_WORKFLOWS_HELP)
    elif _is_command('get workflow', args):
        print(GET_WORKFLOW_HELP)
    elif _is_command('kill workflow', args):
        print(KILL_WORKFLOW_HELP)
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)


def workflow_cmd():
    """Interact with workflows."""
    if _is_command('get workflows', sys.argv):
        read_configuration()
        list_workflows()
    elif _is_command('run workflow _', sys.argv):
        read_configuration()
        run_workflow(sys.argv[3])
    elif _is_command('get workflow _', sys.argv):
        read_configuration()
        get_workflow(sys.argv[3], '--watch' in sys.argv)
    elif _is_command('kill workflow _', sys.argv):
        read_configuration()
        kill_workflow(sys.argv[3])
    else:
        _error('Unknown command.  Use --help to list known commands.')
        sys.exit(1)
