# This file is part of Sympathy for Data.
# Copyright (c) 2013 Combine Control Systems AB
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
import os
import shutil
import itertools
import Qt.QtCore as QtCore

from . import settings


class FilenameException(BaseException):
    pass


class FilenameManager(QtCore.QObject):
    def __init__(self, parent=None):
        super(FilenameManager, self).__init__(parent)
        self._allocated_filenames = {}
        self._count = itertools.count()
        self._config_filename = None
        self._prefix = ''

    def allocate_filename(self, namespace, identifier, index, suffix):
        namespaced_filenames = self._allocated_filenames.setdefault(
            namespace, [])
        fq_filename = self._generate_unique_filename(suffix)
        namespaced_filenames.append(fq_filename)
        return fq_filename

    def full_config_filename(self):
        return self._config_filename

    def allocate_config_filename(self, basename):
        if self._config_filename is None:
            self._config_filename = os.path.join(
                settings.instance()['session_folder'], basename)
        else:
            raise FilenameException('Config filename already defined.')
        return self._config_filename

    def deallocate_all_filenames(self):
        for namespace in list(self._allocated_filenames):
            self.deallocate_namespace(namespace)

    def deallocate_namespace(self, namespace):
        for filename in self._allocated_filenames.get(namespace, []):
            self._remove_filename(filename)
        self._allocated_filenames.pop(namespace, None)

    def deallocate_session_folder(self):
        shutil.rmtree(settings.instance()['session_folder'])

    def _remove_filename(self, fq_filename):
        try:
            os.remove(fq_filename)
        except (OSError, IOError):
            pass

    def _generate_unique_filename(self, suffix):
        unique_number = next(self._count)

        filename = '{}.{}'.format(str(unique_number), suffix)
        session_folder = settings.instance()['session_folder']
        fq_filename = os.path.join(session_folder, '{}_{}'.format(
            self._prefix, filename))
        if os.path.isfile(fq_filename):
            raise IOError('File exists. Unique filename generation FAIL.')
        return fq_filename

    def set_prefix(self, prefix):
        self._prefix = prefix


filename_manager_instance = FilenameManager()


def instance():
    return filename_manager_instance
