import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.tktool import gui_checkframe

def test_initiate():
    import tkinter as tk

    gui_checkframe.gui_checkframe(tk.Tk(), tk.Frame)
