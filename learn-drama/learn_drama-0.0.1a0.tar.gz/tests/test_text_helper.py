"""Tests for test_helper package"""

import learn_drama.text_helper as th


def test_check_text_for_line_break_string_positive():
    assert "eins\nzwei" == th.check_line_break_string("eins\\nzwei")


def test_check_text_for_line_break_string_nothing_to_do():
    assert "eins\nzwei" == th.check_line_break_string("eins\nzwei")
