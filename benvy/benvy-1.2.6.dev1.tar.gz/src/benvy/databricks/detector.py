import os


def is_databricks():
    return os.getenv("DATABRICKS_RUNTIME_VERSION") is not None


def is_databricks_repo():
    return is_databricks() and os.getcwd().startswith("/Workspace/Repos")
