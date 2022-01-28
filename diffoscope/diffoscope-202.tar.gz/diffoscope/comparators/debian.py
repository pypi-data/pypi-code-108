#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2014-2015 Jérémy Bobbio <lunar@debian.org>
# Copyright © 2015-2022 Chris Lamb <lamby@debian.org>
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
import os.path
import logging

try:
    from debian.deb822 import Dsc, Deb822
except:
    # Import can fail due to apt_pkg.Error (or similar) tracebacks, but let us
    # re-raise them as ImportErrors so that the Comparator module class
    # handling just works. (See reproducible-builds/diffoscope#300)
    raise ImportError

from diffoscope.changes import Changes
from diffoscope.changes import ChangesFileException
from diffoscope.difference import Difference

from .utils.file import File
from .utils.container import Container

logger = logging.getLogger(__name__)


class DebControlMember(File):
    def __init__(self, container, member_name):
        super().__init__(container)
        self._name = member_name
        self._path = None

    @property
    def container(self):
        return self._container

    @property
    def name(self):
        return self._name

    @property
    def path(self):
        return os.path.join(
            os.path.dirname(self.container.source.path), self.name
        )

    def is_directory(self):
        return False

    def is_symlink(self):
        return False

    def is_device(self):
        return False


class DebControlContainer(Container):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._version_re = DebControlContainer.get_version_trimming_re(self)

    @staticmethod
    def get_version_trimming_re(dcc):
        version = dcc.source._deb822.get("Version")

        # Remove the epoch as it's not in the filename
        version = re.sub(r"^\d+:", "", version)
        if "-" in version:
            upstream, revision = version.rsplit("-", 1)

            return re.compile(
                r"_%s(?:-%s)?" % (re.escape(upstream), re.escape(revision))
            )

        return re.compile(re.escape(version))

    def get_adjusted_members(self):
        for name in self.get_member_names():
            yield self._trim_version_number(name), self.get_member(name)

    def get_member_names(self):
        field = self.source._deb822.get("Files") or self.source._deb822.get(
            "Checksums-Sha256"
        )

        parent_dir = os.path.dirname(self.source.path)

        # Show results from debugging packages last; they are rather verbose,
        # masking other more interesting differences due to truncating the
        # output.
        for name in sorted(
            (x["name"] for x in field),
            key=lambda x: (x.endswith(".deb") and "-dbgsym_" in x, x),
        ):
            # The referenced files are supplied by the user, but the Deb822
            # parser rejects malicious imput such as "../../etc/shadow" etc.
            if not os.path.exists(os.path.join(parent_dir, name)):
                logger.debug(
                    "Could not find file %s referenced in %s",
                    name,
                    self.source.name,
                )
                break

            yield name

    def get_member(self, member_name):
        return DebControlMember(self, member_name)

    def _trim_version_number(self, name):
        return self._version_re.sub("", name)


class DebControlFile(File):
    CONTAINER_CLASSES = [DebControlContainer]

    @staticmethod
    def _get_deb822(file):
        # Be nice to .changes and .dsc comparison in the MissingFile case

        if isinstance(file, DebControlFile):
            return file._deb822

        class NullChanges(dict):
            def get_as_string(self, _):
                return ""

        return NullChanges(Files=[], Version="")

    @staticmethod
    def _parse_gpg(file):
        try:
            with open(file.path) as f:
                header, _, footer = Deb822.split_gpg_and_payload(f)
        except EOFError:
            header = []
            footer = []

        return [b"\n".join(x).decode("utf-8") for x in (header, footer)]

    def compare_details(self, other, source=None):
        gpg_a = self._parse_gpg(self)
        gpg_b = self._parse_gpg(other)

        differences = [
            Difference.from_text(
                gpg_a[0], gpg_b[0], self.path, other.path, source="GPG header"
            )
        ]

        other_deb822 = self._get_deb822(other)

        for field in sorted(
            set(self._deb822.keys()).union(set(other_deb822.keys()))
        ):
            if field.startswith("Checksums-") or field == "Files":
                continue

            my_value = ""
            if field in self._deb822:
                my_value = self._deb822.get_as_string(field).lstrip()

            other_value = ""
            if field in other_deb822:
                other_value = other_deb822.get_as_string(field).lstrip()

            comment = None
            if my_value != other_value and sorted(my_value.split()) == sorted(
                other_value.split()
            ):
                comment = "Ordering differences only"

            differences.append(
                Difference.from_text(
                    my_value,
                    other_value,
                    self.path,
                    other.path,
                    source=field,
                    comment=comment,
                )
            )

        # Compare Files as string
        if self._deb822.get("Files"):
            differences.append(
                Difference.from_text(
                    self._deb822.get_as_string("Files"),
                    other_deb822.get_as_string("Files"),
                    self.path,
                    other.path,
                    source="Files",
                )
            )
        else:
            differences.append(
                Difference.from_text(
                    self._deb822.get_as_string("Checksums-Sha256"),
                    other_deb822.get_as_string("Checksums-Sha256"),
                    self.path,
                    other.path,
                    source="Checksums-Sha256",
                )
            )

        differences.append(
            Difference.from_text(
                gpg_a[1],
                gpg_b[1],
                self.path,
                other.path,
                source="GPG signature",
            )
        )

        return differences


