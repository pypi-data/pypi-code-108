import click

from tktl.commands import login as login_commands


@click.command("login", help="Log in & store api key")
@click.argument("api_key", required=True)
def login(api_key: str):
    command = login_commands.LogInCommand()
    command.execute(api_key=api_key)


@click.command("logout", help="Log out & remove apiKey from config file")
def logout():
    command = login_commands.LogOutCommand()
    command.execute()
