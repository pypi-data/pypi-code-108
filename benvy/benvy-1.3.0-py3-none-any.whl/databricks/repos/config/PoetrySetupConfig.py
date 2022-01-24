from benvy.databricks.repos.config.BootstrapConfig import BootstrapConfig
from benvy.container.dicontainer import Container


class PoetrySetupConfig(BootstrapConfig):
    def get_setup_steps(self, container: Container):
        return [
            container.get_dbx_poetry_downloader(),
            container.get_dbx_poetry_install_script_downloader(),
            container.get_dbx_poetry_installer(),
        ]
