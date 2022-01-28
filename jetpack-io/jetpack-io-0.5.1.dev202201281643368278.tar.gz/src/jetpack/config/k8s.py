import os


def is_in_cluster() -> bool:
    return bool(os.getenv("KUBERNETES_SERVICE_HOST"))
