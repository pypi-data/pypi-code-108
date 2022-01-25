from typing import Union, Optional
from pathlib import Path
import re


class VarDoc:
    """
    Create a table of variables from a Python script. The variables are assumed to be commented like:

    ```
    # This is the comment.
    VAR: int = 0
    ```

    ...and the output will be this:

    | Variable | Type | Value | Description |
    | --- | --- | --- | --- |
    | `VAR` | int | 0 | This is the comment. |
    """

    @staticmethod
    def get(src: Union[str, Path], dst: Optional[Union[str, Path]] = None) -> str:
        """
        :param src: The path to the source file. Can be a string or Path object.
        :param dst: The path to the destination file. If None, don't write a file. Otherwise, can be a string or Path object.

        :return: The text of the API document.
        """

        if isinstance(src, str):
            src = Path(src)
        assert src.exists(), f"Not found: {src.resolve()}"
        txt = src.read_text()
        variables = re.findall(r"#(.*?)\n(.*?)=(.*?)\n", txt, flags=re.MULTILINE)
        if len(variables) == 0:
            return ""
        table = "| Variable | Type | Value | Description |\n| --- | --- | --- | --- |\n"
        for v in variables:
            desc = v[0].strip()
            name = v[1].strip()
            if ":" in name:
                name_split = v[1].split(":")
                name = name_split[0].strip()
                v_type = name_split[1].strip()
            else:
                v_type = ""
            name = f"`{name}`"
            value = v[2].strip()
            table += f"| {name} | {v_type} | {value} | {desc} |\n"
        doc = f"# {src.parent.parts[-1]}.{src.name[:-3]}\n\n{table}"
        if dst is not None:
            if isinstance(dst, str):
                dst = Path(dst)
            dst.write_text(doc)
        return doc
