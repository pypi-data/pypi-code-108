from benvy.databricks.repos.config.BootstrapConfig import BootstrapConfig
from benvy.container.dicontainer import Container


def get_uploader():
    parameters = BootstrapConfig().get_parameters()
    container = Container(parameters)
    return container.get_dbx_repo_file_uploader()
