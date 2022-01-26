# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import io
import logging
import os
import shutil
from logging import error, info, warning
from typing import Dict, Iterable, Optional

from portmodlib.atom import Atom, QualifiedAtom, atom_sat
from portmodlib.colour import bright, green, lblue, lgreen, red, yellow
from portmodlib.l10n import l10n

from ._deps import resolve
from .config import get_config
from .config.profiles import get_system
from .config.sets import BUILTIN_SETS, add_set, get_set, remove_set
from .config.use import add_use
from .download import fetchable, find_download, is_downloaded
from .globals import env
from .loader import (
    AmbiguousAtom,
    _sandbox_execute_pybuild,
    load_all_installed,
    load_installed_pkg,
    load_pkg,
    load_pkg_fq,
)
from .modules import clear_module_updates, require_module_updates, update_modules
from .package import install_pkg, remove_pkg
from .perms import Permissions
from .prompt import prompt_bool
from .query import FlagDesc, LocalFlagDesc, get_flag_desc
from .rebuild import get_rebuild_manifest
from .repo.keywords import add_keyword
from .repo.loader import commit_moved
from .transactions import (
    Delete,
    New,
    Transactions,
    UseDep,
    generate_transactions,
    print_transactions,
    sort_transactions,
)
from .tsort import CycleException
from .util import KeywordDep, LicenseDep, select_package
from .vfs import clear_vfs_sort, require_vfs_sort, sort_vfs, vfs_needs_sorting


def global_prepare():
    """Performs global system changes which must be done prior to changes"""
    commit_moved()


def global_updates():
    """Performs updates to global configuration"""
    # Fix vfs ordering and update modules

    try:
        sort_vfs()
        clear_vfs_sort()
    except CycleException as e:
        error(f"{e}")

    update_modules()
    clear_module_updates()


def deselect(pkgs: Iterable[str], *, no_confirm: bool = False):
    all_to_remove = []

    for name in pkgs:
        atom = Atom(name)
        to_remove = []
        for mod in get_set("selected-packages"):
            if atom_sat(mod, atom):
                to_remove.append(mod)

        if len(to_remove) == 1:
            info(">>> " + l10n("remove-from-world", atom=green(to_remove[0])))
            all_to_remove.append(to_remove[0])
        elif len(to_remove) > 1:
            raise AmbiguousAtom(atom, to_remove)

    if not all_to_remove:
        print(">>> " + l10n("no-matching-world-atom"))
        return

    if no_confirm or prompt_bool(bright(l10n("remove-from-world-qn"))):
        for mod in all_to_remove:
            remove_set("selected-packages", mod)


def _update_configuration(
    keyword_changes: Iterable[KeywordDep],
    license_changes: Iterable[LicenseDep],
    use_changes: Iterable[UseDep],
    *,
    no_confirm: bool,
):
    if keyword_changes:
        for keyword in keyword_changes:
            if keyword.masked:
                error(
                    l10n(
                        "package-masked-keyword",
                        atom=keyword.atom.CPN,
                        arch=env.prefix().ARCH,
                    )
                )
                return

        print(l10n("necessary-keyword-changes"))
        for keyword in keyword_changes:
            if keyword.keyword.startswith("*"):
                c = red
            else:
                c = yellow
            print("    {} {}".format(green(keyword.atom), c(keyword.keyword)))

        if no_confirm or prompt_bool(l10n("apply-changes-qn")):
            for keyword in keyword_changes:
                add_keyword(keyword.atom, keyword.keyword)
        else:
            return

    if license_changes:
        # TODO: For EULA licenses, display the license and prompt the user to accept
        print(l10n("necessary-license-changes"))
        for license in license_changes:
            print("    {} {}".format(green(license.atom), license.license))
        return

    if use_changes:
        display_flags: Dict[str, FlagDesc] = {}
        for use in use_changes:
            flag = use.flag.lstrip("-")
            desc = get_flag_desc(load_pkg_fq(use.atom), flag)
            if isinstance(desc, LocalFlagDesc):
                display_flags[Atom(desc.pkg.ATOM.CPF).use(flag)] = desc
            else:
                display_flags[flag] = desc or FlagDesc("<missing description>")

        for key, value in display_flags.items():
            print(l10n("use-flag-desc", desc=value, flag=bright(lgreen(key))))

        print()
        print(l10n("necessary-flag-changes"))
        for use in use_changes:
            comment = "\n    ".join(use.comment)
            if comment:
                comment += "\n    "
            if use.flag.startswith("-") and use.oldvalue == use.flag.lstrip("-"):
                print(
                    "   {}{} {} # {}".format(
                        comment,
                        lblue(use.atom.CPF),
                        red(use.flag),
                        l10n("enabled-comment"),
                    )
                )
            elif not use.flag.startswith("-") and use.oldvalue == "-" + use.flag:
                print(
                    "    {}{} {} # {}".format(
                        comment,
                        green(use.atom.CPF),
                        red(use.flag),
                        l10n("disabled-comment"),
                    )
                )
            else:
                print("    {}{} {}".format(comment, green(use.atom.CPF), red(use.flag)))
        if no_confirm or prompt_bool(l10n("apply-changes-qn")):
            for use in use_changes:
                add_use(
                    use.flag.lstrip("-"),
                    Atom(use.atom.CPF),
                    use.flag.startswith("-"),
                    use.comment,
                )
        else:
            return


