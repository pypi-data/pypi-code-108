import shutil


def resolve_pylint():
    pylint_executable = shutil.which("pylint")

    if pylint_executable is None:
        raise Exception("pylint executable cannot be resolved, check if pylint is installed")

    return pylint_executable
