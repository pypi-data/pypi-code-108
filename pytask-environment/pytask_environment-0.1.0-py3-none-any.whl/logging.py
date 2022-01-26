import sys

from _pytask.config import hookimpl
from _pytask.console import console
from pony import orm
from pytask_environment.database import Environment


_ERROR_MSG = """\
Aborted execution due to a bad state of the environment. Either switch to the correct \
environment or update the information on the environment using the --update-environment\
 flag.
"""


@hookimpl(trylast=True)
def pytask_log_session_header(session) -> None:
    """Check environment and python version.

    The solution is hacky. Exploit the first entry-point in the build process after the
    database is created.

    Check if the version and path of the Python interpreter have changed and if so, ask
    the user whether she wants to proceed.

    """
    __tracebackhide__ = True

    # If no checks are requested, skip.
    if (
        not session.config["check_python_version"]
        and not session.config["check_environment"]
    ):
        return None

    package = retrieve_package("python")

    same_version = False if package is None else sys.version == package.version
    same_path = False if package is None else sys.executable == package.path

    # Bail out if everything is fine.
    if same_version and same_path:
        return None

    msg = ""
    if not same_version and session.config["check_python_version"]:
        msg += "The Python version has changed "
        if package is not None:
            msg += f"from\n\n{package.version}\n\n"
        msg += f"to\n\n{sys.version}\n\n"
    if not same_path and session.config["check_environment"]:
        msg += "The path to the Python interpreter has changed "
        if package is not None:
            msg += f"from\n\n{package.path}\n\n"
        msg += f"to\n\n{sys.executable}."

    if msg:
        msg = "Your Python environment has changed. " + msg

    if session.config["update_environment"] or package is None:
        console.print("Updating the information in the database.")
        create_or_update_state("python", sys.version, sys.executable)
    elif not msg:
        pass
    else:
        console.print()
        raise Exception(msg + "\n\n" + _ERROR_MSG) from None


@orm.db_session
def retrieve_package(name):
    """Return booleans indicating whether the version or path of a package changed."""
    try:
        package = Environment[name]
    except orm.ObjectNotFound:
        package = None
    return package


@orm.db_session
def create_or_update_state(name, version, path):
    """Create or update a state."""
    try:
        package_in_db = Environment[name]
    except orm.ObjectNotFound:
        Environment(name=name, version=version, path=path)
    else:
        package_in_db.version = version
        package_in_db.path = path
