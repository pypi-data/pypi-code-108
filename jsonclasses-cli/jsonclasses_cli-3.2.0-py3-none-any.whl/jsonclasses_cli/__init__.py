from os import getcwd
from pathlib import Path
from click import group, argument, option, echo
from .new import new as execute_new
from .upgrade import upgrade as execute_upgrade
from .package import package as execute_package
from .console import console as execute_console
from .version import version


def print_version(ctx, param, value):
    if not value or ctx.resilient_parsing:
        return
    echo(f'JSONClasses CLI {version}')
    ctx.exit()


@group()
@option('-v', '--version', is_flag=True, callback=print_version, expose_value=False, is_eager=True, help='Show version and exit.')
def app():
    pass


@app.command(help='Upgrade this CLI to the newest version.')
def upgrade():
    execute_upgrade()


@app.command(help='Create a new project.')
@argument('name')
@option('-i', '--interactive/--no-interactive', ' /-I', default=True, help='Whether run interactively.')
@option('-u', '--include-user', is_flag=True, required=False, default=None, help='Whether include user.')
@option('-a', '--include-admin', is_flag=True, required=False, default=None, help='Whether include admin.')
@option('-g', '--git-init/--no-git-init', ' /-G', is_flag=True, required=False, default=None, help='Whether create a git repo.')
@option('-m', '--venv/--no-venv', ' /-M', is_flag=True, required=False, default=None, help='Whether create a venv.')
def new(name: str,
        interactive: bool | None,
        include_user: bool | None,
        include_admin: bool | None,
        git_init: bool | None,
        venv: bool | None):
    execute_new(Path(getcwd()) / name,
                interactive=interactive,
                include_user=include_user,
                include_admin=include_admin,
                git_init=git_init,
                venv=venv)


@app.command(help='Launch an interactive console.')
@argument('file', default='app.py')
def console(file: str | None):
    dest = Path(getcwd())
    app_file = dest / file
    execute_console(dest, app_file)


@app.command(help='Generate a client package.')
@argument('lang')
@argument('file', default='app.py')
def package(lang: str, file: str | None):
    dest = Path(getcwd())
    app_file = dest / file
    execute_package(dest, app_file, lang)


if __name__ == '__main__':
    app()
