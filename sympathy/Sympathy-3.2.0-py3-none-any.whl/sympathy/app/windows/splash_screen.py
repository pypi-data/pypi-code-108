# This file is part of Sympathy for Data.
# Copyright (c) 2021 Combine Control Systems AB
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

import Qt.QtWidgets as QtWidgets
import Qt.QtGui as QtGui
import Qt.QtCore as QtCore

from sympathy.utils.prim import get_icon_path, fonts_path
from sympathy.utils import log
from sympathy.platform.hooks import splash_extra_text
from .. import version


core_logger = log.get_logger('core')
app_logger = log.get_logger('app')


class Splash(QtWidgets.QSplashScreen):
    def __init__(self):
        font_path = os.path.join(fonts_path(), 'Quicksand-Medium.ttf')
        res = QtGui.QFontDatabase.addApplicationFont(font_path)
        if res == -1:
            app_logger.error(f'Could not load font: {font_path}')

        ico = get_icon_path('splash.png')
        pixmap = QtGui.QPixmap(ico)
        super().__init__(pixmap)

    def drawContents(self, painter):
        super().drawContents(painter)
        font = QtGui.QFont(
            'Quicksand', pointSize=11, weight=QtGui.QFont.Medium)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 2)
        font.setCapitalization(QtGui.QFont.AllUppercase)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(QtGui.QColor('white')))
        painter.drawText(
            QtCore.QRect(0, 435, 341, 20),
            QtCore.Qt.AlignCenter,
            version.license_info()['edition'])

        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        font.setCapitalization(QtGui.QFont.MixedCase)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRect(0, 460, 341, 20),
            QtCore.Qt.AlignCenter,
            version.version)

        extra_text = splash_extra_text.value()
        if extra_text:
            text_rect = QtCore.QRect(0, 510, 341, 80)
            painter.drawText(
                text_rect,
                QtCore.Qt.AlignHCenter,
                extra_text)

        font = QtGui.QFont(
            'Quicksand', pointSize=9, weight=QtGui.QFont.Medium)
        painter.setFont(font)
        painter.drawText(
            QtCore.QRect(0, 680, 341, 20),
            QtCore.Qt.AlignCenter,
            self.message())
