import json
import os

from valohai_cli.exceptions import PackageTooLarge

from jupyhai import consts
from jupyhai.excs import Problem
from jupyhai.handlers.base import JupyhaiHandler
from jupyhai.preparer import PackagePreparer
from jupyhai.utils import get_current_ignore, get_current_mounts


def get_effective_ignore(ignore: list) -> list:
    return list(consts.ALWAYS_IGNORE) + list(ignore)


class PrepareHandler(JupyhaiHandler):
    def initialize(self, root_dir: str) -> None:
        self.root_dir = root_dir

    def get(self) -> None:
        ignore = get_effective_ignore(get_current_ignore())
        notebook_path = self.get_argument("notebook_path", "", True)
        try:
            pp = self.get_preparer()
            file_count, total_uncompressed_size = pp.measure_commit(
                ignore, notebook_path
            )
        except PackageTooLarge:
            file_count = -1
            total_uncompressed_size = -1

        self.finish(
            {'fileCount': file_count, 'totalUncompressedSize': total_uncompressed_size}
        )

    def get_preparer(self) -> PackagePreparer:
        return PackagePreparer(log=self.log, root_dir=self.root_dir)

    def post(self) -> None:
        args = self.get_json_body()
        notebook_path = os.path.join(self.root_dir, args['path'])
        ignore = get_effective_ignore(get_current_ignore())
        mounts = get_current_mounts()
        content = json.dumps(args['content'])
        pp = self.get_preparer()
        if not pp.project:
            raise Problem(
                "No project set; unable to prepare package", code="no_project"
            )
        commit_obj = pp.generate_commit(notebook_path, content, ignore, mounts)
        self.finish({'commit': commit_obj['identifier']})
