# This file is part of Sympathy for Data.
# Copyright (c) 2013, Combine Control Systems AB
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
import sympathy.version
import sympathy.api
import sympathy.api.library
from . import librarytag_sylib
import sylib.imageprocessing.image
import sylib.machinelearning.model
import sylib.html.html
import sylib.html.geojson


def identifier():
    return 'org.sysess.sympathy'


def name():
    return 'Sympathy'


def description():
    return 'The Standard library of nodes included in Sympathy for Data'


def documentation():
    return ''


def maintainer():
    return 'Combine Control Systems <support@sympathyfordata.com>'


def copyright():
    return 'Copyright (c) 2011-2019, Combine Control Systems AB'


def documentation_url():
    major = sympathy.version.major
    minor = sympathy.version.minor
    micro = sympathy.version.micro
    return f'https://www.sympathyfordata.com/doc/{major}.{minor}.{micro}/'


def nodes():
    return sympathy.api.library.scan_files(
        os.path.dirname(__file__), 'node_*.py')


def flows():
    return sympathy.api.library.scan_files(
        os.path.dirname(__file__), 'flow_*.syx')


def plugins():
    return sympathy.api.library.scan_files(
        os.path.dirname(__file__), 'plugin_*.py')


def tags():
    return [
        librarytag_sylib.SylibLibraryTags
    ]


def types():
    return [
        sympathy.api.adaf.File,
        sympathy.api.datasource.File,
        sympathy.api.figure.File,
        sympathy.api.report.File,
        sympathy.api.table.File,
        sympathy.api.text.File,
        sympathy.api.json.File,
        sylib.imageprocessing.image.File,
        sylib.machinelearning.model.File,
        sylib.html.html.File,
        sylib.html.geojson.File,
    ]
