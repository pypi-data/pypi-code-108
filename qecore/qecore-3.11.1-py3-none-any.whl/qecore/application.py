#!/usr/bin/env python3
from time import sleep
import shlex
import configparser
from subprocess import Popen, PIPE
from dogtail.rawinput import typeText, pressKey, keyCombo
from qecore.utility import run
from qecore.logger import QELogger

log = QELogger()

class Application:
    def __init__(self, component, a11y_app_name=None, desktop_file_exists=True,
                 desktop_file_name="", desktop_file_path="", app_process_name="",
                 shell=None, session_type="", session_desktop=""):
        """
        .. note::

            Do **NOT** call this by yourself.
            This class is instanced by :py:meth:`sandbox.TestSandbox.get_application`.

        :type component: str
        :param component: Component name - usually the name of the application package.

        :type a11y_app_name: str
        :param a11y_app_name: Name of application as it appears in accessibility tree.

        :type desktop_file_exists: bool
        :param desktop_file_exists: States that desktop file of given application exists or not.

        :type desktop_file_path: str
        :param desktop_file_path: Full posix path to .desktop file of application.

        :type desktop_file_name: str
        :param desktop_file_name: Name of desktop file if not same as component.

        :type app_process_name: str
        :param app_process_name: Name of application process if not same as component.
        """

        log.info(" ".join((
                f"__init__(self, component={component}, a11y_app_name={a11y_app_name},",
                f"desktop_file_exists={desktop_file_exists},",
                f"desktop_file_name={desktop_file_name},",
                f"desktop_file_path={desktop_file_path},",
                f"app_process_name={app_process_name}, shell='shell',",
                f"session_type={session_type}, session_desktop={session_desktop})"
        )))

        self.shell = shell
        self.session_type = session_type
        self.session_desktop = session_desktop
        self.pid = None
        self.instance = None
        self.component = component
        self.a11y_app_name = a11y_app_name if a11y_app_name else component
        self.desktop_file_exists = desktop_file_exists
        self.exit_shortcut = "<Control_L><Q>"
        self.kill = True
        self.kill_command = None
        self.desktop_file_name = desktop_file_name
        self.desktop_file_path = desktop_file_path
        self.application_list = []
        self.app_process_name = app_process_name if app_process_name else component
        self.icon = None
        self.get_desktop_file_data()

        if 'Flatpak' not in f'{type(self)}':
            # Preserving old api names of functions.
            self.getDesktopFileData = self.get_desktop_file_data
            self.getRoot = self.get_root
            self.isRunning = self.is_running
            self.getPidList = self.get_pid_list
            self.getAllKillCandidates = self.get_all_kill_candidates


    def get_desktop_file_data(self):
        """
        Parse desktop file.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`__init__`.
        """

        log.info(f"{self.component} get_desktop_file_data(self)")

        # zenity/gnome-shell do not have desktop file.
        if self.desktop_file_exists:
            if self.desktop_file_path:
                log.info(f"get_desktop_file_data: loading user provided .desktop file: '{self.desktop_file_path}'")
                desktop_file = self.desktop_file_path
            else:
                desktop_run = run(" ".join((
                    f"rpm -qlf $(which {self.component}) |",
                    "grep /usr/share/applications/ |",
                    "grep .desktop |",
                    f"grep '{self.desktop_file_name}'"
                )), verbose=True)

                if desktop_run[1] != 0:
                    raise Exception(f"Desktop file of application '{self.component}' was not found.")

                desktop_file = desktop_run[0].strip("\n")
                log.info(f"get_desktop_file_data: .desktop file found: '{desktop_file}'")

            desktop_files_list = desktop_file.split("\n")
            if len(desktop_files_list) != 1:
                assert False, "\n".join((
                    f"More than one .desktop file found: \n{desktop_file}\n",
                    "Specify one when initializing your application in environment.py, options are:",
                    "1) Specify your <name>.desktop file name 'desktop_file_name=\"<name>\"'.",
                    "2) Provide full path to your .desktop file 'desktop_file_path=\"/path/to/desktop/file\"'.",
                    " ... = context.sandbox.get_application(..., desktop_file_name=\"\", desktop_file_path=\"\")\n"
                ))

            desktop_file_config = configparser.RawConfigParser()
            list_of_successfully_parsed_files = desktop_file_config.read(desktop_file)

            if list_of_successfully_parsed_files == []:
                assert False, "".join((
                    f"Failed attepmt to parse the .desktop file: '{desktop_file}'."
                ))

            self.name = desktop_file_config.get("Desktop Entry", "name")
            self.exec = desktop_file_config.get("Desktop Entry", "exec").split(" ")[0]
            self.icon = desktop_file_config.get("Desktop Entry", "icon", fallback=None)
            log.info(f"get_desktop_file_data: data name='{self.name}' exec='{self.exec}' icon='{self.icon}'")


    def start_via_command(self, command=None, **kwargs):
        """
        Start application via command.

        :type command: str
        :param command: Complete command that is to be used to start application.

        :type in_session: bool
        :param in_session: Start application via command in session.
        """

        kill_override = self.kill
        in_session = False

        for key, val in kwargs.items():
            if "session" in str(key).lower():
                in_session = val

            if "kill" in str(key).lower():
                kill_override = val

        log.info("".join((
                f"{self.component} ",
                f"start_via_command(self, command={command}, in_session={in_session})"
        )))

        if self.is_running() and kill_override:
            self.kill_application()

        command_to_use = command if command else self.exec

        if in_session:
            pressKey("Esc")
            keyCombo("<Alt><F2>")
            sleep(0.5)
            keyCombo("<Alt><F2>")
            sleep(0.5)
            enter_a_command = self.shell.findChild(lambda x: "activate" in x.actions and x.showing)
            enter_a_command.text = command_to_use
            sleep(0.5)
            pressKey("Enter")
        else:
            self.process = Popen(shlex.split(command_to_use),
                                 stdout=PIPE,
                                 stderr=PIPE,
                                 encoding="utf-8")

            process_is_running = self.process.poll() is None
            if not process_is_running:
                stdout_data, stderr_data = self.process.communicate()

                stdout_data = stdout_data.strip("\n")
                stderr_data = stderr_data.strip("\n")

                error_message = "\n".join((
                    f"The command used to start the application '{command_to_use}' failed.",
                    f"The 'stdout_data' of executed command are: '{stdout_data}'.",
                    f"The 'stderr_data' of executed command are: '{stderr_data}'."
                ))
                raise RuntimeError(error_message)

        self.wait_before_app_starts(30)
        self.instance = self.get_root()


    def start_via_menu(self, kill=None):
        """
        Start application via menu.

        Starting the application by opening shell overview and typing the application
        name that is taken from the application's desktop file. This does no longer work
        in a new gnome-classic as it lost the search bar.
        """

        log.info(f"{self.component} start_via_menu(self)")

        if "classic" in self.session_desktop:
            assert False, "".join((
                f"Application cannot be started via menu in {self.session_desktop}."
            ))

        if not self.desktop_file_exists:
            raise Exception("".join((
                f"Testing target '{self.a11y_app_name}' does not have desktop file. ",
                "Indication of user failure!"
            )))

        kill_override = kill if kill else self.kill

        if self.is_running() and kill_override:
            self.kill_application()

        run(" ".join((
            "dbus-send",
            "--session",
            "--type=method_call",
            "--dest=org.gnome.Shell",
            "/org/gnome/Shell",
            "org.gnome.Shell.FocusSearch"
        )))

        sleep(1)
        typeText(self.name)
        pressKey("Enter")

        self.wait_before_app_starts(30)
        self.instance = self.get_root()


    def close_via_shortcut(self):
        """
        Close application via shortcut.

        Closing application via shortcut Ctrl+Q.
        If for any reason the application does not have this shortcut you can define the shortcut
        to use in class attribute :py:attr:`exit_shortcut`

        .. note::

            Format of the shortcut is a string with each key character encapsuled in < >.
            Here are  a few examples: <Ctrl><Q> <Alt><F4> <Ctrl><Shift><Q>
        """

        log.info(f"{self.component} close_via_shortcut(self)")

        if not self.is_running():
            raise Exception("".join((
                f"Application '{self.a11y_app_name}' is no longer running. ",
                "Indication of test failure!"
            )))

        keyCombo(self.exit_shortcut)

        self.wait_before_app_closes(30)
        self.instance = None


    def already_running(self):
        """
        If application is started by other means, other than methods from this class,
        this will retrieve the root of the application.
        """

        log.info(f"{self.component} already_running(self)")

        self.wait_before_app_starts(15)
        self.instance = self.get_root()


    def get_root(self):
        """
        Get accessibility root of appllication.

        :return: Return root object of application.
        :rtype: <dogtail.tree.root.application>

        This method is used upon application start to retrieve a11y object to use in the test.
        You do not need to use this by yourself, but can be useful in some situations.
        """

        log.info(f"{self.component} get_root(self) search by '{self.a11y_app_name}'")

        # Importing here for issue with accessibility if the connection is not ready yet.
        # This will make sure the import will happen after the session is loaded.
        from dogtail.tree import root
        return root.application(self.a11y_app_name)


    def is_running(self):
        """
        Get running state of application.
        This state is retrieved by checking if application is present in the accessibility tree.

        :return: Return state of application. Running or not.
        :rtype: bool

        This method is used by various other methods in this class to ensure correct behaviour.
        You do not need to use this by yourself, but can be useful in some situations.
        """

        log.info(f"{self.component} is_running(self)")

        is_running = False

        try:
            # Preventing issues of loading a11y on import before session is ready.
            from dogtail.tree import root

            self.application_list = [x.name for x in root.applications()]
            for _ in range(3):
                is_running = self.a11y_app_name in self.application_list
                if is_running:
                    break
            return is_running
        except Exception:
            return False


    def get_pid_list(self):
        """
        Get list of processes of running application.

        :return: Return all running processes of application, \
            seperated by new line character, not converting to list. \
            Return nothing if application is not running.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`get_all_kill_candidates`
            when stopping the application.
        """

        log.info(f"{self.component} get_pid_list(self)")

        if self.is_running():
            return run(f"pgrep -fla {self.app_process_name}").strip("\n")

        return None


    def get_all_kill_candidates(self):
        """
        Take result of :func:`get_pid_list` and return only processes of application.

        :rtype: list
        :return: Return all IDs of application processes.

        .. note::

            Do **NOT** call this by yourself. This method is called by :func:`kill_application`\
            when stopping the application.

        If kill candidate happens to have ['runtest', 'behave', 'dogtail', '/usr/bin/gnome-shell']
        in its process name. Process will not be killed.
        Return empty list if no satisfactory process was found.
        This prevents testname colliding with found process so we will not kill the test itself.
        """

        log.info(f"{self.component} get_all_kill_candidates(self)")

        application_pid_string = self.get_pid_list()
        if application_pid_string:
            application_pid_list = application_pid_string.split("\n")
        else:
            return []

        final_pid_list = []
        for process in application_pid_list:
            if not (("runtest" in process) or \
                    ("behave" in process) or \
                    ("dogtail" in process) or \
                    (process == "/usr/bin/gnome-shell")):
                extracted_pid = process.split(" ", 1)[0]
                try:
                    final_pid_list.append(int(extracted_pid))
                except ValueError:
                    # Skip non-digits.
                    pass

        return final_pid_list


    def kill_application(self):
        """
        Kill application.

        This method is used by :func:`start_via_command` and :func:`start_via_menu` to ensure
        the application is not running when starting the test. So we kill all application instances
        and open a new one to test on.
        You do not need to use this by yourself, but can be useful in some situations.
        """

        log.info(f"{self.component} kill(self)")

        if self.is_running() and self.kill:
            if not self.kill_command:
                for pid in self.get_all_kill_candidates():
                    run(f"sudo kill -9 {pid} > /dev/null")
            else:
                run(self.kill_command)


    # Following two could be merged, I could not think of a nice way of doing it though.
    def wait_before_app_starts(self, time_limit):
        """
        Wait before application starts.

        :type time_limit: int
        :param time_limit: Number which signifies time before the run is stopped.
        """

        log.info("".join((
                f"{self.component} ",
                f"wait_before_app_starts(self, time_limit={time_limit})"
        )))

        for _ in range(time_limit * 10):
            if not self.is_running():
                sleep(0.1)
            else:
                return

        assert False, "".join((
            f"Application '{self.a11y_app_name}' was not found in application tree: '{self.application_list}'."
        ))

    def wait_before_app_closes(self, time_limit):
        """
        Wait before application stops.

        :type time_limit: int
        :param time_limit: Number which signifies time before the run is stopped.
        """

        log.info("".join((
                f"{self.component} ",
                f"wait_before_app_closes(self, time_limit={time_limit}"
        )))

        for _ in range(time_limit * 10):
            if self.is_running():
                sleep(0.1)
            else:
                return

        assert False, "".join((
            f"Application '{self.a11y_app_name}' was still found in application tree: '{self.application_list}'."
        ))


    # Using properties to preserve old api of attributes.
    @property
    def a11yAppName(self):
        return self.a11y_app_name
    @a11yAppName.setter
    def a11yAppName(self, value):
        self.a11y_app_name = value


    @property
    def desktopFileExists(self):
        return self.desktop_file_exists
    @desktopFileExists.setter
    def desktopFileExists(self, value):
        self.desktop_file_exists = value


    @property
    def exitShortcut(self):
        return self.exit_shortcut
    @exitShortcut.setter
    def exitShortcut(self, value):
        self.exit_shortcut = value


    @property
    def desktopFileName(self):
        return self.desktop_file_name
    @desktopFileName.setter
    def desktopFileName(self, value):
        self.desktop_file_name = value


    @property
    def appProcessName(self):
        return self.app_process_name
    @appProcessName.setter
    def appProcessName(self, value):
        self.app_process_name = value
