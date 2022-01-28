from __future__ import print_function

import six

from kabaret import flow

# from .utils import import_object

from kabaret.app.actors.flow.generic_home_flow import AbstractHomeRoot
from kabaret.app.actors.flow.utils import import_object

"""

    This flow defines a generic "Home" page for Flow Actor.

"""


class ProjectNameChoiceValue(flow.values.ChoiceValue):
    def choices(self):
        projects_info = self.root().flow_actor.get_projects_info()
        return [n for n, i in projects_info]


class GetProjectTypeFromProjectAction(flow.Action):

    _ptv = flow.Parent()

    project = flow.Param("", ProjectNameChoiceValue)

    def needs_dialog(self):
        return True

    def get_buttons(self):
        return ["Get Project Type"]

    def run(self, button):
        projects_info = dict(self.root().flow_actor.get_projects_info())
        project_info = projects_info.get(self.project.get())
        if not project_info:
            self.message.set("Unknow Project %r" % (self.project.get()))
            return self.get_result(close=False)
        project_type = project_type["type"]
        self._ptv.set(project_type)


class ProjectTypeValue(flow.values.Value):

    from_project = flow.Child(GetProjectTypeFromProjectAction)


class CreateProjectAction(flow.Action):

    ICON = ("icons.gui", "plus-sign-in-a-black-circle")

    _projects = flow.Parent()
    project_name = flow.Param("MyProject")
    project_type = flow.Param(
        "dev_studio.flow.demo_project.DemoProject",
        # ProjectTypeValue
        # NB: we can't use this value bc of a bug in action dialog management
        # that prevents me from having an action dialog inside an action
        # dialog. We'll activate this once the bug is fixed
        # (Also: remember to update the tutorials text & screenshots !!!)
    )

    def get_buttons(self):
        return ["Test Type", "Create Project"]

    def run(self, button):
        flow_actor = self.root().flow_actor

        if button == "Test Type":
            try:
                TYPE = import_object(self.project_type.get())
            except Exception as err:
                self.message.set("<font color=red>Error:</font><br>%s" % (err,))
            else:
                self.message.set("Project Type looks good:\n%s" % (TYPE,))
            return self.get_result(close=False)

        else:
            flow_actor.create_project(self.project_name.get(), self.project_type.get())
            self._projects.touch()
            return self.get_result()


class ProjectStatusChoiceValue(flow.values.ChoiceValue):

    CHOICES = ("NYS", "WIP", "DONE", "Archived")


class SetProjectStatusAction(flow.Action):

    ICON = "input"

    _home = flow.Parent()

    # project_name = flow.Param('')
    project = flow.Param("", ProjectNameChoiceValue)
    status = flow.Param("WIP", ProjectStatusChoiceValue)

    def get_buttons(self):
        return ["Set Status"]

    def run(self, button):
        actor = self.root().flow_actor
        project_name = self.project.get().strip()
        if not project_name:
            self.message.set("Please select a project !")
            return self.get_result(close=False)

        actor.set_project_status(project_name, self.status.get())
        self._home.touch()


class ToggleArchivedProjectsAction(flow.Action):

    _home = flow.Parent()

    def needs_dialog(self):
        return False

    def get_buttons(self):
        return []

    def run(self, button):
        self._home.do_toggle_archived_projects()


class ToggleProjectsTypeAction(flow.Action):

    _home = flow.Parent()

    def needs_dialog(self):
        return False

    def get_buttons(self):
        return []

    def run(self, button):
        self._home.do_toggle_projects_type()


class ProjectsMap(flow.Map):

    ICON = "asset_family"

    toggle_archived_projects = flow.Child(ToggleArchivedProjectsAction)
    toggle_project_type = flow.Child(ToggleProjectsTypeAction)

    create_project = flow.Child(CreateProjectAction).ui(group="Admin")
    set_project_status = flow.Child(SetProjectStatusAction).ui(group="Admin")

    def __init__(self, *args, **kwargs):
        super(ProjectsMap, self).__init__(*args, **kwargs)
        self._show_archived = False
        self._show_project_type = False

    def do_toggle_archived_projects(self):
        self._show_archived = not self._show_archived
        self.touch()

    def do_toggle_projects_type(self):
        self._show_project_type = not self._show_project_type
        self.touch()

    def columns(self):
        cols = ["Name", "Status"]
        if self._show_project_type:
            cols.append("Type")
        return cols

    def rows(self):
        rows = []
        projects_info = self.root().flow_actor.get_projects_info()
        for name, infos in projects_info:
            type_name = infos["type"]
            status = infos["status"]
            if not self._show_archived and status == "Archived":
                continue
            style = dict(
                icon=("icons.gui", "team"),
                Status_icon=("icons.status", status),
            )
            rows.append(
                (
                    "/" + name,
                    dict(
                        Name=name,
                        Status=status,
                        Type=type_name,
                        _style=style,
                    ),
                )
            )
        return rows


class ClassicHome(flow.Object):
    """
    Access the classic home with right click on the oid on top of the page
    Usefull to add projects or change status
    """

    projects = flow.Child(ProjectsMap).ui(
        auto_fit=False, columns_width=(50, 20), expanded=True
    )


class Home(flow.Object):
    """
    This Home is completly overrided bu the custom_page
    designed in the custom_home.ui
    """

    ClassicHome = flow.Child(ClassicHome)

    def _fill_ui(self, ui):
        ui["custom_page"] = "libreflow.custom_home.ui.ProjectHomePageWidget"

    def get_projects(self):
        return self.root().flow_actor.get_projects_info()


class MyHomeRoot(AbstractHomeRoot):
    """"""

    Home = flow.Child(Home)

    def set_flow_actor(self, flow_actor):
        self.flow_actor = flow_actor
