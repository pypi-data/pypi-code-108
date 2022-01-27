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
import os.path

import Qt.QtGui as QtGui

from . import settings
from . import util

_instance = None


def _icon_path(icon):
    return os.path.join(util.icon_path('actions'), icon)


class Theme(object):
    """
    Base class for themes that holds the graphical theme of the application.
    Currently, primarily used for the flow view.
    """
    # Misc flow colors
    selection_color = None
    active_color = None
    highlight_color = None
    label_color = None
    grid_color = None
    background_color = None
    border_color = None
    connection_color = None
    connection_highlight_color = None

    # Colors for flow objects, depending on state.
    object_color = None
    configurable_color = None
    error_color = None
    done_color = None
    done_locked_color = None
    queued_color = None
    executing_color = None
    executable_color = None

    # Colors.
    beige_color = None
    blue_color = None
    brown_color = None
    dark_color = None
    green_color = None
    light_color = None
    pink_color = None
    purple_color = None
    red_color = None
    yellow_color = None

    # Tab bar project indicators
    project_color0 = None
    project_color1 = None
    project_color2 = None
    project_color3 = None
    project_color4 = None
    project_color5 = None
    project_color6 = None
    project_color7 = None

    # Message colors
    exception_msg_color = None
    error_msg_color = None
    warning_msg_color = None
    notive_msg_color = None

    # Icons
    open_flow = _icon_path('fontawesome/svgs/regular/folder-open.svg')
    new_flow = _icon_path('fontawesome/svgs/regular/file.svg')
    save_flow = _icon_path('fontawesome/svgs/regular/save.svg')
    close_flow = _icon_path('fontawesome/svgs/regular/times-circle.svg')
    preferences = _icon_path('fontawesome/svgs/solid/cog.svg')
    quit = _icon_path('fontawesome/svgs/solid/power-off.svg')
    execute = _icon_path('fontawesome/svgs/solid/play-outline.svg')
    profile = _icon_path('fontawesome/svgs/solid/stopwatch.svg')
    stop = _icon_path('fontawesome/svgs/solid/stop-outline.svg')
    reload = _icon_path('fontawesome/svgs/solid/sync-alt-small.svg')
    undo = _icon_path('fontawesome/svgs/solid/undo.svg')
    redo = _icon_path('fontawesome/svgs/solid/redo.svg')
    cut = _icon_path('fontawesome/svgs/solid/cut.svg')
    copy = _icon_path('fontawesome/svgs/regular/copy.svg')
    paste = _icon_path('fontawesome/svgs/regular/clipboard.svg')
    delete = _icon_path('fontawesome/svgs/regular/trash-alt.svg')
    text_field = _icon_path('fontawesome/svgs/regular/comment-alt.svg')
    insert_node = _icon_path('fontawesome/svgs/solid/plus-thin.svg')
    find = _icon_path('fontawesome/svgs/solid/search.svg')
    zoom_in = _icon_path('fontawesome/svgs/regular/plus-square.svg')
    zoom_out = _icon_path('fontawesome/svgs/regular/minus-square.svg')
    zoom_default = _icon_path('fontawesome/svgs/regular/square.svg')
    zoom_fit = _icon_path('fontawesome/svgs/regular/caret-square-up.svg')
    zoom_fit_selection = _icon_path(
        'fontawesome/svgs/regular/caret-square-down.svg')
    grid = _icon_path('view-grid-symbolic.svg')
    fullscreen = _icon_path('view-fullscreen-symbolic-black.svg')
    help = _icon_path('fontawesome/svgs/regular/question-circle.svg')
    panning = _icon_path('fontawesome/svgs/solid/arrows-alt.svg')
    selection = _icon_path('selection-tool.svg')
    report_issue = _icon_path('fontawesome/svgs/solid/bug.svg')
    exception_msg = _icon_path('fontawesome/svgs/solid/bug.svg')
    error_msg = util.icon_path('node_error.svg')
    warning_msg = util.icon_path('node_warning.svg')
    notice_msg = util.icon_path('node_executed.svg')
    archive = _icon_path('fontawesome/svgs/solid/archive.svg')
    show_archived = _icon_path('fontawesome/svgs/solid/history.svg')
    filter = _icon_path('fontawesome/svgs/solid/filter.svg')
    current_in_list = _icon_path(
        'fontawesome/svgs/solid/long-arrow-alt-right.svg')

    new_item = _icon_path('list-add-symbolic.svg')
    delete_item = _icon_path('list-remove-symbolic.svg')

    @classmethod
    def text_field_colors(cls):
        return {
            'Beige': cls.beige_color,
            'Blue': cls.blue_color,
            'Brown': cls.brown_color,
            'Dark': cls.dark_color,
            'Green': cls.green_color,
            'Light': cls.light_color,
            'Pink': cls.pink_color,
            'Purple': cls.purple_color,
            'Red': cls.red_color,
            'Yellow': cls.yellow_color
        }

    @classmethod
    def project_colors(cls):
        return [
            cls.project_color0,
            cls.project_color1,
            cls.project_color2,
            cls.project_color3,
            cls.project_color4,
            cls.project_color5,
            cls.project_color6,
            cls.project_color7,
        ]


