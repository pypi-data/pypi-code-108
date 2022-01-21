from io import TextIOBase
from pathlib import Path
from typing import Optional, Union


def write_output(
    content: str,
    output: Optional[Union[TextIOBase, str, Path]] = None,
    encoding: Optional[str] = None,
) -> None:
    if isinstance(output, (str, Path)):
        with open(output, "w", encoding=encoding) as file:
            file.write(content)
        return

    if isinstance(output, TextIOBase):
        output.write(content)
        return

    raise ValueError(f"Unsupported output type: {type(output)}")
