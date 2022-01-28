import pytest
from finesse.script.containers import KatFile, KatElement, KatKwarg
from finesse.script.exceptions import KatScriptError
from .....util import dedent_multiline
from ..util import NAME, NUMBER, SPACE, EQUALS


@pytest.fixture
def three_components():
    """Kat file representing three components."""
    return KatFile(
        dedent_multiline(
            """
            fake_component mycomponent1 A=1 B=2
            fake_component mycomponent2 A=3 B=4
            fake_component mycomponent3 A=5 B=6

            fake_component mycomponent4 A=7 B=8
            fake_component mycomponent5 A=9 B=10
            """
        )
    )


@pytest.mark.parametrize(
    "error_items,error",
    (
        # Only lines 1 and 2 are shown because the error is on the first line.
        (
            [[NAME(1, 16, "mycomponent1")]],
            (
                "line 1: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                     ^^^^^^^^^^^^\n"
                "   2: fake_component mycomponent2 A=3 B=4"
            ),
        ),
        # Lines 1-3 shown.
        (
            [[NAME(2, 16, "mycomponent2")]],
            (
                "line 2: __error_msg__\n"
                "   1: fake_component mycomponent1 A=1 B=2\n"
                "-->2: fake_component mycomponent2 A=3 B=4\n"
                "                     ^^^^^^^^^^^^\n"
                "   3: fake_component mycomponent3 A=5 B=6"
            ),
        ),
        # Lines 2-4 shown.
        (
            [[NAME(3, 16, "mycomponent3")]],
            (
                "line 3: __error_msg__\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "-->3: fake_component mycomponent3 A=5 B=6\n"
                "                     ^^^^^^^^^^^^\n"
                "   4: "
            ),
        ),
        # Lines 4-6 shown.
        (
            [[NAME(5, 16, "mycomponent4")]],
            (
                "line 5: __error_msg__\n"
                "   4: \n"
                "-->5: fake_component mycomponent4 A=7 B=8\n"
                "                     ^^^^^^^^^^^^\n"
                "   6: fake_component mycomponent5 A=9 B=10"
            ),
        ),
        # Only lines 6 and 7 are shown because the error is on the last line.
        (
            [[NAME(6, 16, "mycomponent5")]],
            (
                "line 6: __error_msg__\n"
                "   5: fake_component mycomponent4 A=7 B=8\n"
                "-->6: fake_component mycomponent5 A=9 B=10\n"
                "                     ^^^^^^^^^^^^"
            ),
        ),
    ),
)
def test_token_error(three_components, error_items, error):
    exception = KatScriptError("__error_msg__", three_components, error_items)
    assert exception.message() == error


