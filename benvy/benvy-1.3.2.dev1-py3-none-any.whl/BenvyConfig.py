import os
from penvy.env.EnvConfig import EnvConfig
from benvy.container.dicontainer import Container
from benvy.java.JavaVersion import JavaVersion


class BenvyConfig(EnvConfig):
    def get_parameters(self) -> dict:
        return {
            "hadoop": {
                "winutils_url": "https://raw.githubusercontent.com/steveloughran/winutils/d4f715173fb232dea42e26776685a5ed90eb1a99/hadoop-3.0.0/bin/winutils.exe",
            },
            "java": {"version": JavaVersion(8, 242, "08"), "install_dir": os.path.expanduser("~") + os.sep + ".databricks-connect-java"},
        }

    def get_setup_steps(self, container: Container):
        steps = [container.get_libgit2_installer()]

        if not container.get_databricks_connect_detector().detect():
            container.get_logger().debug("databricks-connect not installed, skipping benvy setup steps")

            return steps

        return steps + [
            container.get_winutils_downloader(),
            container.get_databricks_connect_config_creator(),
            container.get_java_setup(),
            container.get_bin_executable_flag_setter(),
        ]
