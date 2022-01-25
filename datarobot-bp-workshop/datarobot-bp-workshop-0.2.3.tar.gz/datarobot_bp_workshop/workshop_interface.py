"""
Copyright 2021 DataRobot, Inc. and its affiliates.

All rights reserved.

DataRobot, Inc. Confidential.

This is unpublished proprietary source code of DataRobot, Inc. and its affiliates.

The copyright notice above does not evidence any actual or intended publication of such source code.

Released under the terms of DataRobot Tool and Utility Agreement.
"""
from __future__ import annotations

from typing import Dict, Optional, List, Collection

from datarobot import UserBlueprint

from .datarobot_client import (
    UserBlueprintAvailableTasks,
    UserBlueprintTaskArgument,
    UserBlueprintTaskDefinition,
    ColnameAndType,
)

from datarobot_bp_workshop.auto_rate_limiter import AutoRateLimiter
from datarobot_bp_workshop.sharing import SharingInterface
from .user_blueprint_helper import UserBlueprintHelper


class WorkshopInterface(SharingInterface):
    """ Interface to use to allow working with a Workshop in BlueprintGraph and Task. """

    def __init__(self, project_id=None, enforce_rate_limit=True):
        self._task_definitions_by_task_code: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_task_definitions_by_task_code: Dict[
            str, List[UserBlueprintTaskDefinition]
        ] = {}
        self._custom_tasks_by_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._custom_tasks_by_version_id: Dict[str, UserBlueprintTaskDefinition] = {}
        self._task_argument_lookup: Dict[str, Dict[str:UserBlueprintTaskArgument]] = {}
        self._input_name_lookup: Dict[str, str] = {}
        self._available_tasks: Optional[UserBlueprintAvailableTasks] = None
        self._colname_and_type_colname_lookup: Dict[str, ColnameAndType] = {}
        self._colname_and_type_hex_lookup: Dict[str, ColnameAndType] = {}
        self._project_id: Optional[str] = project_id
        self._associated_user_blueprint_id: Optional[str] = None

        self.auto_rate_limiter: AutoRateLimiter = (
            AutoRateLimiter() if enforce_rate_limit else AutoRateLimiter(0)
        )

    @property
    def project_id(self):
        return self._project_id

    def initialize(
        self, user_blueprint_id: Optional[str] = None, clean: bool = False
    ) -> WorkshopInterface:
        """ Must be implemented on inheriting class. """
        raise NotImplementedError()

    def _custom_task_key_string(self, custom_task_id: str) -> str:
        task_code = self._custom_tasks_by_id[custom_task_id].task_code
        return "{}_{}".format(task_code, custom_task_id)

    def has_all_version_ids(self, version_ids: Collection[str]) -> bool:
        """ Return whether all version ids are already available. """
        if not len(version_ids):
            return True
        keys = set(self._custom_tasks_by_version_id.keys())
        if len(set(version_ids) - keys):
            return False
        for version_id in version_ids:
            task_code = self._custom_task_key_string(
                self._custom_tasks_by_version_id[version_id].custom_task_id
            )
            custom_tasks = getattr(self, "CustomTasks", None)
            if not hasattr(custom_tasks, task_code):
                return False
        return True

    def has_all_task_codes(self, task_codes: Collection[str]) -> bool:
        """ Return whether all task_codes are already available. """
        if not len(task_codes):
            return True
        keys = set(self._task_definitions_by_task_code.keys())
        if len(set(task_codes) - keys):
            return False
        return True

    def ensure_definitions_for_user_blueprint(self, user_blueprint: UserBlueprint):
        """
        Retrieve definitions for built-in or custom tasks, if they are not available.
        """
        # If there are any custom tasks that we have not retrieved definitions for,
        # do so now.
        version_ids = UserBlueprintHelper.get_custom_task_version_ids(user_blueprint)
        if not self.has_all_version_ids(version_ids):
            self.initialize(user_blueprint_id=user_blueprint.user_blueprint_id)
        else:
            # If there are any built-in tasks that we have not retrieved definitions for,
            # do so now
            task_codes = UserBlueprintHelper.get_task_codes(user_blueprint)
            if not self.has_all_task_codes(task_codes):
                self.initialize(user_blueprint_id=user_blueprint.user_blueprint_id)
