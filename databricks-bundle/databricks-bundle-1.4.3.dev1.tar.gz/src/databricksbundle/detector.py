import os


def is_databricks():
    """
    Check, if scripts are running on databricks cluster or locally.

    DATABRICKS_RUNTIME_VERSION available for all version and only on databricks cluster
    :return: true, if running on databricks
    """
    return os.getenv("DATABRICKS_RUNTIME_VERSION") is not None


def is_databricks_repo():
    cwd = os.getcwd()
    return is_databricks() and (cwd.startswith("/Workspace/Repos") or cwd.startswith("/local_disk0/.wsfs/Repos"))
