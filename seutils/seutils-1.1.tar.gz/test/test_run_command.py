import pytest
import fakefs
import seutils

def test_run_command_rcode_and_output():
    rcode, output = seutils.run_command_rcode_and_output(['echo', 'test'])
    assert rcode == 0
    assert output == ['test\n']

def test_run_command_rcode_and_output_nonexistingdir():
    rcode, output = seutils.run_command_rcode_and_output(['ls', 'doesnotexist'])
    assert rcode != 0

def test_run_command():
    output = seutils.run_command(['echo', 'test'])
    assert output == ['test\n']
    with pytest.raises(seutils.NonZeroExitCode):
        seutils.run_command(['ls', 'doesnotexist'])
    with pytest.raises(seutils.NoSuchPath):
        seutils.run_command(['cd', 'doesnotexist'], rcodes={1: seutils.NoSuchPath})

def test_get_exitcode():
    assert seutils.get_exitcode(['echo']) == 0
    assert seutils.get_exitcode(['ls', 'doesnotexist']) > 0
