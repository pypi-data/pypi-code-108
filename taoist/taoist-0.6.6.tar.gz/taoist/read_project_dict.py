""""read_project_dict.py"""

from typing import Tuple
from taoist.read_config import read_config
from todoist_api_python.api_async import TodoistAPIAsync


async def read_project_dict() -> Tuple:
    """
    Read project list into dictionary
    """

    # Read taoist user configuration
    config = read_config()

    # Initialize Todoist API
    api = TodoistAPIAsync(config['Default']['token'])

    # Initialize project dictionary
    project_dict = {}

    # Read projects into memory
    try:
        projects = await api.get_projects()
    except Exception as error:
        raise error
    
    # Construct project dictionary
    for project in projects:
        project_dict[project.id] = project

    return api, project_dict
