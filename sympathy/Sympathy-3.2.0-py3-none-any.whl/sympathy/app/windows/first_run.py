# This file is part of Sympathy for Data.
# Copyright (c) 2019 Combine Control Systems AB
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
import Qt.QtWidgets as QtWidgets
import Qt.QtCore as QtCore
import distutils.version
from .. import settings


# In this module some imports are delayed to avoid excessive addition
# to startup time in the normal case. TODO: refactor such functionality
# to utility modules which can be shared without slowdown.

def send_stats():
    from sympathy.app.widgets import settings_widgets as setwidgets
    send_stats = setwidgets.BoolCheckBox('send_stats')
    send_stats.setToolTip(
        'Anonymous statistics never include any identifiable '
        'information. More information about this feature can '
        'be found under "Data Privacy Notice" in the '
        'documentation.')

    # Override default from settings.
    send_stats.setChecked(True)
    # Replacing newlines since we have more space here.
    return (
        'Help to improve Sympathy by sharing anonymous statistics',
        send_stats)


options = {
    (1, 6, 2): [
        send_stats,
    ],
}


def setup(close_signal):
    settings_ = settings.instance()

    configured_version = (1, 0, 0)
    try:
        configured_version = tuple(
            distutils.version.LooseVersion(
                settings_['configured_version']).version[:3])
    except Exception:
        pass

    opt_iter = iter(sorted(options.keys()))
    opt_version = next(opt_iter, None)

    unconfigured_opts = []

    while opt_version:
        if opt_version > configured_version:
            unconfigured_opts.extend(options[opt_version])
        opt_version = next(opt_iter, None)

    if unconfigured_opts:
        from sympathy.app.windows import issues
        import sympathy.app.version
        widgets = []

        vlayout = QtWidgets.QVBoxLayout()
        info = QtWidgets.QLabel('<B>New options need to be configured for '
                                f'Sympathy version {sympathy.app.version.version}</B>')

        vlayout.addWidget(info)
        dialog = QtWidgets.QDialog()
        dialog.setWindowTitle('First time setup for '
                              f'Sympathy version {sympathy.app.version.version}')

        # TODO(erik) calling interal function.
        flayout = issues._info_form_layout()
        for opt in unconfigured_opts:
            label, widget = opt()
            widgets.append(widget)
            flayout.addRow(label, widget)

        default_flags = dialog.windowFlags()
        dialog.setWindowFlags(default_flags
                              & ~QtCore.Qt.WindowCloseButtonHint
                              | QtCore.Qt.CustomizeWindowHint
                              | QtCore.Qt.WindowMinimizeButtonHint
                              | QtCore.Qt.WindowMaximizeButtonHint)

        vlayout.addLayout(flayout)
        buttons = QtWidgets.QDialogButtonBox()
        ok = buttons.addButton(QtWidgets.QDialogButtonBox.Ok)
        ok.clicked.connect(dialog.accept)
        vlayout.addWidget(buttons)

        dialog.setLayout(vlayout)
        close_signal.connect(dialog.reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            settings_['configured_version'] = sympathy.app.version.version
            widget.save()
