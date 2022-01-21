import datetime
import fnmatch
import json
import os
import tempfile
from logging import Logger
from typing import IO, Any, Dict, Iterable, List, Tuple, Union

import valohai_cli.adhoc as adhoc  # Keep this import style so tests can mock the function
from valohai_cli.packager import (
    PackageFileInfo,
    get_files_for_package,
    package_files_into,
)
from valohai_yaml.objs import Mount

import jupyhai.utils
from jupyhai.consts import (
    IPYKERNEL_VERSION,
    JUPYTER_VERSION_LEGACY,
    NBCONVERT_VERSION_LEGACY,
    PAPERMILL_VERSION,
    PAPERMILL_VERSION_LEGACY,
    SEABORN_VERSION_LEGACY,
)
from jupyhai.utils.notebooks import parse_ipynb, parse_parameters_and_inputs
from jupyhai.yaml_generator import write_valohai_yaml


def is_valid_path(path: str, ignore: Iterable[str]) -> bool:
    if '.valohai' in path:
        # Ignore the .valohai folder that contains the user's security token, settings, etc.
        # It should be ignored by packager already, but we want to be safe here
        return False
    for ignored in ignore:
        if fnmatch.fnmatch(path, ignored) or ignored in path:
            return False
    return True


def write_prepare_script(f: IO, legacy: bool = False) -> None:
    # Legacy notebook is one that has use `parameters` or `inputs` tags and expects our own Papermill fork
    if legacy:
        # TODO: the "hash" invocation doesn't version-check papermill
        with open(os.path.join(os.path.dirname(__file__), "templates/prepare_bash_template_legacy.txt"), "r") as t:
            content = t.read().strip().format(
                PAPERMILL_VERSION=PAPERMILL_VERSION_LEGACY,
                NBCONVERT_VERSION=NBCONVERT_VERSION_LEGACY,
                JUPYTER_VERSION=JUPYTER_VERSION_LEGACY,
                SEABORN_VERSION=SEABORN_VERSION_LEGACY,
            )
    else:
        with open(os.path.join(os.path.dirname(__file__), "templates/prepare_bash_template.txt"), "r") as t:
            content = t.read().strip().format(
                PAPERMILL_VERSION=PAPERMILL_VERSION,
                IPYKERNEL_VERSION=IPYKERNEL_VERSION,
            )
    f.write(content)


class PackagePreparer:
    def __init__(self, root_dir: str, log: Logger) -> None:
        project = jupyhai.utils.get_current_project()
        if not project:
            raise ValueError("No current project")
        self.project = project
        self.log = log
        self.base_dir = root_dir
        self.temp_dir = tempfile.mkdtemp(prefix='jupyhai-prepare-')

    def measure_commit(
        self, ignore: Iterable[str], notebook_path: str
    ) -> Tuple[int, int]:
        # Note: valohai.yaml and prepare.sh don't exist yet here, but they will not impact package size much
        total_uncompressed_size = 0
        total_file_count = 0

        files = get_files_for_package(dir=self.base_dir, ignore_patterns=ignore)

        # Guard against original notebook ignored by the ignore filter (for example "*.ipynb")
        if notebook_path not in files and os.path.isfile(notebook_path):
            files[notebook_path] = PackageFileInfo(
                source_path=notebook_path, stat=os.stat(notebook_path)
            )

        for name, pfi in files.items():
            stat = pfi.stat
            total_uncompressed_size += stat.st_size
            total_file_count += 1

        return total_file_count, total_uncompressed_size

    def generate_commit(
        self,
        notebook_path: str,
        content: str,
        ignore: Iterable[str],
        mounts: List[Mount],
    ) -> dict:
        notebook_relative_path = os.path.relpath(notebook_path, self.base_dir)

        # Generate the notebook file, valohai.yaml, and the prepare script
        generated_package_files = self.get_generated_files(
            notebook_relative_path, content, mounts
        )

        # Collect all other files from the notebook's directory
        src_package_files = {
            name: pfi
            for (name, pfi) in get_files_for_package(
                dir=self.base_dir, ignore_patterns=ignore
            ).items()
            if is_valid_path(pfi.source_path, ignore)
        }

        package_files = {}
        package_files.update(src_package_files)
        package_files.update(generated_package_files)
        commit_obj = self.package_into_commit(package_files)
        return commit_obj

    def package_into_commit(
        self, package_files: Dict[str, PackageFileInfo]
    ) -> Dict[str, Any]:
        # TODO: write a file manifest into `temp_dir`?
        self.log.info(
            'Packaging {n} files ({names})'.format(
                n=len(package_files), names=', '.join(sorted(package_files.keys()))
            )
        )
        # On Windows, you can't open another handle to a O_TEMPORARY file while it's still open.
        # That's why we need to set `delete=False` the cleanup manually...
        # See: https://github.com/bravoserver/bravo/issues/111
        #      https://docs.python.org/3/library/tempfile.html#tempfile.NamedTemporaryFile
        #      https://bugs.python.org/issue14243
        try:
            with tempfile.NamedTemporaryFile(
                suffix='.tgz', mode='wb', prefix='jupyhai-', delete=False
            ) as fp:
                temp_name = fp.name
                package_files_into(fp, package_files, progress=False)
                return adhoc.create_adhoc_commit_from_tarball(
                    project=self.project,
                    tarball=fp.name,
                    description='Jupyhai Notebook {}'.format(
                        datetime.datetime.utcnow().isoformat()
                    ),
                )
        finally:
            try:
                os.unlink(temp_name)
            except Exception:
                pass

    def get_generated_files(
        self,
        notebook_relative_path: str,
        content: Union[str, dict],
        mounts: List[Mount],
    ) -> Dict[str, PackageFileInfo]:
        temp_notebook_path = os.path.join(self.temp_dir, notebook_relative_path)
        notebook_dir, notebook_name = os.path.split(temp_notebook_path)
        os.makedirs(notebook_dir, exist_ok=True)
        with open(temp_notebook_path, 'w', newline='\n') as nb_fp:
            # Peel the "type"/"content" wrapper off:
            ipynb_content = parse_ipynb(content)
            json.dump(ipynb_content, nb_fp)
        prepare_script_path = os.path.join(self.temp_dir, 'prepare.sh')
        with open(prepare_script_path, "w", newline='\n') as f:
            uses_tags = parse_parameters_and_inputs(content).uses_tags
            write_prepare_script(f, legacy=uses_tags)
        valohai_yaml_path = os.path.join(self.temp_dir, 'valohai.yaml')
        with open(valohai_yaml_path, 'w', newline='\n') as f:
            write_valohai_yaml(
                f,
                notebook_relative_path=notebook_relative_path,
                content=content,
                mounts=mounts,
                log=self.log,
            )
        # Generate the initial `package_files` dict based on the three files we just wrote into
        # the temporary directory
        generated_package_files = {
            os.path.relpath(os.path.join(root, name), self.temp_dir): PackageFileInfo(
                source_path=os.path.join(root, name), stat=None
            )
            for root, dirs, files in os.walk(self.temp_dir)
            for name in files
            if not name.startswith('.')
        }

        return generated_package_files
