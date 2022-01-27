import platform
import traceback

import settings
import subprocess
import paramiko
from scp import SCPClient


def scp_report_to_specified_path(source_report_path):
    """
    @author: Wang Lin
    """
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh_client.connect(settings.SPECIFIED_REPORT_HOST_IP, settings.SPECIFIED_REPORT_HOST_PORT,
                       settings.SPECIFIED_REPORT_HOST_USERNAME, settings.SPECIFIED_REPORT_HOST_PASSWORD)
    scpclient = SCPClient(ssh_client.get_transport(), socket_timeout=15.0)

    try:
        scpclient.put(source_report_path, settings.SPECIFIED_REPORT_PATH, recursive=True, )
    except FileNotFoundError as e:
        traceback.print_exc()
        print(e)
        print("系统找不到指定文件" + source_report_path)
    else:
        print(
            "文件上传成功 from: " + source_report_path + " ----- to: " + settings.SPECIFIED_REPORT_HOST_PORT + settings.SPECIFIED_REPORT_PATH)
    finally:
        ssh_client.close()
