from penvy.container.diservice import diservice
from penvy.container.dicontainer import Container as PenvyContainer


class Container(PenvyContainer):
    @diservice
    def get_databricks_connect_detector(self):
        from benvy.databricks.DatabricksConnectDetector import DatabricksConnectDetector

        return DatabricksConnectDetector()

    @diservice
    def get_winutils_downloader(self):
        from benvy.hadoop.WinutilsDownloader import WinutilsDownloader

        return WinutilsDownloader(self._parameters["project"]["venv_dir"], self._parameters["hadoop"]["winutils_url"], self.get_logger())

    @diservice
    def get_java_setup(self):
        from benvy.java.JavaSetup import JavaSetup

        return JavaSetup(self._parameters["java"]["version"], self._parameters["java"]["install_dir"], self.get_logger())

    @diservice
    def get_databricks_connect_config_creator(self):
        from benvy.databricks.DatabricksConnectConfigCreator import DatabricksConnectConfigCreator

        return DatabricksConnectConfigCreator(self.get_logger())

    @diservice
    def get_bin_executable_flag_setter(self):
        from benvy.databricks.BinExecutableFlagSetter import BinExecutableFlagSetter

        return BinExecutableFlagSetter(
            self._parameters["conda"]["executable_path"], self._parameters["project"]["venv_dir"], self.get_logger()
        )

    @diservice
    def get_libgit2_installer(self):
        from benvy.git.Libgit2Installer import Libgit2Installer

        return Libgit2Installer(self.get_logger())

    @diservice
    def get_databricks_context(self):
        from benvy.databricks.DatabricksContext import DatabricksContext
        from benvy.databricks.dbutils.DBUtilsResolver import resolve_dbutils

        return DatabricksContext(resolve_dbutils())

    @diservice
    def get_dbx_poetry_downloader(self):
        from benvy.databricks.repos.install.PoetryDownloader import PoetryDownloader

        return PoetryDownloader(
            self._parameters["poetry"]["version"],
            self._parameters["poetry"]["archive_url"],
            self._parameters["poetry"]["archive_path"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_poetry_install_script_downloader(self):
        from benvy.databricks.repos.install.PoetryInstallScriptDownloader import PoetryInstallScriptDownloader

        return PoetryInstallScriptDownloader(
            self._parameters["poetry"]["install_script_url"],
            self._parameters["poetry"]["install_script_path"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_poetry_installer(self):
        from benvy.databricks.repos.install.PoetryInstaller import PoetryInstaller

        return PoetryInstaller(
            self._parameters["poetry"]["version"],
            self._parameters["poetry"]["home"],
            self._parameters["poetry"]["executable"],
            self._parameters["poetry"]["archive_path"],
            self._parameters["poetry"]["install_script_path"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_package_installer(self):
        from benvy.databricks.repos.install.PackageInstaller import PackageInstaller

        return PackageInstaller(
            self._parameters["project"]["dir"],
            self._parameters["poetry"]["executable"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_sys_path_appender(self):
        from benvy.databricks.repos.setup.SysPathAppender import SysPathAppender

        return SysPathAppender(
            self._parameters["project"]["dir"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_project_root_dir_setter(self):
        from benvy.databricks.repos.setup.ProjectRootDirSetter import ProjectRootDirSetter

        return ProjectRootDirSetter(
            self._parameters["project"]["dir"],
            self.get_logger(),
        )

    @diservice
    def get_dbx_bootstrap_env_setter(self):
        from benvy.databricks.repos.setup.BootstrapEnvSetter import BootstrapEnvSetter

        return BootstrapEnvSetter(
            self.get_logger(),
        )

    @diservice
    def get_dbx_repo_file_uploader(self):
        from benvy.databricks.repos.uploader.RepoFileUploader import RepoFileUploader

        return RepoFileUploader(
            self.get_databricks_context(),
        )

    @diservice
    def get_dbx_poetry_wrapper(self):
        from benvy.databricks.repos.poetry.PoetryWrapper import PoetryWrapper

        return PoetryWrapper(
            self._parameters["project"]["dir"],
            self._parameters["poetry"]["executable"],
            self.get_dbx_repo_file_uploader(),
            self.get_logger(),
        )