@pytest.mark.parametrize(
    "error_items,error",
    (
        pytest.param(
            [
                [
                    KatElement(
                        directive=NAME(1, 1, "fake_component"),
                        name=NAME(1, 16, "mycomponent1"),
                        arguments=[
                            KatKwarg(
                                key=NAME(1, 29, "A"),
                                value=NUMBER(1, 31, "1"),
                                extra=[EQUALS(1, 30)],
                            ),
                            KatKwarg(
                                key=NAME(1, 33, "B"),
                                value=NUMBER(1, 35, "2"),
                                extra=[EQUALS(1, 34)],
                            ),
                        ],
                        extra=[SPACE(1, 15), SPACE(1, 28)],
                    )
                ]
            ],
            (
                "line 1: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                "   2: fake_component mycomponent2 A=3 B=4"
            ),
            id="error on first line",
        ),
        pytest.param(
            [
                [
                    KatElement(
                        directive=NAME(2, 1, "fake_component"),
                        name=NAME(2, 16, "mycomponent2"),
                        arguments=[
                            KatKwarg(
                                key=NAME(2, 29, "A"),
                                value=NUMBER(2, 31, "3"),
                                extra=[EQUALS(2, 30)],
                            ),
                            KatKwarg(
                                key=NAME(2, 33, "B"),
                                value=NUMBER(2, 35, "4"),
                                extra=[EQUALS(2, 34)],
                            ),
                        ],
                        extra=[SPACE(2, 15), SPACE(2, 28)],
                    ),
                ]
            ],
            (
                "line 2: __error_msg__\n"
                "   1: fake_component mycomponent1 A=1 B=2\n"
                "-->2: fake_component mycomponent2 A=3 B=4\n"
                "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                "   3: fake_component mycomponent3 A=5 B=6"
            ),
            id="error on intermediate (second) line",
        ),
        pytest.param(
            [
                [
                    KatElement(
                        directive=NAME(3, 1, "fake_component"),
                        name=NAME(3, 16, "mycomponent3"),
                        arguments=[
                            KatKwarg(
                                key=NAME(3, 29, "A"),
                                value=NUMBER(3, 31, "5"),
                                extra=[EQUALS(3, 30)],
                            ),
                            KatKwarg(
                                key=NAME(3, 33, "B"),
                                value=NUMBER(3, 35, "6"),
                                extra=[EQUALS(3, 34)],
                            ),
                        ],
                        extra=[SPACE(3, 15), SPACE(3, 28)],
                    ),
                ]
            ],
            (
                "line 3: __error_msg__\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "-->3: fake_component mycomponent3 A=5 B=6\n"
                "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                "   4: "
            ),
            id="error on intermediate (third) line",
        ),
        pytest.param(
            [
                [
                    KatElement(
                        directive=NAME(5, 1, "fake_component"),
                        name=NAME(5, 16, "mycomponent4"),
                        arguments=[
                            KatKwarg(
                                key=NAME(5, 29, "A"),
                                value=NUMBER(5, 31, "7"),
                                extra=[EQUALS(5, 30)],
                            ),
                            KatKwarg(
                                key=NAME(5, 33, "B"),
                                value=NUMBER(5, 35, "8"),
                                extra=[EQUALS(5, 34)],
                            ),
                        ],
                        extra=[SPACE(5, 15), SPACE(5, 28)],
                    ),
                ]
            ],
            (
                "line 5: __error_msg__\n"
                "   4: \n"
                "-->5: fake_component mycomponent4 A=7 B=8\n"
                "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^\n"
                "   6: fake_component mycomponent5 A=9 B=10"
            ),
            id="error on intermediate (fifth) line",
        ),
        pytest.param(
            [
                [
                    KatElement(
                        directive=NAME(6, 1, "fake_component"),
                        name=NAME(6, 16, "mycomponent5"),
                        arguments=[
                            KatKwarg(
                                key=NAME(6, 29, "A"),
                                value=NUMBER(6, 31, "9"),
                                extra=[EQUALS(6, 30)],
                            ),
                            KatKwarg(
                                key=NAME(6, 33, "B"),
                                value=NUMBER(6, 35, "10"),
                                extra=[EQUALS(6, 34)],
                            ),
                        ],
                        extra=[SPACE(6, 15), SPACE(6, 28)],
                    ),
                ]
            ],
            (
                "line 6: __error_msg__\n"
                "   5: fake_component mycomponent4 A=7 B=8\n"
                "-->6: fake_component mycomponent5 A=9 B=10\n"
                "      ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^"
            ),
            id="error on last line",
        ),
    ),
)
def test_element_error(three_components, error_items, error):
    exception = KatScriptError("__error_msg__", three_components, error_items)
    assert exception.message() == error


