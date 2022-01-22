#!/usr/bin/env python3
"""
GRAPHICS.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A basic graphics demo using a container.
"""

import sys
import os

from plib.ui.toolkits import set_toolkit, ToolkitError

# We have to do this before any other plib.ui modules are imported,
# to avoid triggering the toolkit auto-detection machinery

try:
    set_toolkit('pyside2')
except ToolkitError:
    try:
        set_toolkit('qt5')
    except ToolkitError:
        print("Can't find pyside2 or qt5 toolkit.")
        sys.exit(1)

from plib.ui import __version__
from plib.ui.app import PApplication
from plib.ui.widgets import *  # this also imports get_toolkit


def make_graphic(parent, *filenames):
    print("Setting up graphic")
    toolkit = get_toolkit()
    if toolkit == 'pyside2':
        from PySide2 import QtGui, QtWidgets
    elif toolkit == 'qt5':
        from PyQt5 import QtGui, QtWidgets
    
    scene = QtWidgets.QGraphicsScene(parent)
    
    background = None
    if len(filenames) > 0:
        print("Loading background from", filenames[0])
        background = scene.addPixmap(QtGui.QPixmap(filenames[0]))
        background.setScale(0.2)
    
    sprites = []
    if len(filenames) > 1:
        for filename in filenames[1:]:
            print("Loading sprite from", filenames[1])
            sprite = scene.addPixmap(QtGui.QPixmap(filename))
            sprite.setScale(0.05)
            sprite.setPos(510.0 - 37.5, 255.0 - 26.25)
            sprites.append(sprite)
    
    graphic = QtWidgets.QGraphicsView(scene, parent)
    return graphic, background, sprites


class GraphicsDisplay(PApplication):
    
    about_data = {
        'name': "GraphicsDisplay",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "Graphics Display Tester",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net"
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    main_title = "Graphics Display Tester"
    
    main_widget = frame(ALIGN_JUST, LAYOUT_VERTICAL, [
        container('display'),
        panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, [
            padding(),
            button('left', "<"),
            combo('sprite'),
            num_edit('move_by'),
            button('right', ">"),
            padding(),
        ]),
        panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, [
            padding(),
            action_button(ACTION_ABOUT),
            action_button(ACTION_ABOUT_TOOLKIT),
            action_button(ACTION_EXIT),
        ]),
    ])
    
    # TODO: file open/save needed?
    menu_actions = [
        (MENU_FILE, (ACTION_FILE_OPEN, ACTION_FILE_SAVE, ACTION_EXIT,)),
        (MENU_HELP, (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,)),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_OPEN, ACTION_FILE_SAVE,),
        (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    graphic = None
    background = None
    sprites = ()
    
    move_unit = 1.0
    
    def after_create(self):
        if len(sys.argv) > 1:
            filenames = sys.argv[1:]
            self.graphic, self.background, self.sprites = make_graphic(self.container_display, *filenames)
            self.container_display.add_child(self.graphic)
            if len(filenames) > 1:
                self.combo_sprite.extend(os.path.basename(filename) for filename in filenames[1:])
    
    def on_app_shown(self):
        self.main_window.center()  # do after widgets are constructed and sized
    
    def move_sprite(self, left_right, up_down):
        index = self.combo_sprite.current_index()
        if index > -1:
            move_by = self.edit_move_by.edit_value * self.move_unit
            if move_by:
                sprite = self.sprites[index]
                sprite.moveBy(move_by * left_right, move_by * up_down)
            else:
                self.message_box.error("Move Error", "Can't move by zero units")
        else:
            self.message_box.error("Move Error", "No sprite selected")
    
    def on_left_clicked(self):
        self.move_sprite(-1, 0)
    
    def on_right_clicked(self):
        self.move_sprite(1, 0)
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()


if __name__ == "__main__":
    GraphicsDisplay().run()
