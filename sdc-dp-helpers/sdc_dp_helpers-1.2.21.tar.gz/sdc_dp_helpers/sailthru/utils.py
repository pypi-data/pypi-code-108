"""
    Utils functions
"""
import yaml


def init_config(file_name: str = './example.yaml'):
    """
        Util method that creates an example config at the given file_name.
        :file_name: Full path to config YAML file.
    """
    config = {
        "blast": {
            "status": "sent",
            "start_date": "yesterday",
            "end_date": "yesterday"
        },
        "list": {
            "start_date": "yesterday",
            "end_date": "yesterday"
        },
        "send": {
            "start_date": "yesterday",
            "end_date": "yesterday"
        }
    }

    # write to file
    with open(file_name, 'w') as file_:
        yaml.dump(config, file_)
