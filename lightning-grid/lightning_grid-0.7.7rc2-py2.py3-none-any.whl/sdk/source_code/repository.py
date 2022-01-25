from contextlib import contextmanager
import os
from pathlib import Path
from shutil import copytree, ignore_patterns, rmtree
from typing import Optional, Set

import grid.sdk.source_code.gridignore as gridignore
from grid.sdk.source_code.git import check_github_repository, check_if_uncommited_files, \
    check_if_remote_head_is_different, execute_git_command
from grid.sdk.source_code.hashing import dirhash
from grid.sdk.utils import current_working_directory
from grid.sdk.utils.tar import tar_path
from grid.sdk.utils.uploader import S3Uploader


class LocalSourceCodeDir:
    """Utilities for managing local source-code used for creating Runs."""
    cache_location: Path = Path.home() / ".grid" / "cache" / "repositories"

    def __init__(self, path: Path):
        self.path = path

        # cache checksum version
        self._version: Optional[str] = None
        self._files_used_in_checksum: Optional[Set[Path]] = set()

        # create global cache location if it doesn't exist
        if not self.cache_location.exists():
            self.cache_location.mkdir(parents=True, exist_ok=True)

        # clean old cache entries
        self._prune_cache()

    @property
    def _ignore_patterns(self):
        """Generates set of paths from a `.gridignore` file. This is a wrapper for `gridignore.generate()`."""
        return gridignore.generate(src=self.path)

    @property
    def version(self):
        """
        Calculates the checksum of a local path.

        Parameters
        ----------
        path: Path
            Reference to a path.
        """
        # cache value to prevent doing this over again
        if self._version is not None:
            return self._version

        # stores both version and a set with the files used to generate the checksum
        self._files_used_in_checksum, self._version = dirhash(
            path=self.path, algorithm="blake2", ignore=self._ignore_patterns
        )
        return self._version

    @property
    def package_path(self):
        """Location to tarball in local cache."""
        filename = f"{self.version}.tar.gz"
        return self.cache_location / filename

    @contextmanager
    def packaging_session(self) -> Path:
        """Creates a local directory with source code that is used for creating a local source-code package."""
        session_path = self.cache_location / "packaging_sessions" / self.version
        try:
            rmtree(session_path, ignore_errors=True)
            copytree(self.path, session_path, ignore=ignore_patterns(*self._ignore_patterns))
            yield session_path
        finally:
            rmtree(session_path, ignore_errors=True)

    def _prune_cache(self) -> None:
        """Prunes cache; only keeps the 10 most recent items."""
        packages = sorted(self.cache_location.iterdir(), key=os.path.getmtime)
        for package in packages[10:]:
            if package.is_file():
                package.unlink(missing_ok=True)

    def package(self) -> Path:
        """Packages local path using tar."""
        if self.package_path.exists():
            return self.package_path
        # create a packaging session if not available
        with self.packaging_session() as session_path:
            tar_path(source_path=session_path, target_file=str(self.package_path), compression=True)
        return self.package_path

    def upload(self, url: str) -> None:
        """Uploads package to URL, usually pre-signed URL.

        Notes
        -----
        Since we do not use multipart uploads here, we cannot upload any
        packaged repository files which have a size > 2GB.

        This limitation should be removed during the datastore upload redesign
        """
        if self.package_path.stat().st_size > 2e9:
            raise OSError(
                "cannot upload directory code whose total fize size is greater than 2GB (2e9 bytes)"
            ) from None

        uploader = S3Uploader(
            presigned_urls={1: url},
            already_uploaded_parts=[],
            source_file=str(self.package_path),
            name=self.package_path.name,
            total_size=self.package_path.stat().st_size,
            split_size=self.package_path.stat().st_size
        )
        uploader.upload()


class GitRepository:
    """Utilities for managing git repositories."""
    def __init__(self, path: Path):
        self.path = Path(path).absolute()
        self.commit_sha = ""
        self.repo_name = ""
        with current_working_directory(path):
            check_github_repository()
            check_if_uncommited_files()
            check_if_remote_head_is_different()
            self.commit_sha = execute_git_command(['rev-parse', 'HEAD'])
            #  Get repo name
            repo_name = execute_git_command(["config", "--get", "remote.origin.url"])
            repo_name = repo_name.replace('git@github.com:', 'github.com/')
            repo_name = repo_name.replace('https://', '')
            repo_name = repo_name.replace('http://', '')  # noqa
            self.repo_name = repo_name.replace('.git', '')

            self.repository_root = execute_git_command(['rev-parse', '--show-toplevel'], cwd=self.path)

    def url(self):
        # TODO - Does this work
        return f"https://{self.repo_name}.git#ref={self.commit_sha}"

    def relative_working_dir(self) -> Path:
        return self.path.relative_to(self.repository_root)
