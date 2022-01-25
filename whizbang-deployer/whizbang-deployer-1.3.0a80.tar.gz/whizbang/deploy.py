from whizbang.__main__ import execute


def deploy(solution_type, solution_directory, env_config_file_name: str = "env_config.json", client_config_file_name: str = None):

    json_extension = ".json"

    # if we didn't have a specified extension, add it
    if not env_config_file_name.endswith(json_extension):
        env_config_file_name += json_extension

    if client_config_file_name is not None and not client_config_file_name.endswith(json_extension):
        client_config_file_name += json_extension

    execute(solution_type, solution_directory, env_config_file_name, client_config_file_name)