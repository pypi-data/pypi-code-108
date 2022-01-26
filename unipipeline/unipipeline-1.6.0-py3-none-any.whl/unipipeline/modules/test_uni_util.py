import pytest

from unipipeline.utils.uni_util_color import UniUtilColor


@pytest.mark.parametrize('enabled,color,text,expected', [
    (True, UniUtilColor.COLOR_RED, 'some', '\u001b[31msome\u001b[0m'),
    (False, UniUtilColor.COLOR_RED, 'some', 'some'),
])
def test_color(enabled: bool, color: str, text: str, expected: str) -> None:
    uc = UniUtilColor(enabled)
    assert uc.color_it(color, text) == expected
