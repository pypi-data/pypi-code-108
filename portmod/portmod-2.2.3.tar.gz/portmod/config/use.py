# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3

import os
import re
import sys
from logging import info, warning
from typing import (
    Callable,
    Dict,
    Generator,
    Mapping,
    Optional,
    Sequence,
    Set,
    Tuple,
    cast,
)

from portmod.functools import install_cache, prefix_aware_cache
from portmod.globals import env
from portmod.parsers.flags import add_flag, collapse_flags, get_flags, remove_flag
from portmod.pybuild import Pybuild
from portmod.repo import get_repo
from portmod.repo.metadata import get_use_flag_atom_aliases
from portmodlib.atom import Atom, QualifiedAtom
from portmodlib.l10n import l10n
from portmodlib.usestr import use_reduce

from . import get_config, read_config, set_config_value
from .profiles import profile_parents
from .textures import select_texture_size


class InvalidFlag(Exception):
    """Exception indicating an invalid use flag"""

    def __init__(self, flag: str, atom: Optional[Atom] = None):
        if atom:
            super().__init__(l10n("invalid-flag-atom", flag=flag, atom=atom))
        else:
            super().__init__(l10n("invalid-flag", flag=flag))


@prefix_aware_cache
def _get_use_defaults(
    pkg: Pybuild, is_installed: Optional[Callable[[QualifiedAtom], bool]] = None
) -> Set:
    """
    Returns a set of USE flags, each prepended with a plus, minus, or nothing,
    """

    from portmod.loader import load_installed_pkg

    if is_installed is None:

        def is_installed(atom):
            pkg = load_installed_pkg(atom)
            if pkg is not None:
                if atom.USE <= pkg.INSTALLED_USE:
                    return True
            return False

    assert is_installed is not None

    defaults: Set[str] = set()

    # Default values in IUSE have the lowest priority
    for x in pkg.IUSE:
        if x.startswith("+"):
            defaults.add(x[1:])
        else:
            defaults.add("-" + x)

    # Aliases override the default value provided in IUSE,
    # Unless they are prototypical aliases
    #   E.g. pkg "cat/foo" where "bar" is aliased to "cat/foo[bar]"
    aliases: Mapping[str, QualifiedAtom] = {}
    if "local" not in pkg.PROPERTIES:
        aliases = get_use_flag_atom_aliases(get_repo(pkg.REPO).location)
    aliased_flags = set()
    for flag in pkg.IUSE_EFFECTIVE:
        if (
            flag in aliases
            and is_installed(aliases[flag])
            and aliases[flag].CPN != pkg.CPN
        ):
            aliased_flags.add(flag)
    return collapse_flags(defaults, aliased_flags)


@prefix_aware_cache
def get_use_defaults(pkg: Pybuild) -> Dict[str, bool]:
    """
    Returns a dictionary containing the default states of the
    given Pybuild's USE flags.
    """

    default_flags = _get_use_defaults(pkg)
    defaults_dict: Dict[str, bool] = {}

    # Default values in IUSE have the lowest priority
    for flag in default_flags:
        if flag.startswith("+"):
            defaults_dict[flag[1:]] = True
        elif flag.startswith("-"):
            defaults_dict[flag[1:]] = False
        else:
            defaults_dict[flag] = False

    return defaults_dict


