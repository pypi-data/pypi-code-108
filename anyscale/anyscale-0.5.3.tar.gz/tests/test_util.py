from typing import Any
from unittest.mock import patch

from anyscale.util import updating_printer


def test_updating_printer() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1")
            print_status("Step 2")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1"
        "\r          \r"
        "Step 2"
        "\r          \r"
        "Step 3"
        "\r          \r"
    )


def test_updating_printer_multiline() -> None:
    out = ""

    def mock_print(
        string: str, *args: Any, end: str = "\n", flush: bool = False, **kwargs: Any
    ) -> None:
        nonlocal out
        out += string
        out += end

    with patch("anyscale.util.print", new=mock_print), patch(
        "shutil.get_terminal_size"
    ) as get_terminal_size_mock:
        get_terminal_size_mock.return_value = (10, 24)
        with updating_printer() as print_status:
            print_status("Step 1\nExtra stuff")
            print_status("ExtraLongLine12345")
            print_status("ExtraLongLine12345\nExtra stuff")
            print_status("Step 3")

    assert out == (
        "\r          \r"
        "Step 1..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "ExtraLo..."
        "\r          \r"
        "Step 3"
        "\r          \r"
    )
