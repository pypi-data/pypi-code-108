import click

from .migration import _command


@click.group("sql")
def main():
    """EZTea SQL commands"""


@main.command()
@click.argument("app", type=str)
def init(app):
    """
    Init alembic migration configs.

    Example: eztea sql init myapp
    """
    _command.init(app)


@main.command()
def auto_revision():
    """Auto generate migration version."""
    _command.auto_revision()


@main.command()
def generate_ddl():
    """Generate DDL SQL of migration versions."""
    _command.generate_ddl()


@main.command()
@click.argument("target", type=str, default="head")
def migrate(target):
    """
    Update database schema to target revision.

    TARGET: revision identifier, base or head, default is head.
    """
    _command.migrate(target)
