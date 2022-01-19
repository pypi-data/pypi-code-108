import datetime

import pkg_resources


def get_version():
    try:
        return pkg_resources.get_distribution("tecton").version
    except pkg_resources.DistributionNotFound:
        return None


def get_status():
    try:
        from tecton._stamp import BUILD_STATUS

        return BUILD_STATUS
    except ImportError:
        return {}


def get_hash() -> str:
    status = get_status()
    return status.get("GIT_COMMIT", "n/a")


def summary():
    status = get_status()

    ts_seconds = status.get("BUILD_TIMESTAMP", None)
    ts = datetime.datetime.utcfromtimestamp(int(ts_seconds)).isoformat() if ts_seconds else "n/a"

    commit = status.get("GIT_COMMIT", "n/a")

    print(f"Version: {get_version() or 'n/a'}")
    print(f"Git Commit: {commit}")
    print(f"Build Datetime: {ts}")
