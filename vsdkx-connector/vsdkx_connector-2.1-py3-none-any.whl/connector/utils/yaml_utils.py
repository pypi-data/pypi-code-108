import yaml


def import_config_file(path):
    """
    Imports the contents of an entire yaml file into a dictionary
    for future use

    Args:
        path (string): path to a yaml file

    Returns:
        (dict): dictionary of yaml key-value pairs
    """
    with open(path) as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)
    return config_data



def parse_yaml_string_to_dict(conf_str):
    """
    Receive config as yaml formatted string and parse it into dictionary

    Args:
        conf_str (str): yaml formatted string

    Returns:
        (dict): config dictionary to be passed to the EventDetector class
    """
    conf_dict = yaml.load(conf_str, Loader=yaml.Loader)
    return conf_dict
