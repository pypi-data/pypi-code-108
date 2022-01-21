#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015 Clemens Lang <cal@macports.org>
# Copyright © 2016-2020 Chris Lamb <lamby@debian.org>
# Copyright © 2021 Jean-Romain Garnier <salsa@jean-romain.com>
#
# diffoscope is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# diffoscope is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with diffoscope.  If not, see <https://www.gnu.org/licenses/>.

import re
import abc
import logging
import collections

from diffoscope.difference import Difference
from diffoscope.exc import RequiredToolNotFound
from diffoscope.tools import tool_required, tool_check_installed

from .utils.file import File
from .utils.container import Container
from .decompile import DecompilableContainer
from .utils.command import Command, our_check_output


logger = logging.getLogger(__name__)


class MachoContainerFile(File, metaclass=abc.ABCMeta):
    """
    A "fake" File subclass used to represent architectures or sections found in
    a Mach-O file. Also see ElfSection in elf.py.
    """

    auto_diff_metadata = False

    @property
    def progress_name(self):
        return "{} [{}]".format(
            self.container.source.progress_name, super().progress_name
        )

    @property
    def path(self):
        return self.container.source.path

    def cleanup(self):
        pass

    def is_directory(self):
        return False

    def is_symlink(self):
        return False

    def is_device(self):
        return False

    def has_same_content_as(self, other):
        # Always force diff of the container
        return False

    @property
    def fuzzy_hash(self):
        return None

    @classmethod
    def recognizes(cls, file):
        # No file should be recognized as a Mach-O container
        return False


##################
# Otool Commands #
##################


class OtoolReadobj(Command):
    def __init__(self, path, arch, *args, **kwargs):
        self._path = path
        self._arch = arch
        super().__init__(path, *args, **kwargs)

    @staticmethod
    def fallback():
        return None

    @tool_required("otool")
    def cmdline(self):
        return ["otool"] + self.otool_options() + [self._path]

    def otool_options(self):
        return ["-arch", self._arch]

    def filter(self, line):
        # Strip filename
        prefix = f"{self._path}:".encode("utf-8")
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
        return line


class OtoolHeaders(OtoolReadobj):
    def otool_options(self):
        return super().otool_options() + ["-h"]


class OtoolLibraries(OtoolReadobj):
    def otool_options(self):
        return super().otool_options() + ["-L"]


class OtoolRelocations(OtoolReadobj):
    def otool_options(self):
        return super().otool_options() + ["-r"]


class OtoolIndirectSymbols(OtoolReadobj):
    def otool_options(self):
        return super().otool_options() + ["-I"]


# List otool of commands to run on the base file
OTOOL_COMMANDS = [
    OtoolHeaders,
    OtoolLibraries,
    OtoolRelocations,
    OtoolIndirectSymbols,
]


class OtoolObjdump(Command):
    def __init__(self, path, arch, section, *args, **kwargs):
        self._path = path
        self._arch = arch
        self._section = section
        super().__init__(path, *args, **kwargs)

    @staticmethod
    def fallback():
        return None

    @tool_required("otool")
    def cmdline(self):
        return ["otool"] + self.otool_options() + [self._path]

    def otool_options(self):
        return ["-arch", self._arch]

    def filter(self, line):
        # Strip filename
        prefix = f"{self._path}:".encode("utf-8")
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
        return line


class OtoolDump(OtoolObjdump):
    def otool_options(self):
        segname, sectname = self._section.split(",")
        return super().otool_options() + ["-V", "-s", segname, sectname]


class OtoolDisassemble(OtoolObjdump):
    @staticmethod
    def fallback():
        return OtoolDisassembleInternal

    def otool_options(self):
        segname, sectname = self._section.split(",")
        return super().otool_options() + ["-v", "-V", "-s", segname, sectname]


class OtoolDisassembleInternal(OtoolObjdump):
    def otool_options(self):
        segname, sectname = self._section.split(",")
        return super().otool_options() + [
            "-v",
            "-V",
            "-Q",
            "-s",
            segname,
            sectname,
        ]


#################
# LLVM Commands #
#################


class LlvmReadobj(Command):
    def __init__(self, path, *args, **kwargs):
        self._path = path
        super().__init__(path, *args, **kwargs)

    @staticmethod
    def fallback():
        return None

    @tool_required("llvm-readobj")
    def cmdline(self):
        return ["llvm-readobj"] + self.readobj_options() + [self._path]

    def readobj_options(self):
        return []

    def filter(self, line):
        # Strip filename
        if line.startswith(b"File: "):
            return b""
        return line


class LlvmFileHeaders(LlvmReadobj):
    """Display file headers"""

    def readobj_options(self):
        return super().readobj_options() + ["--file-headers"]


class LlvmNeededLibs(LlvmReadobj):
    """Display the needed libraries"""

    def readobj_options(self):
        return super().readobj_options() + ["--needed-libs"]


class LlvmSymbols(LlvmReadobj):
    """Display the symbol table"""

    def readobj_options(self):
        return super().readobj_options() + ["--symbols"]


