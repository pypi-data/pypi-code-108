
from scaleup import *

def test_create_simulation_no_values():
    actual = create_simulation_scenario('scenName', 'dsName')
    assert actual == 'scenName~dsName'


def test_create_simulation_no_values_escape_tilde():
    actual = create_simulation_scenario('scen~Name', 'dsName')
    assert actual == 'scen&TLD;Name~dsName'
    


def test_create_simulation_param_values():
    actual = create_simulation_scenario('scenName', 'dsName', 1, 2, 3, 4, 5)
    assert actual == 'scenName~dsName~1~2~3~4~5'


# no options selected, defaults to showing the UI
def test_create_script_option_string_defaults():
    actual = create_script_option_string()
    assert actual == 'SHOWUI:TRUE'


# show ui, default reader
def test_create_script_option_string_show_ui():
    actual = create_script_option_string(True)
    assert actual == 'SHOWUI:TRUE'


# hide ui, default reader
def test_create_script_option_string_hide_ui():
    actual = create_script_option_string(False)
    assert actual == ''


# show ui, alt reader
def test_create_script_option_string_altreader():
    actual = create_script_option_string(altReader = True)
    assert actual == 'SHOWUI:TRUE~ALTREADER:TRUE'


    # show ui, alt reader
def test_create_script_option_string_hide_ui_altreader():
    actual = create_script_option_string(False, True)
    assert actual == 'ALTREADER:TRUE'


def test_get_run_type():
    file_names = ['sim1.xls', 'sim1.xlsx', 'sim1.old.xlsx', 'sim1.xls.old', 'sim1.rxm', 'sim1.old.rxm']

    actual = [get_run_type(file_name) for file_name in file_names]
    expected = [1,1,1,0,2,2]

    assert expected == actual
  