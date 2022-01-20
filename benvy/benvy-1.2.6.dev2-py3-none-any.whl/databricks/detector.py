import os


def is_databricks():
    return os.getenv("DATABRICKS_RUNTIME_VERSION") is not None


def is_databricks_repo():
    cwd = os.getcwd()
    return is_databricks() and (cwd.startswith("/Workspace/Repos") or cwd.startswith("/local_disk0/.wsfs/Repos"))