@install_cache
def get_use(
    pkg: Pybuild, is_installed: Optional[Callable[[QualifiedAtom], bool]] = None
) -> Tuple[Set[str], Set[str]]:
    """
    Returns a list of enabled and a list of disabled use flags

    The disabled flag list only contains the flags which have been explicitly disabled.
    Any flags missing from both lists should be considered implicitly disabled.
    """

    defaults = _get_use_defaults(pkg, is_installed)

    GLOBAL_USE = get_config().get("USE", [])
    use: Set[str] = get_use_expand_flags()
    use = collapse_flags(use, GLOBAL_USE)
    for parent_dir in profile_parents():
        for use_file in _iter_files(parent_dir, "package", "use"):
            flags = get_flags(use_file, pkg.ATOM)
            use = collapse_flags(use, flags)

    # User config is the last added, overriding profile flags
    use = collapse_flags(use, get_user_use(pkg.ATOM))

    # Finally, apply environment variables (technically, we do this twice,
    # as GLOBAL_USE also includes these, but we need to apply them again to
    # ensure they override
    use = collapse_flags(use, os.environ.get("USE", []))

    # Forced use flags must be collapsed last to ensure that the
    # forced flags override any other values
    use = collapse_flags(use, get_forced_use(pkg.ATOM))

    enabled_use = {x for x in use if not x.startswith("-")}
    disabled_use = {x.lstrip("-") for x in use if x.startswith("-")}

    enabled_use |= {
        x for x in defaults if not x.startswith("-") and x not in disabled_use
    }

    enabled_use = enabled_use.intersection(pkg.IUSE_EFFECTIVE)
    disabled_use = disabled_use.intersection(pkg.IUSE_EFFECTIVE)

    texture_sizes = use_reduce(
        pkg.TEXTURE_SIZES, enabled_use, disabled_use, token_class=int
    )
    texture_size = select_texture_size(texture_sizes)
    if texture_size is not None:
        found = None
        for useflag in enabled_use:
            if useflag.startswith("texture_size_"):
                if not found:
                    found = useflag
                elif useflag != found:
                    raise Exception(
                        l10n(
                            "multiple-texture-flags",
                            flag1=use,
                            flag2=found,
                            atom=pkg.ATOM,
                        )
                    )
        enabled_use.add(found or "texture_size_{}".format(texture_size))

    return (enabled_use, disabled_use)


def get_use_expand_flags() -> Set[str]:
    """Returns all currently enabled USE_EXPAND flags"""
    flags = set()
    for use in get_config().get("USE_EXPAND", []):
        if not use.startswith("-"):
            for flag in get_config().get(use, "").split():
                flags.add(f"{use.lower()}_{flag}")
    return flags


def get_use_expand(pkg: Pybuild, use_expand: str) -> Tuple[Set[str], Set[str]]:
    """
    Returns the set of enabled flags for the given package and USE_EXPAND category
    """
    flags = {
        re.sub(f"^{use_expand.lower()}_", "", flag)
        for flag in pkg.IUSE_EFFECTIVE
        if flag.startswith(f"{use_expand.lower()}_")
    }
    enabled_use = pkg.get_use()
    enabled_expand = {
        re.sub(f"^{use_expand}_", "", val, flags=re.IGNORECASE)
        for val in enabled_use
        if val.startswith(use_expand.lower() + "_")
    }

    return enabled_expand, flags - enabled_expand


@prefix_aware_cache
def get_user_global_use() -> Set[str]:
    """Returns user-specified global use flags"""
    global_use = cast(
        Set[str], read_config(env.prefix().CONFIG, {}, user=True).get("USE", set())
    )

    # Also return global user-set USE_EXPAND values
    for use in get_config().get("USE_EXPAND", []):
        values = set(
            read_config(env.prefix().CONFIG, {}, user=True).get(use, "").split()
        )
        flags = {use.lower() + "_" + value for value in values}
        global_use |= flags

    return global_use


@prefix_aware_cache
def get_user_use(atom: Atom) -> Set[str]:
    """Returns user-specified use flags for a given mod"""
    use_file = os.path.join(env.prefix().CONFIG_DIR, "package.use")
    if os.path.exists(use_file):
        return get_flags(use_file, atom)

    return set()


def _iter_files(
    directory: str, basename: Optional[str], suffix: str
) -> Generator[str, None, None]:
    if basename:
        paths = [
            ".".join([basename, suffix]),
            ".".join([basename, sys.platform, suffix]),
        ]
    else:
        paths = [".".join([suffix]), ".".join([sys.platform, suffix])]

    for path in paths:
        path = os.path.join(directory, path)
        if os.path.exists(path):
            yield path


@prefix_aware_cache
def get_forced_use(atom: Atom) -> Set[str]:
    """Returns a list of forced use flags for the given mod"""
    force: Set[str] = set()
    for parent_dir in profile_parents():
        for force_file in _iter_files(parent_dir, None, "use.force"):
            flags = get_flags(force_file)
            force = collapse_flags(force, flags)

        for pkg_force_file in _iter_files(parent_dir, "package", "use.force"):
            flags = get_flags(pkg_force_file, atom)
            force = collapse_flags(force, flags)

    return force


