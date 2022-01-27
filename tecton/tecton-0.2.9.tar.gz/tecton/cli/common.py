import inspect
import re
from pathlib import Path

from tecton import conf
from tecton_proto.args.repo_metadata_pb2 import SourceInfo

# Matches frame strings such as "<string>"
SKIP_FRAME_REGEX = re.compile("\<.*\>")


def get_current_workspace():
    return conf.get_or_none("TECTON_WORKSPACE")


def get_fco_source_info() -> SourceInfo:
    from tecton_spark.repo_file_handler import _maybe_get_repo_root

    source_info = SourceInfo()
    if not _maybe_get_repo_root():
        pass
    else:
        frames = inspect.stack()
        repo_root_path = Path(_maybe_get_repo_root())
        for frame in frames:
            if SKIP_FRAME_REGEX.match(frame.frame.f_code.co_filename) is not None:
                continue
            frame_path = Path(frame.frame.f_code.co_filename).resolve()
            if frame_path.exists() and (repo_root_path in frame_path.parents):
                rel_filename = frame_path.relative_to(repo_root_path)
                source_info.source_lineno = str(frame.lineno)
                source_info.source_filename = str(rel_filename)
                break
    return source_info
