"""copy or control files under 'skelton' directory
"""

import shutil
from pathlib import Path


class Error(Exception):
    pass

# if this module compressed in library.zip by cx_Freeze
# replace the path starts from s/library.zip/library_package_data/
skelton_dir = Path(__file__.replace('library.zip', 'library_package_data')).with_name('skelton')

# test existence of skelton_dir
if not skelton_dir.is_dir():
    raise('cannot find marlowe_ui/postprocess/skelton directory (supporsed at {})'.format(skelton_dir))


def copy_contents(outputdir):
    """copy contents under skleton_dir to output_dir

    output_dir is pathlib.Path object of a directory to which
      contetns of skelton_dir is copied, and should be prepared before
      this function called.
    """
    shutil.copy(str(skelton_dir / 'summary.pvsm'), str(outputdir))
