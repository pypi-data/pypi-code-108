# Copyright 2009-2018 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import absolute_import, print_function

from collections import defaultdict
import os
import re
import subprocess
import tempfile
from textwrap import dedent
import traceback

import apt_pkg
from debian.deb822 import (
    Dsc,
    PkgRelation,
    )
from debian.debian_support import Version

from lpbuildd.debian import (
    DebianBuildManager,
    DebianBuildState,
    )


class SBuildExitCodes:
    """SBUILD process result codes."""
    OK = 0
    FAILED = 1
    ATTEMPTED = 2
    GIVENBACK = 3
    BUILDERFAIL = 4


APT_MISSING_DEP_PATTERNS = [
    r'but [^ ]* is to be installed',
    r'but [^ ]* is installed',
    r'but it is not installable',
    r'but it is a virtual package',
    ]


APT_DUBIOUS_DEP_PATTERNS = [
    r'but it is not installed',
    r'but it is not going to be installed',
    ]


class BuildLogRegexes:
    """Various build log regexes.

    These allow performing actions based on regexes, and extracting
    dependencies for auto dep-waits.
    """
    GIVENBACK = [
        (r"^E: There are problems and -y was used without --force-yes"),
        ]
    MAYBEDEPFAIL = [
        r'The following packages have unmet dependencies:\n'
        r'.* Depends: [^ ]*( \([^)]*\))? (%s)\n'
        % r'|'.join(APT_DUBIOUS_DEP_PATTERNS),
        ]
    DEPFAIL = {
        r'The following packages have unmet dependencies:\n'
        r'.* Depends: (?P<p>[^ ]*( \([^)]*\))?) (%s)\n'
        % r'|'.join(APT_MISSING_DEP_PATTERNS): r"\g<p>",
        }


class DpkgArchitectureCache:
    """Cache the results of asking questions of dpkg-architecture."""

    def __init__(self):
        self._matches = {}

    def match(self, arch, wildcard):
        if (arch, wildcard) not in self._matches:
            command = ["dpkg-architecture", "-i%s" % wildcard]
            env = dict(os.environ)
            env["DEB_HOST_ARCH"] = arch
            ret = (subprocess.call(command, env=env) == 0)
            self._matches[(arch, wildcard)] = ret
        return self._matches[(arch, wildcard)]


dpkg_architecture = DpkgArchitectureCache()


class BinaryPackageBuildState(DebianBuildState):
    SBUILD = "SBUILD"


