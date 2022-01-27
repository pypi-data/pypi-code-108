# This file is part of Sympathy for Data.
# Copyright (c) 2020, Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.

# UserStatistics interface:

class UserStatistics:

    def start(self):
        pass

    def stop(self):
        pass

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *exec_info):
        self.stop()

    def user_created_connection(self, src, dst):
        pass

    def user_created_node(self, node):
        pass

    def user_configured_node(self, node, result):
        pass

    def user_created_subflow(self, subflow):
        pass

    def user_executed_node(self, node, result):
        pass

    def user_aborted_node(self, node):
        pass

    def user_started_sympathy(self, interface):
        pass

    def user_stopped_sympathy(self):
        pass

    def user_running_sympathy(self):
        pass

    def user_crashed_sympathy(self):
        pass

    def user_opened_workflow(self, flow):
        # After the workflow is opened.
        pass

    def user_closed_workflow(self, flow):
        # Before the workflow is closed.
        pass

    def user_saved_workflow(self, flow):
        pass

    def user_loaded_library(self, library_id, path, name, is_global):
        pass

    def user_unloaded_library(self, library_id, path, name, is_global):
        pass


# Package interface:

def user_statistics() -> UserStatistics:
    raise NotImplementedError()


# Plugin identifier:

identifier = 'sympathy.user_statistics.plugins'
