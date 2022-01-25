"""Console script for aop2db."""
import logging
import sys

import click
from sqlalchemy_utils import create_database, database_exists

from aop2db.aop.importer import import_aop_data
from aop2db.utils import set_conn

logger = logging.getLogger(__name__)


@click.group(
    help=f"AOP2DB Database Framework Command Line Utilities on {sys.executable}"
)
@click.version_option()
def main():
    """Console script for aop2db."""
    pass


@main.command()
def load():
    """Download the AO wiki data and imports into the relational database."""
    import_aop_data()


@main.command()
@click.argument("conn_str")
@click.option(
    "-c",
    "--create",
    is_flag=True,
    default=False,
    help="Create the database if it doesn't exist.",
)
def conn(conn_str: str, create: bool = True):
    """Set the SQL connection string in the configuration file.

    conn_str
        A python compatible SQL connection string. Drivers (e.g. pymysql) will need to be downloaded manually.
    """
    if create:
        if not database_exists(conn_str):
            create_database(conn_str)

    set_conn(conn_string=conn_str)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
