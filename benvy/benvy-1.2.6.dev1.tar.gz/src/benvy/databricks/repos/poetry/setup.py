from benvy.databricks.repos.runner.BootstrapRunner import BootstrapRunner
from benvy.databricks.repos.config.PoetrySetupConfig import PoetrySetupConfig
from benvy.container.dicontainer import Container


def setup_poetry():
    configs = [PoetrySetupConfig()]
    runner = BootstrapRunner(configs, Container)  # noqa
    runner.run()
