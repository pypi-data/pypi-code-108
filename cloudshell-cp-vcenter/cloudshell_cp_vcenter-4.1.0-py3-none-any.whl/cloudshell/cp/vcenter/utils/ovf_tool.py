import logging
import subprocess

from cloudshell.cp.vcenter import exceptions


class OVFToolScript:
    COMPLETED_SUCCESSFULLY = "completed successfully"
    OVF_DESTINATION_TPL = (
        "vi://{username}:{password}@{host}/{datacenter}/host/{cluster}{resource_pool}"
    )
    RESOURCE_POOL_TPL = "/Resources/{}"
    HIDEN_PASSWORD_TPL = "<hidden_password>"

    class KwArgs:
        NO_SSL = "--noSSLVerify"
        ACCEPT_ALL = "--acceptAllEulas"
        POWER_ON = "--powerOn"
        POWER_OFF = "--powerOffTarget"
        VM_FOLDER = "--vmFolder={}"
        VM_NAME = "--name={}"
        DATA_STORE = "--datastore={}"
        QUIET = "--quiet"

    def __init__(
        self,
        ovf_tool_path: str,
        datacenter: str,
        vm_storage: str,
        vm_cluster: str,
        vm_resource_pool: str,
        vm_folder: str,
        vm_name: str,
        vcenter_image: str,
        custom_args: list,
        vcenter_user: str,
        vcenter_password: str,
        vcenter_host: str,
        logger: logging.Logger,
    ):
        self._ovf_tool_path = ovf_tool_path
        self._datacenter = datacenter
        self._vm_storage = vm_storage
        self._vm_cluster = vm_cluster
        self._vm_resource_pool = vm_resource_pool
        self._vm_folder = vm_folder
        self._vm_name = vm_name
        self._vcenter_image = vcenter_image
        self._custom_args = custom_args
        self._vcenter_user = vcenter_user
        self._vcenter_password = vcenter_password
        self._vcenter_host = vcenter_host
        self._logger = logger

    def run(self):
        process = subprocess.Popen(
            self._prepare_script_args(),
            shell=True,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        result = process.communicate()
        process.stdin.close()

        if result:
            res = b"\n\r".join(result).decode()

            if self.COMPLETED_SUCCESSFULLY not in res.lower():
                self._logger.error(
                    f"Failed to deploy VM image with OVF tool. Script args:"
                    f" {self._prepare_script_args(sensitive=True)}. Result: {res}"
                )

                raise exceptions.DeployOVFToolException(
                    f"Failed to deploy VM image with OVF tool. Error: {res}"
                )
        else:
            if self.KwArgs.QUIET not in self._custom_args:
                raise exceptions.EmptyOVFToolResultException(
                    "No result from the OVF Tool"
                )

    def _prepare_script_args(self, sensitive=False):
        script_args = [
            self._ovf_tool_path,
            self.KwArgs.NO_SSL,
            self.KwArgs.ACCEPT_ALL,
            self.KwArgs.POWER_OFF,
            self.KwArgs.VM_NAME.format(self._vm_name),
            self.KwArgs.DATA_STORE.format(self._vm_storage),
        ]

        if self._vm_folder:
            script_args.append(OVFToolScript.KwArgs.VM_FOLDER.format(self._vm_folder))

        script_args += self._custom_args

        script_args += [
            self._vcenter_image,
            self._prepare_ovf_destination(sensitive=sensitive),
        ]

        return script_args

    def _prepare_ovf_destination(self, sensitive):
        resource_pool = (
            OVFToolScript.RESOURCE_POOL_TPL.format(self._vm_resource_pool)
            if self._vm_resource_pool
            else ""
        )

        password = (
            OVFToolScript.HIDEN_PASSWORD_TPL if sensitive else self._vcenter_password
        )

        return self.OVF_DESTINATION_TPL.format(
            username=self._vcenter_user,
            password=password,
            host=self._vcenter_host,
            datacenter=self._datacenter,  # default datacenter from the resource config
            cluster=self._vm_cluster,  # VM Cluster  from the resource config
            resource_pool=resource_pool,
        )

        # todo: check if we needed this or can use some default encode function
        # return fixurl(ovf_destination)  # noqa
