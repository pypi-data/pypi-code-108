import os
import yaml
import pathlib


class ClusterBase:
    def __init__(self, config_path=None):
        """
        Base class for cluster class that generates batch files

        Parameters
        ----------
        config_path: str
            path to the configuration file, if None user cluster_config
        """
        if config_path is None:
            package_path = pathlib.Path(__file__).parent.parent.absolute()
            config_path = os.path.join(package_path, "cluster_config")

        self.config_path = config_path
        self.project_path = None

    def set_project_path(self, path):
        self.project_path = path

    def read_configuration(self):
        """
        Reads configuration file, called once per run
        """

        raise RuntimeError("Running ClusterBase which is a base class.")

    def start_launch_script(self):
        """
        Setup method that is called once per run before any write_task call
        """
        raise RuntimeError("Running ClusterBase which is a base class.")

    def write_task(self, foldername, scan_name):
        """
        Method called for each guide optimization, defining this task

        Parameters
        ----------
        foldername: str
            Name of the folder in which to run files

        scan_name: str
            scan name of this guide optimization, name of plk file
        """

        raise RuntimeError("Running ClusterBase which is a base class.")