class BinaryPackageBuildManager(DebianBuildManager):
    """Handle buildd building for a debian style binary package build"""

    initial_build_state = BinaryPackageBuildState.SBUILD

    def __init__(self, builder, buildid, **kwargs):
        DebianBuildManager.__init__(self, builder, buildid, **kwargs)
        self._sbuildpath = os.path.join(self._bin, "sbuild-package")

    @property
    def chroot_path(self):
        return os.path.join(
            self.home, "build-" + self._buildid, 'chroot-autobuild')

    @property
    def schroot_config_path(self):
        return os.path.join('/etc/schroot/chroot.d', 'build-' + self._buildid)

    def initiate(self, files, chroot, extra_args):
        """Initiate a build with a given set of files and chroot."""

        self._dscfile = None
        for f in files:
            if f.endswith(".dsc"):
                self._dscfile = f
        if self._dscfile is None:
            raise ValueError(files)

        self.archive_purpose = extra_args.get('archive_purpose')
        self.distribution = extra_args['distribution']
        self.suite = extra_args['suite']
        self.component = extra_args['ogrecomponent']
        self.arch_indep = extra_args.get('arch_indep', False)
        self.build_debug_symbols = extra_args.get('build_debug_symbols', False)

        super(BinaryPackageBuildManager, self).initiate(
            files, chroot, extra_args)

    def doRunBuild(self):
        """Run the sbuild process to build the package."""
        with tempfile.NamedTemporaryFile(mode="w") as schroot_file:
            # Use the "plain" chroot type because we do the necessary setup
            # and teardown ourselves: it's easier to do this the same way
            # for all build types.
            print(
                dedent('''\
                    [build-{buildid}]
                    description=build-{buildid}
                    groups=sbuild,root
                    root-groups=sbuild,root
                    type=plain
                    directory={chroot_path}
                    ''').format(
                        buildid=self._buildid, chroot_path=self.chroot_path),
                file=schroot_file, end='')
            schroot_file.flush()
            subprocess.check_call(
                ['sudo', 'install', '-o', 'root', '-g', 'root', '-m', '0644',
                 schroot_file.name, self.schroot_config_path])

        currently_building_contents = (
            'Package: %s\n'
            'Component: %s\n'
            'Suite: %s\n'
            'Purpose: %s\n'
            % (self._dscfile.split('_')[0], self.component, self.suite,
               self.archive_purpose))
        if self.build_debug_symbols:
            currently_building_contents += 'Build-Debug-Symbols: yes\n'
        with tempfile.NamedTemporaryFile(mode='w+') as currently_building:
            currently_building.write(currently_building_contents)
            currently_building.flush()
            os.fchmod(currently_building.fileno(), 0o644)
            self.backend.copy_in(currently_building.name, '/CurrentlyBuilding')

        args = ["sbuild-package", self._buildid, self.arch_tag]
        args.append(self.suite)
        args.extend(["-c", "chroot:build-%s" % self._buildid])
        args.append("--arch=" + self.arch_tag)
        args.append("--dist=" + self.suite)
        args.append("--nolog")
        if self.arch_indep:
            args.append("-A")
        args.append(self._dscfile)
        env = dict(os.environ)
        if self.build_debug_symbols:
            env.pop("DEB_BUILD_OPTIONS", None)
        else:
            env["DEB_BUILD_OPTIONS"] = "noautodbgsym"
        self.runSubProcess(self._sbuildpath, args, env=env)

    def getAptLists(self):
        """Yield each of apt's Packages files in turn as a file object."""
        apt_helper = "/usr/lib/apt/apt-helper"
        paths = None
        if os.path.exists(os.path.join(self.chroot_path, apt_helper[1:])):
            try:
                paths = subprocess.check_output(
                    ["sudo", "chroot", self.chroot_path,
                     "apt-get", "indextargets", "--format", "$(FILENAME)",
                     "Created-By: Packages"],
                    universal_newlines=True).splitlines()
            except subprocess.CalledProcessError:
                # This might be e.g. Ubuntu 14.04, where
                # /usr/lib/apt/apt-helper exists but "apt-get indextargets"
                # doesn't.  Fall back to reading Packages files directly.
                pass
        if paths is not None:
            for path in paths:
                helper = subprocess.Popen(
                    ["sudo", "chroot", self.chroot_path,
                     apt_helper, "cat-file", path],
                    stdout=subprocess.PIPE)
                try:
                    yield helper.stdout
                finally:
                    helper.stdout.read()
                    helper.wait()
        else:
            apt_lists = os.path.join(
                self.chroot_path, "var", "lib", "apt", "lists")
            for name in sorted(os.listdir(apt_lists)):
                if name.endswith("_Packages"):
                    path = os.path.join(apt_lists, name)
                    with open(path, "rb") as packages_file:
                        yield packages_file

    def getAvailablePackages(self):
        """Return the available binary packages in the chroot.

        :return: A dictionary mapping package names to a set of the
            available versions of each package.
        """
        available = defaultdict(set)
        for packages_file in self.getAptLists():
            for section in apt_pkg.TagFile(packages_file):
                available[section["package"]].add(section["version"])
                if "provides" in section:
                    provides = apt_pkg.parse_depends(section["provides"])
                    for provide in provides:
                        # Disjunctions are currently undefined here.
                        if len(provide) > 1:
                            continue
                        # Virtual packages may only provide an exact version
                        # or none.
                        if provide[0][1] and provide[0][2] != "=":
                            continue
                        available[provide[0][0]].add(
                            provide[0][1] if provide[0][1] else None)
        return available

    def getBuildDepends(self, dscpath, arch_indep):
        """Get the build-dependencies of a source package.

        :param dscpath: The path of a .dsc file.
        :param arch_indep: True iff we were asked to build the
            architecture-independent parts of this source package.
        :return: The build-dependencies, in the form returned by
            `debian.deb822.PkgRelation.parse_relations`.
        """
        deps = []
        with open(dscpath, "rb") as dscfile:
            dsc = Dsc(dscfile)
            fields = ["Build-Depends"]
            if arch_indep:
                fields.append("Build-Depends-Indep")
            for field in fields:
                if field in dsc:
                    deps.extend(PkgRelation.parse_relations(dsc[field]))
        return deps

    def relationMatches(self, dep, available):
        """Return True iff a dependency matches an available package.

        :param dep: A dictionary with at least a "name" key, perhaps also
            "version", "arch", and "restrictions" keys, and optionally other
            keys, of the kind returned in a list of lists by
            `debian.deb822.PkgRelation.parse_relations`.
        :param available: A dictionary mapping package names to a list of
            the available versions of each package.
        """
        dep_arch = dep.get("arch")
        if dep_arch is not None:
            arch_match = False
            for enabled, arch_wildcard in dep_arch:
                if dpkg_architecture.match(self.arch_tag, arch_wildcard):
                    arch_match = enabled
                    break
                elif not enabled:
                    # Any !other-architecture restriction implies that this
                    # architecture is allowed, unless it's specifically
                    # excluded by some other restriction.
                    arch_match = True
            if not arch_match:
                # This dependency "matches" in the sense that it's ignored
                # on this architecture.
                return True
        dep_restrictions = dep.get("restrictions")
        if dep_restrictions is not None:
            if all(any(restriction.enabled for restriction in restrlist)
                   for restrlist in dep_restrictions):
                # This dependency "matches" in the sense that it's ignored
                # when no build profiles are enabled.
                return True
        if dep["name"] not in available:
            return False
        dep_version = dep.get("version")
        if dep_version is None:
            return True
        operator_map = {
            "<<": (lambda a, b: a < b),
            "<=": (lambda a, b: a <= b),
            "=": (lambda a, b: a == b),
            ">=": (lambda a, b: a >= b),
            ">>": (lambda a, b: a > b),
            }
        operator = operator_map[dep_version[0]]
        want_version = dep_version[1]
        for version in available[dep["name"]]:
            if (version is not None and
                    operator(Version(version), want_version)):
                return True
        return False

    def stripDependencies(self, deps):
        """Return a stripped and stringified representation of a dependency.

        The build master can't handle the various qualifications and
        restrictions that may be present in control-format
        build-dependencies (e.g. ":any", "[amd64]", or "<!nocheck>"), so we
        strip these out before returning them.

        :param deps: Build-dependencies in the form returned by
            `debian.deb822.PkgRelation.parse_relations`.
        :return: A stripped dependency relation string, or None if deps is
            empty.
        """
        stripped_deps = []
        for or_dep in deps:
            stripped_or_dep = []
            for simple_dep in or_dep:
                stripped_simple_dep = dict(simple_dep)
                stripped_simple_dep["arch"] = None
                stripped_simple_dep["archqual"] = None
                stripped_simple_dep["restrictions"] = None
                stripped_or_dep.append(stripped_simple_dep)
            stripped_deps.append(stripped_or_dep)
        if stripped_deps:
            return PkgRelation.str(stripped_deps)
        else:
            return None

    def analyseDepWait(self, deps, avail):
        """Work out the correct dep-wait for a failed build, if any.

        We only consider direct build-dependencies, because indirect ones
        can't easily be turned into an accurate dep-wait: they might be
        resolved either by an intermediate package changing or by the
        missing dependency becoming available.  We err on the side of
        failing a build rather than setting a dep-wait if it's possible that
        the dep-wait might be incorrect.  Any exception raised during the
        analysis causes the build to be failed.

        :param deps: The source package's build-dependencies, in the form
            returned by `debian.deb822.PkgRelation.parse_relations`.
        :param avail: A dictionary mapping package names to a set of the
            available versions of each package.
        :return: A dependency relation string representing the packages that
            need to become available before this build can proceed, or None
            if the build should be failed instead.
        """
        try:
            unsat_deps = []
            for or_dep in deps:
                if not any(self.relationMatches(dep, avail) for dep in or_dep):
                    unsat_deps.append(or_dep)
            return self.stripDependencies(unsat_deps)
        except Exception:
            self._builder.log("Failed to analyse dep-wait:\n")
            for line in traceback.format_exc().splitlines(True):
                self._builder.log(line)
            return None

    def iterate_SBUILD(self, success):
        """Finished the sbuild run."""
        if success == SBuildExitCodes.OK:
            print("Returning build status: OK")
            return self.deferGatherResults()

        log_patterns = []
        stop_patterns = [[r"^Toolchain package versions:", re.M]]

        # We don't distinguish attempted and failed.
        if success == SBuildExitCodes.ATTEMPTED:
            success = SBuildExitCodes.FAILED

        if success == SBuildExitCodes.GIVENBACK:
            for rx in BuildLogRegexes.GIVENBACK:
                log_patterns.append([rx, re.M])
            # Check the last 4KiB for the Fail-Stage. If it failed
            # during install-deps, search for the missing dependency
            # string.
            with open(os.path.join(self._cachepath, "buildlog"), "rb") as log:
                try:
                    log.seek(-4096, os.SEEK_END)
                except IOError:
                    pass
                tail = log.read(4096).decode("UTF-8", "replace")
            if re.search(r"^Fail-Stage: install-deps$", tail, re.M):
                for rx in BuildLogRegexes.MAYBEDEPFAIL:
                    log_patterns.append([rx, re.M | re.S])
                for rx in BuildLogRegexes.DEPFAIL:
                    log_patterns.append([rx, re.M | re.S])

        missing_dep = None
        if log_patterns:
            rx, mo = self.searchLogContents(log_patterns, stop_patterns)
            if mo is None:
                # It was givenback, but we can't see a valid reason.
                # Assume it failed.
                success = SBuildExitCodes.FAILED
            elif rx in BuildLogRegexes.MAYBEDEPFAIL:
                # These matches need further analysis.
                dscpath = os.path.join(
                    self.home, "build-%s" % self._buildid, self._dscfile)
                missing_dep = self.analyseDepWait(
                    self.getBuildDepends(dscpath, self.arch_indep),
                    self.getAvailablePackages())
                if missing_dep is None:
                    success = SBuildExitCodes.FAILED
            elif rx in BuildLogRegexes.DEPFAIL:
                # A depwait match forces depwait.
                missing_dep = mo.expand(
                    BuildLogRegexes.DEPFAIL[rx].encode("UTF-8"))
                missing_dep = self.stripDependencies(
                    PkgRelation.parse_relations(
                        missing_dep.decode("UTF-8", "replace")))
            else:
                # Otherwise it was a givenback pattern, so leave it
                # in givenback.
                pass

        if not self.alreadyfailed:
            if missing_dep is not None:
                print("Returning build status: DEPFAIL")
                print("Dependencies: " + missing_dep)
                self._builder.depFail(missing_dep)
            elif success == SBuildExitCodes.GIVENBACK:
                print("Returning build status: GIVENBACK")
                self._builder.giveBack()
            elif success == SBuildExitCodes.FAILED:
                print("Returning build status: PACKAGEFAIL")
                self._builder.buildFail()
            elif success >= SBuildExitCodes.BUILDERFAIL:
                # anything else is assumed to be a buildd failure
                print("Returning build status: BUILDERFAIL")
                self._builder.builderFail()
            self.alreadyfailed = True
        self.doReapProcesses(self._state)

    def iterateReap_SBUILD(self, success):
        """Finished reaping after sbuild run."""
        # Ignore errors from tearing down schroot configuration.
        subprocess.call(['sudo', 'rm', '-f', self.schroot_config_path])

        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()
