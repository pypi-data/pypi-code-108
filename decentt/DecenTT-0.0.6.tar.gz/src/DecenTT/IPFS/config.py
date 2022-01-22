"""
Module:             IPFS Client
SubModule:          Config
Author:             Amey Mahadik <https://github.com/saapo-ka-baadshah>
"""
import wget
import os
import platform
from DecenTT.IPFS.IPFSExceptions import UnsupportedPlatform
from DecenTT.IPFS.logger import logger
import zipfile
import tarfile
import sys
import subprocess

import shutil

# The endpoints go here:
ENDPOINTS = {
    "pubsub": {
        "sub": "/api/v0/pubsub/sub",
        "pub": "/api/v0/pubsub/pub"
    }
}

# The Setup Class goes here:
class Setup:
    def __init__(self) -> None:
        self.cwd = os.getcwd()

    @staticmethod
    def __get_platform() -> str:
        return str(platform.system())

    def __get_os_name(self) -> str:
        pf = self.__get_platform().lower()

        if "windows" in pf:
            return "windows"
        elif "linux" in pf:
            return "linux"
        elif "darwin" in pf:
            return "macos"
        else:
            raise UnsupportedPlatform

    @staticmethod
    def __bar_progress(current, total, width=80):
        progress_message = "Downloading: %d%% [%d / %d] bytes" % (current / total * 100, current, total)
        # Don't use print() as it will print in new line every time.
        sys.stdout.write("\r" + progress_message)
        sys.stdout.flush()

    @staticmethod
    def __run_ps(cmd):
        completed = subprocess.run(["powershell", "-Command", cmd], capture_output=True)
        return completed

    def __windows_installer(self):
        temp_path = os.path.join(self.cwd, "temp")
        os.mkdir(temp_path)
        fileName = wget.download(
            url="https://dist.ipfs.io/go-ipfs/v0.10.0/go-ipfs_v0.10.0_windows-amd64.zip",
            out=str(temp_path),
            bar=self.__bar_progress
        )
        path_to_zip_file = os.path.join(temp_path, fileName)

        with zipfile.ZipFile(path_to_zip_file, 'r') as zip_ref:
            zip_ref.extractall(temp_path)

        package_dir = os.path.expanduser(os.path.join(temp_path, "go-ipfs"))
        documents_path = os.path.expanduser("~/Documents")
        profile_path = os.path.join(documents_path, "WindowsPowerShell", "profile.ps1")
        command = f'Add-Content {profile_path} "[System.Environment]::SetEnvironmentVariable(`PATH`,`$Env:PATH+`;;' + \
                  f'{package_dir}`)" '
        self.__run_ps(cmd=command)
        logger.log(f"Installed: IPFS")

    def __linux_installer(self):
        temp_path = os.path.join(self.cwd, "temp")
        cur_file_path = os.path.dirname(os.path.realpath(__file__))
        os.mkdir(temp_path)
        fileName = wget.download(
            url="https://dist.ipfs.io/go-ipfs/v0.10.0/go-ipfs_v0.10.0_linux-amd64.tar.gz",
            out=str(temp_path),
            bar=self.__bar_progress
        )

        path_to_tar_file = os.path.join(temp_path, fileName)

        tar = tarfile.open(path_to_tar_file)
        tar.extractall(path=temp_path)
        logger.info("Tarfile Extracted")
        subprocess.call(["sudo", "bash", f"{temp_path}/go-ipfs/install.sh"])
        subprocess.call(["sudo", "ipfs", "init"])
        logger.info(f"Installed: IPFS")
        # subprocess.call(["sudo", "mkdir", f"/var/log/ipfs"])
        # subprocess.call(["sudo", "touch", f"/var/log/ipfs/ipfs.log"])
        # subprocess.call(["sudo", "touch", f"/var/log/ipfs/error.log"])
        # subprocess.call(["sudo", "cp", f"{cur_file_path}/ipfs.service", "/etc/systemd/system"])
        # logger.info(f"Installed: IPFS as Service")

        logger.info(f"Installation: Completed !")

    def install(self, os_name: str = None) -> None:
        temp_path = os.path.join(self.cwd, "temp")
        if os.path.exists(temp_path) and os.path.isdir(temp_path):
            shutil.rmtree(temp_path)
        else:
            pass

        if not os_name:
            os_name = self.__get_os_name()
        else:
            os_name = str(os_name).lower()
        if os_name == "windows":
            self.__windows_installer()
        elif os_name == "macos":
            pass
        elif os_name == "linux":
            try:
                logger.info("Calling linux installer")
                self.__linux_installer()
            except Exception as e:
                logger.error(f"Error:{e}")
                temp_dir = os.path.join(self.cwd, "temp")
                if os.path.exists(temp_dir) and os.path.isdir(temp_dir):
                    shutil.rmtree(temp_dir)

        else:
            raise UnsupportedPlatform
