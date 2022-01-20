import click
from cnvrgv2.cnvrg import UsersClient
from cnvrgv2.cli.utils import messages
from cnvrgv2.errors import CnvrgHttpError, CnvrgFileError
from cnvrgv2.config import Config


@click.command()
@click.option('-d', '--domain', default=None, help=messages.LOGIN_PROMPT_DOMAIN)
@click.option('-e', '--email', default=None, help=messages.LOGIN_PROMPT_EMAIL)
@click.option('-p', '--password', default=None, help=messages.LOGIN_PROMPT_PASSWORD, hide_input=True)
@click.option('-o', '--organization', default=None, help=messages.LOGIN_ORGANIZATION_HELP)
@click.option('-t', '--auth-token', is_flag=True, default=False, help=messages.LOGIN_HELP_AUTH_TOKEN)
def login(domain, email, password, organization, auth_token):

    config = Config()
    config_domain = None
    user_token = None
    if password is None:
        password = ""

    if domain is None:
        config_domain = config.domain
        domain = config_domain or click.prompt(messages.LOGIN_PROMPT_DOMAIN, type=str)

    # The guideline in this block is to receive both email and pass together from the user or config file.
    if email is None:
        config_email = config.user
        config_token = config.token

        if config_email and config_token and config_domain:
            click.echo(messages.LOGIN_ALREADY_LOGGED_IN)
            return
        else:
            email = click.prompt(messages.LOGIN_PROMPT_EMAIL, type=str)
            if auth_token:
                user_token = click.prompt(messages.LOGIN_PROMPT_AUTH_TOKEN, type=str, hide_input=True)
            else:
                password = click.prompt(messages.LOGIN_PROMPT_PASSWORD, type=str, hide_input=True)
    else:
        if auth_token:
            user_token = click.prompt(messages.LOGIN_PROMPT_AUTH_TOKEN, type=str, hide_input=True)
        else:
            password = password or click.prompt(messages.LOGIN_PROMPT_PASSWORD, type=str, hide_input=True)

    try:
        uc = UsersClient(domain=domain, token=user_token)
        token, default_organization = uc.login(user=email, password=password)

        config.domain = domain
        config.organization = organization or default_organization
        config.user = email
        if user_token is not None:
            config.token = user_token
        else:
            config.token = token
        config.check_certificate = False
        config.save()

        click.echo(messages.LOGIN_SUCCESS.format(email))

    except CnvrgHttpError:
        click.echo(messages.LOGIN_INVALID_CREDENTIALS, err=True)


@click.command()
def logout():
    try:
        config = Config()
        config.remove_config_fields("user", "token")
        click.echo(messages.LOGOUT_SUCCESS)

    except CnvrgFileError:
        click.echo(messages.LOGOUT_CONFIG_MISSING, err=True)