@pytest.mark.parametrize(
    "error_items,error",
    (
        # Only lines 1 and 2 are shown because the error is on the first line.
        (
            [
                [
                    KatElement(
                        directive=NAME(1, 1, "fake_component"),
                        name=NAME(1, 16, "mycomponent1"),
                        arguments=[
                            KatKwarg(
                                key=NAME(1, 29, "A"),
                                value=NUMBER(1, 31, "1"),
                                extra=[EQUALS(1, 30)],
                            ),
                            KatKwarg(
                                key=NAME(1, 29, "A"),
                                value=NUMBER(1, 35, "2"),
                                extra=[EQUALS(1, 34)],
                            ),
                        ],
                        extra=[SPACE(1, 15), SPACE(1, 28)],
                    ),
                    NUMBER(1, 31, "1"),
                ]
            ],
            (
                "line 1: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                                    ^\n"
                "   2: fake_component mycomponent2 A=3 B=4"
            ),
        ),
        # Lines 1-3 shown.
        (
            [
                [
                    KatElement(
                        directive=NAME(2, 1, "fake_component"),
                        name=NAME(2, 16, "mycomponent2"),
                        arguments=[
                            KatKwarg(
                                key=NAME(2, 29, "A"),
                                value=NUMBER(2, 31, "3"),
                                extra=[EQUALS(2, 30)],
                            ),
                            KatKwarg(
                                key=NAME(2, 33, "B"),
                                value=NUMBER(2, 35, "4"),
                                extra=[EQUALS(2, 34)],
                            ),
                        ],
                        extra=[SPACE(2, 15), SPACE(2, 28)],
                    ),
                    NUMBER(2, 35, "4"),
                ]
            ],
            (
                "line 2: __error_msg__\n"
                "   1: fake_component mycomponent1 A=1 B=2\n"
                "-->2: fake_component mycomponent2 A=3 B=4\n"
                "                                        ^\n"
                "   3: fake_component mycomponent3 A=5 B=6"
            ),
        ),
        # Lines 2-4 shown.
        (
            [
                [
                    KatElement(
                        directive=NAME(3, 1, "fake_component"),
                        name=NAME(3, 16, "mycomponent3"),
                        arguments=[
                            KatKwarg(
                                key=NAME(3, 29, "A"),
                                value=NUMBER(3, 31, "5"),
                                extra=[EQUALS(3, 30)],
                            ),
                            KatKwarg(
                                key=NAME(3, 29, "A"),
                                value=NUMBER(3, 35, "6"),
                                extra=[EQUALS(3, 34)],
                            ),
                        ],
                        extra=[SPACE(3, 15), SPACE(3, 28)],
                    ),
                    NAME(3, 29, "A"),
                ]
            ],
            (
                "line 3: __error_msg__\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "-->3: fake_component mycomponent3 A=5 B=6\n"
                "                                  ^\n"
                "   4: "
            ),
        ),
        # Lines 4-6 shown.
        (
            [
                [
                    KatElement(
                        directive=NAME(5, 1, "fake_component"),
                        name=NAME(5, 16, "mycomponent4"),
                        arguments=[
                            KatKwarg(
                                key=NAME(5, 29, "A"),
                                value=NUMBER(5, 31, "7"),
                                extra=[EQUALS(5, 30)],
                            ),
                            KatKwarg(
                                key=NAME(5, 33, "A"),
                                value=NUMBER(5, 35, "8"),
                                extra=[EQUALS(5, 34)],
                            ),
                        ],
                        extra=[SPACE(5, 15), SPACE(5, 28)],
                    ),
                    NAME(5, 29, "A"),
                ]
            ],
            (
                "line 5: __error_msg__\n"
                "   4: \n"
                "-->5: fake_component mycomponent4 A=7 B=8\n"
                "                                  ^\n"
                "   6: fake_component mycomponent5 A=9 B=10"
            ),
        ),
        # Only lines 5 and 6 are shown because the error is on the last line.
        (
            [
                [
                    KatElement(
                        directive=NAME(6, 1, "fake_component"),
                        name=NAME(6, 16, "mycomponent5"),
                        arguments=[
                            KatKwarg(
                                key=NAME(6, 29, "A"),
                                value=NUMBER(6, 31, "9"),
                                extra=[EQUALS(6, 30)],
                            ),
                            KatKwarg(
                                key=NAME(6, 29, "A"),
                                value=NUMBER(6, 35, "10"),
                                extra=[EQUALS(6, 34)],
                            ),
                        ],
                        extra=[SPACE(6, 15), SPACE(6, 28)],
                    ),
                    NAME(6, 29, "A"),
                ]
            ],
            (
                "line 6: __error_msg__\n"
                "   5: fake_component mycomponent4 A=7 B=8\n"
                "-->6: fake_component mycomponent5 A=9 B=10\n"
                "                                  ^"
            ),
        ),
    ),
)
def test_token_error_inside_element(three_components, error_items, error):
    exception = KatScriptError("__error_msg__", three_components, error_items)
    assert exception.message() == error


