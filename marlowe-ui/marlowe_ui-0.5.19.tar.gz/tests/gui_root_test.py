import sys
import os
sys.path.insert(0, os.path.join(__file__, '../..'))

import nose

import tkinter as tk

from marlowe_ui.gui_root import Root

def test_initiate():
    Root(tk.Tk())
