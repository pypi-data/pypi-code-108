from benvy.databricks.repos.config.BootstrapConfig import BootstrapConfig
from benvy.container.dicontainer import Container
from benvy.databricks.repos.poetry.setup import setup_poetry


def poetry(line):
    parameters = BootstrapConfig().get_parameters()
    container = Container(parameters)
    poetry_wrapper = container.get_dbx_poetry_wrapper()
    arguments = line.split()
    poetry_wrapper.run_command(arguments)


def load_ipython_extension(ipython):
    setup_poetry()
    ipython.register_magic_function(poetry, "line")
