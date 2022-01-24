"""Setup repro environment.

Downloads and installs particular mongodb versions (each binary is renamed
to include its version) into an install directory and symlinks the binaries
with versions to another directory. This script supports community and
enterprise builds.
"""
import argparse
import logging
import os
import platform
import re
import subprocess
import sys
import time
from itertools import chain
from typing import Any, Dict, List, NamedTuple, Optional

import distro
import structlog
import yaml
from requests.exceptions import HTTPError

from db_contrib_tool.plugin import PluginInterface, Subcommand, SubcommandResult
from db_contrib_tool.setup_repro_env import config, download
from db_contrib_tool.utils import evergreen_conn, is_windows

SUBCOMMAND = "setup-repro-env"

LOGGER = structlog.getLogger(__name__)


class SetupReproEnvError(Exception):
    """Errors in setup_repro_env.py.

    The base class of exceptions for this file/subcommand.
    """

    pass


def setup_logging(debug=False):
    """Enable logging."""
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        format="[%(asctime)s - %(name)s - %(levelname)s] %(message)s",
        level=log_level,
        stream=sys.stdout,
    )
    logging.getLogger("evergreen").setLevel(logging.WARNING)
    logging.getLogger("github").setLevel(logging.WARNING)
    structlog.configure(logger_factory=structlog.stdlib.LoggerFactory())


def infer_platform(edition=None, version=None):
    """Infer platform for popular OS."""
    syst = platform.system()
    pltf = None
    if syst == "Darwin":
        pltf = "osx"
    elif syst == "Windows":
        pltf = "windows"
        if edition == "base" and version == "4.2":
            pltf += "_x86_64-2012plus"
    elif syst == "Linux":
        id_name = distro.id()
        if id_name in ("ubuntu", "rhel"):
            pltf = id_name + distro.major_version() + distro.minor_version()
    if pltf is None:
        raise ValueError(
            "Platform cannot be inferred. Please specify platform explicitly with -p. "
            f"Available platforms can be found in {config.SETUP_REPRO_ENV_CONFIG}."
        )
    else:
        return pltf


def get_merge_base_commit(version: str) -> Optional[str]:
    """Get merge-base commit hash between origin/master and version."""
    cmd = ["git", "merge-base", "origin/master", f"origin/v{version}"]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)

    if result.returncode != 0:
        curr_branch_cmd = ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        curr_branch_res = subprocess.run(
            curr_branch_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
        )

        if curr_branch_res.stdout.decode("utf-8").strip() == "master":
            LOGGER.warning(
                "Git command failed.",
                cmd=cmd,
                error=result.stderr.decode("utf-8").strip(),
            )
            LOGGER.warning("Falling back to the latest starting from the current commit.")

            cmd = ["git", "rev-parse", "--verify", "HEAD"]
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )

    if result.returncode != 0:
        LOGGER.warning(
            "Git command failed.",
            cmd=cmd,
            error=result.stderr.decode("utf-8").strip(),
        )
        LOGGER.warning("Falling back to the latest.")
        return None
    commit_hash = result.stdout.decode("utf-8").strip()
    LOGGER.info("Found commit.", cmd=cmd, commit=commit_hash)
    return commit_hash


class EvgURLInfo(NamedTuple):
    """Wrapper around compile URLs with metadata."""

    urls: Dict[str, Any] = {}
    evg_version_id: str = None


