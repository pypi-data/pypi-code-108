# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import json
import lzma
import os
import shutil
from logging import error, info, warning
from typing import Optional, Set

from portmod.config import get_config
from portmod.download import download_mod
from portmod.globals import env
from portmod.loader import (
    _delete_state,
    _sandbox_execute_pybuild,
    _state_path,
    load_all_installed,
    load_installed_pkg,
)
from portmod.parsers.manifest import FileType, Manifest, ManifestEntry
from portmod.vdb import VDB
from portmodlib._phase import PhaseState
from portmodlib.atom import Atom
from portmodlib.colour import green
from portmodlib.fs import (
    _iter_files_to_patch,
    _patch_file,
    ci_exists,
    get_tree_size,
    is_parent,
    onerror,
)
from portmodlib.l10n import l10n

from .cache import clear_cache_for_path
from .functools import clear_install_cache
from .modules import module_prerm
from .perms import Permissions
from .prompt import prompt_options
from .pybuild import InstalledPybuild, Pybuild
from .rebuild import get_rebuild_manifest
from .vfs import _cleanup_tmp_archive_dir


def belongs(path: str, case_sensitive: bool = True) -> Optional[InstalledPybuild]:
    """
    Returns the package which installed the given file

    args:
        The path of the file to check, relative to the installation root

    If no such package exists, returns None
    """
    normpath = os.path.normpath(path)
    for pkg in load_all_installed():
        if pkg.get_contents().get(normpath, case_sensitive=case_sensitive):
            return pkg

    return None


def src_unpack(
    pkg: Pybuild,
    build_dir: str,
    curdir: Optional[str] = None,
    state: PhaseState = PhaseState(),
):
    permissions = Permissions(
        rw_paths=[build_dir],
        ro_paths=[env.DOWNLOAD_DIR],
        global_read=False,
        network=True,
        tmp=state.T,
    )
    _sandbox_execute_pybuild(
        pkg.FILE,
        "unpack",
        permissions,
        save_state=True,
        init=state.__dict__,
        curdir=curdir or build_dir,
    )


def src_prepare(
    pkg: Pybuild,
    build_dir: str,
    curdir: Optional[str] = None,
    state: PhaseState = PhaseState(),
):
    # Default does nothing unless pkg.PATCHES is set
    if pkg.PATCHES or "src_prepare" in pkg.FUNCTIONS:
        permissions = Permissions(
            rw_paths=[build_dir], global_read=True, network=False, tmp=state.T
        )
        _sandbox_execute_pybuild(
            pkg.FILE,
            "prepare",
            permissions,
            save_state=True,
            init=state.__dict__,
            curdir=curdir or build_dir,
        )


def src_install(
    pkg: Pybuild,
    build_dir: str,
    curdir: Optional[str] = None,
    state: PhaseState = PhaseState(),
):
    permissions = Permissions(
        rw_paths=[build_dir], global_read=True, network=False, tmp=state.T
    )
    _sandbox_execute_pybuild(
        pkg.FILE,
        "install",
        permissions,
        save_state=True,
        init=state.__dict__,
        curdir=curdir or build_dir,
    )


def pkg_postinst(
    pkg: Pybuild, final_install: str, curdir: str, state: PhaseState = PhaseState()
):
    # Default does nothing
    if "pkg_postinst" in pkg.FUNCTIONS:
        permissions = Permissions(
            rw_paths=[final_install],
            global_read=True,
            network=False,
            tmp=state.T,
        )
        _sandbox_execute_pybuild(
            pkg.FILE,
            "postinst",
            permissions,
            save_state=True,
            init=state.__dict__,
            curdir=curdir,
        )


def pkg_prerm(pkg: InstalledPybuild, root: str, state: PhaseState = PhaseState()):
    # Default does nothing
    if "pkg_prerm" in pkg.FUNCTIONS:
        permissions = Permissions(
            rw_paths=[root], global_read=True, network=False, tmp=state.T
        )
        _sandbox_execute_pybuild(
            pkg.FILE,
            "prerm",
            permissions,
            save_state=False,
            init=state.__dict__,
            curdir=root,
        )
    for path, _ in pkg.get_contents().entries.items():
        if path.endswith(".pmodule"):
            try:
                module_prerm(os.path.join(root, path))
            except Exception as e:
                error(e)


