"""Command-line application for installing a particular Spark/Hadoop version"""
from contextlib import suppress
import pathlib3x as pathlib
from cleo import Command
from shui.functions import extract_tarball, get_file_details, get_versions


class InstallCommand(Command):
    """
    Install a particular Spark and Hadoop version

    install
        {--latest : Use the latest available version}
        {--spark=any : Spark version}
        {--hadoop=any : Hadoop version}
        {--target=cwd : Directory to install into}
    """

    def handle(self):
        # Get correct Spark/Hadoop version
        if self.option("latest"):
            selected_version = sorted(get_versions())[-1]
        else:
            matching_versions = get_versions()
            if self.option("spark") != "any":
                matching_versions = [
                    v for v in matching_versions if v.spark == self.option("spark")
                ]
            if self.option("hadoop") != "any":
                matching_versions = [
                    v for v in matching_versions if v.hadoop == self.option("hadoop")
                ]
            if not len(matching_versions) == 1:
                self.line(
                    f"Found {len(matching_versions)} versions matching"
                    + f"<comment>Spark</comment> <info>{self.option('spark')}</info>;"
                    + f"<comment>Hadoop</comment> <info>{self.option('hadoop')}</info>"
                )
                for version in matching_versions:
                    self.line(f"  - Found {version}")
                raise ValueError("Could not identify version to install!")
            selected_version = matching_versions[0]
        # Get installation directory, creating it if necessary
        if self.option("target") != "cwd":
            install_dir = pathlib.Path(self.option("target"))
        else:
            install_dir = pathlib.Path.cwd()
        install_dir = install_dir.expanduser().resolve()
        with suppress(OSError):
            install_dir.mkdir(parents=True, exist_ok=True)
        if not install_dir.is_dir():
            raise ValueError(f"{install_dir} is not a valid installation directory!")
        self.line(
            f"Installing <comment>{selected_version}</comment> in <info>{install_dir}</info>"
        )
        # Download tarball and checksum
        file_with_hash = get_file_details(selected_version, install_dir)
        for fileinfo in file_with_hash:
            self.line(
                f"Downloading <comment>{fileinfo.name}</comment> from <info>{fileinfo.url}</info>"
            )
            fileinfo.download()
            self.line(f"Finished downloading <comment>{fileinfo.name}</comment>")
        # Verify tarball
        if file_with_hash.verify():
            self.line(
                f"Verified <comment>{selected_version.filename}</comment> using SHA512 hash"
            )
        else:
            raise IOError(f"Could not verify {selected_version} using SHA512!")
        # Extract tarball
        self.line(
            f"Extracting <comment>{selected_version}</comment> to <info>{install_dir}</info>"
        )
        installation_path = extract_tarball(file_with_hash.file, install_dir)
        self.line(f"Cleaning up downloaded files from <comment>{install_dir}</comment>")
        file_with_hash.remove()
        self.line(
            f"Finished installing <comment>{selected_version}</comment> to <info>{str(installation_path)}</info>"
        )
