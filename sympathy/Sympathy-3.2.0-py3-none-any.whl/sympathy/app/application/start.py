# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import sys
import traceback

from sympathy.utils import log

core_logger = log.get_logger('core')
app_logger = log.get_logger('app')


def create_gui_application(argv):
    import Qt.QtCore as QtCore
    import Qt.QtGui as QtGui
    import Qt.QtWidgets as QtWidgets
    from sympathy.platform import os_support as oss
    from sympathy.utils.prim import get_icon_path
    from .. import version

    oss.set_high_dpi_unaware()
    oss.set_application_id()
    oss.setup_qt_opengl()

    app = QtWidgets.QApplication(argv)
    app.setApplicationName(version.application_name())
    QtCore.QLocale.setDefault(QtCore.QLocale('C'))

    ico = get_icon_path('application.png')
    app.setWindowIcon(QtGui.QIcon(ico))
    app.setApplicationVersion(version.version)
    return app


def create_cli_application(argv):
    # Using QApplication instead of QCoreApplication on
    # Windows to avoid QPixmap errors.
    import Qt.QtWidgets as QtWidgets
    import Qt.QtCore as QtCore
    from .. import version

    if sys.platform == 'win32':
        app = QtWidgets.QApplication(argv)
    else:
        app = QtCore.QCoreApplication(argv)
    app.setApplicationName(version.application_name())
    app.setApplicationVersion(version.version)
    return app


def _start_gui_application(app, parsed_args, argv):
    import Qt.QtCore as QtCore
    from .. import version
    from .. windows import first_run, splash_screen
    from .. import settings
    from sympathy.platform import os_support

    os_support.set_application_name(version.application_name())

    teardown = [None]
    main_window = [None]
    show_splash_screen = settings.instance()['Gui/show_splash_screen']

    splash = splash_screen.Splash()
    if show_splash_screen:
        splash.show()
    splash.showMessage("Initializing...")

    def create_gui():
        try:
            splash.showMessage("Importing modules...")
            from . import application
            main_window[0], teardown[0] = application.create_gui(
                parsed_args, argv, splash)
            splash.finish(main_window[0])
            first_run.setup(main_window[0].closed)
            splash.close()
            application.create_start_flow(main_window[0], parsed_args)
            main_window[0].started()
        except Exception:
            splash.close()
            traceback.print_exc()
            app_logger.critical('Failed to create GUI.')
            app.exit(-1)

    # Avoid rendering issues of splash on Linux.  Also, it looks better if the
    # splash does not flicker too quickly in case startup is very fast.
    # Symptom on Linux seems similar to:
    # https://bugreports.qt.io/browse/QTBUG-35757.  Though that issues is
    # marked as done, might be the same underlying problem shining through.
    QtCore.QTimer.singleShot(100, create_gui)
    try:
        return app.exec_()
    except Exception:
        splash.close()
    finally:
        if teardown[0]:
            teardown[0]()


def start_gui_application(parsed_args, argv):
    app = create_gui_application(argv)
    from .. import user_statistics
    with user_statistics.active(app):
        user_statistics.user_started_sympathy('gui')
        res = _start_gui_application(app, parsed_args, argv)
        user_statistics.user_stopped_sympathy()
        return res


def start_cli_application(parsed_args, argv):
    # Ensure Q(Core)Application is live while the gui is executing.
    app = create_cli_application(argv)  # NOQA
    from .. import user_statistics
    with user_statistics.active(app):
        from . import application
        user_statistics.user_started_sympathy('cli')
        res = application.start_cli_application(app, parsed_args, argv)
        user_statistics.user_stopped_sympathy()
    return res
