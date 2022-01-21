#!/usr/bin/env python3

import sys
from time import sleep
from ponytail.ponytail import Ponytail

ponytail = Ponytail()

ponytail.connectWindow(ponytail.getWindowId("gnome-terminal-server"))

if len(sys.argv) != 1:
    print(f"Sleeping for {str(sys.argv[1])}")
    sleep(int(sys.argv[1]))
else:
    print("Sleeping for 0.5")
    sleep(0.5)

ponytail.disconnect()

#import gi
#gi.require_version("Gtk", "3.0")
#gi.require_version("Gdk", "3.0")
#from gi.repository import Gdk
#
#keymap = Gdk.Keymap.get_for_display(Gdk.Display.get_default())
#keymap.get_entries_for_keyval(Gdk.keyval_from_name("Shift_L"))[1][0].keycode
#keymap.get_entries_for_keyval(Gdk.keyval_from_name("Control_L"))[1][0].keycode
#keymap.get_entries_for_keyval(Gdk.keyval_from_name("N"))[1][0].keycode


ponytail.connectWindow(ponytail.getWindowId("gnome-terminal-server"))

combo = [50, 37, 57]

for char in combo:
    sleep(0.1)
    ponytail.generateKeycodePress(char)

for char in combo:
    sleep(0.1)
    ponytail.generateKeycodeRelease(char)

ponytail.disconnect()
