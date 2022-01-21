import sys
import os
sys.path.insert(0, os.path.join(__file__, '../..'))

import nose

import tkinter as tk

from marlowe_ui.gui_xtal_layer_elem import XtalLayerElem

def test_initiate():
    xtal_layer_elem = XtalLayerElem(tk.Tk())
