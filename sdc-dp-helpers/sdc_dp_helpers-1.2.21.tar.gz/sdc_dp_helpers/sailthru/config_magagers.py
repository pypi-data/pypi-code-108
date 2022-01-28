import yaml


def get_config(configs):
    """
        Gathers query configurations.yml file data.
    """
    with open(configs, 'r') as file:
        return yaml.safe_load(file)
