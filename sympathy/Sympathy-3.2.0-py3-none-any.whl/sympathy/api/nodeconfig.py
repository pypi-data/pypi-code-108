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
# Ports definition classes.
from .. utils.port import Port, Ports, PortType
from .. platform.port import TemplateTypes

from .. utils.tag import tag_builder as Tag
from .. utils.tag import TagType, GroupTagType, Tags, LibraryTags
from .. utils import preview

# Node parameter API, for accessing fields and building the structure.
from .. platform.parameter_helper_gui import sy_parameters as ParameterRoot

from .. utils.context import (inherit_doc, join_doc, deprecated_node,
                              deprecated_warn)

# Helper for implementing standardized adjust parameters.
from sympathy.platform.node import adjust

# Function returning worker settings.
from sympathy.platform.settings import settings


__all__ = ['Port', 'Ports', 'PortType', 'TemplateTypes', 'Tag', 'TagType',
           'GroupTagType', 'Tags', 'LibraryTags', 'ParameterRoot',
           'inherit_doc', 'join_doc', 'deprecated_node', 'adjust', 'settings',
           'deprecated_warn', 'preview']
