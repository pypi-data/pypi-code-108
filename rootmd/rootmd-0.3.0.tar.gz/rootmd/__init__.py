__version__ = '0.1.0'

import logging
from rich.logging import RichHandler
from .RootHtmlRenderer import RootHtmlRenderer
from .RootMdRenderer import RootMdRenderer
from .Md2MacroRenderer import Md2MacroRenderer


# FORMAT = "%(message)s"
# logging.basicConfig(
#     level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
# )

# log = logging.getLogger("rich")

# TITLE = "rootmd"
# EMBED = False
# ASSET_DIR = ""
# ASSET_PREFIX = ""



if __name__ == "__main__":  # pragma: no cover
    print("Hello, **World**")