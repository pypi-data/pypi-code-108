from pathlib import Path
from typing import Dict

from sandboxcreator.ansible_generator.routes import Routes
from sandboxcreator.input_parser.sandbox import Sandbox
from sandboxcreator.io.writer import Writer


class Vars:

    @staticmethod
    def create_host_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each host"""
        host_vars: Dict[str, Dict] = {}
        for device in sandbox.devices:
            variables: Dict = {"routes": Routes.create_routes(device, sandbox)}
            host_vars[device.name] = variables

        return host_vars

    @staticmethod
    def create_group_vars(sandbox: Sandbox) -> Dict[str, Dict]:
        """Create variables for each group"""
        aliases: Dict[str, str] = {}
        for device in sandbox.devices:
            for interface in device.interfaces:
                aliases[str(interface.ip)] = device.name

        all_vars: Dict = {"device_aliases": aliases}
        if sandbox.controller_present:
            all_vars["controller_name"] = sandbox.config["controller_name"]
        hosts_vars: Dict = {}
        router_vars: Dict = {}
        ssh_vars: Dict = {"ansible_python_interpreter": "python3"}
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
                            "ansible_become_pass": "vagrant",
                            "ansible_port": "5985",
                            "ansible_winrm_scheme": "http",
                            "ansible_winrm_transport": "basic",
                            "ansible_winrm_server_cert_validation": "ignore"}

        if sandbox.ansible_installed:
            ssh_vars.update({"ansible_host": "127.0.0.1",
                             "ansible_user": "vagrant"})
        else:
            ssh_vars.update({"ansible_connection": "local"})

        group_vars: Dict[str, Dict] = {"all": all_vars, "hosts": hosts_vars,
                                       "routers": router_vars, "ssh": ssh_vars,
                                       "winrm": winrm_vars}
        return group_vars

    @staticmethod
    def generate_vars(sandbox: Sandbox, host_dir: Path, group_dir: Path):
        """Generate host and group vars files"""
        host_vars: Dict[str, Dict] = Vars.create_host_vars(sandbox)
        for host, variables in host_vars.items():
            if variables:
                Writer.generate_yaml(host_dir.joinpath(f"{host}.yml"),
                                     variables)

        group_vars: Dict[str, Dict] = Vars.create_group_vars(sandbox)
        for group, variables in group_vars.items():
            if variables:
                Writer.generate_yaml(group_dir.joinpath(f"{group}.yml"),
                                     variables)

    @staticmethod
    def generate_user_group_vars(group_dir: Path):
        """Generate group vars for user provisioning files needed by windows"""
        winrm_vars: Dict = {"ansible_connection": "winrm",
                            "ansible_user": "windows",
                            "ansible_password": "vagrant",
                            "ansible_become_pass": "vagrant",
                            "ansible_port": "5985",
                            "ansible_winrm_scheme": "http",
                            "ansible_winrm_transport": "basic",
                            "ansible_winrm_server_cert_validation": "ignore"}
        group_vars: Dict[str, Dict] = {"winrm": winrm_vars}
        for group, variables in group_vars.items():
            if variables:
                Writer.generate_yaml(group_dir.joinpath(f"{group}.yml"),
                                     variables)
