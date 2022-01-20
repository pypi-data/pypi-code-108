#!/usr/bin/env python3
"""
PYIDSERVER-UI.PY
Copyright (C) 2008-2022 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

A UI wrapper around the pyidserver example program from
the PLIB.STDLIB package.
"""

import sys
import os
import datetime
import urllib.parse

from plib.ui import __version__
from plib.ui.defs import *
from plib.ui.app import PApplication
from plib.ui.output import PTextOutput
from plib.ui.socket import PSocketTransport
from plib.ui.widgets import *


def _load_example_module():
    from plib.stdlib.imp import import_from_path
    from plib.stdlib.postinstall import get_share_dir
    
    return import_from_path(
        os.path.join(
            get_share_dir('plib3.stdlib', 'plib.stdlib'),
            'examples', 'pyidserver'
        ),
        'pyidserver3'
    )


pyidserver = _load_example_module()


PROTOCOL_MAP = {proto: items[0] for proto, items in pyidserver.protocols.items()}

DEFAULT_DNSONLY = pyidserver.run_main.__defaults__[2]
DEFAULT_PROTOCOL = pyidserver.run_main.__defaults__[3]
DEFAULT_PORTNUM = pyidserver.run_main.__defaults__[4]


class IDServerUIClient(pyidserver.IDServerClient):
    
    def __init__(self, transport, fileobj, frame):
        super(IDServerUIClient, self).__init__(transport, fileobj)
        self.frame = frame
    
    def on_close(self):
        super(IDServerUIClient, self).on_close()
        self.frame.done()


CAPTION_GO = "&Go"
ICON_GO = ACTION_OK
CAPTION_STOP = "&Stop"
ICON_STOP = ACTION_CANCEL


