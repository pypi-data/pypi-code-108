import typer

cli = typer.Typer()


@cli.command()
def migrate():
    """
    Run all SQLAlchemy migrations in the current environment
    """

    typer.echo("Running Migrations..")
    from alembic.config import Config
    import alembic.command

    config = Config('alembic.ini')
    config.attributes['configure_logger'] = False

    alembic.command.upgrade(config, 'head')


@cli.command()
def create_migration(
        message: str = typer.Option(..., prompt=True, help="A brief message describing what is included in this migration")
):
    """
    Create a new SQLAlchemy migration in the current environment
    """

    typer.echo("Creating migration..")
    from alembic.config import Config
    import alembic.command

    config = Config('alembic.ini')
    config.attributes['configure_logger'] = False

    alembic.command.revision(config, autogenerate=True, message=message)


if __name__ == '__main__':
    cli()