def verify_use(flag: str, atom: Optional[Atom] = None) -> bool:
    """
    Verifies that the given flag is valid

    args:
        flag: Flag to be added
        atom: If present, checks for local use flags relevant to this atom.
              Otherwise, global use flags will be considered
    returns:
        Whether or not the use flag is valid given either the atom passed,
        or the global context
    """
    from portmod.repo.metadata import get_global_use

    from ..loader import load_pkg

    if atom:
        return any(flag in mod.IUSE_EFFECTIVE for mod in load_pkg(atom))
    else:
        return flag in [
            flag
            for repo in env.prefix().REPOS
            for flag in get_global_use(repo.location)
        ]


def add_use(
    flag: str,
    atom: Optional[Atom] = None,
    disable: bool = False,
    comment: Sequence[str] = (),
):
    """
    Adds the given use flag to the user's configuration

    Args:
        flag: Flag to be added
        atom: If present, the flag will only apply to this package
        disable: If True, the flag is added in its disabled form (prefixed with "-")
    """
    from portmod.loader import load_pkg

    if disable and flag in get_config().get("USE", []):
        remove_use(flag, atom)

    disableflag = "-" + flag

    if (disable and flag in get_config().get("USE", [])) or (
        not disable and disableflag in get_config().get("USE", [])
    ):
        remove_use(flag, atom)

    if not verify_use(flag, atom):
        if atom:
            raise InvalidFlag(flag, atom)
        else:
            raise InvalidFlag(flag)
        return

    if atom is not None:
        from portmod.util import select_package

        (newest, req) = select_package(load_pkg(atom))
        if flag not in newest.IUSE_EFFECTIVE:
            warning(
                l10n(
                    "invalid-use-flag-warning", flag=flag, atom1=newest.ATOM, atom2=atom
                )
            )

    if atom:
        use_file = os.path.join(env.prefix().CONFIG_DIR, "package.use")
        if comment:
            with open(use_file, "a+") as file:
                for line in comment:
                    print(line, file=file)
                if disable:
                    print(atom, disableflag, file=file)
                else:
                    print(atom, flag, file=file)
            info(l10n("flag-add", flag=flag, atom=atom, file=use_file))
        else:
            if disable:
                remove_flag(use_file, atom, flag)
                add_flag(use_file, atom, disableflag)
            else:
                remove_flag(use_file, atom, disableflag)
                add_flag(use_file, atom, flag)
        get_user_use.cache_clear()
    else:
        GLOBAL_USE = get_config()["USE"]

        if (not disable and flag not in GLOBAL_USE) or (
            disable and disableflag not in GLOBAL_USE
        ):
            if disable:
                info(l10n("adding-use-flag", flag="-" + flag))
                GLOBAL_USE.add(disableflag)
            else:
                info(l10n("adding-use-flag", flag=flag))
                GLOBAL_USE.add(flag)

            set_config_value("USE", " ".join(sorted(GLOBAL_USE)))
            get_user_global_use.cache_clear()
        else:
            if disable:
                warning(l10n("global-use-flag-already-disabled", flag=flag))
            else:
                warning(l10n("global-use-flag-already-enabled", flag=flag))
    get_use.cache_clear()


def remove_use(flag: str, atom: Optional[Atom] = None):
    """
    Removes the given use flag from the user's configuration

    This will remove both enabled and disabled flags

    Args:
        flag: Flag to be removed
        atom: If present, the flag will only be removed from configuration specifically
              affecting this package atom
    """

    disableflag = "-" + flag

    if not verify_use(flag, atom):
        warning(l10n("invalid-flag-atom", flag=flag, atom=atom))

    if atom is not None:
        use_file = os.path.join(env.prefix().CONFIG_DIR, "package.use")
        remove_flag(use_file, atom, flag)
        remove_flag(use_file, atom, disableflag)
        get_user_use.cache_clear()
    else:
        GLOBAL_USE = get_config()["USE"]

        if flag in GLOBAL_USE or disableflag in GLOBAL_USE:
            if flag in GLOBAL_USE:
                info(l10n("removing-use-flag", flag=flag))
                GLOBAL_USE.remove(flag)

            if disableflag in GLOBAL_USE:
                info(l10n("removing-use-flag", flag="-" + flag))
                GLOBAL_USE.remove(disableflag)

            set_config_value("USE", " ".join(sorted(GLOBAL_USE)))
            get_user_global_use.cache_clear()
        else:
            warning(l10n("flag-not-set-globally", flag=flag))
    get_use.cache_clear()
