import sys
import os
sys.path.insert(0, os.path.join(__file__, '../../..'))

import nose

from marlowe_ui.physics import element

def test_initiate():
    a = element.table_bynum[1]
    b = element.table_bysym['H']
    c = element.table_byname['hydrogen']
