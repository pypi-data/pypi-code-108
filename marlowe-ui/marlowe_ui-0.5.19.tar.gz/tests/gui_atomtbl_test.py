import sys
import os
sys.path.insert(0, os.path.join(__file__, '../..'))

import nose

import tkinter as tk

from marlowe_ui import gui_atomtbl

def test_initiate():
    gui_atomtbl.AtomTbl(tk.Tk())
