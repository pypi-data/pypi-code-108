import sys
import os
sys.path.insert(0, os.path.join(__file__, '../..'))

import nose

import tkinter as tk

from marlowe_ui import gui_outp

def test_outpinform_initiate():
    gui_outp.OutpInform(tk.Tk())

def test_outp_initiate():
    gui_outp.Outp(tk.Tk())
