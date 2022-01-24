import os
import sys
from logging import getLogger
from typing import List

import urllib3

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

from rallycli.base_api import BaseAPI
from rallycli.models import RallyTypeGeneric, type_names

## logger definition
logger = getLogger(__name__)
## Disable certificate warnings for testing pourposes
urllib3.disable_warnings()


class TimeboxAPI(BaseAPI):
    """Class for accessing Time Boxes domain"""

    ## Releases

    def get_releases_for_project(self, project_ref: str, fetch: str = "true") -> List[RallyTypeGeneric]:
        return self.query(f"(Project = {project_ref})", type_names.RELEASE, fetch=fetch)

    ## Iterations

    def get_active_iterations_for_project(self, project_ref: str, fetch: str = "true") -> List[RallyTypeGeneric]:
        return self.query(f"( (Project = {project_ref}) AND (State != Accepted))",
                          type_names.ITERATION, fetch=fetch)