class LlvmDynSymbols(LlvmReadobj):
    """Display the dynamic symbol table"""

    def readobj_options(self):
        return super().readobj_options() + ["--dyn-symbols"]


class LlvmRelocations(LlvmReadobj):
    """Display the relocation entries in the fil"""

    def readobj_options(self):
        return super().readobj_options() + ["--relocations"]


class LlvmDynRelocations(LlvmReadobj):
    """Display the dynamic relocation entries in the file"""

    def readobj_options(self):
        return super().readobj_options() + ["--dyn-relocations"]


# List llvm of commands to run on the base file
# The other classes are here for the containers
LLVM_COMMANDS = [
    LlvmFileHeaders,
    LlvmNeededLibs,
    LlvmSymbols,
    LlvmDynSymbols,
    LlvmRelocations,
    LlvmDynRelocations,
]


class LlvmObjdump(Command):
    def __init__(self, path, arch, section, *args, **kwargs):
        self._path = path
        self._arch = arch
        self._section = section
        super().__init__(path, *args, **kwargs)

    @staticmethod
    def fallback():
        return None

    @tool_required("llvm-objdump")
    def cmdline(self):
        return ["llvm-objdump"] + self.objdump_options() + [self._path]

    def objdump_options(self):
        return [
            f"--arch={self._arch}",
            f"--section={self._section}",
            "--macho",
            "--demangle",
            "--no-leading-addr",
            "--no-show-raw-insn",
        ]

    def filter(self, line):
        # Strip filename
        prefix = self._path.encode("utf-8")
        if line.startswith(prefix):
            return line[len(prefix) :].strip().strip(b":")
        return line


###################
# Mach-O Backends #
###################


class MachoBackend:
    @staticmethod
    def is_available():
        return False

    @staticmethod
    def sections(path, arch):
        return None

    @staticmethod
    def differences(path1, path2, arch, section_name, cmd):
        differences = []

        diff = Difference.from_operation(
            cmd, path1, path2, operation_args=[arch, section_name]
        )
        differences.append(diff)

        if diff is None and cmd.fallback():
            differences.append(
                Difference.from_operation(
                    cmd.fallback(),
                    path1,
                    path2,
                    operation_args=[arch, section_name],
                )
            )

        return differences


class OtoolBackend(MachoBackend):
    """
    Otool implementation
    Standard toolchain available for macOS
    """

    @staticmethod
    def is_available():
        return tool_check_installed("otool")

    @staticmethod
    def sections(path, arch):
        # Sections are not read dynamically with this backend
        # See https://developer.apple.com/library/archive/documentation/Performance/Conceptual/CodeFootprint/Articles/MachOOverview.html
        return collections.OrderedDict(
            [
                ("__TEXT,__text", OtoolDisassemble),
                ("__TEXT,__const", OtoolDump),
                ("__TEXT,__cstring", OtoolDump),
                ("__DATA,__data", OtoolDump),
                ("__DATA,__const", OtoolDump),
                ("__DATA,__bss", OtoolDump),
                ("__DATA,__common", OtoolDump),
            ]
        )


class LlvmBackend(MachoBackend):
    """
    LLVM implementation
    Toolchain available for most Unix platforms
    """

    @staticmethod
    def is_available():
        return tool_check_installed("llvm-readobj") and tool_check_installed(
            "llvm-objdump"
        )

    @staticmethod
    def sections(path, arch):
        cmd = ["llvm-readobj", "--sections", path]
        output = our_check_output(cmd, shell=False)
        output = output.decode("utf-8")

        sections = collections.OrderedDict()
        should_skip_section = True
        section_name = None
        section_segment = None
        for line in output.splitlines():
            # Remove identation added by llvm
            line = line.lstrip()

            # Check out which architecture is being printed
            # If it's not the right one, ignore it
            if line.startswith("Arch:"):
                section_arch = line.lstrip("Arch:").strip()
                should_skip_section = section_arch != arch

            if should_skip_section:
                continue

            # Look for the section's name and segment
            if line.startswith("Name:"):
                # e.g. __text (5F 5F 74 65 78 74 00 00 00 00 00 00 00 00 00 00)
                section_name = line.lstrip("Name:").strip().split()[0]
            elif line.startswith("Segment:"):
                # e.g. __TEXT (5F 5F 54 45 58 54 00 00 00 00 00 00 00 00 00 00)
                section_segment = line.lstrip("Segment:").strip().split()[0]

            # Once we have both, append the information to the list of sections
            # and reset the state
            if section_name and section_segment:
                section_full_name = "{},{}".format(
                    section_segment, section_name
                )
                logger.debug(
                    "Adding section %s for architecture %s",
                    section_full_name,
                    arch,
                )
                sections[section_full_name] = LlvmObjdump

                section_name = None
                section_segment = None

        return sections


MACHO_BACKENDS = [OtoolBackend, LlvmBackend]


######################
# Files & Containers #
######################