@pytest.mark.parametrize(
    "error_items,error",
    (
        # Errors on lines 1 and 3; lines 1-4 shown.
        (
            [[NUMBER(1, 31, "1")], [NUMBER(3, 31, "5")]],
            (
                "lines 1 and 3: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                                    ^\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "-->3: fake_component mycomponent3 A=5 B=6\n"
                "                                    ^\n"
                "   4: "
            ),
        ),
        # Errors on lines 1 and 5; lines 1-2, 4-6 shown; 1 missing line message shown.
        (
            [[NUMBER(1, 31, "1")], [NUMBER(5, 31, "7")]],
            (
                "lines 1 and 5: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                                    ^\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "      *** 1 skipped line ***\n"
                "   4: \n"
                "-->5: fake_component mycomponent4 A=7 B=8\n"
                "                                    ^\n"
                "   6: fake_component mycomponent5 A=9 B=10"
            ),
        ),
        # Errors on lines 1 and 6; lines 1-2, 5-6 shown; 2 missing lines message shown.
        (
            [[NUMBER(1, 31, "1")], [NUMBER(6, 31, "9")]],
            (
                "lines 1 and 6: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                                    ^\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "      *** 2 skipped lines ***\n"
                "   5: fake_component mycomponent4 A=7 B=8\n"
                "-->6: fake_component mycomponent5 A=9 B=10\n"
                "                                    ^"
            ),
        ),
    ),
)
def test_errors_in_separate_locations(three_components, error_items, error):
    exception = KatScriptError("__error_msg__", three_components, error_items)
    assert exception.message() == error


@pytest.mark.parametrize(
    "error_items,error",
    (
        # Error on line 1: lines 1-3 shown.
        (
            [[NUMBER(1, 31, "1")]],
            (
                "line 1: __error_msg__\n"
                "-->1: fake_component mycomponent1 A=1 B=2\n"
                "                                    ^\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "   3: fake_component mycomponent3 A=5 B=6"
            ),
        ),
        # Error on line 3: lines 1-5 shown.
        (
            [[NUMBER(3, 31, "1")]],
            (
                "line 3: __error_msg__\n"
                "   1: fake_component mycomponent1 A=1 B=2\n"
                "   2: fake_component mycomponent2 A=3 B=4\n"
                "-->3: fake_component mycomponent3 A=5 B=6\n"
                "                                    ^\n"
                "   4: \n"
                "   5: fake_component mycomponent4 A=7 B=8"
            ),
        ),
        # Error on line 5: lines 3-6 shown.
        (
            [[NUMBER(5, 31, "1")]],
            (
                "line 5: __error_msg__\n"
                "   3: fake_component mycomponent3 A=5 B=6\n"
                "   4: \n"
                "-->5: fake_component mycomponent4 A=7 B=8\n"
                "                                    ^\n"
                "   6: fake_component mycomponent5 A=9 B=10"
            ),
        ),
        # Error on line 6: lines 4-6 shown.
        (
            [[NUMBER(6, 31, "1")]],
            (
                "line 6: __error_msg__\n"
                "   4: \n"
                "   5: fake_component mycomponent4 A=7 B=8\n"
                "-->6: fake_component mycomponent5 A=9 B=10\n"
                "                                    ^"
            ),
        ),
    ),
)
def test_nondefault_max_buffer_lines(monkeypatch, three_components, error_items, error):
    """Test setting to control extra lines shown before and after the error line."""
    monkeypatch.setattr(KatScriptError, "MAX_BUFFER_LINES", 2, raising=True)
    exception = KatScriptError("__error_msg__", three_components, error_items)
    assert exception.message() == error
