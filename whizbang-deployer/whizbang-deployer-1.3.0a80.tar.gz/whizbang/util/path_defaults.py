from whizbang.config.app_config import AppConfig


def get_solution_directory(app_config: AppConfig, solution_name: str) -> str:
    return f'{app_config.solutions_rel_path}'


def get_bicep_template_path(app_config: AppConfig, solution_name: str) -> str:
    return f'{app_config.solutions_rel_path}/{solution_name}.bicep'


def get_bicep_parameters_path(app_config: AppConfig, solution_name) -> str:
    return f'{app_config.solutions_rel_path}/{solution_name}_parameters.json'


def get_databricks_state_path(app_config: AppConfig, solution_name) -> str:
    return f'{app_config.solutions_rel_path}/Databricks'


def get_datalake_state_path(app_config: AppConfig, solution_name) -> str:
    return f'{app_config.solutions_rel_path}/Datalake'


def get_output_path(app_config: AppConfig) -> str:
    return f'{app_config.solutions_rel_path}/outputs'
