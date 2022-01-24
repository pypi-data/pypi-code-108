import logging
import os
from typing import cast

from tktl.core.exceptions import validate_config
from tktl.core.managers.base import BaseConfigManager
from tktl.core.managers.project import ProjectManager

log = logging.getLogger("root")


class LearnerManager(BaseConfigManager):
    CONFIG_FILE_NAME: str = "tktl.yaml"
    INPUT_KEYS: str = "x"
    OUTPUT_KEYS: str = "y"
    PLATFORM: str = "tensorflow"

    @classmethod
    @validate_config
    def get_path(cls, name: str) -> str:
        return os.path.join(cast(str, ProjectManager.get_value("saved-models")), name)
