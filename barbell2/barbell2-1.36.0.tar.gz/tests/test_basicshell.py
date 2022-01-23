import pytest

from barbell2.lib import BasicShell


NR_RESULTS = 4


@pytest.fixture
def shell():
    shell = BasicShell()
    for i in range(NR_RESULTS):
        shell.add_result([i] * 5, desc='Array of numbers ({})'.format(i))
    return shell


def test_has_two_results(shell):
    assert len(shell.results.keys()) == NR_RESULTS


def test_results_have_correct_names(shell):
    for i in range(NR_RESULTS):
        assert 'result_{}'.format(i) in shell.results.keys()


def test_last_result_is_current(shell):
    last_key = sorted(shell.results.keys(), reverse=False)[-1]
    assert last_key == shell.current_key


def test_undo_redo(shell):
    key_list = sorted(shell.results.keys(), reverse=False)
    shell.do_undo()
    assert shell.current_key == key_list[-2]
    shell.do_redo()
    assert shell.current_key == key_list[-1]
