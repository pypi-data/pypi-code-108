import getpass

import click
from badook_tests.config import get_config

from badook_tests.context import BadookContext


@click.command()
@click.option('--delete', multiple=True)
@click.option('--delete-run', multiple=True)
@click.option('--from-project', multiple=False)
def project(delete, delete_run, from_project):
    if delete:
        project_list = ', '.join(delete)
        click.secho(f'deleting projects: {project_list}', fg='cyan', bold=True)
        send_delete_project_request(list(delete))

    elif delete_run and from_project:
        send_delete_runs_from_project_request(from_project, list(delete_run))


def send_delete_runs_from_project_request(project_id, runs):
    path = 'runhistory/run'
    config = get_config()
    context = BadookContext(
        config.client_id, config.client_secret, running_in_data_cluster=config.running_in_data_cluster)

    # send service manager request to delet projects
    body = {"projectId": project_id, "runIds": runs}
    response = context.api_client.send_json_delete_request(body, path)

    # send orchestrator request to delete projects records from postgres tables
    if not response['error']:
        request_data = {
            'project_id': project_id,
            'run_id': runs
        }
        response = context.client.send_json_delete_request(
            request_data, path=f'run')

    handle_response(response)


def send_delete_project_request(projects):
    path = f"runhistory/project"

    config = get_config()
    context = BadookContext(
        config.client_id, config.client_secret, running_in_data_cluster=config.running_in_data_cluster)

    # send service manager request to delete projects
    response = context.api_client.send_json_delete_request(
        {'projects': projects}, path)

    # send orchestrator request to delete projects records from postgres tables
    if not response['error']:
        request_data = {
            'project_id': projects
        }
        response = context.client.send_json_delete_request(
            request_data, path=f'project')

    handle_response(response)


def handle_response(response):
    if response['error']:
        err_msg = response['error']['message']
        click.secho(f'\nERROR: {err_msg}', fg='red', bold=True)
    else:
        click.secho(f'\ndeleting projects was successful',
                    fg='green', bold=True)
