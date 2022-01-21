import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.tktool import oneof

def test_initiate():
    import tkinter as tk

    c = oneof.OneofFactory(tk.Frame, None)