class Grey(Theme):
    """Grey theme"""

    selection_color = QtGui.QColor.fromRgb(150, 150, 255)
    active_color = QtGui.QColor.fromRgb(255, 100, 100, 220)
    highlight_color = QtGui.QColor.fromRgb(180, 180, 180)

    label_color = QtGui.QColor.fromRgb(0, 0, 0)
    grid_color = QtGui.QColor.fromRgb(227, 227, 227)
    background_color = QtGui.QColor.fromRgb(255, 255, 255)
    border_color = QtGui.QColor.fromRgb(160, 160, 160)
    connection_color = QtGui.QColor.fromRgb(152, 152, 152)
    connection_highlight_color = connection_color.darker(200)
    object_color = QtGui.QColor.fromRgb(227, 227, 227)

    configurable_color = QtGui.QColor.fromRgb(227, 227, 227)
    error_color = QtGui.QColor.fromRgb(228, 186, 189)
    done_color = QtGui.QColor.fromRgb(201, 228, 200)
    done_locked_color = QtGui.QColor.fromRgb(229, 210, 242)
    queued_color = QtGui.QColor.fromRgb(164, 174, 197)
    executing_color = QtGui.QColor.fromRgb(164, 174, 197)
    executable_color = QtGui.QColor.fromRgb(231, 217, 188)

    beige_color = QtGui.QColor.fromRgb(231, 217, 188)
    blue_color = QtGui.QColor.fromRgb(167, 206, 203)
    brown_color = QtGui.QColor.fromRgb(206, 177, 175)
    dark_color = QtGui.QColor.fromRgb(177, 181, 178)
    green_color = QtGui.QColor.fromRgb(173, 198, 180)
    light_color = QtGui.QColor.fromRgb(226, 224, 220)
    pink_color = QtGui.QColor.fromRgb(250, 201, 184)
    purple_color = QtGui.QColor.fromRgb(229, 210, 242)
    red_color = QtGui.QColor.fromRgb(234, 153, 129)
    yellow_color = QtGui.QColor.fromRgb(242, 197, 125)

    exception_msg_color = QtGui.QColor.fromRgb(128, 49, 55, 255)
    error_msg_color = QtGui.QColor.fromRgb(128, 49, 55, 255)
    warning_msg_color = QtGui.QColor.fromRgb(253, 182, 0, 255)
    notice_msg_color = QtGui.QColor.fromRgb(0, 100, 0, 255)

    (
        project_color0,
        project_color1,
        project_color2,
        project_color3,
        project_color4,
        project_color5,
        project_color6,
        project_color7,
    ) = [QtGui.QColor.fromHsvF(i/8, 0.18, 0.9) for i in range(8)]


class Dark(Theme):
    """
    Dark theme

    Based on Grey, darkening colors by a factor.
    """

    _darken = 200

    selection_color = QtGui.QColor.fromRgb(105, 105, 255)
    active_color = QtGui.QColor.fromRgb(0, 155, 155, 220)
    highlight_color = QtGui.QColor.fromRgb(180, 180, 180).darker(_darken)

    label_color = QtGui.QColor.fromRgb(196, 196, 196)
    grid_color = QtGui.QColor.fromRgb(128, 128, 128)

    background_color = QtGui.QColor.fromRgb(32, 32, 32).darker(_darken)
    border_color = QtGui.QColor.fromRgb(160, 160, 160).darker(_darken)
    connection_color = QtGui.QColor.fromRgb(152, 152, 152).darker(_darken)
    connection_highlight_color = connection_color.lighter(200)
    object_color = QtGui.QColor.fromRgb(227, 227, 227).darker(_darken)

    configurable_color = QtGui.QColor.fromRgb(227, 227, 227).darker(_darken)
    error_color = QtGui.QColor.fromRgb(228, 186, 189).darker(_darken)
    done_color = QtGui.QColor.fromRgb(201, 228, 200).darker(_darken)
    done_locked_color = QtGui.QColor.fromRgb(229, 210, 242).darker(_darken)
    queued_color = QtGui.QColor.fromRgb(164, 174, 197).darker(_darken)
    executing_color = QtGui.QColor.fromRgb(164, 174, 197).darker(_darken)
    executable_color = QtGui.QColor.fromRgb(231, 217, 188).darker(_darken)

    beige_color = QtGui.QColor.fromRgb(231, 217, 188).darker(_darken)
    blue_color = QtGui.QColor.fromRgb(167, 206, 203).darker(_darken)
    brown_color = QtGui.QColor.fromRgb(206, 177, 175).darker(_darken)
    dark_color = QtGui.QColor.fromRgb(177, 181, 178).darker(_darken)
    green_color = QtGui.QColor.fromRgb(173, 198, 180).darker(_darken)
    light_color = QtGui.QColor.fromRgb(226, 224, 220).darker(_darken)
    pink_color = QtGui.QColor.fromRgb(250, 201, 184).darker(_darken)
    purple_color = QtGui.QColor.fromRgb(229, 210, 242).darker(_darken)
    red_color = QtGui.QColor.fromRgb(234, 153, 129).darker(_darken)
    yellow_color = QtGui.QColor.fromRgb(242, 197, 125).darker(_darken)

    exception_color = QtGui.QColor.fromRgb(128, 49, 55, 255).darker(_darken)
    error_color = QtGui.QColor.fromRgb(128, 49, 55, 255).darker(_darken)
    warning_color = QtGui.QColor.fromRgb(253, 182, 0, 255).darker(_darken)
    notive_color = QtGui.QColor.fromRgb(0, 100, 0, 255).darker(_darken)

    (
        project_color0,
        project_color1,
        project_color2,
        project_color3,
        project_color4,
        project_color5,
        project_color6,
        project_color7,
    ) = [QtGui.QColor.fromHsvF(i/8, 0.18, 0.9)
         for i in range(8)]


def available_themes():
    return {'Grey': Grey, 'Dark': Dark}


def get_active_theme():
    return available_themes().get(
        settings.instance()['Gui/theme'],
        settings.permanent_defaults['Gui/theme'])()