class MachoSection(MachoContainerFile):
    """
    Class representing a section of an architecture contained in a Mach-O file
    """

    def __init__(self, macho_container, section, cmd):
        super().__init__(container=macho_container)
        self._name = section
        self._cmd = cmd

    @property
    def name(self):
        return self._name

    def compare(self, other, source=None):
        diff = Difference.from_operation(
            self._cmd,
            self.path,
            other.path,
            operation_args=[self.container.arch, self._name],
        )

        if diff is None and self._cmd.fallback():
            diff = Difference.from_operation(
                self._cmd.fallback(),
                self.path,
                other.path,
                operation_args=[self.container.arch, self._name],
            )

        return diff


class MachoSectionsContainer(DecompilableContainer):
    """
    Second-level container for a Mach-O file:
    Lists sections present an architecture of the file (see MachoSection)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.arch = self.source.name

        # Find out which backend to use
        available_backends = [b for b in MACHO_BACKENDS if b.is_available()]
        if not available_backends:
            raise RequiredToolNotFound(operation="llvm-objdump")

        self._sections = available_backends[0].sections(
            self.source.path, self.arch
        )

    def get_member_names(self):
        decompiled_members = super().get_member_names()
        return list(decompiled_members) + list(self._sections.keys())

    def get_member(self, member_name):
        try:
            cmd = self._sections[member_name]
            return MachoSection(self, member_name, cmd)
        except KeyError:
            # Raised when the member name is not one of ours, which means
            # it was part of the decompiler's output (aka super)
            return super().get_member(member_name)


class MachoArchitecture(MachoContainerFile):
    """
    Class representing an architecture contained in a Mach-O file
    """

    CONTAINER_CLASSES = [MachoSectionsContainer]

    def __init__(self, macho_container, architecture):
        super().__init__(container=macho_container)
        self._name = architecture

    @property
    def name(self):
        return self._name

    def compare_details(self, other, source=None):
        # Run available architecture-specific commands
        # Make sure we don't raise a RequiredToolNotFound error, even if otool
        # is unavalailable, otherwise we would interrupt the compare for cases
        # where llvm in installed
        # If no tool is available, MachoArchitecturesContainer will take care
        # of raising a RequiredToolNotFound error
        if tool_check_installed("otool"):
            return [
                Difference.from_operation(
                    x, self.path, other.path, operation_args=[self._name]
                )
                for x in OTOOL_COMMANDS
            ]

        return []


class MachoArchitecturesContainer(Container):
    """
    First-level container for a Mach-O file:
    Lists architectures present in the file (see MachoArchitecture)
    """

    auto_diff_metadata = False

    @staticmethod
    @tool_required("lipo")
    def lipo_get_arch_from_macho(path):
        lipo_output = our_check_output(["lipo", "-archs", path]).decode(
            "utf-8"
        )
        return lipo_output.split()

    @staticmethod
    @tool_required("llvm-readobj")
    def llvm_get_arch_from_macho(path):
        llvm_output = our_check_output(["llvm-readobj", path]).decode("utf-8")
        archs = [
            line.lstrip("Arch: ")
            for line in llvm_output.splitlines()
            if line.startswith("Arch: ")
        ]
        return archs

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Find out which tool we can use to get the architecures included in
        # the Macho-O binary
        archs = None
        if tool_check_installed("lipo"):
            archs = self.lipo_get_arch_from_macho(self.source.path)
        elif tool_check_installed("llvm-readobj"):
            archs = self.llvm_get_arch_from_macho(self.source.path)
        else:
            raise RequiredToolNotFound(operation="llvm-readobj")

        # Check for fat binaries
        self._architectures = collections.OrderedDict()
        for arch in archs:
            self._architectures[arch] = MachoArchitecture(self, arch)

    def get_member_names(self):
        return self._architectures.keys()

    def get_member(self, member_name):
        return self._architectures[member_name]


class Strings(Command):
    @tool_required("strings")
    def cmdline(self):
        # macOS' strings does not support the "--all" and "--bytes" syntax
        return ("strings", "-a", "-n", "8", self.path)


class MachoFile(File):
    DESCRIPTION = "macOS binaries"
    CONTAINER_CLASSES = [MachoArchitecturesContainer]
    FILE_TYPE_RE = re.compile(r"^Mach-O ")

    def compare_details(self, other, source=None):
        differences = []

        # Show string differences first, if there are any
        difference = Difference.from_operation(Strings, self.path, other.path)
        if difference:
            difference.check_for_ordering_differences()
        differences.append(difference)

        # Next, compute differences in the file's headers
        if tool_check_installed("otool"):
            # otool can display headers separately for each architecture, so
            # run commands in MachoArchitecture instead
            pass
        elif tool_check_installed("llvm-readobj"):
            # llvm-readobj does not have an architecture filter, so output the
            # differences at the file level
            differences += [
                Difference.from_operation(x, self.path, other.path)
                for x in LLVM_COMMANDS
            ]
        else:
            # If no tool is available, MachoArchitecturesContainer will raise a
            # RequiredToolNotFound error. Use the binary comparator here to
            # make sure we don't miss any differences
            difference = self.compare_bytes(other, source=source)
            if difference is None:
                difference = Difference(self.path, other.path, source)

            difference.add_comment(
                "Neither otool nor llvm-readobj was found in path, falling "
                "back to binary comparison."
            )
            differences.append(difference)

        return differences
