from release_mgr.git import git
from release_mgr.version_files.cargo_toml import CargoTOML
from release_mgr.version_files.dunder_version import DunderVersion
from release_mgr.version_files.lerna_json import LernaJSON
from release_mgr.version_files.package_json import PackageJSON
from release_mgr.version_files.pyproject import PyProjectTOML
from release_mgr.version_files.setup_py import SetupPy

VERSION_FILES = [
    PackageJSON,
    LernaJSON,
    SetupPy,
    PyProjectTOML,
    DunderVersion,
    CargoTOML,
]


def update_version_files(version):
    updated = update_vfs(version)
    if updated:
        git("commit", "-m", f"release: {version}")
        git("push")


def update_vfs(version):
    version_file_updated = False
    for version_file in VERSION_FILES:
        vf = version_file.from_file()
        if not vf:
            continue

        updated = vf.update(str(version))
        if updated:
            print("Updated version in:", vf.filename)

        version_file_updated = version_file_updated or updated

    return version_file_updated
