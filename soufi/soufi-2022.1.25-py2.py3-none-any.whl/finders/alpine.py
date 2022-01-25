# Copyright (c) 2021 Cisco Systems, Inc. and its affiliates
# All rights reserved.

import functools
import glob
import hashlib
import pathlib
import shutil
import subprocess  # nosec
import urllib
import warnings
from contextlib import closing
from pathlib import Path
from shutil import copyfile
from typing import Iterable, Union

from soufi import exceptions, finder

warnings.formatwarning = lambda msg, *x, **y: f'WARNING: {msg}\n'

API_TIMEOUT = 30  # seconds
# Shell snippet that will source an APKBUILD and spit out the vars that we
# need. CARCH is set to work around a bug in 3.12.0 scripts. CTARGET_ARCH
# is needed for more complex scripts like `community/go`.
SH_GET_APK_VARS = """
function die () {{
:
}}
export CARCH=$(arch)
export CTARGET_ARCH=$(arch)
. {file}
echo $source
echo $subpackages
echo $provides
echo $pkgver
echo $pkgrel
echo $sha512sums
"""


class AlpineFinder(finder.SourceFinder):
    """Find Alpine APK sources.

    :param aports_dir: An aports branch checked out locally.

    It is recommended to clone the branch like this to save time/space:
    git clone --depth 1 --branch vN.N.N git://git.alpinelinux.org/aports

    The results of parsing each directory with the branch is cached, so it
    is also recommended to check out each branch into its own place.

    The caller therefore must know in which release branch the package is
    likely to reside as it is impossible to know this information outside
    the context of an actual distro image.  This Finder *could* iterate
    over every release, but this is inefficient. There's nothing
    stopping the caller doing this though, as required.
    """

    distro = finder.Distro.alpine.value

    # See https://wiki.alpinelinux.org/wiki/APKBUILD_Reference
    # for info on dealing with APKBUILD files.

    def __init__(self, *args, aports_dir, **kwargs):
        # TODO: take a sudo user name that will be used to run APKBUILDs
        self.aports_dir = aports_dir
        super().__init__(*args, **kwargs)

    @functools.lru_cache(maxsize=128)
    def _find_apkbuilds(self, aports_dir):
        """Given a starting dir, find all the APKBUILD files.

        :return: A dict mapping package names to the APKBUILD path.
        """
        apkbuilds = {}
        for apkbuild in glob.iglob(
            f"{aports_dir}/**/*/APKBUILD", recursive=True
        ):
            path = Path(apkbuild)
            package = path.parent.name
            apkbuilds[package] = path
        return apkbuilds

    def _find_apkbuild_path(self, name):
        """Return the Path to the APKBUILD for package with 'name'."""
        apkbuilds = self._find_apkbuilds(self.aports_dir)
        path = apkbuilds.get(name)
        if path is not None:
            return path

        path = self._search_subpackages(name, apkbuilds)
        return path

    def _search_subpackages(
        self, name: str, apkbuilds: dict
    ) -> Union[Path, None]:
        """Return path to APKBUILD containing named subpackage."""
        for path in apkbuilds.values():
            apkbuild = self._parse_apkbuild(path)
            if name in apkbuild['subpackages']:
                return path
            for prov in apkbuild['provides']:
                if '=' not in prov:
                    # A virtual package, ignore.
                    continue
                prov_name, _ = prov.split('=', 1)
                if name == prov_name:
                    return path
        return None

    def _parse_apkbuild(self, path: Path) -> dict:
        """Return a dict with partial metadata from the APKBUILD."""
        # TODO: run with sudo user, for security purposes.
        cmd = ['bash', '-c', SH_GET_APK_VARS.format(file=str(path))]
        try:
            # This must run with a CWD of where the APKBUILD is located,
            # since it can use relative paths to source other files.
            output = subprocess.run(  # nosec
                cmd, cwd=path.parent, capture_output=True, check=True
            )
            if output.stderr:
                raise subprocess.SubprocessError(output.stderr)
        except subprocess.SubprocessError as e:
            raise exceptions.DownloadError(str(e))
        parsed = output.stdout.decode('utf-8').splitlines()
        # Prepend patch sources with the full path.
        all_sources = parsed[0].split()
        sources = []
        for source in all_sources:
            for scheme in ('http://', 'https://', 'ftp://'):
                if scheme in source:
                    sources.append(source)
                    break
            else:
                abspath = path.resolve().parent / source
                sources.append(f"file://{abspath}")

        # Subpackages can be of the form name:_function. This is where the
        # package is handled in a function in the APKBUILD. We can strip that
        # out for the purposes of matching subpackages.
        subpackages = [item.split(':', 1)[0] for item in parsed[1].split()]
        # SHA-512 checksums for source archives are provided as a big flat list
        # of the form (DIGEST, NAME, [...])  Turn it into a mapping of
        # name->digest for validation lookups later.
        sha512sums = parsed[5].split()
        digests, filenames = sha512sums[0::2], sha512sums[1::2]
        sha512sums_map = dict(zip(filenames, digests))
        return {
            'source': sources,
            'subpackages': subpackages,
            'provides': parsed[2].split(),
            'pkgver': parsed[3],
            'pkgrel': parsed[4],
            'sha512sums': sha512sums_map,
        }

    def _find(self):
        # Main entrypoint from the parent class.
        path = self._find_apkbuild_path(self.name)
        if path is None:
            raise exceptions.SourceNotFound()
        apkbuild = self._parse_apkbuild(path)
        version = f"{apkbuild['pkgver']}-{apkbuild['pkgrel']}"
        # See if there's an 'r' in the release part of the version, and remove
        # it.
        base_version, release = self.version.rsplit('-', 1)
        if release.startswith('r'):
            expect_version = f"{base_version}-{release[1:]}"
        else:
            expect_version = self.version
        if version == expect_version:
            return AlpineDiscoveredSource(
                apkbuild['source'], sha512sums=apkbuild['sha512sums']
            )
        raise exceptions.SourceNotFound()


