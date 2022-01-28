#
# diffoscope: in-depth comparison of files, archives, and directories
#
# Copyright © 2016 Reiner Herrmann <reiner@reiner-h.de>
# Copyright © 2016-2021 Chris Lamb <lamby@debian.org>
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
import binascii
import textwrap
import os.path
import logging
import itertools
import subprocess

from diffoscope.difference import Difference
from diffoscope.exc import RequiredToolNotFound
from diffoscope.tools import (
    tool_required,
    find_executable,
    python_module_missing,
)
from diffoscope.tempfiles import get_temporary_directory

from .utils.archive import Archive
from .utils.command import Command
from .utils.compare import compare_files
from .zip import ZipContainer, zipinfo_differences, ZipFileBase
from .missing_file import MissingFile

logger = logging.getLogger(__name__)

try:
    import androguard
except ImportError:
    python_module_missing("androguard")
    androguard = None


class ApkContainer(Archive):
    @property
    def path(self):
        return self._path

    @tool_required("apktool")
    @tool_required("zipinfo")
    def open_archive(self):
        self._members = []
        self._tmpdir = get_temporary_directory(suffix="apk")
        self._andmanifest = None
        self._andmanifest_orig = None

        logger.debug(
            "Extracting %s to %s", self.source.name, self._tmpdir.name
        )

        subprocess.check_call(
            (
                "apktool",
                "d",
                "-f",
                "-k",
                "-m",
                "-o",
                self._tmpdir.name,
                self.source.path,
            ),
            stderr=None,
            stdout=subprocess.PIPE,
        )

        # Optionally extract a few files that apktool does not
        for x in ("classes.dex", "resources.arsc"):
            subprocess.call(
                ("unzip", "-d", self._tmpdir.name, self.source.path, x),
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )

        # ... including "classes2.dex", "classes3.dex", etc.
        for x in itertools.count(2):
            try:
                subprocess.check_call(
                    (
                        "unzip",
                        "-d",
                        self._tmpdir.name,
                        self.source.path,
                        f"classes{x}.dex",
                    ),
                    stderr=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
            except subprocess.CalledProcessError:
                break

        for root, _, files in os.walk(self._tmpdir.name):
            current_dir = []

            for filename in files:
                abspath = os.path.join(root, filename)

                # apktool.yml is a file created by apktool which contains
                # metadata information. We eename it for clarity and always
                # make it appear at the beginning of the directory listing for
                # reproducibility.
                if filename == "apktool.yml":
                    abspath = filter_apk_metadata(
                        abspath, os.path.basename(self.source.path)
                    )
                    relpath = abspath[len(self._tmpdir.name) + 1 :]
                    current_dir.insert(0, relpath)
                    continue

                relpath = abspath[len(self._tmpdir.name) + 1 :]

                if filename == "AndroidManifest.xml":
                    containing_dir = root[len(self._tmpdir.name) + 1 :]
                    if containing_dir == "original":
                        self._andmanifest_orig = relpath
                    if containing_dir == "":
                        self._andmanifest = relpath
                    continue

                current_dir.append(relpath)

            self._members.extend(current_dir)

        return self

    def get_android_manifest(self):
        return (
            self.get_member(self._andmanifest) if self._andmanifest else None
        )

    def get_original_android_manifest(self):
        if self._andmanifest_orig:
            return self.get_member(self._andmanifest_orig)
        return MissingFile("/dev/null", self._andmanifest_orig)

    def close_archive(self):
        pass

    def get_member_names(self):
        return self._members

    def extract(self, member_name, dest_dir):
        return os.path.join(self._tmpdir.name, member_name)

    def compare_manifests(self, other):
        my_android_manifest = self.get_android_manifest()
        other_android_manifest = other.get_android_manifest()
        comment = None
        diff_manifests = None
        if my_android_manifest and other_android_manifest:
            source = "AndroidManifest.xml (decoded)"
            diff_manifests = compare_files(
                my_android_manifest, other_android_manifest, source=source
            )
            if diff_manifests is None:
                comment = "No difference found for decoded AndroidManifest.xml"
        else:
            comment = (
                "No decoded AndroidManifest.xml found "
                + "for one of the APK files."
            )
        if diff_manifests:
            return diff_manifests

        source = "AndroidManifest.xml (original / undecoded)"
        diff_manifests = compare_files(
            self.get_original_android_manifest(),
            other.get_original_android_manifest(),
            source=source,
        )
        if diff_manifests is not None:
            diff_manifests.add_comment(comment)
        return diff_manifests

    def compare(self, other, *args, **kwargs):
        differences = []
        try:
            differences.append(self.compare_manifests(other))
        except AttributeError:  # no apk-specific methods, e.g. MissingArchive
            pass
        differences.extend(super().compare(other, *args, **kwargs))
        return differences


class Apksigner(Command):
    VALID_RETURNCODES = {0, 1}

    @tool_required("apksigner")
    def cmdline(self):
        # Older versions of the `apksigner` binary under /usr/bin (or similar)
        # are a symbolic link to the apksigner .jar file. If we detect a .jar
        # we resolve its 'real' location and pass that to `java -jar`, so we
        # don't need kernel binfmt_misc to execute. We can't do this in all
        # situations as later versions of apksigner use a wrapper script and
        # will therefore fail to run at all if we use `java -jar`.
        apksigner = os.path.realpath(find_executable("apksigner"))

        prefix = ["java", "-jar"] if apksigner.endswith(".jar") else []

        return prefix + [
            apksigner,
            "verify",
            "--verbose",
            "--print-certs",
            self.path,
        ]


class ApkFile(ZipFileBase):
    DESCRIPTION = "Android APK files"
    FILE_TYPE_HEADER_PREFIX = b"PK\x03\x04"
    FILE_TYPE_RE = re.compile(r"^((Java|Zip) archive data|Dalvik dex file)\b")
    FILE_EXTENSION_SUFFIX = {".apk"}
    CONTAINER_CLASSES = [ApkContainer, ZipContainer]

    def compare_details(self, other, source=None):
        differences = zipinfo_differences(self, other)

        try:
            x = Difference.from_operation(Apksigner, self.path, other.path)
            if x is not None:
                differences.insert(0, x)
        except RequiredToolNotFound as exc:  # noqa
            # Don't require apksigner
            self.add_comment(exc.get_comment())

        if androguard is None:
            self.add_comment(
                "'androguard' Python package not installed; cannot extract V2 signing keys."
            )
        else:
            x = Difference.from_text_readers(
                get_v2_signing_keys(self.path),
                get_v2_signing_keys(other.path),
                self.path,
                other.path,
                source="APK Signing Block",
            )
            if x is not None:
                differences.insert(0, x)

        return differences


def get_v2_signing_keys(path):
    from androguard.core.bytecodes import apk

    try:
        instance = apk.APK(path)
        instance.parse_v2_signing_block()
    except Exception:
        return ""

    def format_key(x):
        return "\n".join(textwrap.wrap(binascii.hexlify(x).decode("utf-8")))

    output = []
    for k, v in sorted(instance._v2_blocks.items()):
        output.append("Key {}:\n{}\n".format(hex(k), format_key(v)))

    return "\n".join(output)


def filter_apk_metadata(filepath, archive_name):
    new_filename = os.path.join(os.path.dirname(filepath), "APK metadata")

    logger.debug("Moving APK metadata from %s to %s", filepath, new_filename)

    # Strip the filename that was passed to apktool as its embedded in the
    # output. (It is unclear why this is conditional - see comments on
    # reproducible-builds/diffoscope#255)
    re_filename = re.compile(r"^apkFileName: %s" % re.escape(archive_name))

    with open(filepath) as in_, open(new_filename, "w") as out:
        out.writelines(x for x in in_ if not re_filename.match(x))

    os.remove(filepath)

    return new_filename
