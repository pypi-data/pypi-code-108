# Copyright 2019-2021 Portmod Authors
# Distributed under the terms of the GNU General Public License v3


import os
from logging import error, info
from typing import Dict, List

from portmod.config.sets import get_set
from portmod.config.use import get_use
from portmod.loader import load_all, load_all_installed, load_installed_pkg, load_pkg
from portmod.pybuild import InstalledPybuild, Pybuild
from portmod.query import (
    get_flags,
    get_maintainer_string,
    print_depgraph,
    query_depends,
)
from portmod.repo.keywords import get_unstable_flag
from portmod.repo.metadata import get_package_metadata
from portmodlib.atom import Atom
from portmodlib.colour import blue, bright, green, red
from portmodlib.l10n import l10n
from portmodlib.vfs import find_file, list_dir

from . import atom_metavar


def subcommand(*sub_args, parent):
    def decorator(func):
        parser = parent.add_parser(
            func.__name__,
            description=l10n(f"query-{func.__name__}-help"),
            help=l10n(f"query-{func.__name__}-help").strip().splitlines()[0],
        )
        for args, kwargs in sub_args:
            parser.add_argument(*args, **kwargs)
        parser.set_defaults(func=func)

    return decorator


def argument(*name_or_flags, **kwargs):
    return name_or_flags, kwargs


