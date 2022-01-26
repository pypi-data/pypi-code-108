from unittest.mock import patch

from zhaostephen.rebrn._internal import table_printer


@patch('builtins.print')
def test_table_printer(mock_print):
    # Given
    table = [
        ["1", "11", "111", "1111"],
        ["1", "11", "111", "1111"],
        ["1111", "1111", "1111", "1111"],
    ]
    expected_out = (
"""   1    1 1111
  11   11 1111
 111  111 1111
1111 1111 1111"""
    )

    # When
    table_printer.print_table_by_columns(table)
    
    # Then
    mock_print.assert_called_with(expected_out)
