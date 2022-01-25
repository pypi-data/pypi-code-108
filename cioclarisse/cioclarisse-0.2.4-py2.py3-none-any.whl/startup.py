"""Script to be added to Clarisse's list of startup scripts.

It registers the conductor_job class in Clarisse.
"""

import ix
import sys
import os

msg = """
The variable CIO_DIR is not defined in your config.env file.
It should point to the Conductor install directory, e.g. ~/Conductor/.
To fix this, please run the post_install script: `python <conductor_location>/cioclarisse/post_install.py`
"""

CIO_DIR = os.environ.get("CIO_DIR")
if not CIO_DIR:
    ix.log_error(msg)
    sys.exit()

sys.path.insert(0,  CIO_DIR)

from ciocore import data as coredata
from cioclarisse.conductor_job import ConductorJob

coredata.init(product="clarisse")
ix.api.ModuleScriptedClass.register_scripted_class(
    ix.application, "ConductorJob", ConductorJob()
)
