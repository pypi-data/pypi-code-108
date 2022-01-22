#!/usr/bin/env python3
"""
PIMGVIEW.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple read-only image file viewer.
"""

import sys
import os

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui import common
from plib.ui.app import PApplication
from plib.ui.fileaware import PFileAware
from plib.ui.widgets import *


IMAGE_EXTENSIONS = []


class ImageFileLoader(PFileAware):
    
    def __init__(self, app):
        PFileAware.__init__(self, app, [
            ("Image Files", list(IMAGE_EXTENSIONS)),
        ] + [
            ("All Files", ["*"]),
        ], file_path=app.main_path)
    
    def open_data(self, filename):
        self.app.add_file(filename)
        self.close_file()  # to be ready for the next load
    
    def save_data(self, filename):
        pass  # this app does not edit/save files


# Add custom actions
ACTION_FIT = ACTION_REFRESH + 20
ACTION_ZOOM_IN = ACTION_REFRESH + 21
ACTION_ZOOM_OUT = ACTION_REFRESH + 22
ACTION_ROTATE_LEFT = ACTION_REFRESH + 23
ACTION_ROTATE_RIGHT = ACTION_REFRESH + 24

common.add_action(
    ACTION_FIT,
    'fit', "&Fit", "Fit image to window", "apply"
)

common.add_action(
    ACTION_ZOOM_IN,
    'zoom_in', "Zoom &In", "Zoom image in", "add"
)

common.add_action(
    ACTION_ZOOM_OUT,
    'zoom_out', "Zoom &Out", "Zoom image out", "remove"
)


def custom_icon(name):
    return os.path.join(os.path.dirname(__file__), "{}.png".format(name))


common.add_action(
    ACTION_ROTATE_LEFT,
    'rotate_left', "Rotate &Left", "Rotate image 90 degrees counterclockwise", custom_icon("rotate_left")
)

common.add_action(
    ACTION_ROTATE_RIGHT,
    'rotate_right', "Rotate &Right", "Rotate image 90 degrees clockwise", custom_icon("rotate_right")
)


class ImageViewer(PApplication):
    
    about_data = {
        'name': "ImageViewer",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "Image Viewer",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net",
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    menu_actions = [
        (MENU_FILE, (ACTION_FILE_OPEN, ACTION_EXIT,)),
        (MENU_ACTION, (ACTION_FIT, ACTION_ZOOM_IN, ACTION_ZOOM_OUT, ACTION_ROTATE_LEFT, ACTION_ROTATE_RIGHT)),
        (MENU_HELP, (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,)),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_OPEN,),
        (ACTION_FIT, ACTION_ZOOM_IN, ACTION_ZOOM_OUT, ACTION_ROTATE_LEFT, ACTION_ROTATE_RIGHT),
        (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    main_path = os.path.split(os.path.realpath(__file__))[0]
    
    main_title = "Image Viewer"
    main_iconfile = os.path.join(main_path, "pimgview.png")
    
    main_size = SIZE_MAXIMIZED
    
    main_widget = tabwidget('images', [])
    
    view_class = get_toolkit_class('imageview', 'PImageView')
    
    filenames_to_open = None
    
    def check_file_open(self, filename):
        if os.path.isfile(filename):
            print("Opening", filename)
            self.loader.open_filename(filename)
        else:
            print(filename, "not found!")
            self.filenames_not_found.append(filename)
    
    def after_create(self):
        # Call this here for safety since some toolkits won't support it until after the app object is created
        IMAGE_EXTENSIONS.extend(sorted(self.view_class.supported_formats()))
        self.filenames = []
        self.views = []
        self.loader = ImageFileLoader(self)
        self.filenames_not_found = []
        for filename in (self.filenames_to_open or ()):
            self.check_file_open(filename)
    
    def add_file(self, filename):
        self.filenames.append(filename)
        view = self.view_class(self, self.tabwidget_images, filename)
        self.views.append(view)
        self.tabwidget_images.append_and_focus((os.path.basename(filename), view))
    
    def on_app_shown(self):
        if self.filenames_not_found:
            self.message_box.error("File Error", "Files {} not found".format(self.filenames_not_found))
    
    def on_file_open(self):
        self.loader.open_file()
    
    def set_status_text(self, text):
        print(text)
        self.main_window.statusbar.set_text(text)
    
    def on_files_selected(self, index):
        self.set_status_text("Viewing file: {}".format(self.filenames[index]))
    
    def selected_view(self):
        return self.views[self.tabwidget_images.current_index()]
    
    def on_fit(self):
        self.selected_view().fit_to_window()
    
    zoom_factor = 1.5
    
    def on_zoom_in(self):
        self.selected_view().zoom_by(self.zoom_factor)
    
    def on_zoom_out(self):
        self.selected_view().zoom_by(1.0 / self.zoom_factor)
    
    def on_rotate_left(self):
        self.selected_view().rotate_left()
    
    def on_rotate_right(self):
        self.selected_view().rotate_right()
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        ImageViewer.filenames_to_open = sys.argv[1:]
    ImageViewer().run()