def add_query_parser(subparsers, parents):
    """
    Main function for omwquery executable
    """
    parser = subparsers.add_parser("query", help=l10n("query-help"), parents=parents)
    subparsers = parser.add_subparsers(title=l10n("query-subcommands-title"))
    parser.add_argument("-a", "--all", help=l10n("query-all-help"), action="store_true")

    @subcommand(
        argument(
            "targets",
            metavar=atom_metavar(sets=True),
            help=l10n("query-list-atom-help"),
            nargs="+",
        ),
        argument(
            "-r", "--remote", help=l10n("query-list-tree-help"), action="store_true"
        ),
        parent=subparsers,
    )
    def list(args):
        """List all packages matching ATOM"""
        # TODO: Wildcard support
        all_atoms: List[Atom] = []
        for atom in args.targets:
            if atom.startswith("@"):
                all_atoms.extend(get_set(atom[1:]))
            else:
                all_atoms.append(Atom(atom))

        groups: Dict[str, List[Pybuild]] = {}
        for atom in all_atoms:
            if args.remote:
                for pkg in load_pkg(atom):
                    if pkg.CP in groups:
                        groups[pkg.CP].append(pkg)
                    else:
                        groups[pkg.CP] = [pkg]
            else:
                ipkg = load_installed_pkg(atom)
                if ipkg:
                    groups[ipkg.CP] = load_pkg(ipkg.CP)

        for group in sorted(groups):
            installed = "I" if any(pkg.INSTALLED for pkg in groups[group]) else "-"
            repo = "R" if any(not pkg.INSTALLED for pkg in groups[group]) else "-"
            if args.quiet:
                print(group)
            else:
                print(f"[{installed}{repo}] {bright(green(group))}")

    @subcommand(
        argument(
            "atom",
            metavar=l10n("atom-placeholder"),
            help=l10n("query-depends-atom-help"),
        ),
        parent=subparsers,
    )
    def depends(args):
        """List all packages directly depending on ATOM"""
        print(" * These mods depend on {}:".format(bright(args.atom)))
        for mod_atom, dep_atom in query_depends(Atom(args.atom), args.all):
            if args.quiet:
                print(mod_atom)
            else:
                print("{} ({})".format(green(mod_atom), dep_atom))

    @subcommand(
        argument(
            "var", metavar=l10n("field-placeholder"), help=l10n("query-has-var-help")
        ),
        argument(
            "expr",
            metavar=l10n("value-placeholder"),
            default="",
            nargs="?",
            help=l10n("query-has-expr-help"),
        ),
        parent=subparsers,
    )
    def has(args):
        """
        List all packages matching variable.

        This can only be used to scan variables in the base Pybuild spec, not custom
        fields declared by specific Pybuilds or their superclasses.
        """
        if args.expr:
            info(
                " * "
                + l10n("query-has-searching-msg", var=args.var)
                + f" '{bright(args.expr)}'"
            )
        else:
            info(" * " + l10n("query-has-searching-msg", var=args.var))
        packages = load_all() if args.all else load_all_installed()
        for pkg in packages:
            if args.expr.lower() in getattr(pkg, args.var, "").lower():
                flags = [" ", " "]
                if pkg.INSTALLED or load_installed_pkg(Atom(pkg.ATOM.CPF)):
                    flags[0] = "I"
                flags[1] = get_unstable_flag(pkg) or " "
                if args.quiet:
                    print(pkg.ATOM.CPF)
                else:
                    print(f'[{"".join(flags)}] {green(pkg.ATOM.CPF)}')

    @subcommand(
        argument(
            "use", metavar=l10n("flag-placeholder"), help=l10n("query-hasuse-use-help")
        ),
        parent=subparsers,
    )
    def hasuse(args):
        """
        List all packages that declare the given use flag.

        Note that this only includes those with the flag in their IUSE
        field and inherited flags through IUSE_EFFECTIVE will not be counted
        """
        info(" * " + l10n("query-hasuse-searching-msg", use=args.use))
        packages = load_all() if args.all else load_all_installed()
        for pkg in packages:
            if args.use in pkg.IUSE:
                flags = [" ", " "]
                if pkg.INSTALLED or load_installed_pkg(Atom(pkg.ATOM.CPF)):
                    flags[0] = "I"
                flags[1] = get_unstable_flag(pkg) or " "
                if args.quiet:
                    print(pkg.ATOM.CPF)
                else:
                    print(f'[{"".join(flags)}] {green(pkg.ATOM.CPF)}')

    @subcommand(
        argument(
            "atom", metavar=l10n("atom-placeholder"), help=l10n("query-uses-atom-help")
        ),
        parent=subparsers,
    )
    def uses(args):
        """Display use flags and their descriptions"""
        modlist = load_pkg(Atom(args.atom))
        if not modlist:
            error(l10n("not-found", atom=args.atom))
            return

        legend_space = " " * len(l10n("query-uses-legend"))
        padding = max(len(l10n("query-uses-final")), len(l10n("query-uses-installed")))
        print(
            f'[ {l10n("query-uses-legend")}: {bright("U")} - {l10n("query-uses-final").ljust(padding)}]'
        )
        print(
            f'[ {legend_space}: {bright("I")} - {l10n("query-uses-installed").ljust(padding)}]'
        )
        print(" * " + l10n("query-uses-found", atom=args.atom))
        local_flags = {}
        global_flags = {}
        use_expand_flags = {}
        for pkg in modlist:
            loc, glob, exp = get_flags(pkg)
            local_flags.update(loc)
            global_flags.update(glob)
            use_expand_flags.update(exp)

        enabled, _ = get_use(pkg)
        print(" U I")

        flag_names = local_flags.keys() | global_flags.keys()

        maxlen = max([len(bright(blue(flag))) for flag in flag_names]) + 2

        def display_group(group, prefix=None):
            for flag in sorted(group):
                fullflag = flag
                if prefix:
                    fullflag = prefix + "_" + flag
                desc = group[flag]
                installed = False
                for pkg in modlist:
                    if isinstance(pkg, InstalledPybuild):
                        installed = fullflag in pkg.INSTALLED_USE
                enabled_flags = ["-", "-"]
                if fullflag in enabled:
                    enabled_flags[0] = "+"
                if installed:
                    enabled_flags[1] = "+"

                colour = blue
                if fullflag in enabled:
                    colour = red

                print(
                    f' {" ".join(enabled_flags)} '
                    + f"{bright(colour(flag))}".ljust(maxlen)
                    + f": {desc}"
                )

        if local_flags:
            print(l10n("query-local-flags"))
            display_group(local_flags)
        if global_flags:
            print(l10n("query-global-flags"))
            display_group(global_flags)
        for use_expand in use_expand_flags:
            print(l10n("query-use-expand-flags", type=use_expand))
            display_group(use_expand_flags[use_expand], prefix=use_expand)

    @subcommand(
        argument(
            "atom", metavar=l10n("atom-placeholder"), help=l10n("query-meta-atom-help")
        ),
        parent=subparsers,
    )
    def meta(args):
        """Display metadata for a package"""
        modlist = load_pkg(Atom(args.atom))
        if not modlist:
            raise Exception(l10n("not-found", atom=args.atom))

        pkgs: Dict[str, List[Pybuild]] = {}
        for pkg in modlist:
            if pkg.CPN in pkgs:
                pkgs[pkg.CPN].append(pkg)
            else:
                pkgs[pkg.CPN] = [pkg]

        for name in pkgs:
            for mod in pkgs[name]:
                mod_metadata = get_package_metadata(mod)
                if mod_metadata:
                    metadata = mod_metadata

            print(f" * {bright(green(name))}")
            if not metadata:
                continue

            if metadata.maintainer:
                maintainer_string = get_maintainer_string(metadata.maintainer)
                print(l10n("package-maintainer") + "\t", maintainer_string)

            if metadata.upstream:
                upstream = metadata.upstream
                first = True
                for key in ["maintainer", "changelog", "doc", "bugs_to"]:
                    if hasattr(upstream, key) and getattr(upstream, key):
                        string = getattr(upstream, key)
                        if key == "maintainer":
                            string = get_maintainer_string(string)

                        if first:
                            print(
                                l10n("package-upstream")
                                + "\t "
                                + key.title()
                                + ":\t"
                                + string
                            )
                            first = False
                        elif key == "doc":
                            print("\t\t " + key.title() + ":\t\t" + string)
                        else:
                            print("\t\t " + key.title() + ":\t" + string)

            print(l10n("package-homepage") + "\t", " ".join(pkg.HOMEPAGE.split()))
            # FIXME: Differentiate between repositories (including installed version)
            for pkg in pkgs[name]:
                path = os.path.dirname(pkg.FILE)
                if os.path.exists(path):
                    print(l10n("package-location") + "\t", path)
            for pkg in pkgs[name]:
                print(
                    l10n("package-keywords") + "\t",
                    pkg.PV + ":",
                    " ".join(pkg.KEYWORDS),
                )
            print(l10n("package-license") + "\t", " ".join(pkg.LICENSE.split()))

    @subcommand(
        argument(
            "atom",
            metavar=l10n("atom-placeholder"),
            help=l10n("package-depgraph-atom-help"),
        ),
        argument("--depth", type=int, help=l10n("query-depgraph-depth-help")),
        parent=subparsers,
    )
    def depgraph(args):
        """Display dependency graph for package""" ""
        modlist = load_pkg(Atom(args.atom))
        if not modlist:
            raise Exception(l10n("not-found", atom=args.atom))

        for mod in modlist:
            print(" * " + l10n("query-depgraph-depgraph", atom=mod.ATOM))
            max_depth = print_depgraph(mod, 1, args.depth or 10)
            print(" " + l10n("query-depgraph-max-depth") + f"({max_depth})")
            print()

    @subcommand(
        argument("name", type=str, help=l10n("query-vfsfind-help")),
        parent=subparsers,
    )
    def vfsfind(args):
        """Display the full path of the given file/directory in the VFS"""
        try:
            print(find_file(args.name))
        except FileNotFoundError:
            error(l10n("file-or-directory-not-found-in-vfs", name=args.name))

    @subcommand(
        argument(
            "directory_path", type=str, help=l10n("query-vfslist-help"), nargs="?"
        ),
        parent=subparsers,
    )
    def vfslist(args):
        """Display the contents of the given directory in the VFS"""
        try:
            if not args.directory_path:
                for file in list_dir("."):
                    print(file)
            else:
                for file in list_dir(args.directory_path):
                    print(file)
        except NotADirectoryError:
            error(l10n("not-a-directory", directory_path=args.directory_path))

    parser.set_defaults(func=lambda args: parser.print_help())
