import os
import platform
import shutil
import urllib.request
import zipfile
import tarfile
from logging import Logger
from penvy.filesystem.rmdir import rmdir
from penvy.setup.SetupStepInterface import SetupStepInterface
from benvy.java.JavaVersion import JavaVersion


class JavaSetup(SetupStepInterface):
    def __init__(
        self,
        java_version: JavaVersion,
        java_install_dir: str,
        logger: Logger,
    ):
        self._java_version = java_version
        self._java_install_dir = java_install_dir
        self._logger = logger

    def get_description(self):
        return f"Download JDK 1.{self._java_version.major} to ~/.databricks-connect-java"

    def run(self):
        os.makedirs(self._java_install_dir)

        self._logger.info(
            f"Downloading JDK 1.{self._java_version.major} (u{self._java_version.minor}b{self._java_version.build}) to {self._java_install_dir}"
        )

        base_url = f"https://github.com/AdoptOpenJDK/openjdk8-binaries/releases/download/{self._java_version.get_build_dir()}"
        java_zip_dir = self._java_install_dir + "/" + self._java_version.get_build_dir()

        if platform.system() == "Windows":
            self._install_java_windows(base_url, java_zip_dir)
        elif platform.system() == "Linux":
            self._install_java_linux(base_url, java_zip_dir)
        elif platform.system() == "Darwin":
            self._install_java_macos(base_url, java_zip_dir)

    def _install_java_windows(self, base_url: str, extracted_java_dir: str):
        url = f"{base_url}/OpenJDK8U-jdk_x64_windows_hotspot_{self._java_version.get_file_sufix()}.zip"
        target_zip_file = self._java_install_dir + "/java.zip"

        urllib.request.urlretrieve(url, target_zip_file)

        with zipfile.ZipFile(target_zip_file, "r") as f:
            f.extractall(self._java_install_dir)
            f.close()

        self._move_extracted_java_files(extracted_java_dir)
        self._cleanup(extracted_java_dir, target_zip_file)

    def _install_java_linux(self, base_url: str, extracted_java_dir: str):
        url = f"{base_url}/OpenJDK8U-jdk_x64_linux_hotspot_{self._java_version.get_file_sufix()}.tar.gz"
        target_tar_file = self._java_install_dir + "/java.tar.gz"

        urllib.request.urlretrieve(url, target_tar_file)

        with tarfile.open(target_tar_file, "r:gz") as f:
            f.extractall(self._java_install_dir)

        self._move_extracted_java_files(extracted_java_dir)
        self._cleanup(extracted_java_dir, target_tar_file)

    def _install_java_macos(self, base_url: str, extracted_java_dir: str):
        url = f"{base_url}/OpenJDK8U-jdk_x64_mac_hotspot_{self._java_version.get_file_sufix()}.tar.gz"
        target_tar_file = self._java_install_dir + "/java.tar.gz"

        urllib.request.urlretrieve(url, target_tar_file)

        with tarfile.open(target_tar_file, "r:gz") as f:
            f.extractall(self._java_install_dir)

        self._move_extracted_java_files(extracted_java_dir + "/Contents/Home")
        self._cleanup(extracted_java_dir, target_tar_file)

    def _move_extracted_java_files(self, extracted_java_dir):
        for files in os.listdir(path=extracted_java_dir):
            shutil.move(os.path.join(extracted_java_dir, files), self._java_install_dir)

    def _cleanup(self, extracted_java_dir: str, java_archive_path: str):
        rmdir(extracted_java_dir)
        os.remove(java_archive_path)
        os.remove(self._java_install_dir + "/src.zip")

    def should_be_run(self) -> bool:
        return not os.path.isdir(self._java_install_dir)
