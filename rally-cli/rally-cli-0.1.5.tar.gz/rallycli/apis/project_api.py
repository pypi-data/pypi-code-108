import os
import sys
from logging import getLogger
from typing import List

import urllib3
from treelib import Tree, Node

from rallycli.models import type_names, User
from rallycli.models.models import Project

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rallycli.base_api import BaseAPI

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class ProjectAPI(BaseAPI):
    """API Class for accessin Project domain"""

    def get_project_by_ref(self, project_ref: str) -> Project:
        return self.get_element_by_ref(project_ref, model_class=Project)

    def get_project_by_name(self, project_name: str, parent_name: str = None) -> Project:
        if parent_name:
            query = f"( ( Name = \"{project_name}\" ) AND (Parent.Name = \"{parent_name}\") )"
            params = dict(**self._baseparams, query=query)
        else:
            params = dict(**self._baseparams, query=f"( Name = \"{project_name}\" )")
        result: List[Project] = self._simple_query(params=params,
                                                   rally_type=type_names.PROJECT,
                                                   keys=[],
                                                   model_class=Project)
        if len(result) > 1:
            logger.warning("get_project_by_name returned more than 1 result, returning first one ...")
        return result[0]

    def get_project_tree(self, root_project_ref: str = None, workspace_ref: str = None) -> Tree:
        params = dict(**self._baseparams, query="")
        if workspace_ref:
            params.update(workspace=workspace_ref)
        projects: List[Project] = self.get_elements_multithread(params=params,
                                                                rally_type=type_names.PROJECT,
                                                                model_class=Project)
        return ProjectAPI._build_project_tree(root_project_ref, projects)

    def get_project_members(self, project_ref: str) -> List[User]:
        team_member_ref = f"{project_ref}/TeamMembers"
        return self.get_elements_by_ref(team_member_ref,model_class=User)

    @staticmethod
    def _build_project_tree(project_ref: str, projects: List[Project]) -> Tree:
        tree: Tree = Tree(identifier="Project Tree")
        tree.create_node(tag="root", identifier="0", parent=None)
        ProjectAPI._add_projects_to_tree(tree, projects)
        project_subtree = tree.subtree(project_ref) if project_ref else tree
        logger.debug(f"Tree size: {tree.size()},tree depth: {tree.depth()}")
        return project_subtree

    @staticmethod
    def _add_projects_to_tree(tree: Tree, project_lst: List[Project]):
        ## Add all project still with no parents: Flat tree
        for project in project_lst:
            tag = f"{project.Name}"
            node: Node = Node(tag=tag, identifier=project._ref, data={"active": True, "project": project})
            tree.add_node(node, parent="0")

        ## set project parent relationship  and create tree structure
        for node_id in [project._ref for project in project_lst]:
            node = tree.get_node(node_id)
            if not node.data["project"].Parent:
                continue
            tree.move_node(node_id, node.data["project"].Parent._ref)