class SetupReproEnv(Subcommand):
    """Main class for the setup repro environment subcommand."""

    def __init__(
        self,
        download_options,
        install_dir="",
        link_dir="",
        mv_platform=None,
        edition=None,
        architecture=None,
        versions=None,
        variant=None,
        install_last_lts=None,
        install_last_continuous=None,
        evergreen_config=None,
        debug=None,
        ignore_failed_push=False,
        evg_versions_file=None,
    ):
        """Initialize."""
        setup_logging(debug)
        self.install_dir = os.path.abspath(install_dir)
        self.link_dir = os.path.abspath(link_dir)

        self.edition = edition.lower() if edition else None
        self.platform = mv_platform.lower() if mv_platform else None
        self.inferred_platform = bool(self.platform is None)
        self.architecture = architecture.lower() if architecture else None
        self.variant = variant.lower() if variant else None
        self.versions = versions
        self.install_last_lts = install_last_lts
        self.install_last_continuous = install_last_continuous
        self.ignore_failed_push = ignore_failed_push

        self.download_binaries = download_options.download_binaries
        self.download_symbols = download_options.download_symbols
        self.download_artifacts = download_options.download_artifacts
        self.download_python_venv = download_options.download_python_venv

        self.evg_api = evergreen_conn.get_evergreen_api(evergreen_config)
        with open(config.SETUP_REPRO_ENV_CONFIG) as file_handle:
            raw_yaml = yaml.safe_load(file_handle)
        self.config = config.SetupReproEnvConfig(raw_yaml)

        self.evg_versions_file = evg_versions_file

        self._is_windows = is_windows()
        self._windows_bin_install_dirs = []

    @staticmethod
    def _get_bin_suffix(version, evg_project_id):
        """Get the multiversion bin suffix from the evergreen project ID."""
        if re.match(r"(\d+\.\d+)", version):
            # If the cmdline version is already a semvar, just use that.
            return version
        elif evg_project_id == "mongodb-mongo-master":
            # If the version is not a semvar and the project is the master waterfall,
            # we can't add a suffix.
            return ""
        else:
            # Use the Evergreen project ID as fallback.
            return re.search(r"(\d+\.\d+$)", evg_project_id).group(0)

    @staticmethod
    def get_multiversionconstants():
        """Import multiversionconstants from resmoke."""
        if not os.path.isfile(
            os.path.join(os.getcwd(), "buildscripts", "resmokelib", "multiversionconstants.py")
        ):
            LOGGER.error("This command should be run from the root of the mongo repo.")
            LOGGER.error(
                "If you're running it from the root of the mongo repo and still seeing"
                " this error, please reach out in #server-testing slack channel."
            )
            raise SetupReproEnvError()
        sys.path.append(os.path.join(os.getcwd(), "buildscripts", "resmokelib"))
        try:
            import multiversionconstants as _multiversionconstants
        except ImportError:
            LOGGER.error("Could not import `multiversionconstants`.")
            LOGGER.error(
                "If you're running this command from the root of the mongo repo,"
                " please reach out in #server-testing slack channel."
            )
            raise
        else:
            return _multiversionconstants

    def _get_release_versions(
        self, install_last_lts: Optional[bool], install_last_continuous: Optional[bool]
    ) -> List[str]:
        """Return last-LTS and/or last-continuous versions."""
        multiversionconstants = self.get_multiversionconstants()
        releases = {
            multiversionconstants.LAST_LTS_FCV: install_last_lts,
            multiversionconstants.LAST_CONTINUOUS_FCV: install_last_continuous,
        }
        out = {version for version, requested in releases.items() if requested}

        return list(out)

    def execute(self):
        """Execute setup repro env mongodb."""
        if self.install_last_lts or self.install_last_continuous:
            self.versions.extend(
                self._get_release_versions(self.install_last_lts, self.install_last_continuous)
            )
            self.versions = list(set(self.versions))

        downloaded_versions = []

        for version in self.versions:
            LOGGER.info("Setting up version.", version=version)
            LOGGER.info("Fetching download URLs from Evergreen.")

            try:
                self.platform = (
                    infer_platform(self.edition, version)
                    if self.inferred_platform
                    else self.platform
                )
                urls_info = self.get_latest_urls(version)
                if not urls_info.urls:
                    LOGGER.warning(
                        "Latest URLs are not available, falling back to getting the URLs for a specific version."
                    )
                    urls_info = self.get_urls(version, self.variant)
                if not urls_info.urls:
                    LOGGER.warning(
                        "Specific version URLs are not available, falling back to getting the URLs from"
                        " 'mongodb-mongo-master' project preceding the merge-base commit."
                    )
                    merge_base_revision = get_merge_base_commit(version)
                    urls_info = self.get_latest_urls("master", merge_base_revision)
                if not urls_info.urls:
                    raise SetupReproEnvError("URLs are not available for the version.")

                urls = urls_info.urls

                bin_suffix = self._get_bin_suffix(version, urls["project_identifier"])
                # Give each version a unique install dir
                install_dir = os.path.join(self.install_dir, version)

                self.download_and_extract(urls, bin_suffix, install_dir)
                downloaded_versions.append(urls_info.evg_version_id)
            except (
                evergreen_conn.EvergreenConnError,
                download.DownloadError,
                SetupReproEnvError,
            ) as ex:
                LOGGER.error(ex)
                LOGGER.error("Setup version failed.", version=version)
            else:
                LOGGER.info("Setup version completed.", version=version)

            LOGGER.info("-" * 50)

        if self._is_windows:
            self._write_windows_install_paths(self._windows_bin_install_dirs)

        if self.evg_versions_file:
            self._write_evg_versions_file(self.evg_versions_file, downloaded_versions)

        if len(downloaded_versions) < len(self.versions):
            LOGGER.error(
                "Some versions were not able to setup.",
                failed_versions=[v for v in self.versions if v not in downloaded_versions],
            )
            return SubcommandResult.FAIL
        return SubcommandResult.SUCCESS

    def download_and_extract(self, urls, bin_suffix, install_dir):
        """Download and extract values indicated in `urls`."""
        artifacts_url = urls.get("Artifacts", "") if self.download_artifacts else None
        binaries_url = urls.get("Binaries", "") if self.download_binaries else None
        python_venv_url = (
            urls.get("Python venv (see included README.txt)", "")
            or urls.get("Python venv (see included venv_readme.txt)", "")
            if self.download_python_venv
            else None
        )
        symbols_url = (
            urls.get(" mongo-debugsymbols.tgz", "")
            or urls.get("mongo-debugsymbols.tgz", "")
            or urls.get(" mongo-debugsymbols.zip", "")
            or urls.get("mongo-debugsymbols.zip", "")
            if self.download_symbols
            else None
        )

        if self.download_symbols and not symbols_url:
            raise download.DownloadError("Symbols download requested but not URL available")

        if self.download_artifacts and not artifacts_url:
            raise download.DownloadError(
                "Evergreen artifacts download requested but not URL available"
            )

        if self.download_binaries and not binaries_url:
            raise download.DownloadError("Binaries download requested but not URL available")

        if self.download_python_venv and not python_venv_url:
            raise download.DownloadError("Python venv download requested but not URL available")

        self.setup_mongodb(
            artifacts_url,
            binaries_url,
            symbols_url,
            python_venv_url,
            install_dir,
            bin_suffix,
            link_dir=self.link_dir,
            install_dir_list=self._windows_bin_install_dirs,
        )

    @staticmethod
    def _write_windows_install_paths(paths):
        with open(config.WINDOWS_BIN_PATHS_FILE, "a") as out:
            if os.stat(config.WINDOWS_BIN_PATHS_FILE).st_size > 0:
                out.write(os.pathsep)
            out.write(os.pathsep.join(paths))

        LOGGER.info(f"Finished writing binary paths on Windows to {config.WINDOWS_BIN_PATHS_FILE}")

    @staticmethod
    def _write_evg_versions_file(file_name: str, versions: List[str]):
        with open(file_name, "a") as out:
            out.write("\n".join(versions))

        LOGGER.info(
            f"Finished writing downloaded Evergreen versions to {os.path.abspath(file_name)}"
        )

    def get_latest_urls(
        self, version: str, start_from_revision: Optional[str] = None
    ) -> EvgURLInfo:
        """Return latest urls."""
        urls = {}
        actual_version_id = None

        # Assuming that project names contain <major>.<minor> version
        evg_project = f"mongodb-mongo-v{version}"
        if version == "master":
            evg_project = "mongodb-mongo-master"

        evg_versions = evergreen_conn.get_evergreen_versions(self.evg_api, evg_project)
        evg_version = None
        try:
            evg_version = next(evg_versions)
        except HTTPError as err:
            if err.response.status_code != 404:
                raise
        except StopIteration:
            return EvgURLInfo()

        buildvariant_name = self.get_buildvariant_name(version)
        LOGGER.debug("Found buildvariant.", buildvariant_name=buildvariant_name)

        found_start_revision = start_from_revision is None

        for evg_version in chain(iter([evg_version]), evg_versions):
            # Skip all versions until we get the revision we should start looking from
            if found_start_revision is False and evg_version.revision != start_from_revision:
                LOGGER.warning("Skipping evergreen version.", evg_version=evg_version)
                continue
            else:
                found_start_revision = True

            if hasattr(evg_version, "build_variants_map"):
                if buildvariant_name not in evg_version.build_variants_map:
                    continue

                curr_urls = evergreen_conn.get_compile_artifact_urls(
                    self.evg_api,
                    evg_version,
                    buildvariant_name,
                    ignore_failed_push=self.ignore_failed_push,
                )
                if "Binaries" in curr_urls:
                    urls = curr_urls
                    actual_version_id = evg_version.version_id
                    break

        return EvgURLInfo(urls=urls, evg_version_id=actual_version_id)

    def get_urls(self, version: str, buildvariant_name: Optional[str] = None) -> EvgURLInfo:
        """Return multiversion urls for a given version (commit hash or evergreen_version_id)."""
        evergreen_projects = evergreen_conn.get_evergreen_projects(self.evg_api)

        evg_version = evergreen_conn.get_evergreen_version(
            evergreen_projects, self.evg_api, version
        )
        if evg_version is None:
            return EvgURLInfo()

        if not buildvariant_name:
            evg_project = evg_version.project_identifier
            LOGGER.debug("Found evergreen project.", evergreen_project=evg_project)

            try:
                major_minor_version = re.findall(r"\d+\.\d+", evg_project)[-1]
            except IndexError:
                major_minor_version = "master"

            buildvariant_name = self.get_buildvariant_name(major_minor_version)
            LOGGER.debug("Found buildvariant.", buildvariant_name=buildvariant_name)

        if buildvariant_name not in evg_version.build_variants_map:
            raise ValueError(
                f"Buildvariant {buildvariant_name} not found in evergreen. "
                f"Available buildvariants can be found in {config.SETUP_REPRO_ENV_CONFIG}."
            )

        urls = evergreen_conn.get_compile_artifact_urls(
            self.evg_api, evg_version, buildvariant_name, ignore_failed_push=self.ignore_failed_push
        )

        return EvgURLInfo(urls=urls, evg_version_id=evg_version.version_id)

    @staticmethod
    def setup_mongodb(
        artifacts_url,
        binaries_url,
        symbols_url,
        python_venv_url,
        install_dir,
        bin_suffix=None,
        link_dir=None,
        install_dir_list=None,
    ):
        """Download, extract and symlink."""

        urls = [
            url
            for url in [artifacts_url, binaries_url, symbols_url, python_venv_url]
            if url is not None
        ]

        for url in urls:

            def try_download(download_url):
                tarball = download.download_from_s3(download_url)
                download.extract_archive(tarball, install_dir)
                os.remove(tarball)

            try:
                try_download(url)
            except Exception as err:
                LOGGER.warning("Setting up tarball failed with error, retrying once...", error=err)
                time.sleep(1)
                try_download(url)

        if binaries_url is None:
            return

        if not link_dir:
            raise ValueError("link_dir must be specified if downloading binaries")

        if is_windows():
            LOGGER.info(
                "Linking to install_dir on Windows; executable have to live in different working"
                " directories to avoid DLLs for different versions clobbering each other"
            )
            link_dir = download.symlink_version(bin_suffix, install_dir, None)
        else:
            link_dir = download.symlink_version(bin_suffix, install_dir, link_dir)
        install_dir_list.append(link_dir)

    def get_buildvariant_name(self, major_minor_version):
        """
        Return buildvariant name.

        Gets buildvariant name from evergreen_conn.get_buildvariant_name() -- if not user specified.
        """
        if self.variant:
            return self.variant

        return evergreen_conn.get_buildvariant_name(
            config=self.config,
            edition=self.edition,
            platform=self.platform,
            architecture=self.architecture,
            major_minor_version=major_minor_version,
        )


