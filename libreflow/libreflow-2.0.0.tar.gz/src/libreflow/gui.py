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
from .resources.icons import libreflow
from .resources import file_templates

CUSTOM_HOME = True
if CUSTOM_HOME:
    from kabaret.app.actors.flow import Flow
    from .custom_home import MyHomeRoot

DEBUG = False
SCRIPT_VIEW = True
try:
    from kabaret.script_view import script_view
except ImportError:
    SCRIPT_VIEW = False

GrayStyle()


class MyStudioGUISession(gui.KabaretStandaloneGUISession):
    def register_view_types(self):
        super(MyStudioGUISession, self).register_view_types()

        # type_name = self.register_view_type(SessionToolBar)
        # self.add_view(type_name)
        if SCRIPT_VIEW:
            type_name = self.register_view_type(script_view.ScriptView)
            self.add_view(
                type_name, hidden=not DEBUG, area=QtCore.Qt.RightDockWidgetArea
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
        subprocess_manager = SubprocessManager(self)


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
    values, _ = parser.parse_known_args(args)

    if values.site:
        os.environ["KABARET_SITE_NAME"] = values.site
    if values.user:
        os.environ["USER_NAME"] = values.user


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
