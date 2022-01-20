from benvy.databricks.repos.runner.BootstrapRunner import BootstrapRunner
from benvy.databricks.repos.config.BootstrapInstallConfig import BootstrapInstallConfig
from benvy.databricks.repos.config.BootstrapSetupEnvConfig import BootstrapSetupEnvConfig
from benvy.container.dicontainer import Container


def install():
    configs = [BootstrapInstallConfig()]
    runner = BootstrapRunner(configs, Container)  # noqa
    runner.run()


def setup_env():
    configs = [BootstrapSetupEnvConfig()]
    runner = BootstrapRunner(configs, Container)  # noqa
    runner.run()


if __name__ == "__main__":
    install()
    setup_env()
