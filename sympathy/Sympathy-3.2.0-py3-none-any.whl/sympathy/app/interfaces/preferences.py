# This file is part of Sympathy for Data.
# Copyright (c) 2020 Combine Control Systems AB
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
from Qt import QtCore
from Qt import QtWidgets

from sympathy.platform import feature


class PreferenceSectionWidget(feature.PreferenceSection):
    """
    PreferenceSectionWidget

    Interface for Preference Sections.

    To implement correct OK/Cancel:

    * save() must store all changed settings.
    * update_data() should load all values from settings.

    When using settings widgets, the easiest way is to return them
    in via _settings_widgets and use default save and update_data
    implementations.

    For custom behavior, override these two and call save(), update_data()
    from this class to handle save and update of settings widgets, and
    then handle other save and updates manually.
    """

    _name = ''

    def __init__(self, app_core, parent=None):
        super().__init__(parent)
        self._app_core = app_core

    def _settings_widgets(self):
        return []

    def save(self):
        """
        Called on confirmed preferences (OK).
        Ensure that all changed settings are stored.
         """
        for widget in self._settings_widgets():
            widget.save()
        return []

    def name(self) -> str:
        return self._name

    def update_data(self):
        """
        Called once every time preferences is shown.  Implement cancel by
        reloading widgets based on stored settings.  The purpose is not limited
        to cancel, external actions can also update settings.
        """
        for widget in self._settings_widgets():
            widget.update_value()

    def _create_layout(self):
        layout = QtWidgets.QFormLayout()
        layout.setFieldGrowthPolicy(QtWidgets.QFormLayout.ExpandingFieldsGrow)
        layout.setFormAlignment(QtCore.Qt.AlignLeft)
        layout.setLabelAlignment(QtCore.Qt.AlignVCenter)
        layout.setVerticalSpacing(15)
        return layout

    def _add_row(self, label, field_widget, tooltip):
        self._layout.addRow(label, field_widget)
        label_widget = self._layout.labelForField(field_widget)
        label_widget.setToolTip(tooltip)
        field_widget.setToolTip(tooltip)

    def _centered_label(self, string):
        label = QtWidgets.QLabel(string)
        return label
