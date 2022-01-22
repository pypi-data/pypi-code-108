from mlsteam import envs


class MLSteamException(Exception):
    def __hash__(self):
        return hash((super().__hash__(), str(self)))


class MLSteamMissingApiTokenException(MLSteamException):
    def __init__(self):
        message = "API token {env_api_token} is missing"
        super().__init__(
            message.format(env_api_token=envs.API_TOKEN_ENV)
        )


class MLSteamInvalidApiTokenException(MLSteamException):
    def __init__(self):
        message = "API token is invalid, make sure your API token is correct."
        super().__init__(message)


# Project
class MLSteamMissingProjectNameException(MLSteamException):
    def __init__(self):
        message = "Project name {env_project_name} is missing"
        super().__init__(
            message.format(env_project_name=envs.PROJECT_ENV)
        )


class MLSteamInvalidProjectNameException(MLSteamException):
    def __init__(self):
        message = "Project name {env_project_name} is invalid"
        super().__init__(
            message.format(env_project_name=envs.PROJECT_ENV)
        )
