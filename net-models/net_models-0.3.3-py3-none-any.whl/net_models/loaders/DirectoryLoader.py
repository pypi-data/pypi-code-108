# Standard Libraries
import pathlib
import yaml
# Third party packages
from pydantic.typing import (
    List,
    Literal
)
# Local package
from net_models.utils import get_logger
from net_models.inventory import Inventory, HostConfig, GroupConfig
# Local module
from .BaseLoader import BaseLoader

class DirectoryLoader(BaseLoader):

    def __init__(self, inventory_path: pathlib.Path, inventory: Inventory = None, verbosity: int = 4):
        super().__init__(inventory=inventory)
        self.logger = get_logger(name="DirectoryLoader", verbosity=verbosity)
        self.inventory_path = pathlib.Path(inventory_path).resolve()


    def get_yml_files(self, path: pathlib.Path):
        if not path.is_dir():
            msg = f"Given path {path} is not a directory."
            self.logger.error(mag=msg)
            raise ValueError(msg)
        yml_files = [x for x in path.iterdir() if x.is_file() and x.suffix in ['.yml', '.yaml']]
        self.logger.debug(msg=f"Found {len(yml_files)} YAML files in path {path}")
        return yml_files

    def load_yml_files(self, files: List[pathlib.Path]):
        for path in files:
            yield path, yaml.safe_load(path.read_text())

    def load(self):
        self.load_inventory_structure()
        self.traverse_host_vars()
        self.traverse_group_vars()
        self.traverse_host_vars()

    def traverse_inventory(self, data: dict, data_type: Literal['groups', 'hosts'], parent_name: str = None):
        if data_type == 'groups':
            for k, v in data.items():
                group = self.get_group(group_name=k, parent_name=parent_name)
                if isinstance(v, dict):
                    if 'children' in v.keys() and v['children'] is not None:
                        self.traverse_inventory(data=v['children'], data_type='groups', parent_name=k)
                    if 'hosts' in v.keys() and v['hosts'] is not None:
                        self.traverse_inventory(data=v['hosts'], data_type='hosts', parent_name=k)
                elif v is None:
                    pass
        elif data_type == 'hosts':
            for k, v in data.items():
                host = self.get_host(host_name=k)
                if parent_name is not None:
                    parent = self.get_group(group_name=parent_name)
                    parent.add_host(host.name)

    def load_inventory_structure(self):
        # Get file contents dict
        for path, data in self.load_yml_files(files=self.get_yml_files(path=self.inventory_path)):
            self.logger.debug(msg=f"Loading {path.name}")
            self.traverse_inventory(data=data, data_type='groups')

    def traverse_host_vars(self):
        host_vars_dir = self.inventory_path.joinpath('host_vars')
        if host_vars_dir.exists():
            self.logger.debug(msg="Loading host_vars")
            directories = [x for x in host_vars_dir.iterdir() if x.is_dir()]
            self.logger.debug(msg=f"Found {len(directories)} directories in  host_vars")
            files = self.get_yml_files(path=host_vars_dir)
            # print(directories)
            # print(files)
            for directory in directories:
                if directory.name in self.inventory.hosts.keys():
                    host = self.get_host(host_name=directory.name, create_if_missing=False)
                    self.logger.debug(msg=f"Traversing host_var directory for host {host.name}")
                    host_vars_files = self.get_yml_files(path=directory)
                    self.logger.debug(msg=f"Loading {len(host_vars_files)} host_vars files for host {host.name}")
                    host_data = {}
                    for path, data in self.load_yml_files(files=host_vars_files):
                        if isinstance(data, dict):
                            host_data.update(data)
                    if len(host_data.keys()):
                        host.config = HostConfig.parse_obj(host_data)
            for file in files:
                if file.stem in self.inventory.hosts.keys():
                    host = self.get_host(host_name=file.stem, create_if_missing=False)
                    self.logger.debug(msg=f"Loading host_var file for host {host.name}")
                    host_data = {}
                    for path, data in self.load_yml_files(files=[file]):
                        if isinstance(data, dict):
                            host_data.update(data)
                    if len(host_data.keys()):
                        host.config = HostConfig.parse_obj(host_data)


    def traverse_group_vars(self):
        group_vars_dir = self.inventory_path.joinpath('group_vars')
        if group_vars_dir.exists():
            self.logger.debug(msg="Loading group_vars")
            directories = [x for x in group_vars_dir.iterdir() if x.is_dir()]
            self.logger.debug(msg=f"Found {len(directories)} directories in  group_vars")
            files = self.get_yml_files(path=group_vars_dir)

            for directory in directories:
                group = self.get_group(group_name=directory.name, create_if_missing=False)
                if group is not None:
                    group_name = directory.name
                    self.logger.debug(msg=f"Traversing group_var directory for group {group_name}")
                    group_vars_files = self.get_yml_files(path=directory)
                    self.logger.debug(msg=f"Loading {len(group_vars_files)} group_vars files for group {group_name}")
                    group_data = {}
                    for path, data in self.load_yml_files(files=group_vars_files):
                        if isinstance(data, dict):
                            group_data.update(data)
                    if len(group_data.keys()):
                        group.config = GroupConfig.parse_obj(group_data)
            for file in files:
                group = self.get_group(group_name=file.stem, create_if_missing=False)
                if group is not None:
                    group_name = file.stem
                    self.logger.debug(msg=f"Loading group_var file for group {group_name}")
                    group_data = {}
                    for path, data in self.load_yml_files(files=[file]):
                        if isinstance(data, dict):
                            group_data.update(data)
                    if len(group_data.keys()):
                        group.config = GroupConfig.parse_obj(group_data)









