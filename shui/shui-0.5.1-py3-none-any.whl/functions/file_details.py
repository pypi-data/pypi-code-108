"""Functions for downloading a particular version from the remote repository"""
from shui.classes import FileInfo, FileWithHash


def get_file_details(version, install_dir):
    """Construct local paths for a particular Spark/Hadoop version"""
    tarball_path = install_dir / version.filename
    sha512_path = tarball_path.append_suffix(".sha512")
    return FileWithHash(
        FileInfo(version.url, tarball_path),
        FileInfo(f"{version.url}.sha512", sha512_path),
    )
