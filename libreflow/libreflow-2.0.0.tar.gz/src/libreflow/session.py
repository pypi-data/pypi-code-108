from qtpy import QtCore

from kabaret.app.ui import gui
from kabaret.app.session import KabaretSession
from kabaret.script_view import ScriptView
from kabaret.subprocess_manager import SubprocessManager, LauncherToolBar

from libreflow.utils.kabaret.jobs.jobs_node import JobsNodeSession

from .utils.kabaret.jobs.jobs_actor import Jobs


class BaseGUISession(gui.KabaretStandaloneGUISession):
    def register_view_types(self):
        super(BaseGUISession, self).register_view_types()

    def _create_actors(self):
        super(BaseGUISession, self)._create_actors()

        # Configure SubprocessManager
        subprocess_manager = SubprocessManager(self)


class DebugGUISession(BaseGUISession):
    def register_view_types(self):
        super(DebugGUISession, self).register_view_types()

        type_name = self.register_view_type(ScriptView)
        self.add_view(type_name, hidden=True, area=QtCore.Qt.RightDockWidgetArea)


class BaseCLISession(KabaretSession):
    def _create_actors(self):
        super(BaseCLISession, self)._create_actors()

        # Configure SubprocessManager
        SubprocessManager(self)
        Jobs(self)


class JobsNodeSession(JobsNodeSession):
    pass