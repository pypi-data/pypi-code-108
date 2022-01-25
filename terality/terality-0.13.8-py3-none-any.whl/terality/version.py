from pathlib import Path
from single_source import get_version

root_package_name = __name__.split(".")[0]
__version__ = get_version(root_package_name, Path(__file__).parent.parent)
