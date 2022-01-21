import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.tktool import gui_abstract

def test_initiate():
    c = gui_abstract.GUIAbstract()
