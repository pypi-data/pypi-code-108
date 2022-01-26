import ssl
from logging import Logger
from urllib.parse import quote

import OpenSSL
from packaging import version

from cloudshell.cp.vcenter.handlers.dc_handler import DcHandler
from cloudshell.cp.vcenter.handlers.si_handler import SiHandler
from cloudshell.cp.vcenter.models.deployed_app import BaseVCenterDeployedApp
from cloudshell.cp.vcenter.resource_config import VCenterResourceConfig

CONSOLE_PORT = 9443
HTTPS_PORT = 443
VCENTER_FQDN_KEY = "VirtualCenter.FQDN"

VCENTER_NEW_CONSOLE_LINK_VERSION = "6.5.0"

VM_WEB_CONSOLE_OLD_LINK_TPL = (
    "https://{vcenter_ip}:9443/vsphere-client/webconsole.html?"
    "vmId={vm_moid}"
    "&vmName={vm_name}"
    "&serverGuid={server_guid}"
    "&host={vcenter_host}:443"
    "&sessionTicket={session_ticket}"
    "&thumbprint={thumbprint}"
)
VM_WEB_CONSOLE_NEW_LINK_TPL = (
    "https://{vcenter_ip}/ui/webconsole.html?"
    "vmId={vm_moid}"
    "&vmName={vm_name}"
    "&serverGuid={server_guid}"
    "&host={vcenter_host}:443"
    "&sessionTicket={session_ticket}"
    "&thumbprint={thumbprint}"
)


def get_vm_web_console(
    resource_conf: VCenterResourceConfig,
    deployed_app: BaseVCenterDeployedApp,
    logger: Logger,
) -> str:
    logger.info("Get VM Web Console")
    si = SiHandler.from_config(resource_conf, logger)
    dc = DcHandler.get_dc(resource_conf.default_datacenter, si)
    vm = dc.get_vm_by_uuid(deployed_app.vmdetails.uid)

    vc_cert = ssl.get_server_certificate((resource_conf.address, HTTPS_PORT)).encode()
    vc_pem = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, vc_cert)
    thumbprint = vc_pem.digest("sha1")

    if version.parse(si.vc_version) >= version.parse(VCENTER_NEW_CONSOLE_LINK_VERSION):
        format_str = VM_WEB_CONSOLE_NEW_LINK_TPL
    else:
        format_str = VM_WEB_CONSOLE_OLD_LINK_TPL

    return format_str.format(
        vcenter_ip=resource_conf.address,
        vm_moid=vm._moId,
        vm_name=quote(vm.name),
        server_guid=si.instance_uuid,
        vcenter_host=si.vcenter_host,
        https_port=HTTPS_PORT,
        session_ticket=quote(si.acquire_session_ticket()),
        thumbprint=quote(thumbprint.decode()),
    )
