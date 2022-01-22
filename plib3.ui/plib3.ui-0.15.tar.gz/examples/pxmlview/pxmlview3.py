#!/usr/bin/env python3
"""
PXMLVIEW.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A simple read-only XML file viewer.
"""

import sys
import os
import io
import xml.etree.ElementTree as etree

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.fileaware import PFileAware
from plib.ui.widgets import *


def get_xml_node_tree(node):
    # Translate node into form suitable for tree view widget
    cols = (
        node.tag,
        ", ".join("{}={}".format(key, value) for key, value in node.items()),
        node.text,
        node.tail,
    )
    children = [get_xml_node_tree(child) for child in list(node)]
    return (cols, children)


def get_xml_tree(filename):
    # Parse XML file into a tree of PTreeView data
    xml = etree.parse(filename)
    return [get_xml_node_tree(xml.getroot())]


class XMLFileLoader(PFileAware):
    
    def __init__(self, app):
        PFileAware.__init__(self, app, [
            ("XML Files", ["xml"]),
            ("All Files", ["*"]),
        ], file_path=app.main_path)
    
    def open_data(self, filename):
        self.app.add_file(filename, get_xml_tree(filename))
        self.close_file()  # to be ready for the next load
    
    def save_data(self, filename):
        pass  # this app does not edit/save files


class XMLViewer(PApplication):
    
    about_data = {
        'name': "XMLViewer",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "XML File Viewer",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net",
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    menu_actions = [
        (MENU_FILE, (ACTION_FILE_OPEN, ACTION_EXIT,)),
        (MENU_HELP, (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT,)),
    ]
    
    toolbar_actions = [
        (ACTION_FILE_OPEN,),
        (ACTION_ABOUT, ACTION_ABOUT_TOOLKIT, ACTION_EXIT,),
    ]
    
    main_path = os.path.split(os.path.realpath(__file__))[0]
    
    main_title = "XML File Viewer"
    main_iconfile = os.path.join(main_path, "pxmlview.png")
    
    main_size = SIZE_MAXIMIZED
    large_icons = True
    
    main_widget = tabwidget('files', [])
    
    view_class = get_toolkit_class('listview', 'PTreeView')
    view_header = ["Tag", "Attrs", "Text", "Tail"]
    view_font_size = 16 if sys.platform == 'darwin' else 12
    
    filenames_to_open = None
    
    def check_file_open(self, filename):
        if os.path.isfile(filename):
            print("Opening", filename)
            self.loader.open_filename(filename)
        else:
            print(filename, "not found!")
            self.filenames_not_found.append(filename)
    
    def after_create(self):
        self.filenames = []
        self.loader = XMLFileLoader(self)
        self.filenames_not_found = []
        for filename in (self.filenames_to_open or ()):
            self.check_file_open(filename)
    
    def add_file(self, filename, data):
        self.filenames.append(filename)
        font_size = self.view_font_size
        view = self.view_class(self, self.tabwidget_files, labels=self.view_header, data=data, auto_expand=True,
                               font=("Arial", font_size), header_font=("Arial", font_size, True))
        self.tabwidget_files.append_and_focus((os.path.basename(filename), view))
    
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
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        XMLViewer.filenames_to_open = sys.argv[1:]
    XMLViewer().run()
