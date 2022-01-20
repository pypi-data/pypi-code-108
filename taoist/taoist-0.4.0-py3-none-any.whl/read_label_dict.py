""""read_label_dict.py"""
from typing import Dict
from configparser import ConfigParser
from todoist_api_python.api import TodoistAPI

def read_label_dict(config: ConfigParser) -> Dict:

    """
    Read label list into dictionary
    """

    # Initialize Todoist API
    api = TodoistAPI(config['Default']['token'])

    # Initialize label dictionary
    label_dict = {}

   # Get labels
    try:
        labels = api.get_labels()
    except Exception as error:
        print(error)
    
    for label in labels:
        label_dict[label.id] = label
    
    return label_dict