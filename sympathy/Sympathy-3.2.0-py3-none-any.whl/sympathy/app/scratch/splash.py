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
import os
import sys
# import subprocess

from Qt import QtWidgets
from Qt import QtGui
from Qt import QtCore

from sympathy.utils.prim import get_icon_path, fonts_path
from sympathy.app import version


# def git_info():
#     head = tag = None

#     res = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'],
#                          capture_output=True, text=True)
#     if res.returncode != 0:
#         return ""
#     head = res.stdout.strip()

#     res = subprocess.run(['git', 'tag', '--points-at', 'HEAD'],
#                          capture_output=True, text=True)
#     if res.returncode != 0:
#         return ""
#     tag = res.stdout.strip()

#     res = subprocess.run(['git', 'branch', '--show-current'],
#                          capture_output=True, text=True)
#     if res.returncode != 0:
#         return ""
#     branch = res.stdout.strip()

#     return f"git: ({tag or branch}) {head}"


def print_font_info(font):
    fi = QtGui.QFontInfo(font)
    print(f"Font: {fi.family()} {fi.pointSize()}pt")
    print(f"  exactMatch: {fi.exactMatch()}")
    print(f"  weight: {fi.weight()}")
    print(f"  italic: {fi.italic()}")
    style = '.'.join(str(fi.style()).split('.')[2:])
    print(f"  style: {style}")
    style_hint = '.'.join(str(fi.styleHint()).split('.')[2:])
    print(f"  styleHint: {style_hint}")
    print(f"  fixedPitch: {fi.fixedPitch()}")


class Splash(QtWidgets.QSplashScreen):
    def __init__(self):
        ico = get_icon_path('splash.png')
        pixmap = QtGui.QPixmap(ico)
        super().__init__(pixmap, QtCore.Qt.WindowStaysOnTopHint)

    def drawContents(self, painter):
        super().drawContents(painter)
        font = QtGui.QFont(
            'Quicksand', pointSize=11, weight=QtGui.QFont.Medium)
        # font.setStyleStrategy(QtGui.QFont.NoSubpixelAntialias)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 2)
        # font.setCapitalization(QtGui.QFont.SmallCaps)
        # font.setCapitalization(QtGui.QFont.AllUppercase)
        print_font_info(font)
        painter.setFont(font)
        painter.setPen(QtGui.QPen(QtGui.QColor('white')))
        rect = QtCore.QRect(0, 435, 341, 20)
        painter.drawText(
            rect,
            QtCore.Qt.AlignCenter,
            "OPEN SOURCE")
        # painter.drawRect(rect)
        font.setLetterSpacing(QtGui.QFont.AbsoluteSpacing, 1)
        painter.setFont(font)
        rect = QtCore.QRect(0, 460, 341, 20)
        painter.drawText(
            rect,
            QtCore.Qt.AlignCenter,
            version.version)
        # painter.drawRect(rect)

    def mousePressEvent(self, event):
        self.close()
        sys.exit(0)


def main():
    app = QtWidgets.QApplication([])

    for font_filename in os.listdir(fonts_path()):
        font_path = os.path.join(fonts_path(), font_filename)
        if os.path.isdir(font_path):
            continue
        res = QtGui.QFontDatabase.addApplicationFont(font_path)
        if res == -1:
            print(f'Could not load font: {font_path}')

    splash = Splash()
    splash.show()
    app.exec_()


if __name__ == '__main__':
    main()
