# Copyright 2018-2021 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

from __future__ import print_function

__metaclass__ = type

import json
import os


class StatusOperationMixin:
    """Methods supporting operations that save extra status information.

    Extra status information will be picked up by the build manager and
    included in XML-RPC status responses.
    """

    @property
    def _status_path(self):
        return os.path.join(self.backend.build_path, "status")

    def get_status(self):
        """Return a copy of this operation's extra status."""
        if os.path.exists(self._status_path):
            with open(self._status_path) as status_file:
                return json.load(status_file)
        else:
            return {}

    def update_status(self, **status):
        """Update this operation's status with key/value pairs."""
        full_status = self.get_status()
        full_status.update(status)
        with open("%s.tmp" % self._status_path, "w") as status_file:
            json.dump(full_status, status_file)
        os.rename("%s.tmp" % self._status_path, self._status_path)