class IDServerApp(PApplication):
    
    about_data = {
        'name': "PyIDServer",
        'version': "{} on Python {}".format(
            __version__,
            sys.version.split()[0]
        ),
        'description': "A Python UI for IDServer",
        'copyright': "Copyright (C) 2008-2022 by Peter A. Donis",
        'license': "GNU General Public License (GPL) Version 2",
        'developer': "Peter Donis",
        'website': "http://www.peterdonis.net",
    }
    
    about_format = "{name} {version}\n\n{description}\n\n{copyright}\n{license}\n\nDeveloped by {developer}\n{website}"
    
    main_title = "PyIDServer"
    main_iconfile = os.path.join(os.path.split(os.path.realpath(__file__))[0],
                                 "pyidserver.png")
    
    main_size = SIZE_OFFSET
    width_offset = 640
    main_placement = MOVE_CENTER
    
    main_widget = frame(ALIGN_JUST, LAYOUT_VERTICAL, [
        panel(ALIGN_TOP, LAYOUT_HORIZONTAL, [
            edit('url'),
            button('go', CAPTION_GO, ICON_GO)
        ]),
        panel(ALIGN_JUST, LAYOUT_VERTICAL, [
            box(ALIGN_TOP, LAYOUT_HORIZONTAL, [
                panel(ALIGN_LEFT, LAYOUT_HORIZONTAL, [
                    checkbox('dnsonly', "DNS Only", DEFAULT_DNSONLY),
                    checkbox('protocol', "Set Protocol"),
                    sorted_combo('protocol', pyidserver.protocols.keys(), pyidserver.PROTO_DEFAULT),
                    checkbox('portnum', "Set Port"),
                    num_edit('portnum', DEFAULT_PORTNUM, expand=False)
                ]),
                padding()
            ]),
            text('output', font=("Courier New", 12))
        ]),
        panel(ALIGN_BOTTOM, LAYOUT_HORIZONTAL, [
            labeled("Transcript Dir:", label('directory', ""), LAYOUT_HORIZONTAL),
            button('select', "Select Dir"),
            button('save', "Save Transcript"),
            action_button(ACTION_ABOUT),
            action_button(ACTION_ABOUT_TOOLKIT),
            action_button(ACTION_EXIT)
        ])
    ])
    
    protocol_map = PROTOCOL_MAP
    
    default_protocol = DEFAULT_PROTOCOL
    default_portnum = DEFAULT_PORTNUM
    
    create_done = False
    client = None
    
    @property
    def outputs_on(self):
        return self.create_done and not self.client
    
    def after_create(self):
        """This method is called after all widgets are created, but before the app is shown.
        """
        
        # Controls affected by the DNS Only checkbox
        self.dnsonly_controls = (
            (self.checkbox_protocol, self.combo_protocol),
            (self.checkbox_portnum, self.edit_portnum)
        )
        
        # Controls independent of DNS Only checkbox
        self.other_controls = (
            self.edit_url,
            self.checkbox_dnsonly
        )
        
        self.on_dnsonly_toggled()  # technically not needed, put in for completeness
        self.on_protocol_toggled()  # initialize enable state of protocol combo
        self.on_portnum_toggled()  # initialize enable state of portnum edit
        
        # Set up socket transport
        self.transport = PSocketTransport()
        
        # Set up output file-like object here for convenience
        self.outputfile = PTextOutput(self.text_output)
        
        # Initialize transcript save dir
        self.transcript_dir = os.getcwd()
        self.update_dir_display()
        self.button_save.enabled = False
        
        # Start with keyboard focus in the URL text entry
        self.edit_url.set_focus()
        
        # Turn on diagnostic outputs
        self.create_done = True
    
    def on_dnsonly_toggled(self, checked=None):
        """Called when the dns_only checkbox is checked/unchecked.
        
        Only enable protocol and port controls if not DNS only.
        """
        
        if checked is not None:
            assert checked is self.checkbox_dnsonly.checked
        enable = not self.checkbox_dnsonly.checked
        for ctrl, subctrl in self.dnsonly_controls:
            ctrl.enabled = enable
            subctrl.enabled = enable and ctrl.checked
        if self.outputs_on:
            print("DNS Only", ("disabled", "enabled")[not enable])
    
    def on_protocol_toggled(self, checked=None):
        """Called when the protocol checkbox is checked/unchecked.
        
        Sync protocol combo enable with check box."""
        
        if checked is not None:
            assert checked is self.checkbox_protocol.checked
        self.combo_protocol.enabled = enable = self.checkbox_protocol.checked
        if self.outputs_on:
            print("Protocol selection", ("disabled", "enabled")[enable])
    
    def on_protocol_selected(self, index):
        """Called when a protocol combo selection is made.
        
        For now, just prints a diagnostic showing the signal response.
        """
        
        protocol = self.combo_protocol[index]
        if self.outputs_on:
            print("Protocol selected:", index, protocol)
        self.edit_portnum.edit_value = self.protocol_map[protocol]
    
    def on_portnum_toggled(self, checked=None):
        """Called when the portnum checkbox is checked/unchecked.
        
        Sync portnum edit enable with check box.
        """
        
        if checked is not None:
            assert checked is self.checkbox_portnum.checked
        self.edit_portnum.enabled = enable = self.checkbox_portnum.checked
        if self.outputs_on:
            print("Port selection", ("disabled", "enabled")[enable])
    
    def on_portnum_changed(self, value):
        """Called when a port number is entered.
        
        For now, just prints a diagnostic showing what was entered.
        """
        
        assert value == self.edit_portnum.edit_value
        if self.outputs_on:
            print("Port number entered:", self.edit_portnum.edit_value)
    
    def on_go_clicked(self):
        """Called when the Go/Stop button is pushed.
        
        Execute the idserver query, or stop a query in progress.
        For executing a query, this method is also called when the
        Enter key is pressed while in the URL edit box.
        """
        
        if self.client:
            print("Query in progress, stopping")
            self.client.close()
        
        else:
            print("Starting query")
            
            # Clear output
            self.outputfile.truncate(0)
            
            # Check URL
            url = self.edit_url.edit_text
            if len(url) < 1:
                self.outputfile.write("Error: No URL entered.")
                self.outputfile.flush()
                return
            
            # Fill in arguments that user selected, if any
            dns_only = self.checkbox_dnsonly.checked
            if self.checkbox_protocol.checked:
                protocol = self.combo_protocol.current_text()
            else:
                protocol = self.default_protocol
            if self.checkbox_portnum.checked:
                portnum = self.edit_portnum.edit_value
            else:
                portnum = self.default_portnum
            
            # Now execute
            for ctrl, subctrl in self.dnsonly_controls:
                ctrl.enabled = subctrl.enabled = False
            for ctrl in self.other_controls:
                ctrl.enabled = False
            self.button_go.set_caption(CAPTION_STOP)
            self.button_go.set_icon(ICON_STOP)
            
            self.client = IDServerUIClient(self.transport, self.outputfile, self)
            self.client.run(url, dns_only, protocol, portnum)
            
            print("Query done")
    
    def done(self):
        # Either we're done, or we've stopped a query in progress
        self.button_save.enabled = True
        self.button_go.set_caption(CAPTION_GO)
        self.button_go.set_icon(ICON_GO)
        for ctrl in self.other_controls:
            ctrl.enabled = True
        self.on_dnsonly_toggled()
        self.client = None
    
    on_url_enter = on_go_clicked  # so hitting Enter in the URL edit box also starts the query
    
    def update_dir_display(self):
        self.label_directory.caption = self.transcript_dir
    
    def on_select_clicked(self):
        new_dir = self.file_dialog.choose_directory(self.transcript_dir)
        if new_dir:
            self.transcript_dir = new_dir
            self.update_dir_display()
    
    def on_save_clicked(self):
        url = self.edit_url.edit_text
        if len(url) < 1:
            self.message_box.info("No Data", "No URL has been queried, nothing to save")
            return
        data = self.outputfile.read()
        if len(data) < 1:
            self.message_box.info("No Data", "No transcript data, nothing to save")
            return
        desc = url
        if self.checkbox_protocol.checked:
            desc = "{}://{}".format(self.combo_protocol.current_text(), desc)
        if self.checkbox_portnum.checked:
            desc = "{}:{}".format(desc, self.edit_portnum.edit_value)
        desc = urllib.parse.quote(desc, safe="")  # we want to quote any slashes as well
        filename = "pyidserver-ui_{}_{}.txt".format(desc, round(datetime.datetime.now().timestamp()))
        data = self.outputfile.read()
        with open(os.path.join(self.transcript_dir, filename), 'w') as f:
            f.write(data)
    
    def on_about(self):
        self.about()
    
    def on_about_toolkit(self):
        self.about_toolkit()
    
    def on_exit(self):
        self.exit_app()
    
    def on_app_closing(self):
        # If query is in progress, shut it down before closing
        if self.client:
            self.client.close()


if __name__ == "__main__":
    IDServerApp().run()
