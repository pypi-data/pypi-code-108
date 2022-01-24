# Copyright 2019 Splunk Inc. All rights reserved.

"""This is a helper module to encapsulate the functionality that represents
Splunk's alert action feature.
"""
import os

import splunk_appinspect

try:
    import itertools.ifilter as filter
except ImportError:
    pass


class AlertActions(object):
    def __init__(self, app):
        self.app = app
        self.configuration_directory_path = "default"
        self.configuration_filename = "alert_actions.conf"
        self._exes_cache = {}

        # architecture stuff
        self.CROSS_PLAT_EXE_TAG = "cross_plat_exe"
        self.WINDOWS_EXE_TAG = "windows_exe"
        self.NIX_EXE_TAG = "nix_exe"

        self.LINUX_ARCH = "linux"
        self.WIN_ARCH = "win"
        self.DARWIN_ARCH = "darwin"
        self.DEFAULT_ARCH = "default"

        # Taken from
        # http://docs.splunk.com/Documentation/Splunk/latest/AdvancedDev/CustomAlertScript
        self.WINDOWS_EXES = [".cmd", ".bat", ".js", ".py", ".exe"]
        self.NIX_EXES = [".sh", ".js", ".py", ""]

        self.CROSS_PLAT_EXES = splunk_appinspect.iter_ext.intersect(
            self.WINDOWS_EXES, self.NIX_EXES
        )
        # TODO: Refactor this along with alert actions.  This can be moved to
        # the app instance
        self.arch_bin_dirs = {
            self.LINUX_ARCH: [
                os.path.join(self.app.app_dir, "linux_x86", "bin"),
                os.path.join(self.app.app_dir, "linux_x86_64", "bin"),
            ],
            self.WIN_ARCH: [
                os.path.join(self.app.app_dir, "windows_x86", "bin"),
                os.path.join(self.app.app_dir, "windows_x86_64", "bin"),
            ],
            self.DARWIN_ARCH: [
                os.path.join(self.app.app_dir, "darwin_x86", "bin"),
                os.path.join(self.app.app_dir, "darwin_x86_64", "bin"),
            ],
            self.DEFAULT_ARCH: [os.path.join(self.app.app_dir, "bin")],
        }

    def get_alert_actions(self):
        configuration_file = self.get_configuration_file()
        for section in configuration_file.sections():
            alert_action = AlertAction(section)

            for key, value, lineno in self.get_configuration_file().items(section.name):
                if key.lower() == "alert.execute.cmd":
                    alert_action.alert_execute_cmd = os.path.join(
                        self.app.app_dir, "bin/", value
                    )
                if key.lower() == "icon_path":
                    alert_action.relative_icon_path = os.path.join(
                        "appserver/static/", value
                    )
                    alert_action.icon_path = os.path.join(
                        self.app.app_dir, alert_action.relative_icon_path
                    )
                if key.lower() == "python.version":
                    alert_action.python_version = value
                alert_action.relative_workflow_html_path = os.path.join(
                    "default/data/ui/alerts/", alert_action.name + ".html"
                )
                alert_action.workflow_html_path = os.path.join(
                    self.app.app_dir, alert_action.relative_workflow_html_path
                )
                alert_action.args[key] = [value, lineno]

            # If an exe is specified in the stanza this overrides other bin
            # files
            if alert_action.alert_execute_cmd_specified():
                alert_action.executable_files.append(
                    splunk_appinspect.file_resource.FileResource(
                        alert_action.alert_execute_cmd
                    )
                )
            else:
                files = []
                for f in self.find_exes(alert_action.name):
                    files.append(f)

                alert_action.cross_plat_exes = list(
                    filter(
                        lambda exe: self.DEFAULT_ARCH in exe.tags
                        and self.CROSS_PLAT_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.win_exes = list(
                    filter(
                        lambda exe: self.DEFAULT_ARCH in exe.tags
                        and self.WINDOWS_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.linux_exes = list(
                    filter(
                        lambda exe: self.DEFAULT_ARCH in exe.tags
                        and self.NIX_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.win_arch_exes = list(
                    filter(
                        lambda exe: self.WIN_ARCH in exe.tags
                        and self.WINDOWS_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.linux_arch_exes = list(
                    filter(
                        lambda exe: self.LINUX_ARCH in exe.tags
                        and self.NIX_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.darwin_arch_exes = list(
                    filter(
                        lambda exe: self.DARWIN_ARCH in exe.tags
                        and self.NIX_EXE_TAG in exe.tags,
                        files,
                    )
                )

                alert_action.executable_files = list(files)

            yield alert_action

    # TODO: generalize this to accept the filename and directory
    def has_configuration_file(self):
        return self.app.file_exists(
            self.configuration_directory_path, self.configuration_filename
        )

    # TODO: generalize this to accept the filename and directory
    def get_configuration_file(self):
        return self.app.get_config(
            self.configuration_filename,
            dir=self.configuration_directory_path,
            config_file=splunk_appinspect.alert_actions_configuration_file.AlertActionsConfigurationFile(),
        )

    # TODO: generalize this to accept the filename and directory
    def get_raw_configuration_file(self):
        return self.app.get_raw_conf(
            self.configuration_filename, dir=self.configuration_directory_path
        )

    def get_configuration_app_filepath(self):
        return self.app.get_filename(
            self.configuration_directory_path, self.configuration_filename
        )

    def find_exes(self, name):
        """For a given named file, find scripts and exes in the standard folders
        :param name: the name of the file to search for
        """
        if name in self._exes_cache:
            return self._exes_cache[name]
        # Find all the files across OS, across platform
        files = []
        for arch in self.arch_bin_dirs:
            for bin_dir in self.arch_bin_dirs[arch]:

                # Determine which extensions to use when checking specific arch
                # folders
                if arch in (self.LINUX_ARCH, self.DARWIN_ARCH):
                    ext_filter = self.NIX_EXES
                elif arch == self.WIN_ARCH:
                    ext_filter = self.WINDOWS_EXES
                elif arch == self.DEFAULT_ARCH:
                    ext_filter = self.WINDOWS_EXES + self.NIX_EXES

                files_iterator = self.app.iterate_files(
                    basedir=bin_dir, types=ext_filter
                )
                for directory, filename, ext in files_iterator:
                    fb, ext = os.path.splitext(filename)

                    if name != fb:
                        pass
                    else:
                        resource = splunk_appinspect.file_resource.FileResource(
                            os.path.join(self.app.app_dir, directory, filename)
                        )
                        resource.ext = ext
                        resource.app_file_path = os.path.join(directory, filename)
                        resource.tags.append(arch)

                        if ext in self.WINDOWS_EXES:
                            resource.tags.append(self.WINDOWS_EXE_TAG)

                        if ext in self.NIX_EXES:
                            resource.tags.append(self.NIX_EXE_TAG)

                        if ext in self.CROSS_PLAT_EXES:
                            resource.tags.append(self.CROSS_PLAT_EXE_TAG)

                        files.append(resource)
        self._exes_cache[name] = files
        return files


class AlertAction(object):
    """Represents an alert action. This belongs to the AlertActions domain
    object.
    """

    def __init__(
        self,
        section,
        alert_execute_cmd="",
        icon_path="",
        is_custom=True,
        workflow_html_path="",
        relative_icon_path="",
        relative_workflow_html_path="",
        python_version="",
    ):
        self.name = section.name
        self.lineno = section.lineno
        self.alert_execute_cmd = alert_execute_cmd
        self.icon_path = icon_path
        self.relative_icon_path = relative_icon_path
        self.is_custom = is_custom
        self.workflow_html_path = workflow_html_path
        self.relative_workflow_html_path = relative_workflow_html_path
        self.python_version = python_version
        self.executable_files = []
        self.args = {}
        self.cross_plat_exes = None
        self.win_exes = None
        self.linux_exes = None
        self.win_arch_exes = None
        self.linux_arch_exes = None
        self.darwin_arch_exes = None

    def alert_execute_cmd_file(self):
        """The exe specified in the stanza. This may not exist"""
        return splunk_appinspect.file_resource.FileResource(self.alert_execute_cmd)

    def alert_execute_cmd_specified(self):
        return self.alert_execute_cmd != ""

    def alert_icon(self):
        """The alert icon specified in the stanza"""
        return splunk_appinspect.file_resource.FileResource(self.icon_path)

    def get_command(self):
        # Should only have one command so only initial index is returned
        command_to_return = self.args["command"][0] if self.has_command() else None
        return command_to_return

    def has_command(self):
        return "command" in self.args

    def workflow_html(self):
        """The html file used to configure the alert. Should match the name of
        the stanza.
        """
        return splunk_appinspect.file_resource.FileResource(self.workflow_html_path)

    def count_cross_plat_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.cross_plat_exes)

    def count_win_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.win_exes)

    def count_linux_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.linux_exes)

    def count_win_arch_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.win_arch_exes)

    def count_linux_arch_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.linux_arch_exes)

    def count_darwin_arch_exes(self):
        return splunk_appinspect.iter_ext.count_iter(self.darwin_arch_exes)
