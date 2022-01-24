import os


def is_running_in_pytest() -> bool:
    return 'PYTEST_CURRENT_TEST' in os.environ
