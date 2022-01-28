import sys
import os
import argparse

os.environ["QT_MAC_WANTS_LAYER"] = '1'

from kabaret.app.ui import gui
from kabaret.app.ui.gui.styles import Style
from kabaret.app.ui.gui.styles.gray import GrayStyle
from qtpy import QtWidgets, QtGui, QtCore
from kabaret.subprocess_manager import SubprocessManager

from .session import BaseGUISession, DebugGUISession
from libreflow.resources.icons import libreflow, status
from libreflow.resources import file_templates
import libreflow.utils.kabaret as kutils

from .thesiren_resources import file_templates


# The siren own style
from .thesiren_resources.gui.styles.siren_style import SirenStyle
SirenStyle()

# New Custom Home just for the Siren
CUSTOM_HOME = True
if CUSTOM_HOME:
    from kabaret.app.actors.flow import Flow
    from .thesiren_custom_home import MyHomeRoot
DEBUG = False
SCRIPT_VIEW = True
JOBS_VIEW = True

try:
    from kabaret.script_view import script_view
except ImportError:
    SCRIPT_VIEW = False

try:
    from libreflow.utils.kabaret.jobs.jobs_view import JobsView
    from libreflow.utils.kabaret.jobs.jobs_actor import Jobs
except ImportError:
    print("ERROR: kabaret.jobs not found")
    JOBS_VIEW = False


class MyStudioGUISession(gui.KabaretStandaloneGUISession):
    def register_view_types(self):
        super(MyStudioGUISession, self).register_view_types()

        if SCRIPT_VIEW:
            type_name = self.register_view_type(script_view.ScriptView)
            self.add_view(
                type_name, hidden=not DEBUG, area=QtCore.Qt.RightDockWidgetArea
            )
            type_name = self.register_view_type(kutils.subprocess_manager.SubprocessView)
            self.add_view(
                type_name,
                view_id='Processes',
                hidden=not DEBUG,
                area=QtCore.Qt.RightDockWidgetArea,
            )

        if JOBS_VIEW:
            type_name = self.register_view_type(JobsView)
            self.add_view(
                type_name,
                hidden=not DEBUG,
                area=QtCore.Qt.RightDockWidgetArea,
            )

    def _create_actors(self):
        """
        Instanciate the session actors.
        Subclasses can override this to install customs actors or
        replace default ones.
        """
        if CUSTOM_HOME:
            Flow(self, CustomHomeRootType=MyHomeRoot)
        else:
            return super(MyStudioGUISession, self)._create_actors()
        subprocess_manager = kutils.subprocess_manager.SubprocessManager(self)

        jobs = Jobs(self)


def process_remaining_args(args):
    parser = argparse.ArgumentParser(
        description='Libreflow Session Arguments'
    )
    parser.add_argument(
        '-u', '--user', dest='user'
    )
    parser.add_argument(
        '-s', '--site', default='LFS', dest='site'
    )
    parser.add_argument(
        '-j', '--jobs_default_filter', dest='jobs_default_filter'
    )
    values, _ = parser.parse_known_args(args)

    if values.site:
        os.environ["KABARET_SITE_NAME"] = values.site
    if values.user:
        os.environ["USER_NAME"] = values.user
    if values.jobs_default_filter:
        os.environ["JOBS_DEFAULT_FILTER"] = values.jobs_default_filter
    else:
        os.environ["JOBS_DEFAULT_FILTER"] = values.site


def main(argv):
    (
        session_name,
        host,
        port,
        cluster_name,
        db,
        password,
        debug,
        remaining_args,
    ) = MyStudioGUISession.parse_command_line_args(argv)

    session = MyStudioGUISession(session_name=session_name, debug=debug)
    session.cmds.Cluster.connect(host, port, cluster_name, db, password)

    process_remaining_args(remaining_args)

    session.start()
    session.close()


if __name__ == "__main__":
    main(sys.argv[1:])