def remove_pkg(pkg: InstalledPybuild, reinstall: bool = False):
    """
    Removes the given mod

    args:
        reinstall: if true, don't touch the installed DB since we'll
                   need it to finish the install
    """
    print(">>> " + l10n("pkg-removing", atom=green(pkg.ATOM.CPF)))

    BUILD_DIR = os.path.join(env.TMP_DIR, pkg.CATEGORY, pkg.P)
    state = PhaseState(BUILD_DIR)
    assert state.T

    state.USE = pkg.INSTALLED_USE
    os.makedirs(state.T, exist_ok=True)

    state.ROOT = env.prefix().ROOT
    pkg_prerm(pkg, state.ROOT, state)
    del state.ROOT

    for path, entry in pkg.get_contents().entries.items():
        # If file on disk matches the one in the manifest, remove it.
        # Otherwise, warn the user and leave it as-is
        fullpath = os.path.join(env.prefix().ROOT, path)
        if os.path.exists(fullpath):
            realentry = ManifestEntry.from_path(FileType.MISC, fullpath, path)
            if realentry == entry:
                os.remove(fullpath)
                if os.path.exists(fullpath + ".orig"):
                    info(l10n("restoring-file-backup", path=fullpath + ".orig"))
                    os.rename(fullpath + ".orig", fullpath)
                # Remove the parent directory. If it is non-empty, this will fail.
                try:
                    os.removedirs(os.path.dirname(fullpath))
                except OSError:
                    pass
            else:
                warning(l10n("package-remove-file-conflict", path=path))

    db_path = os.path.join(env.prefix().INSTALLED_DB, pkg.CATEGORY, pkg.PN)
    if os.path.exists(db_path) and not reinstall:
        with VDB() as vdb:
            # Remove and stage changes
            vdb.git.rm(os.path.join(pkg.CATEGORY, pkg.PN), r=True, f=True)
            # Clean up unstaged files (e.g. pycache)
            shutil.rmtree(db_path, ignore_errors=True, onerror=onerror)
            clear_cache_for_path(os.path.join(db_path, os.path.basename(pkg.FILE)))

    # Remove from pybuild cache
    path = os.path.join(env.prefix().PYBUILD_INSTALLED_CACHE, pkg.CATEGORY, pkg.PF)
    if os.path.exists(path):
        os.remove(path)

    # Cleanup archive dir in case vfs had to extract anything
    _cleanup_tmp_archive_dir()

    print(">>> " + l10n("pkg-finished-removing", atom=green(pkg.ATOM.CPF)))
    clear_install_cache()


