#!/usr/bin/env python3
"""
UI-TEXT.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A demo app to test the text display control and the
TextOutput file-like object wrapper for it.
"""

import sys
import os

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.output import PTextOutput
from plib.ui.widgets import *


class UITextOutputTester(PApplication):
    
    about_data = {
        'name': "UITextOutputTester",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "UI Text Output Test Demo",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net"
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    main_title = "UI Text Output Tester"
    
    main_size = SIZE_OFFSET
    width_offset = height_offset = 50
    main_placement = MOVE_CENTER
    
    main_widget = frame(ALIGN_JUST, LAYOUT_VERTICAL, [
        panel(ALIGN_TOP, LAYOUT_HORIZONTAL, [
            panel(ALIGN_JUST, LAYOUT_HORIZONTAL, [
                edit('text'),
            ]),
            panel(ALIGN_RIGHT, LAYOUT_HORIZONTAL, [
                button('add', "Add Text"),
                num_edit('num'),
                label('num', "times"),
                button('clear', "Clear Text"),
            ]),
        ]),
        text('output', font=("Courier New", 12)),
        panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, [
            labeled("Text Size:", label('size', "", font=(None, None, True)), LAYOUT_HORIZONTAL, ALIGN_LEFT, label_bold=False),
            label('unit', "Bytes"),
        ]),
    ])
    
    def after_create(self):
        self.outputfile = PTextOutput(self.text_output)
        self.edit_text.edit_text = "This is a line of text to be added to the text display."
        self.edit_num.edit_value = 100
        self.update_size()
    
    def update_size(self):
        s = self.outputfile.filesize
        print(s)
        self.label_size.caption = str(s)
    
    def add_output(self, s):
        self.outputfile.write(s)
        self.outputfile.write(os.linesep)
        self.outputfile.flush()
    
    def on_add_clicked(self):
        text = self.edit_text.edit_text
        if text:
            for _ in range(self.edit_num.edit_value):
                self.add_output(text)
            self.update_size()
    
    on_text_enter = on_add_clicked
    
    def on_clear_clicked(self):
        self.outputfile.clear()
        self.update_size()


if __name__ == "__main__":
    UITextOutputTester().run()
