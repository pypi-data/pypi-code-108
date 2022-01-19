import click
import os
from ...utils.env_keys import REPORT_ERROR_KEY
from ...utils.http_client import LaunchableClient
from tabulate import tabulate
from http import HTTPStatus


@click.command()
@click.option(
    '--test-session-id',
    'test_session_id',
    help='test session id',
    required=True
)
def tests(test_session_id):
    try:
        client = LaunchableClient()
        res = client.request(
            "get", "/test_sessions/{}/events".format(test_session_id))

        if res.status_code == HTTPStatus.NOT_FOUND:
            click.echo(click.style(
                "Test session {} not found. Check test session ID and try again.".format(test_session_id), 'yellow'), err=True)
            exit(1)

        res.raise_for_status()
        results = res.json()
    except Exception as e:
        if os.getenv(REPORT_ERROR_KEY):
            raise e
        else:
            click.echo(e, err=True)
        click.echo(click.style(
            "Warning: failed to inspect tests", fg='yellow'),
            err=True)

        return

    header = ["Test Path",
              "Duration (sec)", "Status",  "Uploaded At"]

    rows = [["#".join([path["type"] + "=" + path["name"] for path in result["testPath"]]),
             "{:0.4f}".format(result["duration"]), result["status"], result["createdAt"]] for result in results]

    click.echo(tabulate(rows, header, tablefmt="github"))
