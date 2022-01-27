"""
The ScratchLink Code
"""
from scratchlink.FrontPage import FrontPage
from scratchlink.User import User
from scratchlink.Studio import Studio
from scratchlink.Project import Project
from scratchlink.Forum import Forum


class ScratchLink:
    def __init__(self):
        pass

    def link_frontpage(self):
        return FrontPage()

    def link_user(self, username):
        return User(user=username)

    def link_studio(self, studio_id):
        return Studio(id=studio_id)

    def link_project(self, project_id):
        return Project(id=project_id)

    def link_forum(self, topic_id):
        return Forum(id=topic_id)
