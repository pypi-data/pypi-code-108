"""
    lager.auth.commands

    auth commands
"""

import time
import urllib.parse
import webbrowser
import requests
import click
from . import (
    get_client_id, get_auth_url, get_audience,
    read_config_file, write_config_file,
)
from ..context import LagerContext

SCOPE = 'read:gateway flash:duck offline_access'

def poll_for_token(device_code, interval):
    """
        Poll for an auth token for the specified device at the given interval
    """
    data = {
        'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
        'device_code': device_code,
        'client_id': get_client_id(),
    }
    token_url = urllib.parse.urljoin(get_auth_url(), '/oauth/token')
    while True:
        resp = requests.post(token_url, data=data)
        if resp.status_code == 200:
            return resp.json()

        if resp.status_code >= 500:
            resp.raise_for_status()

        error = resp.json()['error']
        if error == 'authorization_pending':
            time.sleep(interval)
        elif error == 'expired_token':
            click.secho('Session timed out. Please run `lager login` again.', err=True, fg='red')
            click.get_current_context().exit(1)
        elif error == 'access_denied':
            click.secho('Access denied.', err=True, fg='red')
            click.get_current_context().exit(1)


@click.command()
@click.pass_context
def login(ctx):
    """
        Log in
    """
    has_browser = True
    try:
        webbrowser.get()
    except webbrowser.Error:
        has_browser = False

    data = {
        'audience': get_audience(),
        'scope': SCOPE,
        'client_id': get_client_id(),
    }
    code_url = urllib.parse.urljoin(get_auth_url(), '/oauth/device/code')
    response = requests.post(code_url, data=data)
    response.raise_for_status()

    code_response = response.json()
    uri = code_response['verification_uri_complete']
    user_code = code_response['user_code']
    if has_browser:
        click.echo('Please confirm the following code appears in your browser: ', nl=False)
        click.secho(user_code, fg='green')
        if click.confirm('Lager would like to open a browser window to confirm your login info'):
            webbrowser.open_new(uri)
        else:
            click.echo('Cancelled')
    else:
        click.echo('Please visit ', nl=False)
        click.secho(uri, fg='green', nl=False)
        click.echo(' in your browser')
        click.echo('And confirm your device token: ', nl=False)
        click.secho(user_code, fg='green')

    click.echo('Awaiting confirmation... (Could take up to 5 seconds after clicking "Confirm" in your browser)')
    payload = poll_for_token(code_response['device_code'], code_response['interval'])

    config = read_config_file()
    config['AUTH'] = {
        'token': payload['access_token'],
        'type': payload['token_type'],
        'refresh': payload['refresh_token'],
    }
    write_config_file(config)

    ctx = LagerContext(
        ctx=ctx,
        auth=config['AUTH'],
        defaults=None,
        debug=False,
        style=None
    )

    session = ctx.session
    url = 'cli/post-login'
    session.post(url)

    click.secho('Success! You\'re ready to use Lager!', fg='green')

@click.command()
def logout():
    """
        Log out
    """
    try:
        config = read_config_file()
    except FileNotFoundError:
        return

    if 'AUTH' in config:
        del config['AUTH']

    write_config_file(config)
