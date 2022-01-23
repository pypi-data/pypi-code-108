# Copyright 2021 Q-CTRL. All rights reserved.
#
# Licensed under the Q-CTRL Terms of service (the "License"). Unauthorized
# copying or use of this file, via any medium, is strictly prohibited.
# Proprietary and confidential. You may not use this file except in compliance
# with the License. You may obtain a copy of the License at
#
#     https://q-ctrl.com/terms
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS. See the
# License for the specific language.
# pylint:disable=missing-module-docstring
import logging

LOGGER = logging.getLogger(__name__)


class ResultMixin:
    """Adds functionality to GraphQL result types."""

    # action statuses
    PENDING = "PENDING"
    STARTED = "STARTED"
    RETRY = "RETRY"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"

    @property
    def action_id(self):
        """The id of the action."""
        return self.action.model_id

    @property
    def name(self):
        """The name of the action."""
        return self.action.name

    @property
    def status(self):
        """The status of the action."""
        return self.action.status

    @property
    def job_errors(self):
        """Any errors while executing the action."""
        return self.action.errors

    @property
    def progress(self):
        """The progress of the action."""
        return self.action.progress if self.action else 0

    @property
    def is_completed(self) -> bool:
        """Checks if action is completed."""
        if not self.status:
            return False

        return self.status not in (self.PENDING, self.STARTED, self.RETRY)

    @property
    def is_successful(self) -> bool:
        """Checks if action is successful."""
        return self.status == self.SUCCESS
