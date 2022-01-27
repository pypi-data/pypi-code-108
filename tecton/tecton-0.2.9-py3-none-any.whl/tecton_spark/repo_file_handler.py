import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List
from typing import Optional
from typing import Set


@dataclass
class RepoData:
    # paths and file set are different representations of the same data
    paths: List[Path] = None
    file_set: Set[str] = None
    root: str = None

    @property
    def initialized(self):
        return self.paths is not None


_repo_data = RepoData()

# Prepare a repo for tecton objects to be processed.
# If file_in_repo is not set, expects the current directory to be inside the feature repo.
def ensure_prepare_repo(file_in_repo: Optional[str] = None):
    if _repo_data.initialized:
        # repo is already prepared
        return
    root = _maybe_get_repo_root(file_in_repo)
    if root is None:
        raise Exception(f"Feature repository root not found. Run `tecton init` to set it.")
    paths = get_repo_files(root)
    file_set = {str(f) for f in paths}
    _repo_data.paths, _repo_data.file_set, _repo_data.root = paths, file_set, root


def repo_files() -> List[Path]:
    if not _repo_data.initialized:
        raise Exception("Repo is not prepared")
    return _repo_data.paths


def repo_files_set() -> Set[str]:
    if not _repo_data.initialized:
        raise Exception("Repo is not prepared")
    return _repo_data.file_set


def repo_root() -> str:
    if not _repo_data.initialized:
        raise Exception("Repo is not prepared")
    return _repo_data.root


def _fake_init_for_testing():
    fake_root = Path()
    _repo_data.paths, _repo_data.file_set, _repo_data.root = [fake_root], {str(fake_root)}, fake_root


# Finds the repo root of a given python file (a parent directory containing ".tecton")
# If a file is not passed in, searches the current directory's parents.
# Returns None if the root is not found
def _maybe_get_repo_root(file_in_repo: Optional[str] = None) -> Optional[str]:
    if _repo_data.root is not None:
        return _repo_data.root

    if file_in_repo is None:
        d = Path().resolve()
    else:
        d = Path(file_in_repo)
    while d.parent != d and d != Path.home():
        tecton_cfg = d / Path(".tecton")
        if tecton_cfg.exists():
            _repo_data.root = str(d)
            return _repo_data.root
        d = d.parent
    return None


def _get_ignored_files(repo_root: Path) -> Set[Path]:
    import pathspec

    ignorefile = repo_root / Path(".tectonignore")
    if not ignorefile.exists():
        return set()

    with open(ignorefile, "r") as f:
        spec = pathspec.PathSpec.from_lines("gitwildmatch", f)
        return {repo_root / file_name for file_name in spec.match_tree(str(repo_root))}


def get_repo_files(root: str, suffixes=[".py", ".yml", "yaml"]) -> List[Path]:
    root_path = Path(root)
    repo_files = [p.resolve() for p in root_path.glob("**/*") if p.suffix in suffixes]

    # Ignore virtualenv directory if any, typically you'd have /some/path/bin/python as an
    # interpreter, so we want to skip anything under /some/path/
    if sys.executable:
        python_dir = Path(sys.executable).parent.parent

        # we might be dealing with virtualenv
        if root_path.resolve() in python_dir.parents:
            repo_files = [p for p in repo_files if python_dir not in p.parents]

    # Filter out files under hidden dirs starting with "/." for PosixPath or "\." for WindowsPath
    repo_files = list(filter(lambda p: "/." not in str(p) and "\." not in str(p), repo_files))

    # Filter out files that match glob expressions in .tectonignore
    ignored_files = _get_ignored_files(root_path)
    filtered_files = [p for p in repo_files if p not in ignored_files]

    return filtered_files
