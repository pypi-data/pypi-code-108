from pathlib import Path

from sandboxcreator.ansible_generator.vars import Vars
from sandboxcreator.input_parser.sandbox import Sandbox
from sandboxcreator.io.reader import Reader
from sandboxcreator.io.writer import Writer


class Provision:
    """User provisioning generator"""

    @staticmethod
    def _provisioning_exists(sandbox) -> bool:
        """Check whether the provisioning directory already exists"""
        return Reader.file_exists(sandbox.sandbox_dir /
                                  sandbox.config["provisioning_playbook"])

    @staticmethod
    def _generate_template_provisioning(sandbox: Sandbox):
        """Generate an empty template playbook"""
        provisioning_path: Path = sandbox.sandbox_dir / \
                                  sandbox.config["provisioning_dir"]
        if Provision._provisioning_exists(sandbox):
            Writer.remove_directory(provisioning_path)
        Writer.copy_file(Path(__file__).parent.parent /
                         "resources/files/user_playbook.yml", sandbox.sandbox_dir /
                         sandbox.config["provisioning_playbook"])

    @staticmethod
    def _copy_user_provisioning(sandbox: Sandbox):
        """Copy user provided provisioning files to the appropriate directory"""
        provisioning_path: Path = sandbox.sandbox_dir / \
                                  sandbox.config["provisioning_dir"]
        if Provision._provisioning_exists(sandbox):
            Writer.remove_directory(provisioning_path)
        Writer.copy_directory(sandbox.user_provisioning_dir, provisioning_path)

    @staticmethod
    def generate_user_provisioning(sandbox: Sandbox):
        """Generate or copy user provisioning files"""
        if sandbox.user_provisioning_dir is not None:
            Provision._copy_user_provisioning(sandbox)
        elif sandbox.generate_provisioning or \
                not Provision._provisioning_exists(sandbox):
            Provision._generate_template_provisioning(sandbox)
            Vars.generate_user_group_vars(sandbox.sandbox_dir.joinpath(
                               sandbox.config["provisioning_group_vars"]))
        if sandbox.extra_vars is not None:
            Writer.copy_file(sandbox.extra_vars,
                             sandbox.sandbox_dir /
                             sandbox.config["user_extra_vars"])
