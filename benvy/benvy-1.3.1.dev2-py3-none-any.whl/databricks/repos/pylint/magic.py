from benvy.databricks.repos.config.BootstrapConfig import BootstrapConfig
from benvy.container.dicontainer import Container


def pylint(line: str):
    parameters = BootstrapConfig().get_parameters()
    container = Container(parameters)
    pylint_wrapper = container.get_dbx_pylint_wrapper()
    arguments = line.split()
    pylint_wrapper.run(arguments)


def load_ipython_extension(ipython):
    ipython.register_magic_function(pylint, "line")