def configure(
    atoms: Iterable[str],
    *,
    delete: bool = False,
    depclean: bool = False,
    auto_depclean: bool = False,
    no_confirm: bool = False,
    oneshot: bool = False,
    verbose: bool = False,
    update: bool = False,
    nodeps: bool = False,
    deselect: Optional[bool] = None,
    select: Optional[bool] = None,
    deep: bool = False,
    emptytree: bool = False,
):
    global_prepare()
    # Slow import
    import git

    # Ensure that we always get the config before performing operations on packages
    # This way the config settings will be available as environment variables.
    get_config()

    targetlist = list(atoms)
    for modstr in targetlist:
        if modstr.startswith("@"):
            # Atom is actually a set. Load set instead
            targetlist.extend(get_set(modstr.replace("@", "")))
            continue

    to_remove = set()
    if delete or depclean:
        for modstr in targetlist:
            if modstr.startswith("@"):
                continue

            skip = False
            atom = Atom(modstr)
            for system_atom in get_system():
                if atom_sat(system_atom, atom):
                    warning(l10n("skipping-system-package", atom=system_atom))
                    skip = True
                    break

            if not skip:
                to_remove.add(atom)

    atomlist = [
        Atom(modstr)
        for modstr in targetlist
        if modstr not in to_remove and not modstr.startswith("@")
    ]

    selected = set(Atom(atom) for atom in atoms if not atom.startswith("@"))
    selected_sets = set(atom[1:] for atom in atoms if atom.startswith("@"))

    explicit = set(selected)
    for selected_set in selected_sets:
        explicit |= get_set(selected_set)

    if delete:
        # Do nothing. We don't care about deps
        transactions = Transactions()
        for atom in to_remove:
            ipkg = load_installed_pkg(atom)
            if not ipkg:
                raise Exception(l10n("not-installed", atom=atom))
            transactions.append(Delete(ipkg))
    elif nodeps:
        fqatoms = []
        enabled_flags = {}
        usedeps = []
        for atom in atomlist:
            pkg, _ = select_package(load_pkg(atom))
            fqatoms.append(pkg.ATOM)
            enabled_flags[pkg.ATOM] = pkg.get_use()
            for flag in atom.USE:
                usedeps.append(
                    UseDep(
                        pkg.ATOM,
                        flag,
                        None,
                        ["# Use requirement passed on command line"],
                    )
                )
                if flag.startswith("-"):
                    enabled_flags[pkg.ATOM].remove(flag.lstrip("-"))
                else:
                    enabled_flags[pkg.ATOM].add(flag)

        selected_cpn = set()
        for atom in selected:
            pkg, _ = select_package(load_pkg(atom))
            selected_cpn.add(QualifiedAtom(pkg.CPN))

        transactions = generate_transactions(
            fqatoms,
            [],
            set() if oneshot or depclean else selected_cpn,
            usedeps,
            enabled_flags,
            update=update,
            emptytree=emptytree,
        )
    else:
        transactions = resolve(
            atomlist,
            to_remove,
            explicit,
            set() if oneshot or depclean else selected,
            set() if oneshot or depclean else selected_sets,
            deep=deep
            or (depclean and not to_remove),  # No argument depclean implies deep
            update=update,
            depclean=auto_depclean or depclean,
            emptytree=emptytree,
        )

    transactions = sort_transactions(transactions)

    # Inform user of changes
    if transactions.pkgs:
        # Don't print transaction list when in quiet mode and no-confirm is passed
        if not no_confirm or logging.root.level < logging.WARN:
            if delete or depclean:
                print(l10n("to-remove"))
            else:
                print(l10n("to-install"))
            print_transactions(transactions, verbose=verbose)
            print()
    elif vfs_needs_sorting() and not transactions.pkgs:
        global_updates()
        info(l10n("nothing-else-to-do"))
        return
    elif not transactions.pkgs:
        info(l10n("nothing-to-do"))
        return

    if transactions.config:
        keyword_changes = list(
            filter(lambda x: isinstance(x, KeywordDep), transactions.config)
        )
        license_changes = list(
            filter(lambda x: isinstance(x, LicenseDep), transactions.config)
        )
        use_changes = list(filter(lambda x: isinstance(x, UseDep), transactions.config))
        _update_configuration(
            keyword_changes, license_changes, use_changes, no_confirm=no_confirm
        )

    # Create a temporary VDB so that common packages needed for pkg_nofetch and pkg_pretend
    # but that haven't yet been installed can be found by the loader
    if os.path.exists(env.TMP_VDB):
        shutil.rmtree(env.TMP_VDB)
    for trans in transactions.pkgs:
        if isinstance(trans, New) and trans.pkg.CATEGORY == "common":
            os.makedirs(os.path.join(env.TMP_VDB, "common", trans.pkg.PN))
            shutil.copy2(
                trans.pkg.FILE, os.path.join(env.TMP_VDB, "common", trans.pkg.PN)
            )

    def print_restricted_fetch(transactions: Transactions):
        # Check for restricted fetch packages and print their nofetch notices
        for trans in transactions.pkgs:
            if not isinstance(trans, Delete):
                can_fetch = fetchable(trans.pkg, trans.flags)
                sources = trans.pkg.get_sources(trans.flags)
                to_fetch = [
                    source for source in sources if find_download(source) is None
                ]
                if set(to_fetch) - set(can_fetch) and not is_downloaded(
                    trans.pkg, trans.flags
                ):
                    print(
                        bright(yellow(l10n("fetch-instructions", atom=trans.pkg.ATOM)))
                    )
                    state = {
                        "UNFETCHED": to_fetch,
                        "A": sources,
                        "USE": trans.pkg.get_use(),
                    }
                    _sandbox_execute_pybuild(
                        trans.pkg.FILE,
                        "nofetch",
                        Permissions(),
                        init=state,
                    )
                    print()

    print_restricted_fetch(transactions)

    tmp_dir = env.TMP_DIR
    # If TMP_DIR doesn't exist, either use the parent, or if that doesn't exist,
    # just create it
    if not os.path.exists(env.TMP_DIR):
        if os.path.exists(os.path.dirname(env.TMP_DIR)):
            tmp_dir = os.path.dirname(env.TMP_DIR)
        else:
            os.makedirs(tmp_dir, exist_ok=True)
    tmp_space = shutil.disk_usage(tmp_dir).free

    for trans in transactions.pkgs:
        if not isinstance(trans, Delete) and "pkg_pretend" in trans.pkg.FUNCTIONS:
            info(">>> " + l10n("pkg-pretend", atom=green(trans.pkg.ATOM.CPF)))
            # TODO: There are various variables that should be set on mod during pkg_pretend
            _sandbox_execute_pybuild(
                trans.pkg.FILE,
                "pretend",
                Permissions(),
                save_state=True,
                init={"USE": trans.flags},
            )

            total_size = 0
            for source in trans.pkg.get_sources(trans.flags):
                total_size += source.size

            # We assume that files have a compression ratio of approximately 0.5
            # Thus we want at least twice the size of the archives in free space.
            if total_size * 2 > tmp_space:
                warning(
                    l10n(
                        "tmp-space-too-small",
                        dir=env.TMP_DIR,
                        free=tmp_space / 1024 / 1024,
                        size=total_size * 2 / 1024 / 1024,
                    )
                )

    if not (no_confirm or prompt_bool(l10n("continue-qn"))):
        return

    err = None
    merged = Transactions()
    # Install (or remove) packages in order
    for trans in transactions.pkgs:
        if isinstance(trans, Delete):
            remove_pkg(trans.pkg)
            if deselect is None or deselect:
                if trans.pkg.CPN in get_set("selected-packages"):
                    info(">>> " + l10n("remove-from-world", atom=green(trans.pkg.CPN)))
                    remove_set("selected-packages", trans.pkg.CPN)
            merged.pkgs.append(trans)
        elif install_pkg(trans.pkg, trans.flags):
            if trans.pkg in transactions.new_selected and not oneshot:
                if trans.pkg.CPN not in get_set("selected-packages"):
                    info(">>> " + l10n("add-to-world", atom=green(trans.pkg.CPN)))
                    add_set("selected-packages", trans.pkg.CPN)
            merged.pkgs.append(trans)
        else:
            # Unable to install mod. Aborting installing remaining packages
            err = trans.pkg.ATOM
            break

        require_vfs_sort()
        require_module_updates()
        sort_vfs()
        clear_vfs_sort()

    for trans in merged.pkgs:
        pkg = trans.pkg
        warning_path = os.path.join(env.WARNINGS_DIR, pkg.ATOM.CPF)
        info_path = os.path.join(env.MESSAGES_DIR, pkg.ATOM.CPF)
        messages = []
        if os.path.exists(warning_path):
            with open(warning_path, "r") as file:
                messages.append(("WARN", file.read()))

        if os.path.exists(info_path):
            with open(info_path, "r") as file:
                messages.append(("INFO", file.read()))

        if messages:
            print()
            print(">>> " + l10n("pkg-messages", atom=bright(green(pkg))))
            for typ, msg in messages:
                if typ == "WARN":
                    warning(msg)
                elif typ == "INFO":
                    info(msg)
            print()

    for set_name in selected_sets:
        if set_name not in BUILTIN_SETS:
            if deselect or delete or depclean:
                remove_set("selected-sets", Atom(set_name))
            else:
                add_set("selected-sets", Atom(set_name))

    # Commit changes to installed database
    gitrepo = git.Repo.init(env.prefix().INSTALLED_DB)
    try:
        gitrepo.head.commit
    except ValueError:
        gitrepo.git.commit(m=l10n("initial-commit"))

    transstring = io.StringIO()
    print_transactions(merged, verbose=True, out=transstring, summarize=False)
    if gitrepo.git.diff("HEAD", cached=True):
        # There was an error. We report the packages that were successfully merged and
        # note that an error occurred, however we still commit anyway.
        if err:
            gitrepo.git.commit(
                m=(
                    l10n(
                        "merge-success-and-error", num=len(transactions.pkgs), atom=err
                    )
                    + "\n"
                    + transstring.getvalue()
                )
            )
        else:
            gitrepo.git.commit(
                m=(
                    l10n("merge-success", num=len(transactions.pkgs))
                    + "\n"
                    + transstring.getvalue()
                )
            )

    # Check if packages were just modified and can be removed from the rebuild set
    # Any transaction type warrants removal, as they were either rebuilt,
    # and thus can be removed, or deleted, and no longer need to be rebuild
    for atom in get_set("rebuild"):
        installed_pkg = load_installed_pkg(atom)
        if not installed_pkg or installed_pkg.CPN in [
            trans.pkg.CPN for trans in merged.pkgs
        ]:
            remove_set("rebuild", atom)

    info(l10n("checking-rebuild"))
    # Check if packages need to be added to rebuild set
    for pkg in load_all_installed():
        if pkg.CPN not in get_set("rebuild") and pkg.INSTALLED_REBUILD_FILES:
            seen = set()
            for entry in get_rebuild_manifest(
                pkg.get_installed_env().get("REBUILD_FILES", [])
            ):
                seen.add(entry.name)
                if pkg.INSTALLED_REBUILD_FILES.get(entry.name) != entry:
                    add_set("rebuild", pkg.CPN)
                    break
            if not all(entry in seen for entry in pkg.INSTALLED_REBUILD_FILES.entries):
                add_set("rebuild", pkg.CPN)

    if get_set("rebuild"):
        warning(l10n("rebuild-message"))
        for atom in get_set("rebuild"):
            print("    {}".format(green(atom)))
        print(
            l10n(
                "rebuild-prompt",
                command=lgreen(f"portmod {env.PREFIX_NAME} merge @rebuild"),
            )
        )

    global_updates()
