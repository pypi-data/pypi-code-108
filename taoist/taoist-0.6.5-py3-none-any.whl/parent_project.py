"""parent_project.py"""

from typing import Dict


def parent_project(project_id: int, project_dict: Dict) -> str:
    """
    Get parent branch for project
    """

    project_path = [project_dict[project_id].name]
    project_parent_id = project_dict[project_id].parent_id
 
    while project_parent_id:
        project_parent = project_dict[project_parent_id]
        project_path = [project_parent.name] + project_path
        project_parent_id = project_parent.parent_id
 
    project_path_string = '/'.join(project_path)
    
    return project_path_string