def install_pkg(mod: Pybuild, use_flags: Set[str]):
    print(">>> " + l10n("pkg-installing", atom=green(mod.ATOM.CPF)))
    old_curdir = os.getcwd()
    sources = download_mod(mod, use_flags)
    if sources is None:
        error(">>> " + l10n("pkg-unable-to-download", atom=green(mod.ATOM.CPF)))
        return False

    BUILD_DIR = os.path.join(env.TMP_DIR, mod.CATEGORY, mod.P)
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, onerror=onerror)
    state = PhaseState(BUILD_DIR)
    assert state.T
    state.A = [source.as_source() for source in sources]
    state.USE = use_flags

    # Ensure build directory is clean
    if os.path.exists(BUILD_DIR):
        shutil.rmtree(BUILD_DIR, onerror=onerror)

    state.WORKDIR = os.path.join(BUILD_DIR, "work")
    # copy files from filesdir into BUILD_DIR/files so that they are accessible
    # from within the sandbox
    FILESDIR = os.path.join(os.path.dirname(mod.FILE), "files")
    state.FILESDIR = os.path.join(BUILD_DIR, "files")
    if os.path.exists(FILESDIR):
        shutil.copytree(FILESDIR, state.FILESDIR)
    os.makedirs(state.WORKDIR, exist_ok=True)
    os.makedirs(state.T, exist_ok=True)

    state.ROOT = env.prefix().ROOT

    info(">>> " + l10n("pkg-unpacking"))
    # Network access is allowed exclusively during src_unpack, and
    # adds additional filesystem restrictions to the sandbox
    src_unpack(mod, BUILD_DIR, state.WORKDIR, state)

    default_basepath = mod.S or mod.get_default_source_basename()
    state.S = default_basepath or mod.P

    if default_basepath and os.path.exists(
        os.path.join(state.WORKDIR, default_basepath)
    ):
        WORKDIR = os.path.join(state.WORKDIR, default_basepath)
    else:
        WORKDIR = state.WORKDIR

    info(">>> " + l10n("pkg-preparing", dir=WORKDIR))

    src_prepare(mod, BUILD_DIR, WORKDIR, state)

    info(">>> " + l10n("pkg-prepared"))

    final_install = env.prefix().ROOT
    os.makedirs(final_install, exist_ok=True)

    state.D = os.path.join(BUILD_DIR, "image")
    os.makedirs(state.D, exist_ok=True)
    info(">>> " + l10n("pkg-installing-into", dir=state.D, atom=green(mod.ATOM.CPF)))
    src_install(mod, BUILD_DIR, WORKDIR, state)
    info(">>> " + l10n("pkg-installed-into", dir=state.D, atom=green(mod.ATOM.CPF)))

    os.chdir(env.TMP_DIR)

    if os.path.islink(state.D):
        installed_size = 0.0
    else:
        installed_size = get_tree_size(state.D) / 1024 / 1024

    build_size = get_tree_size(WORKDIR) / 1024 / 1024

    info("")
    info(f' {green("*")} ' + l10n("pkg-final-size-build", size=build_size))
    info(f' {green("*")} ' + l10n("pkg-final-size-installed", size=installed_size))
    info("")

    case_sensitive = not get_config().get("CASE_INSENSITIVE_FILES", False)
    old_pkg = load_installed_pkg(Atom(mod.CPN))

    info(">>> Checking for conflicts...")
    for (src, dst) in _iter_files_to_patch(
        state.D,
        final_install,
        case_sensitive=case_sensitive,
    ):
        if is_parent(dst, env.prefix().VARIABLE_DATA):
            raise PermissionError(
                l10n("local-dir-reserved", dir=env.prefix().VARIABLE_DATA)
            )

        relative_path = os.path.normpath(os.path.relpath(dst, final_install))
        if (case_sensitive and os.path.exists(dst)) or (
            not case_sensitive and ci_exists(relative_path, prefix=env.prefix().ROOT)
        ):
            # Check if another package owns this file. If so, abort.
            conflict_pkg = belongs(relative_path, case_sensitive)
            if conflict_pkg and conflict_pkg != old_pkg:
                raise FileExistsError(
                    l10n(
                        "pkg-install-conflicting-file",
                        file=relative_path,
                        pkg=mod,
                        conflict_pkg=conflict_pkg,
                    )
                )

    # If a previous version of this mod was already installed,
    # remove it before doing the final copy
    db_path = os.path.join(env.prefix().INSTALLED_DB, mod.CATEGORY, mod.PN)
    if old_pkg:
        remove_pkg(old_pkg, os.path.exists(db_path) and mod.INSTALLED)

    info(
        ">>> "
        + l10n("pkg-installing-into", dir=final_install, atom=green(mod.ATOM.CPF))
    )

    contents_manifest = Manifest()

    overwrite_all = False

    for (src, dst) in _iter_files_to_patch(
        state.D,
        final_install,
        case_sensitive=not get_config().get("CASE_INSENSITIVE_FILES", False),
    ):
        relative_path = os.path.normpath(os.path.relpath(dst, final_install))
        contents_manifest.add_entry(
            ManifestEntry.from_path(FileType.MISC, src.path, relative_path)
        )
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        try:
            _patch_file(src, dst, overwrite=False)
        except FileExistsError:
            # If not, prompt user to overwrite
            if env.INTERACTIVE and not overwrite_all:
                result = prompt_options(
                    l10n("pkg-file-conflict-prompt", file=relative_path),
                    [
                        (l10n("yes-short"), l10n("overwrite")),
                        (l10n("no-short"), l10n("dont-overwrite")),
                        (l10n("always-short"), l10n("always-overwrite")),
                    ],
                )
            else:
                result = l10n("yes-short")

            if result == l10n("always-short"):
                overwrite_all = True

            if result in (l10n("yes-short"), l10n("always-short")) or overwrite_all:
                preserved = dst + ".orig"
                info(l10n("pkg-file-conflict-overwrite", file=dst, preserved=preserved))
                os.rename(dst, preserved)
                _patch_file(src, dst, overwrite=True, move_function=shutil.copy2)

    state.ROOT = final_install
    pkg_postinst(mod, final_install, state.ROOT, state)

    # If installed database exists and there is no old mod, remove it
    if os.path.exists(db_path) and not old_pkg:
        shutil.rmtree(db_path, onerror=onerror)

    with VDB() as vdb:
        # Update db entry for installed mod
        os.makedirs(db_path, exist_ok=True)

        # Write CONTENTS
        contents_manifest.write(os.path.join(db_path, "CONTENTS"))

        # Copy pybuild to DB
        # unless source pybuild is in DB (i.e we're reinstalling)
        if not mod.FILE.startswith(db_path):
            shutil.copy(mod.FILE, db_path)
        vdb.git.add(os.path.join(mod.CATEGORY, mod.PN, os.path.basename(mod.FILE)))

        manifest_path = os.path.join(os.path.dirname(mod.FILE), "Manifest")
        if os.path.exists(manifest_path):
            # Copy Manifest to DB
            if not mod.FILE.startswith(db_path):
                shutil.copy(manifest_path, db_path)
            vdb.git.add(os.path.join(mod.CATEGORY, mod.PN, "Manifest"))

        def add_installed(field: str, value: str):
            with open(os.path.join(db_path, field), "w") as use:
                print(value, file=use)
            vdb.git.add(os.path.join(mod.CATEGORY, mod.PN, field))

        # Copy installed use configuration to DB
        # Note: mod.get_use() may not be valid, as mod may be
        # an InstalledPybuild and we want to use the new configuration,
        # not the old one.
        add_installed("USE", " ".join(state.USE))
        # Copy repo pybuild was from to DB
        add_installed("REPO", mod.REPO)

        def fix_common(depstring: str):
            """
            Adds operator to dependencies in the common category
            to ensure this package is rebuilt if they change.
            """
            deps = depstring.split()
            for index, dep in enumerate(deps):
                if dep.startswith("common/"):
                    pkg = load_installed_pkg(Atom(dep))
                    # Note tilde operator. Revision bumps to
                    # common packages won't cause rebuilds.
                    if pkg:
                        deps[index] = f"~{dep}-{pkg.PV}"
            return " ".join(deps)

        # Store installed dependencies
        add_installed("DEPEND", fix_common(mod.DEPEND))

        # Copy pybuild environment to DB
        shutil.copy(
            os.path.join(_state_path(mod.FILE), "environment.xz"),
            os.path.join(db_path, "environment.xz"),
        )
        _delete_state(mod.FILE)
        vdb.git.add(os.path.join(mod.CATEGORY, mod.PN, "environment.xz"))

        path = os.path.join(db_path, "environment.xz")
        if os.path.exists(path):
            compressed_environment = lzma.LZMAFile(path)
            try:
                environment = json.load(compressed_environment)
            except EOFError as e:
                raise RuntimeError(f"Failed to read {path}") from e

            if "REBUILD_FILES" in environment and environment["REBUILD_FILES"]:
                manifest = Manifest()
                for entry in get_rebuild_manifest(environment["REBUILD_FILES"]):
                    manifest.add_entry(entry)
                manifest.write(os.path.join(db_path, "REBUILD_FILES"))

        clear_cache_for_path(os.path.join(db_path, os.path.basename(mod.FILE)))

        os.chdir(old_curdir)
        print(">>> " + l10n("pkg-installed", atom=green(mod.ATOM.CPF)))
        info("")

        if not env.DEBUG:
            shutil.rmtree(BUILD_DIR, onerror=onerror)
            # Cleanup archive dir in case vfs had to extract anything
            _cleanup_tmp_archive_dir()
            info(">>> " + l10n("cleaned-up", dir=BUILD_DIR))

        clear_install_cache()
        return True
