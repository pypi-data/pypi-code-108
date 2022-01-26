from pathlib import Path

from sandboxcreator.ansible_generator.vars import Vars
from sandboxcreator.io.writer import Writer
from sandboxcreator.io.reader import Reader
from sandboxcreator.input_parser.sandbox import Sandbox


class Preconfig:
    """Pre-configuration generator"""

    @staticmethod
    def _preconfig_exists(sandbox) -> bool:
        """Check whether the provisioning directory already exists"""
        return Reader.dir_exists(sandbox.sandbox_dir /
                                 sandbox.config["preconfig_dir"])

    @staticmethod
    def generate_preconfig(sandbox: Sandbox) -> None:
        """Generate all files for pre-configuration"""

        if Preconfig._preconfig_exists(sandbox):
            Writer.remove_directory(sandbox.sandbox_dir /
                                    sandbox.config["preconfig_dir"])

        Writer.clone_git_repository(sandbox.config["common_repo"],
                                    sandbox.sandbox_dir / sandbox.config["preconfig_roles"],
                                    sandbox.config["common_role"])
        Writer.clone_git_repository(sandbox.config["interface_repo"],
                                    sandbox.sandbox_dir / sandbox.config["preconfig_roles"],
                                    sandbox.config["interface_role"])

        Vars.generate_vars(sandbox,
                           sandbox.sandbox_dir.joinpath(
                               sandbox.config["preconfig_host_vars"]),
                           sandbox.sandbox_dir.joinpath(
                               sandbox.config["preconfig_group_vars"]))

        Writer.copy_file(Path(__file__).parent.parent /
                         "resources/files/playbook.yml", sandbox.sandbox_dir /
                         sandbox.config["preconfig_playbook"])
