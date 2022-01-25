from memory_tempfile import MemoryTempfile
import contextlib
from typing import Optional

__all__ = ['get_tmp_path']
__version__ = '0.1'

# Credits: https://pypi.org/project/memory-tempfile/
tempfile = MemoryTempfile(preferred_paths=['/run/user/{uid}'], remove_paths=['/dev/shm', '/run/shm'],
                          additional_paths=['/var/run'], filesystem_types=['tmpfs'], fallback=True)

if not tempfile.found_mem_tempdir():
    raise RuntimeError('No tmp directory found')


@contextlib.contextmanager
def get_tmp_path(content: Optional[str] = None, suffix: Optional[str] = None, delete=True) -> str:
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=delete, mode='w+') as ntf:
        if content:
            ntf.write(content)
            ntf.flush()
        yield ntf.name