class _DownloadOptions(object):
    def __init__(self, db, ds, da, dv):
        self.download_binaries = db
        self.download_symbols = ds
        self.download_artifacts = da
        self.download_python_venv = dv


class SetupReproEnvPlugin(PluginInterface):
    """Integration point for setup-repro-env."""

    DEFAULT_INSTALL_DIR = os.path.join(os.getcwd(), "build", "multiversion_bin")
    DEFAULT_LINK_DIR = os.getcwd()
    DEFAULT_WITH_ARTIFACTS_INSTALL_DIR = os.path.join(os.getcwd(), "repro_envs")
    DEFAULT_WITH_ARTIFACTS_LINK_DIR = os.path.join(
        DEFAULT_WITH_ARTIFACTS_INSTALL_DIR, "multiversion_bin"
    )

    @classmethod
    def _update_args(cls, args):
        """Update command-line arguments."""
        if not args.versions:
            args.install_last_lts = True
            args.install_last_continuous = True

        if args.download_artifacts:
            args.install_dir = cls.DEFAULT_WITH_ARTIFACTS_INSTALL_DIR
            args.link_dir = cls.DEFAULT_WITH_ARTIFACTS_LINK_DIR

    def parse(self, subcommand, parser, parsed_args, **kwargs):
        """Parse command-line arguments."""
        if subcommand != SUBCOMMAND:
            return None

        # Shorthand for brevity.
        args = parsed_args
        self._update_args(args)

        download_options = _DownloadOptions(
            db=(not args.skip_binaries),
            ds=args.download_symbols,
            da=args.download_artifacts,
            dv=args.download_python_venv,
        )

        return SetupReproEnv(
            install_dir=args.install_dir,
            link_dir=args.link_dir,
            mv_platform=args.platform,
            edition=args.edition,
            architecture=args.architecture,
            versions=args.versions,
            install_last_lts=args.install_last_lts,
            variant=args.variant,
            install_last_continuous=args.install_last_continuous,
            download_options=download_options,
            evergreen_config=args.evergreen_config,
            ignore_failed_push=(not args.require_push),
            evg_versions_file=args.evg_versions_file,
            debug=args.debug,
        )

    @classmethod
    def _add_args_to_parser(cls, parser):
        parser.add_argument(
            "-i",
            "--installDir",
            dest="install_dir",
            default=cls.DEFAULT_INSTALL_DIR,
            help=f"Directory to install the download archive,"
            f" [default: %(default)s, if `--downloadArtifacts` is passed: {cls.DEFAULT_WITH_ARTIFACTS_INSTALL_DIR}]",
        )
        parser.add_argument(
            "-l",
            "--linkDir",
            dest="link_dir",
            default=cls.DEFAULT_LINK_DIR,
            help=f"Directory to contain links to all binaries for each version in the install directory,"
            f" [default: %(default)s, if `--downloadArtifacts` is passed: {cls.DEFAULT_WITH_ARTIFACTS_LINK_DIR}]",
        )
        editions = ("base", "enterprise", "targeted")
        parser.add_argument(
            "-e",
            "--edition",
            dest="edition",
            choices=editions,
            default="enterprise",
            help="Edition of the build to download, [default: %(default)s].",
        )
        parser.add_argument(
            "-p",
            "--platform",
            dest="platform",
            help="Platform to download. "
            f"Available platforms can be found in {config.SETUP_REPRO_ENV_CONFIG}.",
        )
        parser.add_argument(
            "-a",
            "--architecture",
            dest="architecture",
            default="x86_64",
            help="Architecture to download, [default: %(default)s]. Examples include: "
            "'arm64', 'ppc64le', 's390x' and 'x86_64'.",
        )
        parser.add_argument(
            "-v",
            "--variant",
            dest="variant",
            default=None,
            help="Specify a variant to use, which supersedes the --platform, --edition and"
            " --architecture options.",
        )
        parser.add_argument(
            "versions",
            nargs="*",
            help="Accepts binary versions, `master`, full git commit hashes, evergreen version ids."
            " Binary version examples: <major.minor>, 4.2, 4.4, 5.0 etc. If no version is specified"
            " the last LTS and the last continuous versions will be installed.",
        )
        parser.add_argument(
            "--installLastLTS",
            dest="install_last_lts",
            action="store_true",
            help="If specified, the last LTS version will be installed",
        )
        parser.add_argument(
            "--installLastContinuous",
            dest="install_last_continuous",
            action="store_true",
            help="If specified, the last continuous version will be installed",
        )
        parser.add_argument(
            "-sb",
            "--skipBinaries",
            dest="skip_binaries",
            action="store_true",
            help="whether to skip downloading binaries.",
        )
        parser.add_argument(
            "-ds",
            "--downloadSymbols",
            dest="download_symbols",
            action="store_true",
            help="whether to download debug symbols.",
        )
        parser.add_argument(
            "-da",
            "--downloadArtifacts",
            dest="download_artifacts",
            action="store_true",
            help="whether to download artifacts.",
        )
        parser.add_argument(
            "-dv",
            "--downloadPythonVenv",
            dest="download_python_venv",
            action="store_true",
            help="whether to download python venv.",
        )
        parser.add_argument(
            "-ec",
            "--evergreenConfig",
            dest="evergreen_config",
            help="Location of evergreen configuration file. If not specified it will look "
            f"for it in the following locations: {evergreen_conn.EVERGREEN_CONFIG_LOCATIONS}",
        )
        parser.add_argument(
            "-d",
            "--debug",
            dest="debug",
            action="store_true",
            help="Set DEBUG logging level.",
        )
        parser.add_argument(
            "-rp",
            "--require-push",
            dest="require_push",
            action="store_true",
            help="Require the push task to be successful for assets to be downloaded",
        )
        # Hidden flag to write out the Evergreen versions of the downloaded binaries.
        parser.add_argument(
            "--evgVersionsFile", dest="evg_versions_file", default=None, help=argparse.SUPPRESS
        )

    def add_subcommand(self, subparsers):
        """Create and add the parser for the subcommand."""
        parser = subparsers.add_parser(SUBCOMMAND, help=__doc__)
        self._add_args_to_parser(parser)
