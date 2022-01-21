import sys
import os
sys.path.insert(0, os.path.join(__file__, '..', '..'))

import nose  # noQA

from marlowe_ui import guidata


def test_initiate():
    c = guidata.root_example  # noQA
    d = guidata.root_default  # noQA
