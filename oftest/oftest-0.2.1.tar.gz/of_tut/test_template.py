
import os
import pytest
import oftest
from oftest import run_reset_case

# file_mod =  { "system/controlDict": [] }

# dir_name = os.path.dirname(os.path.abspath(__file__))
# c = oftest.Case_modifiers(file_mod,dir_name)

# @pytest.mark.parametrize("run_reset_case",[c], indirect=True)
def test_completed(run_reset_case):
    log = oftest.path_log()
    assert oftest.case_status(log) == 'completed'

