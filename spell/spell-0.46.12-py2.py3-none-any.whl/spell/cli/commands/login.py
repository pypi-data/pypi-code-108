import click
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import re
import webbrowser
import warnings

from spell import deployment_constants
from spell.api.base_client import SpellDecoder
from spell.api.exceptions import UnauthorizedRequest
from spell.configs.config_handler import ConfigException
from spell.cli.commands.logout import logout
from spell.cli.commands.keys import cli_ssh_key_path, get_remote_key, generate
from spell.cli.log import logger
from spell.cli.exceptions import ExitException, api_client_exception_handler
from spell.cli.utils import try_add_known_host


@click.command(name="login")
@click.pass_context
@click.option(
    "--identity",
    "identity",
    help="Spell username or email address",
)
@click.password_option(
    help="Spell password",
    prompt=False,
)
def login(ctx, identity, password):
    """
    Login to your Spell account.

    By default, authentication is handled by the Spell web console in your web browser.

    If your web browser settings prevent this flow, or you wish to log in on a remote
    machine without web browser access, you may use the authentication token login flow
    instead. For more information refer to the Spell documentation:
    /docs/access_tokens/#advanced-logging-in-using-an-access-token.

    Alternatively, if your account uses Spell authentication, you may log in using the
    identity (email or user) and password flags instead.

    If you don't have an account with Spell, please create one at https://spell.ml.
    """
    config_handler = ctx.obj["config_handler"]
    config = config_handler.config

    # Log out of existing session, if any.
    if config:
        try:
            ctx.invoke(logout, quiet=True)
        except Exception as e:
            logger.warning("Log out failed for previous session: %s", e)

    if config_handler.config is None:
        config_handler.load_default_config(type="global")

    config = config_handler.config
    client = ctx.obj["client"]

    # If the access token environment variable is set, maybe use it to log in.
    # NOTE(aleksey): this enables login for users with SSO accounts (Sign In With Google) in
    # environments that do not support the web browser flow.
    if "SPELL_TOKEN" in os.environ:
        if click.confirm("The SPELL_TOKEN environment variable is set, log in using this access token?"):
            # NOTE(aleksey): we prompt for the user email because it's an indexed field in the DB,
            # this avoids a table scan in the DB query
            email = click.prompt("Email")
            user, token, spell_admin_token = login_via_access_token(client, email, os.environ["SPELL_TOKEN"])

    # If an identity and/or password is passed, login using password (legacy).
    elif identity or password:
        warnings.warn(
            "Log in via identity/password is deprecated and will be removed in a future version the Spell client."
            "Consider logging in using the web browser instead."
        )
        if not identity:
            identity = click.prompt("Username")
        if not password:
            password = click.prompt("Password", hide_input=True)
        user, token, spell_admin_token = login_via_password(client, identity, password)

    # Otherwise, login using the web browser.
    else:
        user, token, spell_admin_token = login_via_web(ctx.obj["web_url"])

    logger.info("Sucessfully logged in.")
    client.token = token
    config.token = token
    config.spell_admin_token = spell_admin_token
    config.user_name = user.user_name
    config.email = user.email

    # If an owner is not configured, default to the organization (if any)
    if not config.owner:
        if not user.memberships:
            if deployment_constants.on_prem:
                raise ExitException(
                    "You are not part of any organization, "
                    "please contact your system administrator to continue using Spell"
                )
            else:
                config.owner = config.user_name
        else:
            # in onprem, always fetch the first membership.
            # otherwise if there is only one org, use that, otherwise fall back on community (see main.py)
            if deployment_constants.on_prem or len(user.memberships) == 1:
                config.owner = user.memberships[0].organization.name
            else:
                config.owner = config.user_name
    try:
        config_handler.write()
    except ConfigException as e:
        raise ExitException(e.message)

    # Generate CLI key for user if one does not exist, or if the existing one
    # is not registered with the user's Spell account
    local_key = cli_ssh_key_path(ctx.obj["config_handler"])
    matching_remote_key = os.path.isfile(local_key) and get_remote_key(ctx, local_key)
    if not matching_remote_key:
        ctx.invoke(generate, force=True)

    # Attempt to add git.spell.ml to known_hosts, ignore failures
    try_add_known_host(ctx)

    click.echo("Hello, {}!".format(user_addressing_noun(user)))


def login_via_password(client, identity, password):
    with api_client_exception_handler():
        try:
            if is_email(identity):
                return client.login_with_email(identity, password)
            else:
                return client.login_with_username(identity, password)
        except UnauthorizedRequest as exception:
            raise ExitException(str(exception))


def login_via_web(web_root_url):
    user = None
    token = None
    spell_admin_token = None

    class NewSessionRequestHandler(BaseHTTPRequestHandler):
        def do_POST(self):
            nonlocal user, token, spell_admin_token

            length = int(self.headers["Content-Length"])
            payload = json.loads(self.rfile.read(length), cls=SpellDecoder)
            user = payload["user"]
            token = payload["token"]
            spell_admin_token = payload.get("spell_admin_token", None)

            self.send_response(204)
            self.end_headers()

        def log_message(self, *args):
            pass  # Do not log HTTP traffic.

    httpd = HTTPServer(("localhost", 0), NewSessionRequestHandler)
    port = httpd.server_address[1]
    web_auth_url = "{}/local/login?port={}".format(web_root_url, port)
    webbrowser.open(web_auth_url)
    click.echo("Waiting for authentication from the Spell web console…")
    click.echo("Login URL: {}".format(web_auth_url))
    httpd.handle_request()

    return user, token, spell_admin_token


def login_via_access_token(client, email, token):
    with api_client_exception_handler():
        try:
            return client.login_with_access_token(email, token)
        except UnauthorizedRequest as exception:
            raise ExitException(str(exception))


def is_email(input):
    return re.match(".+@.+[.].+", input) is not None


def user_addressing_noun(user):
    nouns = [user.full_name, user.user_name, user.email]
    return next((s for s in nouns if s), "")