class AlpineDiscoveredSource(finder.DiscoveredSource):
    """A discovered Alpine source package."""

    def __init__(self, urls: Iterable[str], sha512sums=None):
        self.sha512sums = sha512sums or {}
        super().__init__(urls)

    def populate_archive(self, temp_dir, tar):
        # The file name is the last segment of the URL path, unless the source
        # is the special format containing a ::, in which case the part
        # preceding the :: is the file name.
        names = []
        urls = []
        for url in self.urls:
            if '::' in url:
                name, url = url.split('::', 1)
            else:
                name = url.rsplit('/', 1)[-1]
            names.append(name)
            urls.append(url)

        for name, url in zip(names, urls):
            if url.startswith('file:'):
                _, srcfile = url.split('file://', 1)
                arcfile_name = Path(temp_dir) / name
                copyfile(srcfile, arcfile_name)
            elif url.startswith('ftp://'):
                # Requests cannot do FTP, fall back to urllib.
                arcfile_name = self.download_ftp_file(temp_dir, name, url)
            else:
                arcfile_name = self.download_file(
                    temp_dir, name, url, timeout=API_TIMEOUT
                )
            if name in self.sha512sums:
                self.verify_sha512sum(arcfile_name, self.sha512sums[name])
            else:
                warnings.warn(
                    f'No checksum for source file {name}, cannot verify'
                )
            tar.add(arcfile_name, arcname=name, filter=self.reset_tarinfo)

    def verify_sha512sum(self, filename, sha512sum):
        """Verify that the contents of filename match the provided sha512sum.

        :return: True on a checksum match.
        :raises: exceptions.DownloadError on a checksum mismatch.
        :raises: IOError on any problem reading the input file.
        """
        file_hash = hashlib.sha512()
        with open(filename, 'rb') as f:
            # TODO(nic): this loop can be simplified with a walrus operator
            #  if/when Python 3.7 support is dropped
            chunk = f.read(0x10000)
            while chunk:
                file_hash.update(chunk)
                chunk = f.read(0x10000)
        if file_hash.hexdigest() == sha512sum:
            return True
        raise exceptions.DownloadError(
            f'checksum of dowmloaded file {filename} does not match: '
            f'{file_hash.hexdigest()} != {sha512sum}'
        )

    def download_ftp_file(self, temp_dir, name, url):
        tmp_file_name = pathlib.Path(temp_dir) / name
        with closing(
            # B310 restricts permitted schemes, but we only call with ftp here.
            urllib.request.urlopen(url, timeout=API_TIMEOUT)  # nosec B310
        ) as ftp, open(tmp_file_name, 'wb') as f:
            shutil.copyfileobj(ftp, f)
        return tmp_file_name

    def __repr__(self) -> str:
        return "\n".join(self.urls)