class DotChangesFile(DebControlFile):
    DESCRIPTION = "Debian .changes files"
    FILE_EXTENSION_SUFFIX = {".changes"}

    # .changes files can be identified "data" if they contain non-printable
    # characters (Re: reproducible-builds/diffoscope#286)
    FILE_TYPE_RE = re.compile(r"^(ASCII text|UTF-8 Unicode text|data)")

    @classmethod
    def recognizes(cls, file):
        if not super().recognizes(file):
            return False

        try:
            file._deb822 = Changes(filename=file.path)
        except ChangesFileException as exc:
            logger.warning(
                f"Rejecting {file.path} as a Debian .changes file: {exc}"
            )
            return False

        try:
            file.validation_msg = None
            file._deb822.validate("sha256", check_signature=False)
        except FileNotFoundError as exc:
            # Continue even though this .changes file may be invalid
            file.validation_msg = f"{os.path.basename(file.path)} is missing referenced files: {exc}"
            logger.warning(file.validation_msg)

        return True

    def compare(self, other, *args, **kwargs):
        differences = super().compare(other, *args, **kwargs)

        if differences is None:
            return None

        for x in (self, other):
            if x.validation_msg:
                differences.add_comment(x.validation_msg)

        other_deb822 = self._get_deb822(other)

        files = zip(self._deb822.get("Files"), other_deb822.get("Files"))

        files_identical = all(
            x == y for x, y in files if not x["name"].endswith(".buildinfo")
        )

        if (
            files_identical
            and len(differences.details) == 1
            and differences.details[0].source1 == "Files"
        ):
            logger.warning("Ignoring buildinfo file differences")
            return None

        return differences


class DotDscFile(DebControlFile):
    DESCRIPTION = "Debian source packages (.dsc)"
    FILE_EXTENSION_SUFFIX = {".dsc"}

    @classmethod
    def recognizes(cls, file):
        if not super().recognizes(file):
            return False

        with open(file.path, "rb") as f:
            file._deb822 = Dsc(f)

        return True


class DotBuildinfoContainer(DebControlContainer):
    def get_member_names(self):
        result = super(DotBuildinfoContainer, self).get_member_names()

        # As a special-case, if the parent container of this .buildinfo is a
        # .changes file, ignore members here that are referenced in both. This
        # avoids recursing into files twice where a .buildinfo references a
        # file that is also listed in that member's parent .changes file:
        #
        #    foo.changes → foo.deb
        #    foo.changes → foo.buildinfo → foo.deb
        #
        ignore = set()
        if isinstance(self.source.container, DebControlContainer):
            ignore.update(self.source.container.get_member_names())

        return [x for x in result if x not in ignore]


class DotBuildinfoFile(DebControlFile):
    DESCRIPTION = "Debian .buildinfo files"
    CONTAINER_CLASSES = [DotBuildinfoContainer]
    FILE_EXTENSION_SUFFIX = {".buildinfo"}
    FILE_TYPE_RE = re.compile(
        r"^(ASCII text|UTF-8 Unicode text|PGP signed message)"
    )

    @classmethod
    def recognizes(cls, file):
        if not super().recognizes(file):
            return False

        # Parse .buildinfo files like .dsc files
        with open(file.path, "rb") as f:
            file._deb822 = Dsc(f)

        # Check we have a *Debian* .buildinfo file
        if not (
            "Format" in file._deb822 and "Checksums-Sha256" in file._deb822
        ):
            return False

        return True
