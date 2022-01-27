# This file is part of Sympathy for Data.
# Copyright (c) 2015, Combine Control Systems AB
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

from . import models
from . import plugins


def build(model_root, binding_context, target):
    """
    Entry function to this module.
    :param model_root: Root model from model_wrapper.
    :param target: Target for builder.
    :return: Widget representing root.
    """
    backend = plugins.backend_modules[target].backend
    root_element = None
    for child in model_root.children:
        if type(child) == models.Pages:
            factory = backend.ItemFactory(binding_context)
            root_element = factory.build(child)
    return root_element
