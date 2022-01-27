import os


def get_env_value(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise KeyError(f"Expected to find an environment variable named '{name}', but didn't")
    return value


def get_github_token() -> str:
    return get_env_value("GITHUB_TOKEN")


def get_repo_name_auto() -> str:
    return get_env_value("GITHUB_REPOSITORY_TOKEN")
